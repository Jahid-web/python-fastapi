import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.db.main import Base
from src.core.exceptions import ValidationException

if TYPE_CHECKING:
    from .user import User
    from .book import Book


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True        
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="orders",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid.uuid4
    )

    order_id: Mapped[str] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE"
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

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="order_items",
    )

    @validates("price")
    def validate_price(self, key, value):
        if value < 0:
            raise ValidationException(
                message="Order price cannot be negative.",
                details="validation_error"
            )
        return value.strip()


    @validates("quantity")
    def validate_rating(self, key, value):
        if value < 0:
            raise ValidationException(
                message="Order quantity cannot be negative.",
                details="validation_error"
            )                
        return value.strip()