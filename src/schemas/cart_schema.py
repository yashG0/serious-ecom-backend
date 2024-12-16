from pydantic import BaseModel, Field
from uuid import UUID


class CartCreate(BaseModel):
    product_id: UUID = Field(..., description="The ID of the product to add to the cart")
    quantity: int = Field(..., gt=0, description="The quantity of the product to add to the cart")


class CartItemOut(BaseModel):
    id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
