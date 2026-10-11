from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder

from src.db.main import get_session
from src.core.exceptions import NotFoundException, ForbiddenException
from src.services.book_services import BookService
from src.utils.dependencies import RoleChecker, AccessTokenBearer
from src.schemas.book import BookCreateSchema, BookUpdateSchema, BookResponseSchema, BookSchema
from src.models.user import UserRole

book_router = APIRouter()
role_checker = Depends(RoleChecker([UserRole.AUTHOR, UserRole.ADMIN]))
access_token_bearer = AccessTokenBearer()
book_service = BookService()


@book_router.post("/create-book", response_model=BookResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_book(book_data: BookCreateSchema, session: AsyncSession = Depends(get_session), token_datils: dict = Depends(access_token_bearer)) -> dict:    
    user_id = token_datils.get("user")["user_id"]
    user_role = token_datils.get("user")["role"]

    # book_title = book_data.title

    if user_role != UserRole.AUTHOR:
        raise ForbiddenException(
            message="You are not allowed to create book.",
            details="Only user role author can create book."
        )

    # existing_book = await book_service.get_book_by_title(book_title, session)

    # if existing_book:
    #     raise ConflictException(
    #         message="Book already exists with this title.",
    #         details={}
    #     )
    
    new_book = await book_service.create_book(book_data, user_id, session)
    return JSONResponse(
        content=jsonable_encoder({
            "message": "Book created successfully.",
            "book": new_book
        })
    )

@book_router.get("/", response_model=list[BookResponseSchema], dependencies=[role_checker], status_code=status.HTTP_200_OK)
async def get_all_book(session: AsyncSession = Depends(get_session), _:dict = Depends(access_token_bearer)):
    books = await book_service.get_all_book(session)

    if not books:
        raise NotFoundException(
            message="No book found",
            details={}
        )

    return JSONResponse(
        content=jsonable_encoder({
            "message": "Avalable books list.",
            "book_nos": f"{len(books)} Nos",
            "books": books
        })
    )

@book_router.patch("/{book_id}", response_model=BookSchema, dependencies=[role_checker], status_code=status.HTTP_201_CREATED)
async def update_book(book_id:str, book_data: BookUpdateSchema, session: AsyncSession = Depends(get_session)):
    updated_book = await book_service.update_book(book_id, book_data, session)

    if updated_book is None:
        raise NotFoundException(
            message="No book found.",
            details={}
        )

    return updated_book

@book_router.delete("/{book_id}", status_code=status.HTTP_200_OK, dependencies=[role_checker])    
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session)):
    result = await book_service.delete_book(book_id, session)

    if result is False:
        raise NotFoundException(
            message="No book found to delete."
        )

    return {
        "sucess": True,
        "message": "Book deleted successfully."
    }




