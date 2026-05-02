from fastapi import APIRouter, UploadFile, File, Request
from app.schemas.fit import FitAnalysisResponse
from app.services.fit_service import analyze_virtual_try_on

router = APIRouter()

@router.post("/analyze", response_model=FitAnalysisResponse)
async def analyze(
    request: Request,
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    base_url = str(request.base_url).rstrip("/")
    
    result = await analyze_virtual_try_on(person_image, garment_image, base_url)
    
    return FitAnalysisResponse(**result)
