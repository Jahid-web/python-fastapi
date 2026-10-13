from fastapi import APIRouter, status, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from typing import Literal

from src.db.main import get_session
from src.core.exceptions import NotFoundException, ForbiddenException
from src.services.book_services import BookService
from src.utils.dependencies import RoleChecker, AccessTokenBearer
from src.schemas.book import BookCreateSchema, BookUpdateSchema, BookResponseSchema, BookSchema, PaginatedBookResponseSchema
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

@book_router.get("/", response_model=PaginatedBookResponseSchema, dependencies=[role_checker], status_code=status.HTTP_200_OK)
async def get_all_book(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=200),
    category_name: str | None = Query(None, max_length=200),
    # language: str | None = Query(None, max_length=10),
    year: int | None = Query(None, ge=1, le=9998),
    sort_by: Literal[
        "created_at", "title", "publication_date"
    ] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    session: AsyncSession = Depends(get_session), 
    _:dict = Depends(access_token_bearer)):

    books = await book_service.get_all_book(
        session=session,
        page=page,
        page_size=page_size,
        search=search,
        category_name=category_name,
        # language=language,
        year=year,
        sort_by=sort_by,
        sort_order=sort_order
    )

    if not books["items"]:
        raise NotFoundException(
            message="No books found",
            details={
                "page": page,
                "search": search,
            },
        )

    return {
        "message": "Available books list.",
        "book_nos": f'{books["pagination"]["total"]} Nos',
        **books,
    }

@book_router.patch("/{book_id}", response_model=BookSchema, dependencies=[role_checker], status_code=status.HTTP_201_CREATED)
async def update_book(book_id:str, book_data: str = Form(), session: AsyncSession = Depends(get_session), cover_key: UploadFile | None = File(None), file_key: UploadFile | None = File(None)):
    try:
    
        parse_data = BookUpdateSchema.model_validate_json(book_data)

    except (ValidationError, ValueError) as exc:       
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid book_data JSON or fields",
        ) from exc

    updated_book = await book_service.update_book(book_id, parse_data, session, cover_key, file_key)

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




