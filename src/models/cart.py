import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.main import Base

if TYPE_CHECKING:
    from .user import User
    from .book import Book


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="cart",
    )

    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "book_id",
            name="uq_cart_book",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )

    cart_id: Mapped[str] = mapped_column(
        ForeignKey(
            "carts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    book_id: Mapped[str] = mapped_column(
        ForeignKey(
            "books.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    cart: Mapped["Cart"] = relationship(
        "Cart",
        back_populates="items",
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="cart_items",
    )
