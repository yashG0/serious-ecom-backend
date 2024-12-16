from pydantic import BaseModel, Field
from uuid import UUID


# Schema for creating a category
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=32, description="Category name")
    description: str | None = Field(None, min_length=10, max_length=1024, description="Category description")


class CategoryOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    class Config:
        from_attributes = True
