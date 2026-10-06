import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ReviewModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: uuid.UUID
    rating: int = Field(lt=5)
    review_text: str
    user_id: uuid.UUID
    book_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str