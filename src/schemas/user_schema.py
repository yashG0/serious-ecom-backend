from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=22)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
