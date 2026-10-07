import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, func, Integer, ForeignKey, Text, Uuid, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.db.main import Base


if TYPE_CHECKING:
    from .author import Author
    from .category import Category
    from .review import Review
    from .order import OrderItem
    from .cart import CartItem
    from .library import Library


class Book(Base):
    __tablename__ = "books"

    __table_args__ = (
        UniqueConstraint("title", name="uq_book_title")
    ),

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index= True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    author_id: Mapped[str] = mapped_column(
        ForeignKey(
            "authors.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    file_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    cover_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

# relations
    author: Mapped["Author"] = relationship(
        "Author",
        back_populates="books"
    )

    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary="book_categories",
        back_populates="books"
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="book"
    )

    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="book"
    )

    library_entries: Mapped[list["Library"]] = relationship(
        "Library",
        back_populates="book",
        cascade="all, delete-orphan",
    )