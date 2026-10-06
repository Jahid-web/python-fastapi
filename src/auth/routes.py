from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from src.core.celery_task import send_mail
from .schemas import UserCreate, LoginRequest, EmailModel, UserBookModel, PasswordRequestModel, PasswordResetConfirmModed
from src.db.main import get_session
from .service import UserService
from .utils import verify_password, create_access_token, create_url_safe_token, decode_url_safe_token, hash_password
from src.core.exceptions import UnAuthorizedException, ConflictException
from src.auth.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from src.db.redis import add_jti_to_blocklist
from src.core.config import Config
from src.core.exceptions import ForbiddenException, DatabaseException, BadRequestException, NotFoundException




REFRESH_TOKEN_EXPIRY = 2



auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/send_mail")
async def send_a_mail(email: EmailModel):
    email = email.addresses

    html = "<h1>Where to our knowledge store</h1>"
    subject = "Welcome to the E-Book"

    send_mail.delay(email, subject, html)

    return JSONResponse(content={"message": "Email sent successfully."})


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data:UserCreate, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    existing_user = await user_service.get_user_by_email(email, session)

    if existing_user:
        raise ConflictException(
            message="User already exist with this email address.",
            details= f"Existing email: {email}"
        )

    new_user = await user_service.create_user_account(user_data, session)
    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h2>Verify your email</h2>
    <p>Please click this <a href="{link}">link</a> to verify your email </p>
    """

    subject = "Verify Your Email"

    email = [email]

    send_mail.delay(email, subject, html)

    return JSONResponse (
        content= {
            "message": "Account Created successfully! Check email to verify your account.",
            "user": new_user
        }
    )


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    print(f"Email: {token_data.email}")
    user_email = token_data.get("email")


    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise ForbiddenException(
                message="User Not Found."
            )

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully."},
            status_code=status.HTTP_200_OK
        )
    
    raise DatabaseException(
        message="Internal server error.",
        details={}
    )


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(login_data:LoginRequest, session: AsyncSession = Depends(get_session)):

    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)


    if user is not None:
        password_valid = verify_password(password, user.hashed_password)

        if password_valid:        
            token_data = {
                "user_id": str(user.id),
                "email": user.email
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
                    "token_type": "Bearer",
                    "user_data": token_data
                }
            )
    
    raise UnAuthorizedException(
        message="Invalid email or password."
    )


@auth_router.get("/me", response_model=UserBookModel)
async def get_current_user(user = Depends(get_current_user), _:bool = Depends(role_checker)):
    return user


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-request/{token}"

    html_msg = f"""
    <h1>Reset your password</h1>
    <p>Please click this <a href="{link}">link</a> to reset your password.</p>
    """

    subject = "Reset Your Password"

    send_mail.delay([email], subject, html_msg)
    return JSONResponse(
        content= {
            "message": "Please check your email for instruction to reset your reset."
        },

        status_code = status.HTTP_200_OK
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_password(token: str, password: PasswordResetConfirmModed, session: AsyncSession = Depends(get_session)):
    new_password = password.new_password
    confirm_password = password.confirm_new_password

    if new_password != confirm_password:
        raise BadRequestException(
            message="Passwords do not match."
        )

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise NotFoundException(
                message="No user found.",
                details="email: {user_email}"
            )

        hash_pass = hash_password(new_password)

        await user_service.update_user(user, {"hashed_password": hash_pass}, session)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= {
                "message": "Password reset successfully."
            }
        )

    raise DatabaseException(
        message="Error occurd during password reset.",
        details="Database error."
    )


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content= {
            "message": "Logged Out Successfully"
        },
        status_code=status.HTTP_200_OK
    )

