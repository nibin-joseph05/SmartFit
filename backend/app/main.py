import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.router import api_router
from app.core.exceptions import global_exception_handler

os.makedirs("uploads/person", exist_ok=True)
os.makedirs("uploads/garment", exist_ok=True)
os.makedirs("uploads/generated", exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_exception_handler(Exception, global_exception_handler)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}