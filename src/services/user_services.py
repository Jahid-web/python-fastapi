from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User
from src.models.author import Author
from src.schemas.user import UserCreateSchema
from src.core.security import hash_password
from src.models.user import UserRole

class UserService:
    async def get_user_by_email(self, email:str, session: AsyncSession):
        result = await session.execute(
            select(User).where(
                User.email == email
            )
        )

        user = result.scalar_one_or_none()
        return user


    async def create_user_account(self, data: UserCreateSchema, session: AsyncSession):
        user_data_dict = data.model_dump()
        password = user_data_dict.pop("password")

        new_user = User(**user_data_dict,
                        password = hash_password(password))


        session.add(new_user)
        await session.flush()
     
        if new_user.role == UserRole.AUTHOR:
            new_author = Author(
                user_id=new_user.id,
                name=new_user.name,
            )

            session.add(new_author)

        await session.commit()
        await session.refresh(new_user)
        return new_user


    async def get_all_users(self, session: AsyncSession):
        try:
            result = await session.execute(
                select(User).options(selectinload(User.author))
                )
            users = result.scalars().all()
            return users
        except Exception:
            await session.rollback()
            raise

    async def get_authors(self, session: AsyncSession):
        try:
            result = await session.execute(
                select(Author).options(selectinload(Author.books))
            )
            authors = result.scalars().all()
            return authors

        except Exception:
            await session.rollback()
            raise