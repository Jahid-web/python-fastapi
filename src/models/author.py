import uuid
from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from typing import TYPE_CHECKING

from src.db.main import Base
from src.core.exceptions import ValidationException

if TYPE_CHECKING:
    from .book import Book


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        index=True,
        nullable=False,
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # relation
    books: Mapped[list["Book"]] = relationship(
        "Book",
        back_populates="author"
    )


    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValidationException(
                message="Author name is required!",
                details="validation_error"
            )
        return value.strip()
