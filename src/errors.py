from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "APP_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

        super().__init__(message)

class UserAlreadyExistException(AppException):
    def __init__(self):
        super().__init__ (
            message="User already exists.",
            status_code= status.HTTP_409_CONFLICT,
            error_code="USER_ALREADY_EXIST."
        )


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid email or password.",
            status_code= status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS"
        )

class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid or expired.",
            status_code= status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN"
        )


class InactiveUserException(AppException):
    def __init__(self):
        super().__init__(
            message="User account is inactive",
            status_code= status.HTTP_403_FORBIDDEN,
            error_code="INACTIVE_USER"
        )

class AccessTokenRequired(AppException):
    def __init__(self):
        super().__init__(
            message="Access token required.",
            status_code= status.HTTP_401_UNAUTHORIZED,
            error_code="TOKEN_REQUIRED"
        )

class InsufficientPermission(AppException):
    def __init__(self):
        super().__init__(
            message="You do not have enough permission to do this perform.",
            status_code= status.HTTP_401_UNAUTHORIZED,
            error_code="INSUFFICIENT_PERMISSION"
        )

class AccountNotVerified(AppException):
    def __init__(self):
        super().__init__(
            message="Account Not Verified",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="Check your email for verification."
        )

class UserNotFound(AppException):
    def __init__(self):
        super().__init__(
            message="User Not Found",
            status_code= status.HTTP_403_FORBIDDEN,
            error_code="USER_NOT_FOUND"
        )


async def appExceptionHandler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message
            }
        }
    )

async def generalExceptionHandler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occured."
            }
        }
    )


def register_all_errors(app:FastAPI):
    app.add_exception_handler(
        AppException,
        appExceptionHandler
    )

    app.add_exception_handler(
        Exception,
        generalExceptionHandler
    )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, err):
        print(err)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "message": "Oops something went wrong.",
                    "code": "SERVER_ERROR"
                }
            }
        )



