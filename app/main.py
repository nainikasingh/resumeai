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

# Allow cross-origin requests from the frontend's domain
origins = [
    "https://nishantz3.sg-host.com",  # your frontend's domain
    "http://localhost",  # allow localhost for local development (if needed)
]

# Allow your WordPress site to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    # Directory setup
    upload_dir = os.getenv("UPLOAD_DIR", "nishantz2.sg-host.com/public_html/wp-content/uploads/advanced-cf7-upload")

    # Validate file type
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed types are {ALLOWED_EXTENSIONS}",
        )

    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)

    # Save the file to the new directory
    file_path = os.path.join(upload_dir, file.filename)
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
        # Perform layout analysis
        layout_score = layout_analysis_with_pillow(file_path)

        # Calculate the resume score
        get_score = rate_resume(text, detected_profile, experience_years)

        total_final_score = get_score[0]
        grammar_final_score = get_score[1]
        action_final_score = get_score[2]
        ats_final_score = get_score[3]
        keywords_final_score = get_score[4]
        page_length_final_score = get_score[5]


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
            "total_final_score": total_final_score,
            "grammar_final_score": grammar_final_score,
            "action_final_score": action_final_score,
            "ats_final_score": ats_final_score,
            "keywords_final_score": keywords_final_score,
            "page_length_final_score": page_length_final_score
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=80, reload=True)
