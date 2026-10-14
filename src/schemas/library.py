import uuid
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class LibOrderSchema(BaseModel):
    id: uuid.UUID


class LibBookSchema(BaseModel):
    id: uuid.UUID
    title: str

class LibResponseSchema(BaseModel):
    id: uuid.UUID
    user_id: str
    book_id: str
    order_id: str
    purchased_at: datetime
    book: LibBookSchema = None
    order: LibOrderSchema = None

class LibPurchaseSchema(BaseModel):
    purchased_at: datetime
    book: LibBookSchema = None
    order: LibOrderSchema = None

