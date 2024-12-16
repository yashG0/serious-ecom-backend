from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.utils.looger_handler import logger
from src.config.db_setup import get_db
from src.models.app_model import Product
from src.schemas.product_schema import ProductOut

product_routes = APIRouter(prefix="/api/product", tags=["Product Route"])


@product_routes.get("/all", status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    logger.info(f"All products has been fetched successfully!")
    return products


@product_routes.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductOut)
async def get_product_by_id(product_id: UUID, db: Session = Depends(get_db)):
    is_product_exist = db.query(Product).filter(Product.id == product_id).first()  # type:ignore
    if not is_product_exist:
        logger.warning(f"Product {product_id} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not found")

    return is_product_exist
