from pydantic import BaseModel
from typing import Optional

class FitAnalysisResponse(BaseModel):
    generated_image_url: str
    message: str
    confidence: Optional[float] = None
