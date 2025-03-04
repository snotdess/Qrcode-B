from fastapi import HTTPException


class CustomQRCodeError(HTTPException):
    def __init__(self, status_code, detail=None):
        super().__init__(status_code, detail)


class HourlyQRCodeError(CustomQRCodeError):
    def __init__(self):
        super().__init__(
            400, "QR Code already generated for this course within the last hour."
        )

class QRCodeNotFoundError(CustomQRCodeError):
    def __init__(self):
        super().__init__(403, "QR code not found for this course")


class ExpiredQRCodeError(CustomQRCodeError):
    def __init__(self):
        super().__init__(
            403,
            "QR code has expired; you have been marked as absent for this session",
        )
