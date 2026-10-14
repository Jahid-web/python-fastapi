from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
from typing import Any

from src.core.book_api_feature_config import BOOK_API_CONFIG
from src.models.book import Book
from src.models.author import Author
from src.core.exceptions import DatabaseException, NotFoundException
from src.schemas.book import BookCreateSchema, BookUpdateSchema
from src.models.category import Category
from src.utils.uploads import uploads
from src.utils.api_features import APIFeatures


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


    async def get_book_by_id(self, id:str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Book)
                .options(selectinload(Book.categories))
                .where(Book.id == id)
            )

            book = result.scalar_one_or_none()
            return book

        except Exception:
            await session.rollback()
            raise


    async def get_all_book(self, session: AsyncSession, *, page: int = 1, page_size: int = 20, search: str | None = None, category_name: str | None = None, year: int | None = None, sort_by = "created_at", sort_order: str = "desc") -> dict[str, Any]:        
        try:
            statement = (select(Book).options(selectinload(Book.categories), selectinload(Book.author)))

            # search
            # search_fields = [
            #     lambda term: Book.title.ilike(f"%{term}%"),
            #     lambda term: Book.author.has(
            #         Author.name.ilike(f"%{term}%")
            #     ),
            # ]

            # filter
            # filter_fields = {
            #     "category_name": lambda value: Book.categories.any(
            #         Category.name == str(value)
            #     ),
            #     "year": lambda value: (
            #         (Book.created_at >= date(int(value), 1, 1))
            #         & (
            #             Book.created_at < date(int(value) + 1, 1, 1)
            #         )
            #     )
            # }

            # sorting
            # sort_fields = {
            #     "created_at": Book.created_at,
            #     "title": Book.title
            # }
 
            params = {
                "page": page,
                "page_size": page_size,
                "search": search,
                "category_name": category_name,
                "year": year,
                "sort_by": sort_by,
                "sort_order": sort_order
            }

            features = APIFeatures(
                statement,
                params=params,
                config=BOOK_API_CONFIG,
                stable_sort=Book.id
            )

            return await (
                features
                .search()
                .filter()
                .sort()
                .paginate()
                .execute(session)
            )            

        except Exception:
            raise


    async def update_book(self, book_id:str, book_data:BookUpdateSchema, session: AsyncSession, cover_key: UploadFile | None = None, file_key: UploadFile | None = None):
        try:
            book_to_update = await self.get_book_by_id(book_id, session)

            if book_to_update is not None:
                update_data_dict = book_data.model_dump(exclude={"id", "category_ids", "cover_key", "file_key"}, exclude_unset=True)

                for k, v in update_data_dict.items():
                    setattr(book_to_update, k, v)

                if cover_key is not None:
                    upload_file = await uploads(cover_key)
                    book_to_update.cover_key = upload_file["filename"]

                if file_key is not None:
                    upload_file = await uploads(file_key)
                    book_to_update.file_key = upload_file["filename"]

                if "category_ids" in book_data.model_fields_set:
                    result = await session.execute(
                        select(Category).where(
                            Category.id.in_(book_data.category_ids)
                        )
                    )

                    categories = result.scalars().all()

                    if len(categories) != len(set(book_data.category_ids)):
                        raise ValueError("One or more categories do not exist")

                    book_to_update.categories = categories

                await session.commit()

                update_data = await session.execute(
                    select(Book).options(
                        selectinload(Book.categories)
                    ).where(Book.id == book_to_update.id)
                )

                book = update_data.scalar_one_or_none()
                return book

            else:
                None

        except Exception:
            await session.rollback()
            raise


    async def delete_book(self, book_id: str, session: AsyncSession):
        try:
            book = await self.get_book_by_id(book_id, session)

            if book is not None:
                await session.delete(book)
                await session.commit()

                return True

            else:
                None

        except Exception:
            await session.rollback()
            raise
