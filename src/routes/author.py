from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from src.db.main import get_session
from src.services.author_services import AuthorService
from src.schemas.author import AuthorCreateSchema, AuthorResponseSchema, AuthorUpdateSchema
# from src.core.exceptions
from src.utils.dependencies import RoleChecker, AccessTokenBearer


author_router = APIRouter()
role_checker = Depends(RoleChecker(["admin", "user"]))
access_token_bearer = AccessTokenBearer()
author_service = AuthorService()


@author_router.post("/", response_model=AuthorResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def creat_author(author_data: AuthorCreateSchema, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    user_id = token_details.get("user")["user_id"]

    new_author = await author_service.create_author(author_data, session)

    return JSONResponse(
        content=jsonable_encoder(
            {
                "message": "Author created successfully.",
                "author": new_author
            }
        ) 
    )
