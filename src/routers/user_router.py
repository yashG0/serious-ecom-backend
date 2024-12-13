from fastapi import APIRouter, status, Depends

from src.routers.auth_router import get_user
from src.schemas.user_schema import UserOut

user_routes = APIRouter(prefix="/api/user", tags=["User Routes"])


@user_routes.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: UserOut = Depends(get_user)):
    return current_user
