import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field

from src.reviews.schema import ReviewModel
from src.tags.schema import TagModel

class Book(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str = Field(min_length=3, max_length=50)
    author: str = Field(min_length=3, max_length=40)
    publisher: str = Field(min_length=3, max_length=40)
    published_date: datetime
    page_count: int
    language: str = Field(min_length=3, max_length=40)
    created_at: datetime
    updated_at: datetime

class BookDetailModel(Book):
    reviews: List[ReviewModel]
    tags: List[TagModel]

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str