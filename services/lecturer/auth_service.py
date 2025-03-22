from sqlalchemy.ext.asyncio import AsyncSession
from models import Lecturer
from util.auth_utils import (
    get_password_hash,
    create_access_token,
    verify_password,
    filter_records,
)
from errors.auth_errors import EmailAlreadyExistError, LecturerNotFoundError, PasswordError, EmailDoesNotExistError
from fastapi import HTTPException


class AuthService:
    @staticmethod
    async def register_lecturer(lecturer_data, db: AsyncSession):
        existing_lecturer = await filter_records(
            Lecturer, db, lecturer_email=lecturer_data.lecturer_email
        )

        if existing_lecturer:
            raise EmailAlreadyExistError()

        hashed_password = get_password_hash(lecturer_data.lecturer_password)
        new_lecturer = Lecturer(
            lecturer_name=lecturer_data.lecturer_name,
            lecturer_email=lecturer_data.lecturer_email,
            lecturer_department=lecturer_data.lecturer_department,
            lecturer_password=hashed_password,
        )
        db.add(new_lecturer)
        await db.commit()
        await db.refresh(new_lecturer)

        return {
            "message": "Lecturer successfully registered.",
            "lecturer_email": new_lecturer.lecturer_email,
        }

    @staticmethod
    async def login_lecturer(lecturer_data, db: AsyncSession):
        db_lecturer = await filter_records(
            Lecturer, db, lecturer_email=lecturer_data.lecturer_email
        )

        if not db_lecturer:
            raise LecturerNotFoundError()

        if not verify_password(
            lecturer_data.lecturer_password, db_lecturer.lecturer_password
        ):
            raise PasswordError()

        token = create_access_token(data={"sub": db_lecturer.lecturer_email})

        return {
            "token": token,
            "lecturer_id": db_lecturer.lecturer_id,
            "lecturer_name": db_lecturer.lecturer_name,
            "lecturer_email": db_lecturer.lecturer_email,
            "lecturer_department": db_lecturer.lecturer_department,
        }

    @staticmethod
    async def change_lecturer_password(data, db: AsyncSession):
        lecturer = await filter_records(Lecturer, db, lecturer_email=data.email)

        if not lecturer:
            raise EmailDoesNotExistError()

        lecturer.lecturer_password = get_password_hash(data.new_password)
        db.add(lecturer)
        await db.commit()
        await db.refresh(lecturer)

        return {"message": "Password updated successfully"}
