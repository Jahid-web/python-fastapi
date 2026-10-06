from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from .service import BookService
from src.db.main import get_session
from src.core.exceptions import NotFoundException
from .schema import Book, BookCreateModel, BookUpdateModel, BookDetailModel


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))



@book_router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_book(session: AsyncSession = Depends(get_session), _:dict = Depends(access_token_bearer)):
    books = await book_service.get_all_books(session)

    if not books:
        raise NotFoundException(
            message="Books Not Found.",
            details={}
        )

    return books


@book_router.get("/user/{user_id}", response_model=List[Book], dependencies=[role_checker])
async def get_user_book_submission(user_id: str, session: AsyncSession = Depends(get_session)):
    books = await book_service.get_user_books(user_id, session)

    if not books:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="User book not found.")

    return books


@book_router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def create_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    user_id = token_details.get('user')["user_id"]
    
    new_book = await book_service.create_book(book_data, user_id, session)

    return new_book


@book_router.get("/{book_id}", response_model=BookDetailModel, dependencies=[role_checker])
async def get_book(book_id: str, session: AsyncSession = Depends(get_session), _:dict = Depends(access_token_bearer)):
    book = await book_service.get_a_book(book_id, session)

    if book:
        return book
    else:
        raise NotFoundException(
            message="No Book Found."
        )

