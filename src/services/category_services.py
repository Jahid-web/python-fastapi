from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.models.category import Category
from src.schemas.category import CategoryCreateSchema

class CategoryService:
    async def create_categories(self, data:CategoryCreateSchema, session: AsyncSession):
        try:
            cat_data_dict = data.model_dump()

            new_cat = Category(**cat_data_dict)
            session.add(new_cat)

            await session.commit()
            await session.refresh(new_cat)
            return new_cat

        except Exception:
            await session.rollback()
            raise

    async def get_cat_by_name(self, name:str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Category).where(
                    Category.name == name
                )
            )

            cat = result.scalar_one_or_none()
            return cat

        except Exception:
            await session.rollback()
            raise

    async def get_all_cat(self, session: AsyncSession):
        try:
            result = await session.execute(
                select(Category)
            )

            categories = result.scalars().all()
            return categories

        except Exception:
            await session.rollback()
            raise
