from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil

from parser import parse_resume
from skills import SKILL_CATEGORIES
from utils import calculate_match_score, ELIGIBILITY_THRESHOLD

app = FastAPI(title="Resume Analyzer API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

@app.get("/api/skills")
def get_skills():
    if "Programming Languages" in SKILL_CATEGORIES:
        return {"Programming Languages": list(SKILL_CATEGORIES["Programming Languages"].keys())}
    return {}

@app.post("/api/analyze")
async def analyze_resumes(
    files: List[UploadFile] = File(...),
    selected_skills: str = Form("")
):
    selected_skills_list = [s.strip() for s in selected_skills.split(",")] if selected_skills else []
    
    results = []
    
    for file in files:
        temp_file_path = f"uploads/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            with open(temp_file_path, "rb") as f:
                parsed_data = parse_resume(f, file.filename)
                
            if parsed_data:
                match_score, matched_skills, missing_skills = calculate_match_score(
                    parsed_data["Skills"], selected_skills_list
                )
                
                parsed_data["match_score"] = match_score
                parsed_data["matched_skills"] = matched_skills
                parsed_data["missing_skills"] = missing_skills
                parsed_data["is_eligible"] = match_score >= ELIGIBILITY_THRESHOLD
                
                results.append(parsed_data)
        except Exception as e:
            print(f"Failed to parse {file.filename}: {e}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
