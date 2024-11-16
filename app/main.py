from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.services.resume_service import (
    extract_text,
    split_into_sections,
    extract_experience,
    extract_date_range,
    grammar_check,
    rate_resume,
)

app = FastAPI()

# Allow your WordPress site to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nishantz2.sg-host.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("FastAPI application is starting...")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume Analyzer API"}

@app.post("/analyze-resume/")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        file_path = file.filename
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Extract text and perform analysis
        text = extract_text(file_path)
        sections = split_into_sections(text)
        work_experience_text = sections.get("work experience", "")
        experience_years = extract_experience(work_experience_text) or extract_date_range(work_experience_text)
        
        total_score = rate_resume(text, experience_years)

        return {
            "total_score": total_score,
            "experience_years": experience_years
            
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
