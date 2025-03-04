from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Optional
from datetime import datetime


# Student model
class Student(SQLModel, table=True):
    matric_number: str = Field(
        primary_key=True, unique=True, index=True
    ) 
    student_fullname: str
    student_email: str
    student_password: str

    # Relationships
    courses: List["StudentCourses"] = Relationship(back_populates="student")
    attendance_records: List["AttendanceRecords"] = Relationship(
        back_populates="student"
    )


# lecturer model
class Lecturer(SQLModel, table=True):
    lecturer_id: int = Field(primary_key=True, index=True)
    lecturer_name: str
    lecturer_email: str
    lecturer_department: str
    lecturer_password: str

    # Relationships
    courses: List["LecturerCourses"] = Relationship(back_populates="lecturer")
    qr_codes: List["QRCode"] = Relationship(back_populates="lecturer")


# Course model
class Course(SQLModel, table=True):
    course_code: str = Field(
        primary_key=True, unique=True, index=True
    )  # Unique course identifier
    course_name: str
    course_credits: int
    semester: str
    creation_date: datetime

    # Relationships
    students: List["StudentCourses"] = Relationship(back_populates="course")
    lecturer: List["LecturerCourses"] = Relationship(back_populates="course")
    qr_codes: List["QRCode"] = Relationship(back_populates="course")
    attendance_records: List["AttendanceRecords"] = Relationship(
        back_populates="course"
    )


# TeacherCourses (Relationship Table for Lecturer and Courses)
class LecturerCourses(SQLModel, table=True):
    lecturer_course_id: int = Field(primary_key=True, index=True)
    lecturer_id: int = Field(foreign_key="lecturer.lecturer_id")  # FK to Lecturer
    course_code: str = Field(foreign_key="course.course_code")  # FK to Course

    # Relationships
    lecturer: Optional[Lecturer] = Relationship(back_populates="courses")
    course: Optional[Course] = Relationship(back_populates="lecturer")


# QR Code model
class QRCode(SQLModel, table=True):
    qr_code_id: int = Field(primary_key=True, index=True)
    course_code: str = Field(foreign_key="course.course_code")
    lecturer_id: int = Field(foreign_key="lecturer.lecturer_id")  # FK to lecturer
    generation_time: datetime
    latitude: float
    longitude: float
    url: str

    # Relationships
    lecturer: Optional[Lecturer] = Relationship(back_populates="qr_codes")
    course: Optional[Course] = Relationship(back_populates="qr_codes")


# StudentCourses (Relationship Table for Students and Courses)
class StudentCourses(SQLModel, table=True):
    matric_number: str = Field(
        foreign_key="student.matric_number", primary_key=True
    )  # FK to Student
    course_code: str = Field(
        foreign_key="course.course_code", primary_key=True
    )  # FK to Course

    # Relationships
    student: Optional[Student] = Relationship(back_populates="courses")
    course: Optional[Course] = Relationship(back_populates="students")


# AttendanceRecords model
class AttendanceRecords(SQLModel, table=True):
    record_id: int = Field(primary_key=True, index=True)
    matric_number: str = Field(foreign_key="student.matric_number")  # FK to Student
    course_code: str = Field(foreign_key="course.course_code")  # FK to Course
    date: datetime = Field(default=datetime.utcnow)  # Attendance date and time
    geo_location: str
    status: str  # Attendance status ("Present" or "Absent")

    # Relationships
    student: Optional[Student] = Relationship(back_populates="attendance_records")
    course: Optional[Course] = Relationship(back_populates="attendance_records")
