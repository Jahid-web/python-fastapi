import uuid
from sqlalchemy import String, Text, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.db.main import Base
from src.core.exceptions import ValidationException

if TYPE_CHECKING:
    from .book import Book
    from .user import User


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

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )

    # relation
    user: Mapped["User"] = relationship(
        "User",
        back_populates="author"
    )

    books: Mapped[list["Book"]] = relationship(
        "Book",
        back_populates="author"
    )

