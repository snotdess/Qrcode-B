from backend.config import settings
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from geopy.distance import geodesic
from datetime import datetime, timedelta
from backend.models import Student, Course, QRCode, StudentCourses
from backend.utils import filter_records
from backend.errors.qr_code_errors import HourlyQRCodeError


# # --------------------
# # Helper Functions
# # --------------------


def build_qr_code_url(course_code, lecturer_id, latitude, longitude, generated_at):
    """
    Construct the QR code URL with query parameters.
    """
    base_url = settings.BASE_URL.strip("/")
    return (
        f"{base_url}/?course_code={course_code}"
        f"&lecturer_id={lecturer_id}"
        f"&latitude={latitude}"
        f"&longitude={longitude}"
        f"&generated_at={generated_at}"
    )


def get_current_utc_time():
    return datetime.utcnow()


def get_start_of_current_hour():
    now = get_current_utc_time()
    return now.replace(minute=0, second=0, microsecond=0)


async def check_recent_qr_code(
    db: AsyncSession, course_code, lecturer_id, time_threshold=timedelta(hours=1)
):
    """
    Ensure that a QR code was not generated within the last given time threshold.
    """
    one_hour_ago = get_current_utc_time() - time_threshold
    existing_qr_code = await filter_records(
        QRCode, db, course_code=course_code, lecturer_id=lecturer_id
    )

    if existing_qr_code and existing_qr_code.generation_time >= one_hour_ago:
        HourlyQRCodeError()

    return existing_qr_code


def is_within_timeframe(qr_time: datetime) -> bool:
    return datetime.utcnow() - qr_time <= timedelta(hours=1)

def validate_geolocation(
    student_lat: float,
    student_long: float,
    qr_lat: float,
    qr_long: float,
    max_distance: float = 50,
):
    student_location = (round(student_lat, 2), round(student_long, 2))
    lecturer_location = (round(qr_lat, 2), round(qr_long, 2))
    distance = geodesic(student_location, lecturer_location).meters
    if distance > max_distance:
        raise HTTPException(
            status_code=403, detail="Student is not within the valid location range"
        )

async def fetch_student(db: AsyncSession, matric_number: str):
    result = await db.execute(
        select(Student).where(Student.matric_number == matric_number)
    )
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=403, detail="Student not found")
    return student

async def fetch_course(db: AsyncSession, course_code: str):
    result = await db.execute(select(Course).where(Course.course_code == course_code))
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=403, detail="Course not found")
    return course

async def validate_enrollment(db: AsyncSession, matric_number: str, course_code: str):
    result = await db.execute(
        select(StudentCourses).where(
            (StudentCourses.matric_number == matric_number)
            & (StudentCourses.course_code == course_code)
        )
    )
    enrollment = result.scalars().first()
    if not enrollment:
        raise HTTPException(
            status_code=403, detail="Student is not enrolled in this course"
        )

async def fetch_latest_qr_code(db: AsyncSession, course_code: str, lecturer_id: str):
    result = await db.execute(
        select(QRCode)
        .where(
            (QRCode.course_code == course_code) & (QRCode.lecturer_id == lecturer_id)
        )
        .order_by(QRCode.generation_time.desc())
    )
    qr_code = result.scalars().first()
    if not qr_code:
        raise HTTPException(status_code=403, detail="QR code not found for this course")
    return qr_code
