from pydantic import BaseModel

class BodyInput(BaseModel):
    height: float
    weight: float
    chest: float | None = None
    waist: float | None = None