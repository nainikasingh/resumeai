from docx import Document
import pdfplumber
import re
from datetime import datetime
from dateutil import parser
import spacy
import language_tool_python
from PIL import Image
import fitz
from fastapi import HTTPException
from datetime import datetime
from dateutil import parser

# Initialize spaCy and LanguageTool
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

# Extract text from PDF or DOCX
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages])
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are allowed.")
    return text

# Split text into sections based on headers
def split_into_sections(text):
    section_headers = [
        r"work experience" or r"professional experience" or r"employment history",
        r"education", r"skills", r"certifications", r"projects", r"summary", r"contact information"
    ]
    pattern = r'(?i)\b(?:' + '|'.join(section_headers) + r')\b'
    sections = re.split(pattern, text)
    headers = re.findall(pattern, text)
    resume_sections = {header.strip().lower(): section.strip() for header, section in zip(headers, sections[1:])}
    return resume_sections

def extract_experience_from_dates(text):
    """
    Calculate total experience by aggregating all date ranges in the text.
    """
    # Pattern to capture date ranges (e.g., "Jan 2015 - Dec 2020" or "Jan 2015 - Present")
    date_pattern = r"(\b\w{3,9}\b \d{4})\s*-\s*(\b\w{3,9}\b \d{4}|\bPresent\b)"
    date_matches = re.findall(date_pattern, text)
    
    total_experience = 0  # Total experience in years
    today = datetime.today()

    parsed_date_ranges = []

    for start_date, end_date in date_matches:
        try:
            start = parser.parse(start_date)
            end = today if "present" in end_date.lower() else parser.parse(end_date)
            parsed_date_ranges.append((start, end))
        except (ValueError, TypeError):
            continue

    # Merge overlapping or contiguous date ranges
    merged_ranges = merge_date_ranges(parsed_date_ranges)

    # Calculate the total experience from merged date ranges
    for start, end in merged_ranges:
        total_experience += (end - start).days / 365.25  # Convert days to years

    return round(total_experience, 2)  # Return experience rounded to 2 decimal places


def merge_date_ranges(date_ranges):
    """
    Merge overlapping or contiguous date ranges.
    """
    if not date_ranges:
        return []

    # Sort date ranges by start date
    date_ranges.sort(key=lambda x: x[0])

    merged_ranges = [date_ranges[0]]

    for current_start, current_end in date_ranges[1:]:
        last_start, last_end = merged_ranges[-1]

        if current_start <= last_end:  # Overlapping or contiguous ranges
            # Merge ranges
            merged_ranges[-1] = (last_start, max(last_end, current_end))
        else:
            merged_ranges.append((current_start, current_end))

    return merged_ranges

# Grammar check using LanguageTool
def grammar_check(text):
    matches = tool.check(text)
    return len(matches), matches

# Detect job profiles in the text
def detect_job_profile(text):
    job_titles = [
        "Accountant", "Software Engineer", "Data Scientist", "Marketing Manager",
        "Project Manager", "UX Designer", "Web Developer", "Business Analyst",
        "Sales Manager", "Cybersecurity Specialist"
    ]
    doc = nlp(text)
    detected_profiles = {ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.text in job_titles}
    return list(detected_profiles)

def action_verbs_quality(text):
    """
    Analyze the text for action verbs and provide suggestions.
    Returns a list of found verbs and strong verb suggestions.
    """
    strong_verbs = [
        "led", "developed", "engineered", "optimized", "created", "designed", 
        "built", "initiated", "launched", "implemented", "enhanced"
    ]
    found_verbs = [word for word in text.split() if word.lower() in strong_verbs]
    return found_verbs, strong_verbs

# Suggest keywords based on job profile
def suggest_keywords(job_profile):
    profile_keywords = {
        "Data Scientist": ["Machine Learning", "Python", "Big Data", "Artificial Intelligence"],
        "Software Engineer": ["Java", "C#", "Agile", "Git", "CI/CD", "Cloud Computing"],
        "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Responsive Design"]
    }
    return profile_keywords.get(job_profile, [])

# ATS-friendly check
def ats_friendly_check(text):
    symbols_or_tables = re.search(r'[\u2500-\u257F]', text)
    if symbols_or_tables:
        return 5  # Deduct points for tables or symbols
    return 10  # ATS-friendly

# Layout analysis using Pillow
def layout_analysis_with_pillow(file_path):
    if not file_path.endswith(".pdf"):
        return 10  # Only analyze PDFs, return max score for other formats

    pdf_document = fitz.open(file_path)
    layout_score = 10  # Start with maximum score

    for page_num in range(len(pdf_document)):
        try:
            pix = pdf_document[page_num].get_pixmap(dpi=200)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            if _detect_tables_or_images(image):
                layout_score -= 3  # Deduct points for tables or non-text elements
        except Exception as e:
            print(f"Error processing page {page_num + 1}: {e}")
            continue

    pdf_document.close()
    return max(layout_score, 0)

def _detect_tables_or_images(image):
    grayscale = image.convert("L")
    histogram = grayscale.histogram()
    black_pixels = histogram[0]
    white_pixels = histogram[-1]
    total_pixels = sum(histogram)
    return black_pixels / total_pixels > 0.1 or white_pixels / total_pixels > 0.9

# Function to find repeated action verbs
def find_repeated_action_verbs(text):
    if not isinstance(text, str):
        raise ValueError("Input to find_repeated_action_verbs must be a string")

    action_verbs = [
        "helped", "assisted", "worked", "supported", "participated", 
        "contributed", "provided", "handled", "managed", "maintained", 
        "followed", "collaborated", "executed", "processed", "organized", 
        "oversaw", "documented", "used", "carried out", "updated"
    ]
    repeated_verbs = [verb for verb in action_verbs if text.lower().count(verb) > 1]
    return repeated_verbs

# Calculate the resume's final score
def rate_resume(resume_text, job_profile, experience_years):
    """
    Calculate the overall score of the resume based on various factors.
    """
    if not isinstance(resume_text, str):
        raise ValueError("resume_text must be a string")
    if not isinstance(job_profile, str):
        raise ValueError("job_profile must be a string")
    if not isinstance(experience_years, (int, float)):
        raise ValueError("experience_years must be an int or float")

    # Grammar score
    grammar_errors, _ = grammar_check(resume_text)
    grammar_score = 10 if grammar_errors == 0 else (5 if grammar_errors <= 5 else 0)

    # Action verbs quality
    action_verbs_used, action_verb_suggestions = action_verbs_quality(resume_text)
    action_verbs_score = len(action_verbs_used) * 2  # Score based on number of action verbs used

    # Keyword suggestions
    keyword_suggestions = suggest_keywords(job_profile)
    found_keywords = [kw for kw in keyword_suggestions if kw.lower() in resume_text.lower()]
    if len(keyword_suggestions) > 0:
        keywords_score = 10 if len(found_keywords) / len(keyword_suggestions) >= 0.5 else 5
    else:
        keywords_score = 0  # No keywords to evaluate

    # Page length score
    page_length_score = 10 if experience_years and experience_years <= 10 else 5

    # ATS-friendly score
    ats_score = ats_friendly_check(resume_text)

    # Total score calculation
    total_score = grammar_score + action_verbs_score + keywords_score + \
                  page_length_score + ats_score

    return (total_score / 50) * 100

def analyze_resume(file_path):
    """
    Analyze the resume file and return detailed results.
    """
    # Extract text and split into sections
    text = extract_text(file_path)
    sections = split_into_sections(text)

    # Extract work experience using the new method
    experience_years = extract_experience_from_dates(text)

    # Debugging logs
    print(f"Extracted experience_years: {experience_years}")

    # Validate experience_years
    if not isinstance(experience_years, (int, float)):
        raise HTTPException(status_code=500, detail="experience_years must be an int or float")

    # Detect job profile
    job_profile = detect_job_profile(text)
    detected_profile = job_profile[0] if job_profile else "Unknown"

    # Perform grammar check
    grammar_errors, _ = grammar_check(text)

    # Check for repeated action verbs
    repeated_verbs = find_repeated_action_verbs(text)

    # Get action verb suggestions
    _, action_verb_suggestions = action_verbs_quality(text)

    # Generate keyword suggestions based on detected profile
    keyword_suggestions = suggest_keywords(detected_profile)

    # Find missing sections
    required_sections = ['experience', 'education', 'skills', 'achievements', 'hobbies', 'certifications', 'references']
    missing_sections = [section for section in required_sections if section not in sections]

    # Perform layout analysis
    layout_score = layout_analysis_with_pillow(file_path)

    # Calculate the resume score
    total_score = rate_resume(text, detected_profile, experience_years)

    # Return detailed results
    return {
        "total_score": total_score,
        "grammar_errors": grammar_errors,
        "repeated_verbs": repeated_verbs,
        "action_verb_suggestions": action_verb_suggestions,
        "keyword_suggestions": keyword_suggestions,
        "missing_sections": missing_sections,
        "layout_score": layout_score
    }
