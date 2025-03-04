#### app/routes/lecturer.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models import Lecturer
from backend.schemas import (
    LecturerCreate,
    LecturerLogin,
    LecturerToken,
    ChangePassword,
    CourseCreate,
    CourseResponse,
    QRCodeCreate,
    QRCodeResponse,
    CourseStats,
    LecturerCoursesListResponse,
    AttendanceResponse,
)
from backend.services.lecturer.auth_service import AuthService
from backend.services.lecturer.qrcode_service import QRCodeService
from backend.services.lecturer.lecturer_course_service import LecturerCourseService
from backend.util.auth_utils import get_current_lecturer
from backend.services.lecturer_service import (
    get_attendance_service,
)
from typing import List


router = APIRouter()


# # **Lecturer Signup Route**
@router.post("/signup")
async def lecturer_signup(lecturer: LecturerCreate, db: AsyncSession = Depends(get_db)):
    response = await AuthService.register_lecturer(lecturer, db)
    return response


# # **Lecturer Login Route**
@router.post("/login", response_model=LecturerToken)
async def lecturer_login(
    lecturer: LecturerLogin,
    db: AsyncSession = Depends(get_db),
) -> LecturerToken:

    result = await AuthService.login_lecturer(lecturer, db)

    return LecturerToken(
        access_token=result["token"],
        token_type="bearer",
        role="lecturer",
        lecturer_id=result["lecturer_id"],
        lecturer_name=result["lecturer_name"],
        lecturer_email=result["lecturer_email"],
        lecturer_department=result["lecturer_department"],
    )


# #**Lecturer Change Password Route**
@router.put("/change-password", status_code=200)
async def change_password(
    data: ChangePassword, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    return await AuthService.change_lecturer_password(data, db)


# #**Lecturer Courses Creation Route**
@router.post("/courses", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_lecturer: Lecturer = Depends(get_current_lecturer),
):
    return await LecturerCourseService.create_course_for_lecturer(
        course, db, current_lecturer
    )

# #**Lecturer Courses Info Route**
@router.get("/course_info", response_model=List[CourseCreate])
async def get_course_info(
    db: AsyncSession = Depends(get_db),
    current_lecturer: Lecturer = Depends(get_current_lecturer),
):
    # Call the service to get courses
    courses = await LecturerCourseService.get_courses_for_lecturer(db, current_lecturer)
    return courses

#  #**Lecturer course statistics**
@router.get("/course_stats", response_model=CourseStats)
async def get_course_stats(
    db: AsyncSession = Depends(get_db),
    current_lecturer: Lecturer = Depends(get_current_lecturer),
):
    # Call on the service to get course stats
    courses_stats = await LecturerCourseService.get_courses_stats(db, current_lecturer)
    return courses_stats

#  #**Lecturer course list**
@router.get("/lecturer_courses", response_model=LecturerCoursesListResponse)
async def fetch_lecturer_courses(db: AsyncSession = Depends(get_db)):
    """
    API route to fetch all lecturers and their registered course codes.
    """
    lecturer_courses = await LecturerCourseService.get_lecturer_courses(db)
    return {"lecturer_courses": lecturer_courses}


#  #**Lecturer course register Students**
@router.get("/lecturer_course_students")
async def lecturer_course_students(
    db: AsyncSession = Depends(get_db),
    current_lecturer: Lecturer = Depends(get_current_lecturer),
):
    """
    API endpoint to get courses taught by the current lecturer and the total number of students in each course.
    """
    return await LecturerCourseService.get_lecturer_course_students(
        db, current_lecturer
    )


# #**Lecturer QRCODE Creation Route**
@router.post("/generate_qr_code", response_model=QRCodeResponse)
async def generate_qr_code(
    qr_code_data: QRCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_lecturer: Lecturer = Depends(get_current_lecturer),
):
    return await QRCodeService.generate_qr_code(qr_code_data, db, current_lecturer)


@router.get("/latest_qr_codes")
async def get_lecturer_latest_qr_codes(
    current_lecturer: dict = Depends(get_current_lecturer),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest QR codes for all courses assigned to the currently logged-in lecturer.
    """
    # lecturer_id = current_lecturer["lecturer_id"]
    qr_codes = await QRCodeService.get_latest_qr_codes(current_lecturer.lecturer_id, db)

    if not qr_codes:
        raise HTTPException(
            status_code=204, detail="No QR Codes found in the last hour."
        )

    return qr_codes


# Lecturer QR Code Deletion Route
@router.delete("/delete_qr_code", status_code=204)
async def delete_qr_code(
    course_name: str,  # Ensure this is a query parameter
    db: AsyncSession = Depends(get_db),
    current_lecturer: Lecturer = Depends(get_current_lecturer),
):
    return await QRCodeService.delete_qr_code(course_name, db, current_lecturer)


@router.get("/attendance/{course_code}", response_model=AttendanceResponse)
async def get_attendance(
    course_code: str,
    db: AsyncSession = Depends(get_db),
    current_lecturer=Depends(get_current_lecturer),
):
    return await get_attendance_service(course_code, current_lecturer, db)


# @router.get("/me")
# async def get_logged_in_lecturer(current_lecturer: Lecturer = Depends(get_current_lecturer), response_model=LecturerResponse):

#     details = LecturerResponse(
#         lecturer_name= current_lecturer.lecturer_name,
#         lecturer_email= current_lecturer.lecturer_email,
#         lecturer_department= current_lecturer.lecturer_department,
#         role = "lecturer"
#     )

#     return details
