from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from datetime import timedelta
from typing import Annotated
from src.utils.uploads import uploads

from src.db.main import get_session
from src.schemas.user import UserCreateSchema, UserResponseSchema, LoginRequestSchema, UserGetResponseSchema, UserPasswordResetSchema, UserPasswordResetConfirm
from src.core.security import create_access_token, verify_password, create_url_safe_token, decode_url_safe_token, hash_password
from src.core.exceptions import ConflictException, UnAuthorizedException, ForbiddenException, DatabaseException, BadRequestException, NotFoundException
from src.services.user_services import UserService
from src.core.config import Config
from src.models.user import UserRole
from src.core.celery_task import send_mail
from src.utils.dependencies import get_current_user, RoleChecker


REFRESH_TOKEN_EXPIRY = 2


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker([UserRole.ADMIN, UserRole.AUTHOR, UserRole.USER])


@auth_router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    existing_user = await user_service.get_user_by_email(email, session)

    if existing_user:
        raise ConflictException(
            message="User already exit with this email address.",
            details=f"Existing email is: {email}"
        )

    new_user = await user_service.create_user_account(user_data, session)

    return JSONResponse(
       content=jsonable_encoder(
           {
                "message": "Accounted created successfully.",
                "user": new_user
            }
        )
    )


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(login_data: LoginRequestSchema, session:AsyncSession=Depends(get_session)):
    email = login_data.email
    password = login_data.password

    if email and password is None:
        raise UnAuthorizedException(
            message="Email or password required."            
        )

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password)

        if password_valid:
            token_data = {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role
            }

            access_token = create_access_token(token_data)
            refresh_token = create_access_token(
                token_data,
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse (
                content= {
                    "message": "Login successfully.",
                    "access_token": access_token,
                    "refresh_token": refresh_token,        
                    "user_data": token_data                    
                }
            )
    
    raise UnAuthorizedException(
        message="Invalid email or password."
    )


@auth_router.get("/me", response_model=UserGetResponseSchema, status_code=status.HTTP_200_OK)
async def get_user(user = Depends(get_current_user), _:bool = Depends(role_checker)):
    return user

@auth_router.get("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise ForbiddenException(
                message="User not found."
            )

        await user_service.update_me(user, {"is_verified": True}, session)

        return {
            "success": True,
            "message": "Account verified successfully."
        }

    raise DatabaseException(
        message="Something went wrong.",
        details={}
    )


@auth_router.post("/password-reset-request", status_code=status.HTTP_200_OK)
async def password_reset_request(email_data: UserPasswordResetSchema):
    email = email_data.email

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-request/{token}"

    html_msg = f"""
    <h3>Reset your password</h3>
    <p>Please click this <a href="{link}">link</a> to reset your password.</p>
    """
    subject = "Reset Your Password"

    send_mail.delay([email], subject, html_msg)

    return {
        "message": "Please check your email for instruction to reset your password."
    }


@auth_router.post("/password-reset-confirm/{token}", status_code=status.HTTP_200_OK)
async def reset_password_confirm(token: str, password: UserPasswordResetConfirm, session: AsyncSession = Depends(get_session)):
    new_password = password.new_password
    confirm_password = password.confirm_new_password

    if new_password != confirm_password:
        raise BadRequestException(
            message="Password do not match."
        )

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise NotFoundException(
                message="No user found.",
                details="Email:{user_email}"
            )

        hash_pass = hash_password(new_password)
        await user_service.update_me(user, {"password": hash_pass}, session)

        return {
            "message": "Password reset successfully."
        }

@auth_router.post("/upload", status_code=status.HTTP_200_OK)
async def photo_upload(file: Annotated[UploadFile, File()]):
    return await uploads(file)