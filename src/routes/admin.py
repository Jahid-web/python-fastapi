from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder

from src.db.main import get_session
from src.services.user_services import UserService
from src.services.category_services import CategoryService
from src.core.exceptions import UnAuthorizedException, ConflictException, ForbiddenException
from src.schemas.user import UserCreateSchema, UserResponseSchema
from src.schemas.category import CategoryCreateSchema, CategoryResponseSchema, CategoryUpdateSchema
from src.utils.dependencies import RoleChecker
from src.models.user import UserRole
from src.utils.dependencies import AccessTokenBearer
from src.schemas.author import AuthorResponseSchema

admin_router = APIRouter()
user_service = UserService()
category_service = CategoryService()
role_checker = Depends(RoleChecker(UserRole.ADMIN))
access_token_bearer = AccessTokenBearer()

@admin_router.get("/", response_model=list[UserResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    users = await user_service.get_all_users(session)

    return users

@admin_router.get("/authors", response_model=list[AuthorResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_authors_only(session: AsyncSession = Depends(get_session)):
    authors = await user_service.get_authors(session)

    return authors


@admin_router.post("/category", response_model=CategoryResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_category(cat_data: CategoryCreateSchema, session: AsyncSession = Depends(get_session), token_datils: dict = Depends(access_token_bearer)):
    role = token_datils.get("user")["role"]

    # if role != UserRole.ADMIN:
    #     raise ForbiddenException(
    #         message="You are not permitted to do this action.",
    #         details={}
    #     )

    cat_name = cat_data.name

    existing_cat = await category_service.get_cat_by_name(cat_name, session)

    if existing_cat:
        raise ConflictException(
            message="Category already exists with this name.",
            details={}
        )

    new_cat = await category_service.create_categories(cat_data, session)

    return JSONResponse(
        content=jsonable_encoder({
            "message": "Category created successfully.",            
            "cat_name": new_cat
        })
    )


@admin_router.get("/all_category", response_model=list[CategoryResponseSchema], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_all_category(session: AsyncSession = Depends(get_session)):
    categories = await category_service.get_all_cat(session)
    return JSONResponse(
        content=jsonable_encoder({
            "Cat_nos": f"{len(categories)} Nos",
            "categories": categories
        })
    ) 
        