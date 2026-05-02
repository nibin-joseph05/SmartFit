from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router
from app.core.exceptions import global_exception_handler

app = FastAPI(title=settings.PROJECT_NAME)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}