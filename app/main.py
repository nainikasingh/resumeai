from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from app.services.resume_service import (
    extract_text,
    split_into_sections,
    extract_experience_from_dates,  # New method for experience calculation
    grammar_check,
    detect_job_profile,
    action_verbs_quality,
    suggest_keywords,
    rate_resume,
    find_repeated_action_verbs,
    layout_analysis_with_pillow,
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
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to upload a resume file for analysis.
    """
    try:
        file_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Extract text
        text = extract_text(file_path)

        # Detect job profile
        job_profiles = detect_job_profile(text)
        job_profile = job_profiles[0] if job_profiles else "Unknown"

        # Split text into sections
        sections = split_into_sections(text)

        # Extract experience
        experience_years = extract_experience_from_dates(text)

        # Grammar check
        grammar_errors, _ = grammar_check(text)

        # Check for repeated action verbs
        repeated_verbs = find_repeated_action_verbs(text)

        # Get action verb suggestions
        action_verbs_used, action_verb_suggestions = action_verbs_quality(text)

        # Generate keyword suggestions
        keyword_suggestions = suggest_keywords(job_profile)

        # Find missing sections
        required_sections = ['experience', 'education', 'skills', 'achievements', 'hobbies', 'certifications', 'references']
        missing_sections = [section for section in required_sections if section not in sections]

        # Perform layout analysis
        layout_score = layout_analysis_with_pillow(file_path)

        # Calculate the resume score
        total_score = rate_resume(text, job_profile, experience_years)

        # Clean up
        os.remove(file_path)

        # Return response
        return {
            "total_score": total_score,
            "grammar_errors": grammar_errors,
            "repeated_action_verbs": repeated_verbs,
            "action_verb_suggestions": action_verb_suggestions,
            "keyword_suggestions": keyword_suggestions,
            "missing_sections": missing_sections,
            "layout_score": layout_score,
            "job_profile": job_profile,
            "experience_years": experience_years,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
