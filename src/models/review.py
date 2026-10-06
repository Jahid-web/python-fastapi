import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.db.main import Base
from src.core.exceptions import ValidationException

if TYPE_CHECKING:
    from .user import User
    from .book import Book


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint(
            "rating >=1 AND rating <=5",
            name="check_review_rating"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
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

    book_id: Mapped[str] = mapped_column(
        ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    rating: Mapped[int] = mapped_column(
        nullable=False
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="reviews"
    )

    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="reviews"
    )

    @validates("rating")
    def validate_rating(self, key, value):
        if not 1 <= value <= 5:
            raise ValidationException(
                message="Rating must be between 1 and 5.",
                details="validation_error"
            )
        return value