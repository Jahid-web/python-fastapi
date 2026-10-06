from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.db.model import Book
from .schema import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(Book.created_at.desc())

        result = await session.execute(statement)

        books = result.scalars().all()

        return books


    async def get_user_books(self, user_id: str, session: AsyncSession) -> list[Book]:
        statement = select(Book).where(Book.user_id == user_id).order_by(Book.created_at.desc())
        
        result = await session.execute(statement)
        return result.scalars().all()


    async def get_a_book(self, book_id: str, session: AsyncSession):
        statement = select(Book).where(Book.id == book_id)

        result = await session.execute(statement)
        return result.scalar_one_or_none()


    async def create_book(self, book_data: BookCreateModel, user_id: str, session: AsyncSession):
        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict)

        # new_book.published_date = datetime.strftime(
        #     book_data_dict["published_date"], "%Y-%m-%d"
        # )

        new_book.user_id = user_id
        session.add(new_book)

        await session.commit()
        await session.refresh(new_book)
        return new_book
        

    async def update_book(self, book_id: str, update_data: BookUpdateModel, session: AsyncSession):
        book_to_update = await self.get_a_book(book_id, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            return book_to_update

        else:
            return None


    async def delete_book(self, book_id: str, session: AsyncSession):
        book_tok_delete = await self.get_a_book(book_id, session)

        if book_tok_delete is not None:
            await session.delete(book_tok_delete)

            await session.commit()
            return {}

        else:
            return None