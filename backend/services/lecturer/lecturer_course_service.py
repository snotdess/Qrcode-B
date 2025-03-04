from datetime import datetime
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from backend.models import Lecturer, Course, LecturerCourses, StudentCourses
from backend.utils import filter_records
from backend.util.lecturer_utils import validate_lecturer, count_lecturer_courses
from backend.errors.course_errors import (
    LecturerCourseAlreadyAssociatedError,
    CourseNotFoundError,
)

# --------------------
# LecturerCourseService Class
# --------------------


class LecturerCourseService:
    @staticmethod
    async def create_course_for_lecturer(
        course, db: AsyncSession, current_lecturer: Lecturer
    ):
        # Validate that the user is logged in as a lecturer.
        await validate_lecturer(current_lecturer)

        # Check if the course exists. If not, create a new course.
        existing_course = await filter_records(
            Course, db, course_code=course.course_code
        )
        if not existing_course:
            new_course = Course(
                course_code=course.course_code,
                course_name=course.course_name,
                course_credits=course.course_credits,
                semester=course.semester,
                creation_date=datetime.utcnow(),
            )
            db.add(new_course)
            await db.commit()
            await db.refresh(new_course)
        else:
            new_course = existing_course

        # Validate that the lecturer is not already associated with the course.
        lecturer_course = await filter_records(
            LecturerCourses,
            db,
            course_code=course.course_code,
            lecturer_id=current_lecturer.lecturer_id,
        )
        if lecturer_course:
            raise LecturerCourseAlreadyAssociatedError()

        # Create the association between the lecturer and the course.
        new_lecturer_course = LecturerCourses(
            lecturer_id=current_lecturer.lecturer_id, course_code=course.course_code
        )
        db.add(new_lecturer_course)
        await db.commit()

        return new_course

    @staticmethod
    async def fetch_courses_for_lecturer(
        db: AsyncSession, lecturer_id: int
    ) -> List[Course]:
        result = await db.execute(
            select(Course)
            .join(LecturerCourses, LecturerCourses.course_code == Course.course_code)
            .where(LecturerCourses.lecturer_id == lecturer_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_courses_for_lecturer(
        db: AsyncSession, current_lecturer: Lecturer
    ) -> List[Course]:
        # Validate current lecturer
        await validate_lecturer(current_lecturer)
        courses = await LecturerCourseService.fetch_courses_for_lecturer(
            db, current_lecturer.lecturer_id
        )
        return courses or []

    @staticmethod
    async def get_courses_stats(db: AsyncSession, current_lecturer: Lecturer):
        # Validate current lecturer
        await validate_lecturer(current_lecturer)
        courses = await LecturerCourseService.fetch_courses_for_lecturer(
            db, current_lecturer.lecturer_id
        )
        return {
            "total_courses": len(courses),
            "total_credits": (
                sum(course.course_credits for course in courses) if courses else 0
            ),
        }

    @staticmethod
    async def get_lecturer_courses(db: AsyncSession):
        result = await db.execute(
            select(Lecturer.lecturer_name, Course.course_code, Course.course_name)
            .join(LecturerCourses, Lecturer.lecturer_id == LecturerCourses.lecturer_id)
            .join(Course, LecturerCourses.course_code == Course.course_code)
        )
        lecturer_courses = result.fetchall()
        if lecturer_courses:
            return [
                {
                    "lecturer_name": row[0],
                    "course_code": row[1],
                    "course_name": row[2],
                }
                for row in lecturer_courses
            ]
        return {"message": "No lecturer-course records found."}

    @staticmethod
    async def get_lecturer_course_students(
        db: AsyncSession, current_lecturer: Lecturer
    ):
        # Validate current lecturer
        await validate_lecturer(current_lecturer)
        courses = await LecturerCourseService.fetch_courses_for_lecturer(
            db, current_lecturer.lecturer_id
        )
        if not courses:
            CourseNotFoundError()

        # Build the result list with student counts for each course.
        course_students = []
        for course in courses:
            total_students = await db.scalar(
                select(func.count(StudentCourses.matric_number)).where(
                    StudentCourses.course_code == course.course_code
                )
            )
            course_students.append(
                {
                    "course_name": course.course_name,
                    "total_students": total_students or 0,
                }
            )
        return course_students
