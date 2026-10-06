import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List

class TagModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    created_at: datetime

class TagCreateModel(BaseModel):
    name: str

class TagAddModel(BaseModel):
    tags: List[TagCreateModel]