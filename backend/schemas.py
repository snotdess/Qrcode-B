# #### app/schemas.py

from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict


# # Schema for creating a new Lecturer (receiving data from the frontend)
class LecturerCreate(BaseModel):
    lecturer_name: str
    lecturer_email: EmailStr
    lecturer_department: str
    lecturer_password: str = Field(..., min_length=8)


# # Schema for Loggin Lecturers (receiving data from the frontend)
class LecturerLogin(BaseModel):
    lecturer_email: EmailStr
    lecturer_password: str


# # Schema for Lecturer Token
class LecturerToken(BaseModel):
    access_token: str
    token_type: str
    role: str
    lecturer_id: int
    lecturer_name: str
    lecturer_email: EmailStr
    lecturer_department: str

class Response(BaseModel):
    message :str

# Schema for changing Lecturer Password (receiving data from the frontend)
class ChangePassword(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=8)


# Schema for Course Creation (receiving data from the frontend)
class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    course_credits: int
    semester: str


class CourseResponse(BaseModel):
    course_code: str
    course_name: str
    course_credits: int
    semester: str
    creation_date: Optional[datetime]


# # Schema for creating a QRCODE (receiving data from the frontend)
class QRCodeCreate(BaseModel):
    course_code: str
    latitude: float  # Latitude of the lecturer
    longitude: float  # Longitude of the lecturer


class QRCodeResponse(BaseModel):
    qr_code_id: int
    course_code: str
    lecturer_id: int
    latitude: float
    longitude: float
    generation_time: datetime

class QRCodeSchema(BaseModel):
    course_name: str
    qr_code_link: HttpUrl
    generation_time: datetime

# Schema for creating a new Student (receiving data from the frontend)
class StudentCreate(BaseModel):
    matric_number: str
    student_fullname: str
    student_email: EmailStr
    student_password: str


# Schema for Student Logging (receiving data from the frontend)
class StudentLogin(BaseModel):
    matric_number: str
    student_password: str


# Schema for Token (receiving data from the frontend)
class StudentToken(BaseModel):
    access_token: str
    token_type: str
    role: str
    matric_number: str
    student_fullname: str
    student_email: EmailStr


class StudentResponse(BaseModel):
    qr_code_id: int
    course_code: str
    lecturer_id: int
    matric_number: str
    status: str


# Create the schema for the request body
class EnrollRequest(BaseModel):
    matric_number: str
    course_code: str
    lecturer_name: str


class EnrollResponse(BaseModel):
    matric_number: str
    course_code: str
    lecturer_name: str  # Add lecturer_name instead of lecturer_id
    message: str


# Schema for Attendance marking (receiving data from the frontend)
class AttendanceCreate(BaseModel):
    matric_number: str  # Student's matric number
    course_code: str  # Course code
    latitude: float  # Latitude of the student
    longitude: float  # Longitude of the student
    lecturer_id: int


class CourseStats(BaseModel):
    total_courses: int
    total_credits: int


class LecturerCourseResponse(BaseModel):
    lecturer_name: str
    course_code: str
    course_name: str


class LecturerCoursesListResponse(BaseModel):
    lecturer_courses: List[LecturerCourseResponse]


class CourseDetails(BaseModel):
    course_code: str
    course_name: str
    course_credits: int
    semester: str
    lecturer_name: str


class StudentAttendance(BaseModel):
    matric_number: str
    full_name: str
    attendance: Dict[str, str]  # Date as key, status (Present/Absent) as value



class StudentAttendanceRecord(BaseModel):
    matric_number: str
    course_name: str
    course_code: str
    lecturer_name: str
    course_credits:int
    semester: str
    attendance_score: float


class AttendanceResponse(BaseModel):
    course_name: str
    attendance: List[StudentAttendance]


class QRCodeDeleteRequest(BaseModel):
    course_code: str
