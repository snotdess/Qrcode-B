from fastapi import HTTPException


class CustomAttendanceError(HTTPException):
    def __init__(self, status_code, detail=None):
        super().__init__(status_code=status_code, detail=detail)


class AttendanceAuthError(CustomAttendanceError):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="You are not authorized to mark attendance for another student.",
        )

class MarkedAttendanceError(CustomAttendanceError):
    def __init__(self):
        super().__init__(403, "You have already marked attendance for this session.")

class LocationRangeError(CustomAttendanceError):
    def __init__(self):
        super().__init__(422, "Student is not within the valid location range.")
