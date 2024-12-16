from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from src.models.app_model import OrderStatusEnum


class OrderCreate(BaseModel):
    user_id: UUID
    total_price: float
    status: OrderStatusEnum | None = OrderStatusEnum.PENDING


class OrderOut(BaseModel):
    id: UUID
    user_id: UUID
    total_price: float
    status: OrderStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
