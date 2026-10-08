from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.book import Book
from src.models.author import Author
from src.core.exceptions import DatabaseException, NotFoundException
from src.schemas.book import BookCreateSchema, BookUpdateSchema
from src.models.category import Category


class BookService:
    async def create_book(self, book_data: BookCreateSchema, user_id: str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Author).where(
                    Author.user_id == user_id
                )
            )

            author = result.scalar_one_or_none()

            if not author:
                raise NotFoundException(
                    message="Author profile not found.",
                    details={}
                )


            categories = []

            if book_data.category_ids:
                result = await session.execute(
                    select(Category).where(
                        Category.id.in_(book_data.category_ids)
                    )
                )

                categories = list(result.scalars().all())

                found_cat_ids = {category.id for category in categories}
                req_ids = set(book_data.category_ids)

                missing_ids = req_ids - found_cat_ids

                if missing_ids:
                    raise NotFoundException(
                        message="One or more categories not found",
                        details={}
                    )

            book_data_dict = book_data.model_dump(
                exclude={"category_ids"}
            )            
                        
            new_book = Book(**book_data_dict,
                            author_id=author.id
                            )
    
            new_book.categories = categories

            session.add(new_book)
    
            await session.commit()
            await session.refresh(new_book)
            return new_book

        except Exception:
            raise


    async def get_book_by_title(self, title:str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Book).where(
                    Book.title == title
                )
            )

            book = result.scalar_one_or_none()
            return book

        except Exception:
            await session.rollback()
            raise



    async def get_all_book(self, session: AsyncSession):
        try:
            statement = select(Book).options(selectinload(Book.categories)).order_by(Book.created_at.desc())
            result = await session.execute(statement)
    
            books = result.scalars().all()
            return books

        except Exception:
            raise