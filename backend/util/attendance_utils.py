from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict
from datetime import timedelta, datetime
from backend.models import QRCode, AttendanceRecords, Course, LecturerCourses, Lecturer, StudentCourses


# # --------------------
# # Helper Functions
# # --------------------

async def fetch_total_sessions_per_course(db: AsyncSession) -> Dict[str, int]:
    """
    Fetch the total number of QR code generations (attendance sessions) per course.
    """
    total_qr_stmt = select(
        QRCode.course_code, func.count().label("total_sessions")
    ).group_by(QRCode.course_code)

    result = await db.execute(total_qr_stmt)
    return {row.course_code: row.total_sessions for row in result.all()}


async def fetch_student_attendance_records(db: AsyncSession, matric_number: str):
    """
    Fetch attendance records where the student was present.
    """
    student_attendance_stmt = (
        select(
            AttendanceRecords.course_code,
            Course.course_name,
            Course.semester,
            Course.course_credits,
            Lecturer.lecturer_name,
            func.count().label("attended_sessions"),
        )
        .join(Course, Course.course_code == AttendanceRecords.course_code)
        .join(LecturerCourses, LecturerCourses.course_code == Course.course_code)
        .join(Lecturer, Lecturer.lecturer_id == LecturerCourses.lecturer_id)
        .where(
            AttendanceRecords.matric_number == matric_number,
            AttendanceRecords.status == "Present",
        )
        .group_by(
            AttendanceRecords.course_code,
            Course.course_name,
            Course.semester,
            Course.course_credits,
            Lecturer.lecturer_name,
        )
    )

    result = await db.execute(student_attendance_stmt)
    return result.all()


def calculate_attendance_percentage(
    attended_sessions: int, total_sessions: int
) -> float:
    """
    Calculate attendance percentage, ensuring it doesn't exceed 100%.
    """
    if total_sessions == 0:
        return 0.0
    return min((attended_sessions / total_sessions) * 100, 100)


async def check_existing_attendance(
    db: AsyncSession, matric_number: str, course_code: str, qr_generation_time: datetime
):
    end_time = qr_generation_time + timedelta(hours=1)
    result = await db.execute(
        select(AttendanceRecords).where(
            (AttendanceRecords.matric_number == matric_number)
            & (AttendanceRecords.course_code == course_code)
            & (AttendanceRecords.date >= qr_generation_time)
            & (AttendanceRecords.date <= end_time)
        )
    )
    return result.scalars().first()


async def mark_absent_students(
    db: AsyncSession, course_code: str, qr_code_time: datetime
):
    """
    Automatically marks students absent if they haven't marked attendance within the QR code's valid period (1 hour).
    """
    # Fetch students registered for the course
    registered_students = await db.execute(
        select(StudentCourses.matric_number).where(
            StudentCourses.course_code == course_code
        )
    )
    registered_students = registered_students.scalars().all()

    # Fetch students who have already marked attendance
    attendance_records = await db.execute(
        select(AttendanceRecords.matric_number).where(
            (AttendanceRecords.course_code == course_code)
            & (AttendanceRecords.date >= qr_code_time)
        )
    )
    present_students = attendance_records.scalars().all()

    # Identify absent students
    absent_students = set(registered_students) - set(present_students)

    # Mark absent students
    for matric_number in absent_students:
        new_absence = AttendanceRecords(
            matric_number=matric_number,
            course_code=course_code,
            status="Absent",
            geo_location=None,
            date=datetime.utcnow(),
        )
        db.add(new_absence)

    await db.commit()
