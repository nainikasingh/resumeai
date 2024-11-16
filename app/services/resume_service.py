from docx import Document
import pdfplumber
import re
from datetime import datetime
from dateutil import parser
import spacy
import language_tool_python

# Initialize spaCy and LanguageTool
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

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

def split_into_sections(text):
    section_headers = [
        r"work experience" or r"professional experience" or r"employment history",
        r"education", r"skills", r"certifications", r"projects", r"summary", r"contact information",
    ]
    pattern = r'(?i)\b(?:' + '|'.join(section_headers) + r')\b'
    sections = re.split(pattern, text)
    headers = re.findall(pattern, text)
    resume_sections = {header.strip().lower(): section.strip() for header, section in zip(headers, sections[1:])}
    return resume_sections

def extract_experience(text):
    experience_pattern = r"(\d+)\s*(years?|months?)\s*experience"
    match = re.search(experience_pattern, text, re.IGNORECASE)
    if match:
        years = int(match.group(1))
        return years
    return None

def extract_date_range(text):
    date_pattern = r"(\b\w{3,9}\b \d{4})\s*-\s*(\b\w{3,9}\b \d{4}|\bPresent\b)"
    date_matches = re.findall(date_pattern, text)
    total_experience = 0
    today = datetime.today()
    for start_date, end_date in date_matches:
        try:
            start = parser.parse(start_date)
            end = today if "present" in end_date.lower() else parser.parse(end_date)
            total_experience += (end - start).days / 365.25
        except (ValueError, TypeError):
            continue
    return total_experience if total_experience > 0 else None

def grammar_check(text):
    matches = tool.check(text)
    return len(matches), matches

def rate_resume(resume_text, experience_years):
    grammar_errors, _ = grammar_check(resume_text)
    grammar_score = 10 if grammar_errors == 0 else (5 if grammar_errors <= 5 else 0)
    page_length_score = 10 if experience_years is not None and experience_years < 10 else 5
    ats_score = 10
    contact_score = 10
    final_score = grammar_score + page_length_score + ats_score + contact_score
    total_score = (final_score / 40) * 100
    return total_score
