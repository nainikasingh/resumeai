from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.resume_service import analyze_resume
import os

router = APIRouter()

@router.post("/upload-file", tags=["Resume Analysis"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX) for analysis.
    """
    print("API /analyze-resume/ endpoint called with file:", file.filename)
    try:
        # Save the uploaded file locally
        file_location = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        # Call the service layer for analysis
        result = analyze_resume(file_location)
        
        # Clean up the uploaded file
        os.remove(file_location)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
