import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.main import Base

if TYPE_CHECKING:
    from .user import User
    from .book import Book
    from .order import Order


class Library(Base):
    __tablename__ = "library"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_library_user_book",
        ),
    )

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

    order_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="library",
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="library_entries",
    )

    order: Mapped["Order | None"] = relationship(
        "Order",
    )
