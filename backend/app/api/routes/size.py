from fastapi import APIRouter
from app.models.schemas import BodyInput
from app.services.size_service import get_size

router = APIRouter()

@router.post("/recommend")
def recommend_size(body: BodyInput):
    size = get_size(body)
    return {
        "recommended_size": size,
        "confidence": "medium",
        "note": "Based on body proportions (MVP logic)"
    }