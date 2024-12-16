from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.schemas.cart_schema import CartOut, CartItemOut, CartCreate
from src.utils.looger_handler import logger
from src.config.db_setup import get_db
from src.routers.user_router import get_current_user
from src.schemas.user_schema import UserOut
from src.models.app_model import Cart, Product, CartItem

cart_routes = APIRouter(prefix="/api/cart", tags=["cart"])


# CART ->
@cart_routes.get("/get_cart", status_code=status.HTTP_200_OK, response_model=CartOut)
async def get_cart(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    is_cart_exist = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type:ignore
    if is_cart_exist is None:
        logger.info(f"Cart {current_user.username} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    logger.info(f"Cart has been successfully retrieved for user {current_user.username}!")
    return is_cart_exist


@cart_routes.post("/add_cart", status_code=status.HTTP_200_OK)
async def add_cart(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    is_cart_exist = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type:ignore
    if is_cart_exist:
        logger.info(f"Cart {current_user.id} already exists!")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cart already exists")

    cart = Cart(user_id=current_user.id)
    try:
        db.add(cart)
        db.commit()
        db.refresh(cart)  # Make sure to refresh to get the ID after commit
        logger.info(f"Cart {current_user.id} has been created!")
        return cart  # Ensure you are returning the cart object
    except Exception as e:
        logger.error(f"Failed to create cart {current_user.id}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create cart: {e}")


@cart_routes.delete("/remove_cart", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    is_cart_exist = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type:ignore
    if is_cart_exist is None:
        logger.info(f"Cart {current_user.username} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    try:
        db.delete(is_cart_exist)
        db.commit()
        logger.info(f"User {current_user.username}'s cart has been removed successfully!")
    except Exception as e:
        logger.error(f"Failed to remove cart {current_user.id}")
        raise Exception(f"Failed to remove cart: {e}")


# CART_ITEM ->
@cart_routes.get("/get_cart_items", status_code=status.HTTP_200_OK, response_model=list[CartItemOut])
async def get_cart_items(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    is_cart_exist = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type:ignore
    if is_cart_exist is None:
        logger.info(f"Cart {current_user.username} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    logger.info(f"Cart items has been successfully retrieved for user {current_user.username}!")
    cart_items = db.query(CartItem).filter(CartItem.cart_id == is_cart_exist.id).all()  # type:ignore
    return cart_items


@cart_routes.post("/add_cart_item", status_code=status.HTTP_201_CREATED)
async def add_cart_item(cart_item: CartCreate, db: Session = Depends(get_db),
                        current_user: UserOut = Depends(get_current_user)):
    is_cart_exist = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type:ignore
    if is_cart_exist is None:
        logger.info(f"Cart {current_user.username} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    is_product_exist = db.query(Product).filter(Product.id == cart_item.product_id).first()  # type:ignore
    if is_product_exist is None:
        logger.info(f"Product {cart_item.product_id} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if is_product_exist.stock < cart_item.quantity:
        logger.warning(f"Product {cart_item.product_id} doesn't have enough stock!")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product doesn't have enough stock!")

    is_product_exist.stock -= cart_item.quantity
    new_cart_item = CartItem(
        cart_id=is_cart_exist.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    db.add(new_cart_item)
    db.commit()  # Save changes to the database

    logger.info(f"Product {cart_item.product_id} added to cart for user {current_user.username}")


@cart_routes.put("/update_cart_item/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_cart_item(cart_item_id: UUID, quantity: int = Query(gt=0), db: Session = Depends(get_db),
                         current_user: UserOut = Depends(get_current_user)):
    is_cart_exist = db.query(CartItem).filter(CartItem.id == cart_item_id).first()  # type:ignore
    if is_cart_exist is None:
        logger.info(f"Cart item {cart_item_id} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    is_product_exist = db.query(Product).filter(Product.id == is_cart_exist.product_id).first()  # type:ignore
    if not is_product_exist:
        logger.warning(f"Product {is_cart_exist.product_id} doesn't exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if is_product_exist.stock + is_cart_exist.quantity < quantity:
        logger.warning(f"Product {is_cart_exist.product_id} doesn't have enough stock!")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product doesn't have enough stock!")

    is_product_exist.stock += is_cart_exist.quantity - quantity
    is_cart_exist.quantity = quantity
    db.commit()
    logger.info(f"Cart item {cart_item_id} has been updated successfully!")
    return is_cart_exist


@cart_routes.delete("/remove_cart_item/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(cart_item_id: UUID, db: Session = Depends(get_db),
                           current_user: UserOut = Depends(get_current_user)):
    is_cart_item_exist = db.query(CartItem).filter(CartItem.id == cart_item_id).first()  # type:ignore
    if is_cart_item_exist is None:
        logger.info(f"Cart item {cart_item_id} does not exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    is_product = db.query(Product).filter(Product.id == is_cart_item_exist.product_id).first()  # type:ignore
    if is_product is None:
        logger.warning(f"Product {is_cart_item_exist.product_id} doesn't exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    is_product.stock += is_cart_item_exist.quantity
    db.commit()
    try:
        db.delete(is_cart_item_exist)
        db.commit()
        logger.info(f"Cart item {cart_item_id} has been removed successfully!")

    except Exception as e:
        logger.error(f"Failed to remove cart item {cart_item_id}")
        raise Exception(f"Failed to remove cart item: {e}")
