from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.config.db_setup import get_db
from src.schemas.categories import CategoryOut
from src.models.app_model import Category

category_routes = APIRouter(prefix="/api/category", tags=["Category Route"])


@category_routes.get("/all", response_model=list[CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


@category_routes.get("/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def get_category(category_id: UUID, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()  # type:ignore
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category
