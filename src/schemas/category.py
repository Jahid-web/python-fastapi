import uuid
from pydantic import BaseModel, ConfigDict, field_validator

class CategoryCreateSchema(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def cat_name_validator(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Category name is required.")
        return value

class CategoryUpdateSchema(BaseModel):
    name: str

class CategoryResponseSchema(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)