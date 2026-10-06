import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class BookCreateSchema(BaseModel):
    title: str
    price: Decimal = Field(ge=0, decimal_places=2, description="book price")
    stock: int = Field(default=0, ge=0)
    author_id: uuid.UUID = Field(description="Author uuid")
    file_key: str | None = Field(default=None)
    cover_key: str | None = Field(default=None)
    description: str | None = Field(default=None)

class BookUpdateSchema(BaseModel):
    title: str
    price: Decimal = Field(ge=0, decimal_places=2, description="book price")
    stock: int = Field(default=0, ge=0)
    author_id: uuid.UUID = Field(description="Author uuid")
    file_key: str | None = Field(default=None)
    cover_key: str | None = Field(default=None)
    description: str | None = Field(default=None)

class BookResponseSchema(BaseModel):
    id: uuid.UUID
    title: str
    price: Decimal
    stock: int
    author_id: uuid.UUID
    file_key: str | None
    cover_key: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

