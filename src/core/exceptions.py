from fastapi import status

class AppException(Exception):
    def __init__(
            self,
            message: str,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            error_code: str = "APP_ERROR",
            details = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

        super().__init__(message)


class UnAuthorizedException(AppException):
    def __init__(self, message):
        super().__init__(
            message = message,
            status_code = status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )

class ForbiddenException(AppException):
    def __init__(self, message, details):
        super().__init__(
            message = message,
            status_code = status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
            details=details
        )

class ValidationException(AppException):
    def __init__(self, message, details):
        super().__init__(
            message = message,
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code="VALIDATION_ERROR",
            details=details
        )

class NotFoundException(AppException):
    def __init__(self, message, details):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )

class BadRequestException(AppException):
    def __init__(self, message):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST"
        )

class ConflictException(AppException):
    def __init__(self, message, details):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="ALREADY_EXIST",
            details=details
        )

class DatabaseException(AppException):
    def __init__(self, message, details):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )        