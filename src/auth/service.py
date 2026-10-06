from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.model import User
from src.auth.schemas import UserCreate
from src.auth.utils import hash_password

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        result =await session.execute(
            select(User).where(
                User.email == email
            )
        )

        user = result.scalar_one_or_none()
        return user


    async def user_exist(self, email:str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False


    async def create_user_account(self, data: UserCreate, session: AsyncSession):
        user_data_dict = data.model_dump()      
        password = user_data_dict.pop("password")  

        new_user = User(**user_data_dict,
                        hashed_password = hash_password(password)
                        )        

        session.add(new_user)
        await session.commit()

        return new_user


    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return user
