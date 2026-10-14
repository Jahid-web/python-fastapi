from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import DatabaseException, NotFoundException
from src.models.library import Library
from src.schemas.library import LibResponseSchema

class LibraryService:
    async def get_all_lib(self, session: AsyncSession):
        try:
            result = await session.execute(
                select(Library).options(
                    selectinload(Library.book),
                    selectinload(Library.order),
                )
            )

            librarys = result.scalars().all()

            return librarys

        except Exception:
            await session.rollback()
            raise

    async def get_lib_by_id(self, lib_id: str, lib_data: LibResponseSchema, session: AsyncSession):
        try:
            result = await session.execute(
                select(Library).options(
                    selectinload(Library.book),
                    selectinload(Library.order),
                ).where(
                    Library.id == lib_id
                )
            )

            library = result.scalar_one_or_none()
            return library

        except Exception:
            await session.rollback()
            raise


    async def get_lib_purchase_details(self, lib_id: str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Library).options(
                    selectinload(Library.book),
                    selectinload(Library.order),
                ).where(
                    Library.id == lib_id
                )
            )

            library = result.scalar_one_or_none()
            return library

        except Exception:
            await session.rollback()
            raise

    async def get_lib_order(self, user_id: str, order_id: str, session: AsyncSession):
        try:
            result = await session.execute(
                select(Library).options(
                    selectinload(Library.book),
                    selectinload(Library.order),
                ).where(
                    Library.user_id == user_id,
                    Library.order_id == order_id,
                )
            )

            lib_order = result.scalar_one_or_none()
            return lib_order

        except Exception:
            await session.rollback()
            raise