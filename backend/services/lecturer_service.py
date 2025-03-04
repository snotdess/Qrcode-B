from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.models import (
    Course,
    LecturerCourses,
    StudentCourses,
    AttendanceRecords,
    Student,
)
from backend.errors.course_errors import UnauthorizedLecturerCourseError
from typing import Dict


async def get_attendance_service(course_code: str, current_lecturer, db: AsyncSession):
    # Find the course by course_code
    course_query = select(Course).where(
        func.trim(Course.course_code) == func.trim(course_code)
    )
    course_result = await db.execute(course_query)
    course = course_result.scalars().first()

    if not course:
        return {
            "course_name": course_code,
            "attendance": [],
        }

    # Check if the lecturer is assigned to the course
    lecturer_course_query = select(LecturerCourses).where(
        (LecturerCourses.course_code == course.course_code)
        & (LecturerCourses.lecturer_id == current_lecturer.lecturer_id)
    )
    lecturer_course_result = await db.execute(lecturer_course_query)
    lecturer_course = lecturer_course_result.scalars().first()

    if not lecturer_course:
        UnauthorizedLecturerCourseError()

    # Find students enrolled in the course
    student_query = (
        select(Student.matric_number, Student.student_fullname)
        .join(StudentCourses, Student.matric_number == StudentCourses.matric_number)
        .where(StudentCourses.course_code == course.course_code)
    )
    student_result = await db.execute(student_query)
    students = student_result.fetchall()

    if not students:
        return {
            "course_name": course.course_name,
            "attendance": [],
        }

    # Get the last 5 attendance dates
    date_query = (
        select(AttendanceRecords.date)
        .where(AttendanceRecords.course_code == course.course_code)
        .order_by(AttendanceRecords.date.desc())
        .limit(5)
    )
    date_result = await db.execute(date_query)
    recent_dates = [record[0].strftime("%Y-%m-%d") for record in date_result.fetchall()]

    if not recent_dates:
        return {"course_name": course.course_name, "attendance": []}

    # Fetch attendance records for students
    attendance_query = select(
        AttendanceRecords.matric_number,
        AttendanceRecords.date,
        AttendanceRecords.status,
    ).where(AttendanceRecords.course_code == course.course_code)
    attendance_result = await db.execute(attendance_query)
    attendance_records = attendance_result.fetchall()

    if not attendance_records:
        return {"course_name": course.course_name, "attendance": []}

    # Organize attendance data
    attendance_dict: Dict[str, Dict] = {
        student[0]: {
            "matric_number": student[0],
            "full_name": student[1],
            "attendance": {
                date: "Absent" for date in recent_dates
            },  # Default to Absent
        }
        for student in students
    }

    for record in attendance_records:
        matric_no, date, status = record
        formatted_date = date.strftime("%Y-%m-%d")
        if formatted_date in recent_dates:
            attendance_dict[matric_no]["attendance"][formatted_date] = status

    # Convert to list for response
    return {
        "course_name": course.course_name,
        "attendance": list(attendance_dict.values()),
    }
