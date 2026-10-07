from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.services.user_services import UserService
from src.core.exceptions import UnAuthorizedException, ConflictException
from src.schemas.user import UserCreateSchema, UserResponseSchema
from src.utils.dependencies import RoleChecker
from src.models.user import UserRole
from src.schemas.author import AuthorResponseSchema

admin_router = APIRouter()
user_service = UserService()
role_checker = Depends(RoleChecker(UserRole.ADMIN))

@admin_router.get("/", response_model=list[UserResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    users = await user_service.get_all_users(session)

    return users

@admin_router.get("/authors", response_model=list[AuthorResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_authors_only(session: AsyncSession = Depends(get_session)):
    authors = await user_service.get_authors(session)

    return authors
    # return JSONResponse(
    #     content={
    #         "message": "All Authors list.",
    #         "Authors": authors
    #     }
    # )