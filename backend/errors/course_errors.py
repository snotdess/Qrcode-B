from fastapi import HTTPException

class CustomCourseError(HTTPException):
    def __init__(self, status_code, detail = None):
        super().__init__(status_code, detail)

class LecturerCourseAlreadyAssociatedError(CustomCourseError):
    def __init__(self):
        super().__init__(400, "Lecturer already associated with this course.")

class CourseNotFoundError(CustomCourseError):
    def __init__(self):
        super().__init__(404, "Course not found.")


class UnauthorizedLecturerCourseError(CustomCourseError):
    def __init__(self):
        super().__init__(
            403, "You are not authorized to perform this action for this course."
        )

class LecturerNotLoggedInError(CustomCourseError):
    def __init__(self):
        super().__init__(403, "You must be logged in as a lecturer.")

class StudentEnrolledError(CustomCourseError):
    def __init__(self):
        super().__init__(403, "Student is not enrolled in this course.")
