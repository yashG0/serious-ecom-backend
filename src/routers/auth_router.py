from timeit import default_timer

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.utils.looger_handler import logger
from src.utils.jwt_handler import get_jwt_token, verify_jwt_token
from src.utils.password_handler import hash_password, verify_password
from src.config.db_setup import get_db
from src.models.app_model import User
from src.schemas.user_schema import UserOut, UserIn

auth_routes = APIRouter(prefix="/api/auth", tags=["Auth Routers"])


@auth_routes.post("/register", status_code=status.HTTP_201_CREATED)
async def signup(new_user: UserIn, db: Session = Depends(get_db)):
    is_user_exist = db.query(User).filter(User.email == new_user.email).first()  # type:ignore
    if is_user_exist:
        logger.warning("User doesn't exists! please signup")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists!")

    hashed_password = hash_password(new_user.password)
    user = User(
        username=new_user.username,
        email=new_user.email,
        password=hashed_password
    )

    try:
        db.add(user)
        db.commit()
        logger.info(f"User {user.username} has been created successfully!")
    except Exception as e:
        logger.error(f"Failed to create new user {user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to add new user: {e}")


@auth_routes.post("/login", status_code=status.HTTP_200_OK)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    is_user_exist = db.query(User).filter(User.email == form.username).first()  # type:ignore
    if is_user_exist is None:
        logger.exception("User doesn't exists! please signup")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist! please signup")

    if not verify_password(form.password, is_user_exist.password):
        logger.exception(f"Incorrect password attempt for user {is_user_exist.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password!")

    access_token = get_jwt_token(data={"sub": is_user_exist.email})

    logger.info(f"User '{is_user_exist.username}' logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}
