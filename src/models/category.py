import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.main import Base

if TYPE_CHECKING:
    from .book import Book



class BookCategories(Base):
    __tablename__ = "book_categories"

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    books: Mapped[list["Book"]] = relationship(
        "Book",
        secondary="book_categories",
        back_populates="categories"
    )

