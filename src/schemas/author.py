import uuid
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.book import BookResponseSchema, BookSchema

class AuthorSchema(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    bio: str
class AuthorCreateSchema(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )
    bio: str | None = None

class AuthorUpdateSchema(BaseModel):
    id: uuid.UUID
    bio: str | None

class AuthorBookResponseSchema(BaseModel):
    id: uuid.UUID
    title: str
class AuthorResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    bio: str | None = None
    books: list[AuthorBookResponseSchema] = Field(
        default_factory=list
    )

    model_config = ConfigDict(from_attributes=True)