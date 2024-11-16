from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.resume_service import (
    extract_text,
    split_into_sections,
    extract_experience,
    extract_date_range,
    grammar_check,
    detect_job_profile,
    action_verbs_quality,
    suggest_keywords,
    rate_resume,
    find_repeated_action_verbs,
    layout_analysis_with_opencv,
)
import os

router = APIRouter()

@router.post("/upload-file", tags=["Resume Analysis"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX) for analysis.
    """
    print("API /upload-file endpoint called with file:", file.filename)
    try:
        # Save the uploaded file locally
        file_location = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        # Analyze the resume
        text = extract_text(file_location)

        # Detect job profile
        job_profiles = detect_job_profile(text)
        job_profile = job_profiles[0] if job_profiles else "Unknown"

        # Split text into sections
        sections = split_into_sections(text)

        # Extract work experience
        work_experience_text = sections.get("work experience", "")
        work_experience_years = extract_experience(work_experience_text)
        timeline_experience_years = extract_date_range(work_experience_text)

        # Use timeline experience if available, otherwise fall back to basic work experience
        experience_years = timeline_experience_years if timeline_experience_years else work_experience_years

        # Grammar check
        grammar_errors, grammar_matches = grammar_check(text)

        # Action verbs quality and suggestions
        action_verbs_used, action_verb_suggestions = action_verbs_quality(text)

        # Generate keyword suggestions based on job profile
        keyword_suggestions = suggest_keywords(job_profile)

        # Detect repeated action verbs
        repeated_verbs = find_repeated_action_verbs(text)

        # Identify missing sections in the resume
        required_sections = ['experience', 'education', 'skills', 'achievements', 'hobbies', 'certification', 'references']
        missing_sections = [section for section in required_sections if section not in sections]

        # Perform layout analysis
        layout_score = layout_analysis_with_opencv(file_location)

        # Calculate the total score based on the resume content
        total_score = rate_resume(text, job_profile, experience_years)

        # Prepare the response
        result = {
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

        # Clean up the uploaded file
        os.remove(file_location)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
