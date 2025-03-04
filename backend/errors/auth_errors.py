from fastapi import HTTPException

class CustomAuthError(HTTPException):
    def __init__(self, status_code, detail = None):
        super().__init__(status_code, detail)

class EmailAlreadyExistError(CustomAuthError):
    def __init__(self):
        super().__init__(400, "Email already registered.")

class MatNoAlreadyExistError(CustomAuthError):
    def __init__(self):
        super().__init__(400, "Student Matric Number already registered.")

class LecturerNotFoundError(CustomAuthError):
    def __init__(self):
        super().__init__(404, "Lecturer not found.")

class StudentNotFoundError(CustomAuthError):
    def __init__(self):
        super().__init__(404, "Student not found.")

class PasswordError(CustomAuthError):
    def __init__(self):
        super().__init__(401, "Incorrect password.")
