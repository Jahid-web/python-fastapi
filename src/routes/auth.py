from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from datetime import timedelta

from src.db.main import get_session
from src.schemas.user import UserCreateSchema, UserResponseSchema, LoginRequestSchema
from src.core.security import create_access_token, verify_password, hash_password
from src.core.exceptions import ConflictException, UnAuthorizedException
from src.services.user_services import UserService


REFRESH_TOKEN_EXPIRY = 2


auth_router = APIRouter()
user_service = UserService()


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
        content={
            "message": "Accounted created successfully.",
            "user": new_user
        }
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
