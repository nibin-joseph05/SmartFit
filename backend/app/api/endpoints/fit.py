from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.fit import FitAnalysisResponse
from app.services.fit_service import analyze_fit

router = APIRouter()

@router.post("/analyze", response_model=FitAnalysisResponse)
async def analyze(
    height: float = Form(...),
    weight: float = Form(...),
    dress_type: str = Form(...),
    image: UploadFile = File(...)
):
    image_bytes = await image.read()
    
    result = analyze_fit(height, weight, dress_type, image_bytes)
    
    return FitAnalysisResponse(**result)
