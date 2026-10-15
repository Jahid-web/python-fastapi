import uuid
from typing import Literal
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class OrderItemCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_id: uuid.UUID
    quantity: int = Field(gt=0, le=1000)
    price: Decimal = Field(default=None, ge=0)


class OrderCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[OrderItemCreateSchema] = Field(
        min_length=1,
        max_length=100,
    )


class OrderItemResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    book_id: uuid.UUID
    quantity: int
    price: Decimal


class OrderResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemResponseSchema]

class OrderStatusUpdate(BaseModel):
    status: Literal[
        "confirmed",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
    ]


class OrderListResponse(BaseModel):
    items: list[OrderResponseSchema]
    total: Decimal
    page: int
    page_size: int

