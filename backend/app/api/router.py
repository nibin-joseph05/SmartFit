from fastapi import APIRouter
from app.api.endpoints import fit

api_router = APIRouter()

api_router.include_router(fit.router, prefix="/fit", tags=["Fit Analysis"])