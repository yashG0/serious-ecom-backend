from jose import jwt
from os import getenv
from datetime import datetime, timedelta

JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"


def get_jwt_token(data: dict, expire_delta: timedelta = timedelta(days=6)) -> str:
    to_encode = data.copy()

    expire = datetime.now() + expire_delta
    to_encode.update({"ext": expire})
    return jwt.encode(data, key=JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    return jwt.decode(token, algorithms=[ALGORITHM], key=JWT_SECRET_KEY)
