# import uuid
# from datetime import datetime
# from sqlalchemy import Boolean, DateTime, String, func, Uuid, ForeignKey, CheckConstraint, Text
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from src.db.main import Base



# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     email: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         index=True,
#         nullable=False
#     )

#     username: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False
#     )

#     role: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         server_default="user"
#     )

#     hashed_password: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False
#     )

#     is_verified: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         nullable=False
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#         nullable=False
#     )

#     # relation
#     books: Mapped[list["Book"]] = relationship(
#         back_populates="user",
#         lazy="selectin",
#     )

#     reviews: Mapped[list["Review"]] = relationship(
#         back_populates="user",
#         lazy="selectin"
#     )


# # BOOKS MODEL
# class Book(Base):
#     __tablename__ = "books"

#     id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     title: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False      
#     )

#     author: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False      
#     )

#     publisher: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False      
#     )

#     published_date: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False    
#     )

#     page_count: Mapped[int] = mapped_column(
#         nullable=False
#     )

#     language: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False       
#     )

#     created_at: Mapped[DateTime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now()
#     )

#     updated_at: Mapped[DateTime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#         onupdate=func.now()
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         ForeignKey("users.id"),
#         nullable=True
#     )

#     # Relationships
#     user: Mapped["User | None"] = relationship(
#         back_populates="books"
#     )

#     reviews: Mapped[list["Review"]] = relationship(
#         back_populates="book",
#         lazy="selectin",
#         cascade="all, delete-orphan"
#     )

#     tags: Mapped[list["Tag"]] = relationship(
#         secondary="book_tags",
#         back_populates="books",
#         lazy="selectin"
#     )

# # REVIEW MODEL
# class Review(Base):
#     __tablename__ = "reviews"

#     __table_args__ = (
#         CheckConstraint(
#             "rating >= 1 AND rating <= 5",
#             name = "check_review_rating",
#         ),
#     )

#     id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     rating: Mapped[int] = mapped_column(
#         nullable=False
#     )

#     review_text: Mapped[str] = mapped_column(
#         Text,
#         nullable=False
#     )

#     book_id: Mapped[uuid.UUID | None] = mapped_column(
#         ForeignKey("books.id"),
#         nullable=True
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         ForeignKey("users.id"),
#         nullable=True
#     )

#     created_at: Mapped[DateTime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now()
#     )
    
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#         onupdate=func.now()
#     )

#     # relations
#     user: Mapped["User | None"] = relationship(
#         back_populates="reviews"
#     )

#     book: Mapped["Book | None"] = relationship(
#         back_populates="reviews"
#     )     

# # TAG MODEL
# class BookTag(Base):
#     __tablename__ = "book_tags"

#     book_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("books.id"),
#         primary_key=True,
#     )

#     tag_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("tags.id"),
#         primary_key=True,
#     )

    

# class Tag(Base):
#     __tablename__ = "tags"

#     id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#         index=True
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now()
#     )

#     books: Mapped[list["Book"]] = relationship(
#         secondary="book_tags",
#         back_populates="tags",
#         lazy="selectin"
#     )