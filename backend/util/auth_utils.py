#### app/utils.py
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.future import select
from typing import Optional
from backend.database import get_db
from backend.config import settings
from backend.models import Lecturer, Student
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Oauth2 scheme for Lecturer and Student
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="lecturers/login")
oauth2_scheme_student = OAuth2PasswordBearer(tokenUrl="student/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(token: str, db: AsyncSession, user_model, email_field: str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(user_model).where(getattr(user_model, email_field) == user_email)
    result = await db.execute(query)
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_lecturer(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    return await get_current_user(token, db, Lecturer, "lecturer_email")


async def get_current_student(
    token: str = Depends(oauth2_scheme_student), db: AsyncSession = Depends(get_db)
):
    return await get_current_user(token, db, Student, "student_email")


async def filter_records(model, db: AsyncSession, **filters):
    """Reusable function to filter records from a given model."""
    query = select(model).filter_by(**filters)
    result = await db.execute(query)
    return result.scalars().first()
