from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.schemas.order_schema import OrderOut
from src.utils.looger_handler import logger
from src.models.app_model import Cart, CartItem, Order, Product, OrderStatusEnum
from src.config.db_setup import get_db
from src.routers.user_router import get_current_user
from src.schemas.user_schema import UserOut

order_routes = APIRouter(prefix="/api/order", tags=["Orders Routes"])


@order_routes.post("/create_order", status_code=status.HTTP_201_CREATED)
async def create_order(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    is_cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()  # type:ignore
    if is_cart is None or not is_cart.cart_items:
        logger.warning(f"Cart is empty for user {current_user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    total_price = 0
    for cart_item in is_cart.cart_items:
        is_product = db.query(Product).filter(Product.id == cart_item.product_id).first()  # type:ignore
        if is_product is None:
            logger.warning(f"Product {cart_item.product_id} does not exist!")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")
        total_price += is_product.price * cart_item.quantity
    new_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status=OrderStatusEnum.PENDING,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    db.query(CartItem).filter(CartItem.cart_id == is_cart.id).delete()  # type:ignore
    db.commit()

    db.query(Cart).filter(Cart.user_id == current_user.id).delete()  # type:ignore
    db.commit()

    logger.info(f"Order has been created for user {current_user.username}")


@order_routes.get("/all", status_code=status.HTTP_200_OK, response_model=list[OrderOut])
async def get_orders(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    """
        Retrieve all orders for the currently authenticated user.
    """
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()  # type:ignore
    if not orders:
        logger.info(f"No orders found for user {current_user.username}")
        return []

    logger.info(f"{len(orders)} orders retrieved for user {current_user.username}")
    return orders


@order_routes.get("/by_id/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderOut)
async def get_order_by_id(order_id: UUID, db: Session = Depends(get_db),
                          current_user: UserOut = Depends(get_current_user)):
    is_order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if is_order is None:
        logger.warning(f"Order {order_id} not found for user {current_user.username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order doesn't Exists!")

    logger.info(f"Order {order_id} has been retrieved for user {current_user.username}")
    return is_order
