import uuid
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
from decimal import Decimal

from src.schemas.book import BookResponseSchema

class LibCreateSchema(BaseModel):
    book_id: uuid.UUID
    order_id: uuid.UUID | None = None


class LibOrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

class BookEntriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

class LibBookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    library_entries: list[BookEntriesSchema] = []

class LibResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    book_id: uuid.UUID
    order_id: uuid.UUID
    purchased_at: datetime
    book: LibBookSchema


class LibPurchaseSchema(LibResponseSchema):
    book: LibBookSchema = None
    order: LibOrderSchema = None

class LibListResponseSchema(BaseModel):

    items: list[LibResponseSchema]
    total: int


