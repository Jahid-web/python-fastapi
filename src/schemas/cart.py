from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreateSchema(BaseModel):
    book_id: UUID
    quantity: int = Field(default=1, ge=1, le=100)


class CartItemUpdateSchema(BaseModel):
    quantity: int = Field(ge=1, le=100)


class CartItemReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    book_id: UUID
    quantity: int


class CartReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    items: list[CartItemReadSchema]


class CartItemDetailSchema(BaseModel):
    id: UUID
    book_id: UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class CartSummarySchema(BaseModel):
    cart_id: UUID
    total_items: int
    distinct_books: int
    subtotal: Decimal


class CartDetailSchema(BaseModel):
    cart_id: UUID
    created_at: datetime
    updated_at: datetime
    items: list[CartItemDetailSchema]
    total_items: int
    distinct_books: int
    subtotal: Decimal


class CartValidationIssueSchema(BaseModel):
    book_id: UUID
    message: str


class CartValidationResultSchema(BaseModel):
    valid: bool
    issues: list[CartValidationIssueSchema]