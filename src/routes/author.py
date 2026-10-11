from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from src.db.main import get_session
from src.services.user_services import UserService
from src.schemas.author import AuthorCreateSchema, AuthorResponseSchema, AuthorUpdateSchema, AuthorSchema
from src.models.user import UserRole
from src.utils.dependencies import RoleChecker, AccessTokenBearer


author_router = APIRouter()
role_checker = Depends(RoleChecker([UserRole.AUTHOR, UserRole.ADMIN]))
access_token_bearer = AccessTokenBearer()
user_service = UserService()


@author_router.post("/create-author", response_model=AuthorResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def creat_author(author_data: AuthorCreateSchema, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    user_id = token_details.get("user")["user_id"]

    new_author = await user_service.create_author(author_data, session)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": "Author created successfully.",
                "author": new_author
            }
        ) 
    )

@author_router.patch("/{author_id}", response_model=AuthorSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def update_author(author_id: str, author_data: AuthorUpdateSchema, session: AsyncSession = Depends(get_session)):
    update_author_data = await user_service.update_author(author_id, author_data, session)

    return update_author_data