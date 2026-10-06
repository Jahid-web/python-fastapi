from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List

from src.books.schema import Book
from src.reviews.schema import ReviewModel



class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=6)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class RefreshTokenRequest(BaseModel):
    refresh_totken: str

class MessageResponse(BaseModel):
    message: str

class EmailModel(BaseModel):
    addresses: List[str]

class PasswordRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModed(BaseModel):
    new_password: str
    confirm_new_password: str


class UserBookModel(UserResponse):
    books: List[Book]
    reviews: List[ReviewModel]