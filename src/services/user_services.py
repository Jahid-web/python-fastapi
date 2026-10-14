from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User
from src.models.author import Author
from src.models.book import Book
from src.schemas.user import UserCreateSchema, UserUpdateSchema
from src.core.security import hash_password
from src.models.user import UserRole
from src.models.author import Author
from src.schemas.author import AuthorCreateSchema, AuthorUpdateSchema

class UserService:
    async def get_user_by_email(self, email:str, session: AsyncSession):
        result = await session.execute(
            select(User).options(selectinload(User.author)).where(
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

    async def update_me(self, user_email: str, data:UserUpdateSchema, session: AsyncSession):
        try:
            user = await self.get_user_by_email(user_email, session)

            if user is not None:
                user_dict = data.model_dump(exclude_unset=True)

                for k, v in user_dict.items():
                    setattr(user, k, v)

                if "name" in user_dict and user.author is not None:
                    user.author.name = user.name

            await session.commit()
            await session.refresh(user)
            return user
        except Exception:
            await session.rollback()
            raise

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

    async def get_author_by_id(self, author_id:str, session: AsyncSession):

        try:
            result = await session.execute(
                select(Author).where(
                    Author.id == author_id
                )
            )
            author = result.scalar_one_or_none()
            return author
        except Exception:
            await session.rollback()
            raise

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

    async def update_author(self, author_id:str, author_data:AuthorUpdateSchema, session: AsyncSession):
        try:
            author = await self.get_author_by_id(author_id, session)

            if author is not None:
                author_dict = author_data.model_dump()

                for k, v in author_dict.items():
                    setattr(author, k, v)

                await session.commit()
                return author
            else:
                return None
        
        except Exception:
            await session.rollback()
            raise

    async def delete_author(self, author_id:str, session: AsyncSession):
        try:
            author = await self.get_author_by_id(author_id, session)

            if author is not None:
                await session.delete(author)
                await session.commit()
                return True
            else:
                return None

        except Exception:
            await session.rollback()
            raise

    async def delete_user(self, user_id:str, session: AsyncSession):
        try:
            result = await session.execute(
                select(User).where(
                    User.id == user_id
                )
            )

            user = result.scalar_one_or_none()

            if user is not None:
                await session.delete(user)
                await session.commit()
                return True
            else:
                return None

        except Exception:
            await session.rollback()
            raise