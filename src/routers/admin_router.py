from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from uuid import UUID

from src.models.app_model import Category, Product, OrderStatusEnum, Order
from src.schemas.categories import CategoryCreate, CategoryOut
from src.schemas.product_schema import ProductCreate
from src.utils.looger_handler import logger
from src.config.db_setup import get_db
from src.routers.auth_router import is_admin_user
from src.schemas.user_schema import UserOut

admin_routes = APIRouter(prefix="/api/admin", tags=["Admin routes"], dependencies=[Depends(is_admin_user)])


# check is user admin?
@admin_routes.get("/is_user_admin", status_code=status.HTTP_200_OK)
async def check_admin(current_user: UserOut = Depends(is_admin_user)) -> bool:
    return current_user.is_admin


# category routes ->
@admin_routes.post("/add_category", status_code=status.HTTP_201_CREATED)
async def add_new_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    new_category = Category(**category_data.model_dump())

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        logger.info(f"New Category {category_data.name} has been created successfully!")
    except Exception as e:
        logger.error(f"Failed to create new category {category_data.name}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create new category {e}")


@admin_routes.get("/categories", response_model=list[CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


@admin_routes.get("/category/{category_id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def get_category(category_id: UUID, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()  # type:ignore
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


# product router ->
@admin_routes.post("/product/add_product", status_code=status.HTTP_201_CREATED)
async def add_new_product(new_product: ProductCreate, db: Session = Depends(get_db)):
    is_category_exist = db.query(Category).filter(Category.id == new_product.category_id).first()  # type:ignore
    if is_category_exist is None:
        logger.warning(f"Category doesn't exist! please register first")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category doesn't Exist! please re-check id!")

    new_product = Product(
        name=new_product.name,
        description=new_product.description,
        price=new_product.price,
        stock=new_product.stock,
        image_url=new_product.image_url,
        category_id=new_product.category_id
    )
    try:
        db.add(new_product)
        db.commit()
        logger.info(f"Product {new_product.name} has been successfully created!")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create new product {e}")


@admin_routes.put("/product/update/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(new_product: ProductCreate, product_id: UUID, db: Session = Depends(get_db)):
    is_product_exist = db.query(Product).filter(Product.id == product_id).first()  # type:ignore
    if is_product_exist is None:
        logger.warning(f"Product doesn't exist! please register first")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product doesn't Exist! please re-check id!")
    is_product_exist.name = new_product.name
    is_product_exist.description = new_product.description
    is_product_exist.price = new_product.price
    is_product_exist.stock = new_product.stock
    is_product_exist.category_id = new_product.category_id
    is_product_exist.image_url = new_product.image_url

    try:
        db.commit()
        logger.info(f"Product {new_product.name} has been updated Successfully!")
    except Exception as e:
        db.rollback()
        logger.error("Failed to update existing product!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update Product {e}")


@admin_routes.delete("/product/remove/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(product_id: UUID, db: Session = Depends(get_db)):
    is_product_exist = db.query(Product).filter(Product.id == product_id).first()  # type:ignore
    if is_product_exist is None:
        logger.warning(f"Product {product_id} doesn't exist! please verify product id.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product doesn't exist")
    try:
        db.delete(is_product_exist)
        db.commit()
        logger.info(f"Product {is_product_exist.name} has been removed successfully!")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to remove product {product_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to remove product {e}")


# order router ->
@admin_routes.put("/order/update_status/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_status_in_order(order_id: UUID, new_status: OrderStatusEnum, db: Session = Depends(get_db)):
    is_order = db.query(Order).filter(Order.id == order_id).first()  # type:ignore
    if is_order is None:
        logger.warning(f"Order {order_id} doesn't Found!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} doesn't Found!")

    try:
        is_order.status = new_status
        logger.info(f"Order {order_id} has been updated!")
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Failed to update order {order_id}: {str(e)}")
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to update order {order_id}: {str(e)}")
