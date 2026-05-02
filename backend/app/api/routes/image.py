from fastapi import APIRouter, UploadFile, File
import shutil

router = APIRouter()

@router.post("/upload")
def upload_image(file: UploadFile = File(...)):
    with open(f"temp_{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Image uploaded successfully"}