from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound, StatementError, OperationalError

from src.core.exceptions import AppException

# APP EXCEPTION HANDLER
async def app_exception_handler(
        req: Request,
        exc: AppException
):
    return JSONResponse (
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


# PYDANTIC VALIDATION ERROR HANDLER
async def validation_exception_handler(
        req: Request,
        exc: RequestValidationError
):
    errors = []

    for err in exc.errors():
        location = ".".join(
            str(item) for item in err["loc"]
        )
        errors.append({
            "field": location,
            "message": err["msg"],
            "type": err["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": errors
            }
        }
    )


# SQLALCHEMY INTEGRITYERROR
async def sqlalchemy_integrity_error_handler(
        req: Request,
        exc: IntegrityError
):
    # error_message = str(exc.orig)

    # if "user_email_key" in error_message:
    #     field = "email"
    #     msg = "Email already exist."

    # else:
    #     field = None
    #     msg = "Database constraint violation."

    print("######################")    
    print(exc.orig)
    print(exc)

    constraint_name = None

    # postgres
    if hasattr(exc.orig, "diag"):
        constraint_name = exc.orig.diag.constraint_name

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_CONSTRAINT_ERROR",
                "message": "A database constraint was violated.",
                "details": {
                    "field": constraint_name
                }
            }
        }
    )


# SQLALCHEMY NO RESULT FOUND
async def no_result_found_handler(
        req: Request,
        exc: NoResultFound
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content= {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Result not found.",
                "details": {}
            }
        }
    )


# SQLALCHEMY STATEMENT ERROR
async def statement_error_handler(
        req: Request,
        exc: StatementError
):
    original_exception = exc.orig


    if isinstance(original_exception, AppException):

        return JSONResponse(
            status_code=original_exception.status_code,
            content={
                "success": False,
                "error": {
                    "code": original_exception.error_code,
                    "message": original_exception.message,
                    "details": original_exception.details,
                },
            },
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content= {
            "success": False,
            "error": {
                "code": "DATABASE_STATEMENT_ERROR",
                "message": "Invalid database operation",
                "details": {"original_error": str(original_exception)}
            }
        }
    )


# DATABASE/OPERATIONAL ERROR
async def operational_error_handler(
        req: Request,
        exc: OperationalError
):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content= {
            "success": False,
            "error": {
                "code": "DATABASE_UNAVAILABLE",
                "message": "Database service is temporally unavailable.",
                "details": {}
            }
        }
    )


def register_all_exceptions_handlers(
        app: FastAPI
):
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )

    app.add_exception_handler(
        AppException,
        app_exception_handler
    )

    app.add_exception_handler(
        StatementError,
        statement_error_handler
    )

    app.add_exception_handler(
        IntegrityError,
        sqlalchemy_integrity_error_handler
    )

    app.add_exception_handler(
        NoResultFound,
        no_result_found_handler
    )

    app.add_exception_handler(
        OperationalError,
        operational_error_handler
    )