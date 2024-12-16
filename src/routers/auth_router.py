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

oAuthBear = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


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


def get_user(token: str = Depends(oAuthBear), db: Session = Depends(get_db)) -> UserOut:
    payload = verify_jwt_token(token)

    if not payload:
        logger.warning(f"Token is invalid!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()  # type:ignore

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not found")

    return UserOut(id=user.id, username=user.username, email=user.email, is_admin=user.is_admin,
                   created_at=user.created_at, updated_at=user.updated_at)


def is_admin_user(current_user: UserOut = Depends(get_user)) -> UserOut:
    if not current_user.is_admin:
        logger.warning(f"User {current_user.username} is not an Admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have admin privileges",
        )
    logger.info(f"Admin access granted to {current_user.username}")
    return current_user
