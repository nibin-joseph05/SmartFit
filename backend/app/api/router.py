from fastapi import APIRouter
from app.api.routes import health, size, image

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(size.router, prefix="/size", tags=["Size"])
api_router.include_router(image.router, prefix="/image", tags=["Image"])