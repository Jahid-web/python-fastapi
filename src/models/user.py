import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, func, String, Uuid, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from email_validator import validate_email, EmailNotValidError

from src.db.main import Base
from src.core.exceptions import ValidationException


if TYPE_CHECKING:
    from .review import Review
    from .cart import Cart
    from .order import Order
    from .library import Library
    from .author import Author


class UserRole(str, enum.Enum):
    USER = "user"
    AUTHOR = "author"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        unique=True,
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    author: Mapped["Author | None"] = relationship(
        "Author",
        back_populates="user",
        uselist=False
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


# relation
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    library: Mapped[list["Library"]] = relationship(
        "Library",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    cart: Mapped[list["Cart | None"]] = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValidationException(
                message="Name cannot be empty.",
                details="validation_error"
            )
        if len(value.strip()) < 3:
            raise ValidationException(
                message="Name must contain at least 3 character.",
                details="validation_error"
            )
        return value.strip()

    @validates("email")
    def validate_email(self, key, value):
        try:
            validated = validate_email(value)
            return validated.normalized
        except EmailNotValidError as exc:
            raise ValidationException(
                message="Email is Not valid.",
                details= str(exc)
            )

        