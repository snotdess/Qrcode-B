from config import settings
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geopy.distance import geodesic
from datetime import datetime, timedelta
from models import Student, Course, QRCode, StudentCourses
from errors.qr_code_errors import HourlyQRCodeError, QRCodeNotFoundError
from errors.auth_errors import StudentNotFoundError
from errors.course_errors import CourseNotFoundError, StudentEnrolledError
from errors.attendance_errors import LocationRangeError

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


async def check_recent_qr_code(db: AsyncSession, course_code, lecturer_id):
    """
    Ensure that a QR code for the same course does not exist within the current hour.
    """
    start_of_current_hour = get_start_of_current_hour()

    result = await db.execute(
        select(QRCode)
        .where(
            QRCode.course_code == course_code,
            QRCode.lecturer_id == lecturer_id,
            QRCode.generation_time
            >= start_of_current_hour,  # Only consider QR codes from this hour
        )
        .order_by(QRCode.generation_time.desc())
    )

    existing_qr_code = result.scalars().first()

    if existing_qr_code:
        raise HourlyQRCodeError()


def is_within_timeframe(qr_time: datetime) -> bool:
    return datetime.utcnow() - qr_time <= timedelta(minutes=10)


def validate_geolocation(
    student_lat: float,
    student_long: float,
    qr_lat: float,
    qr_long: float,
    max_distance: float = 15,
):
    student_location = (student_lat, student_long)
    lecturer_location = (qr_lat, qr_long)
    distance = geodesic(student_location, lecturer_location).meters
    if distance > max_distance:
        raise LocationRangeError()
    return True


async def fetch_student(db: AsyncSession, matric_number: str):
    result = await db.execute(
        select(Student).where(Student.matric_number == matric_number)
    )
    student = result.scalars().first()
    if not student:
        raise StudentNotFoundError()
    return student


async def fetch_course(db: AsyncSession, course_code: str):
    result = await db.execute(select(Course).where(Course.course_code == course_code))
    course = result.scalars().first()
    if not course:
        raise CourseNotFoundError()
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
        raise StudentEnrolledError()


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
        raise QRCodeNotFoundError()
    return qr_code
