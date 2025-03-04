from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.models import Student, AttendanceRecords
from backend.schemas import AttendanceCreate, StudentAttendanceRecord
from datetime import datetime
from backend.util.qrcode_utils import (
    fetch_student,
    fetch_course,
    validate_enrollment,
    fetch_latest_qr_code,
    is_within_timeframe,
    validate_geolocation,
)
from backend.util.attendance_utils import (
    check_existing_attendance,
    mark_absent_students,
)
from backend.util.attendance_utils import (
    fetch_total_sessions_per_course,
    fetch_student_attendance_records,
    calculate_attendance_percentage,
)
from backend.errors.attendance_errors import AttendanceAuthError, MarkedAttendanceError
from backend.errors.qr_code_errors import ExpiredQRCodeError


class AttendanceService:
    @staticmethod
    async def scan_qr_service(
        attendance_data: AttendanceCreate, db: AsyncSession, current_student: Student
    ):
        # Ensure logged-in student is the one marking attendance
        if attendance_data.matric_number != current_student.matric_number:
            raise AttendanceAuthError()

        # Perform checks using utility functions
        await fetch_student(db, attendance_data.matric_number)
        await fetch_course(db, attendance_data.course_code)
        await validate_enrollment(
            db, attendance_data.matric_number, attendance_data.course_code
        )

        qr_code = await fetch_latest_qr_code(
            db, attendance_data.course_code, attendance_data.lecturer_id
        )

        if not is_within_timeframe(qr_code.generation_time):
            # Mark absent students automatically when QR code has expired
            await mark_absent_students(
                db, attendance_data.course_code, qr_code.generation_time
            )
            ExpiredQRCodeError()

        existing_attendance = await check_existing_attendance(
            db,
            attendance_data.matric_number,
            attendance_data.course_code,
            qr_code.generation_time,
        )
        if existing_attendance:
            MarkedAttendanceError()

        validate_geolocation(
            attendance_data.latitude,
            attendance_data.longitude,
            qr_code.latitude,
            qr_code.longitude,
        )

        # Record attendance
        new_attendance = AttendanceRecords(
            matric_number=attendance_data.matric_number,
            course_code=attendance_data.course_code,
            status="Present",
            geo_location=f"{attendance_data.latitude},{attendance_data.longitude}",
            date=datetime.utcnow(),
        )
        db.add(new_attendance)
        await db.commit()

        return {"message": "Attendance marked successfully"}

    @staticmethod
    async def get_student_attendance_details(
        db: AsyncSession, current_student: Student
    ) -> List[StudentAttendanceRecord]:
        # Fetch total attendance sessions and student-specific attendance records
        total_sessions = await fetch_total_sessions_per_course(db)
        attendance_records = await fetch_student_attendance_records(
            db, current_student.matric_number
        )

        # Calculate attendance percentage and compile attendance data
        attendance_data = []
        for record in attendance_records:
            total_sessions_count = total_sessions.get(
                record.course_code, 1
            )  # Prevent division by zero
            attendance_percentage = calculate_attendance_percentage(
                record.attended_sessions, total_sessions_count
            )

            attendance_data.append(
                StudentAttendanceRecord(
                    matric_number=current_student.matric_number,
                    course_name=record.course_name,
                    course_code=record.course_code,
                    lecturer_name=record.lecturer_name,
                    course_credits=record.course_credits,
                    semester=record.semester,
                    attendance_score=round(attendance_percentage, 2),
                )
            )

        return attendance_data
