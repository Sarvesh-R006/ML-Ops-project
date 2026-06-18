# ML-Ops-project: Resume Analyzer

projects for ML Ops

A robust Streamlit web application designed for placement coordinators to bulk-process, analyze, and rank student resumes against customizable skill sets.

## Features
- **Multi-format Support:** Upload and parse PDF, DOCX, and TXT resumes.
- **Smart Skill Matching:** Uses fuzzy matching (RapidFuzz) to identify variations and abbreviations of skills based on a comprehensive taxonomy.
- **Dynamic Filtering:** Filter candidates by programming languages, web dev, AI/ML, cloud, and more.
- **Instant Ranking:** Calculates a "Match %" based on selected skills and highlights missing ones.
- **Dashboard Overview:** Displays high-level metrics like total resumes, eligible count, top skills, and languages.
- **Export Capabilities:** Export the shortlisted candidates to CSV or Excel instantly.

## Setup Instructions

### Local Environment
1. Ensure Python 3.8+ is installed.
2. Clone this repository or download the files.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

### GitHub Codespaces
This project is built to run flawlessly in GitHub Codespaces.
1. Open the repository in a new Codespace.
2. Run the following command in the integrated terminal:
   ```bash
   pip install -r requirements.txt && streamlit run app.py
   ```
3. Codespaces will prompt you to open the forwarded port in your browser.

## Project Structure
- `app.py`: The main Streamlit application, handling UI and session state cache.
- `parser.py`: Logic for text extraction from documents and regex/fuzzy parsing of fields.
- `skills.py`: A comprehensive taxonomy of tech skills with their aliases and abbreviations.
- `utils.py`: Helper functions for score calculation and Excel/CSV exporting.
- `requirements.txt`: Python package dependencies.
- `uploads/`: Directory to store any necessary temporary files.

## Screenshots

