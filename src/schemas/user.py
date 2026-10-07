import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.models.user import UserRole

class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str 
    password: str
    role: UserRole = UserRole.USER

    @field_validator("name")
    @classmethod
    def name_validator(cls, value:str):
        value = value.strip()
        if not value:
            raise ValueError("User name is required.")
        return value
    
    @field_validator("password")
    @classmethod
    def password_validator(cls, value:str):
        if not 3 <= len(value) <= 6:
            raise ValueError("Password must be between 3 and 6 characters.")
        return value

class UserResponseSchema(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    role: UserRole
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