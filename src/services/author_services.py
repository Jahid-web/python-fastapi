from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.models.author import Author
from src.schemas.author import AuthorCreateSchema, AuthorResponseSchema

class AuthorService:
    async def create_author(self, author_data:AuthorCreateSchema, session: AsyncSession):
        try:
            author_data_dict = author_data.model_dump()
            
            new_author = Author(**author_data_dict)

            session.add(new_author)
            await session.commit()
            return new_author
       
        except Exception:
            await session.rollback()
            raise