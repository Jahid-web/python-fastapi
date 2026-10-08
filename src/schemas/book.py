import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.category import CategoryResponseSchema


class BookCreateSchema(BaseModel):
    title: str
    price: Decimal 
    stock: int 
    file_key: str | None = Field(default=None)
    cover_key: str | None = Field(default=None)
    description: str | None = Field(default=None)
    category_ids: list[uuid.UUID] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value:str):
        value = value.strip()
        if not value:
            raise ValueError("Book title must be required")            
        return value
    
    @field_validator("price")
    @classmethod
    def validate_price(cls, value:int):
        if value < 0:
            raise ValueError("Book price cannot be negative.")     
        if value.as_tuple().exponent < -2:
            raise ValueError(
                "Book price must have at most 2 decimal places."
            )       
        return value
    
    @field_validator("stock")
    @classmethod
    def validate_qty(cls, value:int):
        if value < 0:
            raise ValueError("Book quantity cannot be negative.")            
        return value

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
    categories: list[CategoryResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)

