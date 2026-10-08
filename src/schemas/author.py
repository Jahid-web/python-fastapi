import uuid
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.book import BookResponseSchema


class AuthorCreateSchema(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )
    bio: str | None = None

class AuthorUpdateSchema(BaseModel):
    name: str = Field(min_length=3)
    bio: str | None

class AuthorResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    bio: str | None = None
    books: BookResponseSchema | None = None

    model_config = ConfigDict(from_attributes=True)