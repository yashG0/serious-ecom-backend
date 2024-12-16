from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=32, description="The name of the product")
    description: str | None = Field(None, min_length=12, max_length=1024,
                                    description="Detailed description of the product")
    price: float = Field(..., gt=0, description="Price of the product, must be greater than 0")
    stock: int = Field(1, gt=0, description="Number of items in stock, defaults to 1")
    category_id: UUID = Field(..., description="The category ID the product belongs to")
    image_url: str = Field(None, description="URL to the product's image")


class ProductOut(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    stock: int
    category_id: UUID | None = None
    image_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
