from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.db_setup import get_db
from src.models.app_model import User
from src.routers.auth_router import get_user
from src.schemas.user_schema import UserOut, UpdatePassword
from src.utils.looger_handler import logger
from src.utils.password_handler import hash_password

user_routes = APIRouter(prefix="/api/user", tags=["User Routes"])


@user_routes.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: UserOut = Depends(get_user)):
    return current_user


@user_routes.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(password: UpdatePassword, current_user: UserOut = Depends(get_user),
                          db: Session = Depends(get_db)):
    is_user_exist = db.query(User).filter(User.email == current_user.email).first()  # type:ignore

    new_hashed_password = hash_password(password.confirm_password)
    is_user_exist.password = new_hashed_password

    try:
        db.commit()
        logger.info(f"Password has been updated of user {current_user.username}")
    except Exception as e:
        logger.error(f"Failed to update password of user {current_user.username}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update password: {e}")
