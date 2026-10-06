from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.schemas.user import UserCreateSchema
from src.core.security import hash_password

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
        await session.commit()
        return new_user