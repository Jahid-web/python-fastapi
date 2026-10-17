import uuid
from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime

class LibCreateSchema(BaseModel):
    book_id: uuid.UUID
    order_id: uuid.UUID | None = None


class LibOrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

class LibBookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str

class LibResponseSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    book_id: uuid.UUID
    order_id: uuid.UUID
    purchased_at: datetime

class LibPurchaseSchema(LibResponseSchema):
    book: LibBookSchema = None
    order: LibOrderSchema = None

class LibListResponseSchema(BaseModel):

    items: list[LibResponseSchema] = []
    total: int = Field(ge=0)

