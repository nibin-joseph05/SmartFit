from pydantic import BaseModel

class FitAnalysisResponse(BaseModel):
    recommended_size: str
    fit_classification: str
    confidence: float
