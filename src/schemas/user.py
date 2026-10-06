import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str = Field(min_length=3, max_length=15)
    password: str = Field(min_length=3)

class UserResponseSchema(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=3)


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str

class MessageResponseSchema(BaseModel):
    message: str