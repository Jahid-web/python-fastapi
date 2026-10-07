from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from src.models.book import Book
from src.core.exceptions import ConflictException, DatabaseException
from src.schemas.book import BookCreateSchema, BookUpdateSchema


class BookService:
    async def create_book(self, book_data: BookCreateSchema, user_id: str, session: AsyncSession):
        try:
            book_data_dict = book_data.model_dump()
            
            new_book = Book(**book_data_dict)
    
            new_book.author_id = user_id
            session.add(new_book)
    
            await session.commit()
            await session.refresh(new_book)
            return new_book

        except Exception:
            raise

        # except IntegrityError as exc:
        #     await session.rollback()

        #     err_msg = str(exc.orig)

        #     if "uq_book_title" in err_msg:
        #         raise ConflictException(
        #             message="Title already exits.",
        #             details= { "field": "title"}
        #         )
        #     raise ConflictException(
        #         message="Book already exits.",
        #         details={}
        #     )

        # except OperationalError:
        #     await session.rollback()

        #     raise DatabaseException(
        #         message="Database error occured.",
        #         details={}
        #     )

        # except SQLAlchemyError:
        #     await session.rollback()

        #     raise DatabaseException(
        #         message="Database error occured.",
        #         details={}
        #     )



    async def get_all_book(self, session: AsyncSession):
        try:
            statement = select(Book).order_by(Book.created_at.desc())
            result = await session.execute(statement)
    
            books = result.scalars().all()
            return books

        except Exception:
            raise