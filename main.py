from fastapi import FastAPI

from src.config.db_setup import Base, engine
from src.routers.auth_router import auth_routes
from src.routers.user_router import user_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-com site", description="this is my ecom project")

app.include_router(user_routes)
app.include_router(auth_routes)
