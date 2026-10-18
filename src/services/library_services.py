import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import DatabaseException, NotFoundException, ConflictException
from src.models.library import Library
from src.models.book import Book
from src.models.order import Order
from src.schemas.library import LibResponseSchema, LibResponseSchema, LibPurchaseSchema

class LibraryService:
    # GET /library  ----  List the authenticated user's books
    async def get_user_all_lib(self, user_id: str, session: AsyncSession) -> tuple[list[LibResponseSchema], int]:
        try:
            count_result = await session.execute(
                select(func.count())
                .select_from(Library).where(
                    Library.user_id == user_id
                )
            )

            total = count_result.scalar_one_or_none()

            result = await session.execute(
                select(Library).where(
                    Library.user_id == user_id
                ).options(selectinload(Library.book).selectinload(Book.library_entries))
                .order_by(Library.purchased_at.desc())
            )

            librarys = result.scalars().all()

            return list(librarys), total

        except Exception:
            await session.rollback()
            raise

    # GET /library/{entry_id}  ---- Get one library entry        
    async def get_lib_by_entry_id(self, user_id: str, entry_id: str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Library).where(
                    Library.id == entry_id,
                    Library.user_id == user_id
                ).options(
                    selectinload(Library.book),
                    selectinload(Library.order),
                )
            )

            library = result.scalar_one_or_none()
            return library

        except Exception:
            await session.rollback()
            raise
    
    # GET /library/book/{book_id}  ----  Check whether a book is in the user's library
    async def get_lib_book(self, user_id: str, book_id: str, session: AsyncSession) -> LibResponseSchema | None:
        try:
            result = await session.execute(
                select(Library).where(
                    Library.user_id == user_id,
                    Library.book_id == book_id
                ).options(selectinload(Library.book).selectinload(Book.library_entries))
            )

            lib_book = result.scalar_one_or_none()
            return lib_book

        except Exception:
            await session.rollback()
            raise

    # POST /library  ---- Add a book to the library      
    async def add_to_lib(self, user_id: str, book_id: str, order_id: str | None, session: AsyncSession) -> LibResponseSchema:
        
        try:
            book = await session.execute(
                select(Book).where(
                    Book.id == book_id
                )                
            )

            if book.scalar_one_or_none() is None:
                raise NotFoundException(
                    message="No book found.",
                    details={}
                )

            existing_book = await self.get_lib_book(user_id, book_id, session)

            if existing_book is not None:
                raise ConflictException(
                    message="Book already exists in your library",
                    details={}
                )

            if order_id is not None:
                result = await session.execute(
                    select(Order).where(
                        Order.id == order_id,
                        Order.user_id == user_id
                    )
                )

                order = result.scalar_one_or_none()

                if order is None:
                    raise NotFoundException(
                        message="Order not found.",
                        details={}
                    )

                # IMPORTANT:
                # Also validate the order's paid/completed status here,
                # using the actual status field in your Order model.
            entry = Library(
                user_id=user_id,
                book_id=book_id,
                order_id=order_id,
            )

            session.add(entry)
            await session.commit()
            await session.refresh(entry)

            result = await session.execute(
                select(Library).where(
                    Library.id == entry.id
                ).options(
                    selectinload(Library.book),
                    selectinload(Library.order)
                )
            )

            lib = result.scalar_one_or_none()
            return lib

        except Exception:
            await session.rollback()
            raise

    # GET /library/{entry_id}/details  ---- Get the entry with book and order details
    async def get_lib_purchase_details(self, lib_id: str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Library).options(
                    selectinload(Library.book),
                    selectinload(Library.order),
                ).where(
                    Library.id == lib_id
                )
            )

            library = result.scalar_one_or_none()
            return library

        except Exception:
            await session.rollback()
            raise

    async def get_lib_order(self, user_id: str, order_id: str, session: AsyncSession) -> list[LibPurchaseSchema]:
        try:
            result = await session.execute(
                select(Library).options(
                    selectinload(Library.book).selectinload(Book.library_entries),
                    selectinload(Library.order),
                ).where(
                    Library.user_id == user_id,
                    Library.order_id == order_id,
                )
            )

            lib_order = result.scalars().all()
            return lib_order

        except Exception:
            await session.rollback()
            raise

    # DELETE /library/{entry_id}  ---- Remove a library entry
    async def delete_lib(self, user_id: str, entry_id: str, session: AsyncSession) -> None:
        try:
            lib = await self.get_lib_by_entry_id(user_id, entry_id, session)

            await session.delete(lib)
            await session.commit()

            return True
        except Exception:
            await session.rollback()
            raise
    
