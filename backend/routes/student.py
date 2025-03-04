# #### app/routes/student.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from typing import List
from backend.models import Student
from backend.schemas import (
    StudentCreate,
    StudentLogin,
    ChangePassword,
    StudentToken,
    AttendanceCreate,
    EnrollRequest,
    EnrollResponse,
    CourseDetails,
)
from backend.util.auth_utils import get_current_student
from backend.services.student.auth_service import AuthService
from backend.services.student.course_service import CourseService
from backend.services.student.attendance_service import AttendanceService


router = APIRouter()

# **Student Signup Route**
@router.post("/signup")
async def student_signup(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    """
    API endpoint for student signup.
    """
    return await AuthService.student_signup(student, db)


# **Student Login Route**
@router.post("/login", response_model=StudentToken)
async def student_login(student: StudentLogin, db: AsyncSession = Depends(get_db)):
    """
    API endpoint for student login.
    """
    result = await AuthService.student_login(student, db)

    return StudentToken(
        access_token=result["token"],
        token_type="bearer",
        role="student",
        matric_number=result["matric_number"],
        student_fullname=result["student_fullname"],
        student_email=result["student_email"],
    )


# **Student Change Password Route**
@router.put("/change-password", status_code=200)
async def change_password(data: ChangePassword, db: AsyncSession = Depends(get_db)):
    """
    API endpoint to change the password for a student.
    """
    return await AuthService.change_password(data, db)


# **Student Enroll Course Route**
@router.post("/enroll", response_model=EnrollResponse)
async def enroll_student(
    enrollment_data: EnrollRequest, db: AsyncSession = Depends(get_db)
):
    """
    API endpoint to enroll a student in a course with a specific lecturer.
    """
    enrollment_response = await CourseService.enroll_student(enrollment_data, db)
    return enrollment_response


# **Get Student's Enrolled Courses Route**
@router.get("/student_courses", response_model=List[CourseDetails])
async def get_student_courses(
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """
    API endpoint to retrieve the courses a student is enrolled in along with course code, name, credits, and lecturer name.
    """
    return await CourseService.get_student_courses(current_student, db)


@router.get("/course_stats")
async def student_course_stats(
    db: AsyncSession = Depends(get_db), current_student=Depends(get_current_student)
):
    return await CourseService.get_student_course_stats(db, current_student)


@router.post("/scan-qr")
async def scan_qr(
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """
    API endpoint to mark attendance via QR code scanning.
    """
    return await AttendanceService.scan_qr_service(attendance_data, db, current_student)


@router.get("/attendance_details")
async def attendance_details(
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """
    Get the attendance details of the currently logged-in student.
    """
    return await AttendanceService.get_student_attendance_details(db, current_student)


@router.get("/me")
async def get_logged_in_student(
    current_student: Student = Depends(get_current_student),
):
    return {
        "matric_number": current_student.matric_number,
        "FullName": current_student.student_fullname,
        "Student Email": current_student.student_email,
    }
