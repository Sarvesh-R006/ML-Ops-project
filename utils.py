import pandas as pd
from io import BytesIO

ELIGIBILITY_THRESHOLD = 50

def calculate_match_score(resume_skills, selected_skills):
    if not selected_skills:
        return 100, [], []
    
    resume_skills_lower = {s.lower() for s in resume_skills if s != "Not Found"}
    selected_skills_lower = {s.lower() for s in selected_skills}
    
    matched = list(resume_skills_lower.intersection(selected_skills_lower))
    missing = list(selected_skills_lower.difference(resume_skills_lower))
    
    # Return original case for display
    matched_display = [s for s in selected_skills if s.lower() in resume_skills_lower]
    missing_display = [s for s in selected_skills if s.lower() not in resume_skills_lower]
    
    match_percentage = (len(matched) / len(selected_skills)) * 100
    
    return round(match_percentage), matched_display, missing_display

def export_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Shortlist')
    processed_data = output.getvalue()
    return processed_data

def export_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
