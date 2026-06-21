import pdfplumber
import docx
import re
from rapidfuzz import fuzz, process
import nltk
from skills import SKILL_CATEGORIES

# Ensure nltk packages are available (handled at startup, but we can do a quick check)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def extract_text(file_obj, filename):
    text = ""
    try:
        if filename.lower().endswith('.pdf'):
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif filename.lower().endswith('.txt'):
            text = file_obj.read().decode('utf-8')
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None
    return text

def extract_email(text):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_regex, text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    phone_regex = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_regex, text)
    return match.group(0) if match else "Not Found"

def extract_name(text):
    # Very basic name extraction: top line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        return lines[0]
    return "Not Found"

def extract_cgpa(text):
    cgpa_regex = r'(?i)(?:cgpa|gpa)[\s:]*([0-9]\.[0-9]+|[0-9]{1,2}(?:\.[0-9]+)?(?:/[0-9]{1,2})?)'
    match = re.search(cgpa_regex, text)
    if match:
        return match.group(1)
    return "Not Found"

def extract_year(text):
    year_regex = r'(?i)(?:class of|batch of|passing year|graduation year)[\s:]*(20\d{2})'
    match = re.search(year_regex, text)
    if match:
        return match.group(1)
    
    years = re.findall(r'\b20[1-3][0-9]\b', text)
    if years:
        return max(years)
    return "Not Found"

def extract_education_details(text):
    college = "Not Found"
    degree = "Not Found"
    branch = "Not Found"
    
    college_keywords = ["university", "institute", "college", "school of"]
    for line in text.split('\n'):
        line_lower = line.lower()
        if any(kw in line_lower for kw in college_keywords) and len(line) < 100:
            college = line.strip()
            break
            
    degrees = ["B.Tech", "M.Tech", "B.E.", "M.E.", "BSc", "MSc", "BCA", "MCA", "Ph.D", "Bachelor", "Master", "B.A.", "M.A.", "MBA"]
    for d in degrees:
        if re.search(rf'\b{d.replace(".", r"\.")}\b', text, re.IGNORECASE):
            degree = d
            break
            
    branches = ["Computer Science", "Information Technology", "Electrical", "Electronics", "Mechanical", "Civil", "AI", "Machine Learning", "Data Science", "Computer Engineering", "Software Engineering"]
    for b in branches:
        if re.search(rf'\b{b}\b', text, re.IGNORECASE):
            branch = b
            break
            
    return college, degree, branch

def extract_skills(text):
    text_lower = text.lower()
    extracted_skills = set()
    
    for category, skills in SKILL_CATEGORIES.items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                escaped_alias = re.escape(alias)
                if len(alias) <= 2 or alias in ["c++", "c#", ".net"]:
                    if alias in ["c++", "c#", ".net"]:
                        pattern = rf'(?:^|[\s,;()/]){escaped_alias}(?:[\s,;()/]|$)'
                    else:
                        pattern = rf'\b{escaped_alias}\b'
                else:
                    pattern = rf'\b{escaped_alias}\b'
                    
                if re.search(pattern, text_lower):
                    extracted_skills.add(canonical)
                    break
                    
    return list(extracted_skills) if extracted_skills else ["Not Found"]

def extract_projects(text):
    match = re.search(r'(?i)projects?\s*\n(.*?)(?=\n(?:\s*[A-Z][a-z]+)*\s*:|\n[A-Z][A-Z\s]+|\Z)', text, re.DOTALL)
    if match:
        proj_text = match.group(1).strip()
        bullets = re.findall(r'(?:^|\n)\s*[-•*]\s*(.+)', proj_text)
        if bullets:
            return " | ".join(bullets[:3])
        return proj_text[:100] + "..." if len(proj_text) > 100 else proj_text
    return "Not Found"

def extract_certifications(text):
    match = re.search(r'(?i)certifications?\s*\n(.*?)(?=\n(?:\s*[A-Z][a-z]+)*\s*:|\n[A-Z][A-Z\s]+|\Z)', text, re.DOTALL)
    if match:
        cert_text = match.group(1).strip()
        bullets = re.findall(r'(?:^|\n)\s*[-•*]\s*(.+)', cert_text)
        if bullets:
            return " | ".join(bullets[:3])
        return cert_text[:100] + "..." if len(cert_text) > 100 else cert_text
    return "Not Found"

def parse_resume(file_obj, filename):
    text = extract_text(file_obj, filename)
    if not text:
        return None
        
    college, degree, branch = extract_education_details(text)
    
    return {
        "Filename": filename,
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "College": college,
        "Degree": degree,
        "Branch": branch,
        "CGPA": extract_cgpa(text),
        "Year": extract_year(text),
        "Skills": extract_skills(text),
        "Projects": extract_projects(text),
        "Certifications": extract_certifications(text)
    }
