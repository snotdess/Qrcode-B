from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from backend.models import Student
from backend.util.auth_utils import (
    get_password_hash,
    create_access_token,
    verify_password,
    filter_records,
)


class AuthService:
    @staticmethod
    async def student_signup(student_data, db: AsyncSession):
        if await filter_records(Student, db, matric_number=student_data.matric_number):
            raise HTTPException(status_code=400, detail="Student already registered.")

        new_student = Student(
            matric_number=student_data.matric_number,
            student_fullname=student_data.student_fullname,
            student_email=student_data.student_email,
            student_password=get_password_hash(student_data.student_password),
        )
        db.add(new_student)
        await db.commit()
        await db.refresh(new_student)
        return {"message": "Student Registered Successfully"}

    @staticmethod
    async def student_login(student_data, db: AsyncSession):
        db_student = await filter_records(
            Student, db, matric_number=student_data.matric_number
        )
        if not db_student:
            raise HTTPException(status_code=401, detail="Student Not Found.")

        if not verify_password(
            student_data.student_password, db_student.student_password
        ):
            raise HTTPException(status_code=401, detail="Invalid Password.")

        token = create_access_token(data={"sub": db_student.student_email})
        return {
            "token": token,
            "matric_number": db_student.matric_number,
            "student_fullname": db_student.student_fullname,
            "student_email": db_student.student_email,
        }

    @staticmethod
    async def change_password(data, db: AsyncSession):
        student = await filter_records(Student, db, student_email=data.email)
        if not student:
            raise HTTPException(
                status_code=404, detail="Student with this email does not exist"
            )

        student.student_password = get_password_hash(data.new_password)
        db.add(student)
        await db.commit()
        return {"message": "Password updated successfully"}
