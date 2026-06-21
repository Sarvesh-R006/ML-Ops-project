import streamlit as st
import pandas as pd
from parser import parse_resume
from skills import SKILL_CATEGORIES
from utils import calculate_match_score, export_to_excel, export_to_csv, ELIGIBILITY_THRESHOLD

st.set_page_config(page_title="Resume Analyzer", layout="wide")

# Premium Custom CSS
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-weight: 700 !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #3fb950;
        font-size: 2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#3fb950, #2ea043);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    div[data-testid="stMetricLabel"] {
        color: #8b949e;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #238636;
        color: white;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 6px;
        transition: all 0.2s ease-in-out;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #2ea043;
        border-color: #8b949e;
        transform: translateY(-2px);
    }
    
    /* DataFrame Styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for cached parsed resumes
if "parsed_resumes" not in st.session_state:
    st.session_state["parsed_resumes"] = {}

def process_uploaded_files(uploaded_files):
    new_files_parsed = 0
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        if filename not in st.session_state["parsed_resumes"]:
            parsed_data = parse_resume(uploaded_file, filename)
            if parsed_data:
                st.session_state["parsed_resumes"][filename] = parsed_data
                new_files_parsed += 1
    return new_files_parsed

# UI Structure
st.title("📄 Resume Analyzer")
st.markdown("Upload resumes, filter by skills, and rank candidates instantly.")

# Sidebar - Upload
with st.sidebar:
    st.header("1. Upload Resumes")
    uploaded_files = st.file_uploader("Upload PDF, DOCX, or TXT files", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
    if uploaded_files:
        with st.spinner("Parsing resumes..."):
            count = process_uploaded_files(uploaded_files)
        if count > 0:
            st.success(f"Parsed {count} new resume(s)!")
            
    st.divider()
    
    st.header("2. Filter by Programming Languages")
    selected_skills = []
    
    if "Programming Languages" in SKILL_CATEGORIES:
        skills_list = list(SKILL_CATEGORIES["Programming Languages"].keys())
        selected = st.multiselect("Programming Languages", skills_list)
        selected_skills.extend(selected)

# Main Content
if not st.session_state["parsed_resumes"]:
    st.info("👈 Upload resumes in the sidebar to get started.")
    st.stop()

# Prepare Data
data = []
for filename, parsed_data in st.session_state["parsed_resumes"].items():
    match_score, matched_skills, missing_skills = calculate_match_score(parsed_data["Skills"], selected_skills)
    
    row = parsed_data.copy()
    row["Match %"] = match_score
    row["Matched Skills"] = ", ".join(matched_skills) if matched_skills else "None"
    row["Missing Skills"] = ", ".join(missing_skills) if missing_skills else "None"
    row["Status"] = "✅ Eligible" if match_score >= ELIGIBILITY_THRESHOLD else "❌ Not Eligible"
    row["Skills_raw"] = ", ".join(parsed_data["Skills"])
    data.append(row)

df = pd.DataFrame(data)


# Dashboard Metrics
st.subheader("Dashboard Overview")
col1, col2, col3, col4, col5 = st.columns(5)

total_resumes = len(df)
eligible_count = len(df[df["Match %"] >= ELIGIBILITY_THRESHOLD])
avg_match = round(df["Match %"].mean()) if not df.empty else 0

# Top skill overall and most common language
if not df.empty:
    all_skills = [skill for sublist in df["Skills"] for skill in sublist if skill != "Not Found"]
    top_skill = pd.Series(all_skills).mode()[0] if all_skills else "None"

    all_langs = [skill for sublist in df["Skills"] for skill in sublist if skill in SKILL_CATEGORIES["Programming Languages"]]
    top_lang = pd.Series(all_langs).mode()[0] if all_langs else "None"
else:
    top_skill = "None"
    top_lang = "None"

col1.metric("Total Resumes", total_resumes)
col2.metric("Eligible Candidates", eligible_count)
col3.metric("Avg Match Score", f"{avg_match}%")
col4.metric("Top Skill Overall", top_skill)
col5.metric("Most Common Language", top_lang)

# Sorting
st.subheader("Candidate Rankings")
sort_by = st.selectbox("Sort Results By", ["Match % (High to Low)", "Name (A-Z)", "Newest Upload"])

if sort_by == "Match % (High to Low)":
    df = df.sort_values(by="Match %", ascending=False)
elif sort_by == "Name (A-Z)":
    df = df.sort_values(by="Name", ascending=True)
else: # Newest Upload (Assuming current index is upload order)
    pass # Keep original order

# Display Table
# Clean up columns for display
display_cols = ["Name", "Match %", "Status", "Email", "Phone", "College", "Degree", "Branch", "CGPA", "Year", "Matched Skills", "Missing Skills", "Skills_raw"]
df_display = df[display_cols].rename(columns={"Skills_raw": "All Extracted Skills"})

st.dataframe(
    df_display,
    column_config={
        "Match %": st.column_config.ProgressColumn(
            "Match %",
            help="Match score based on selected skills",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
        "Status": st.column_config.TextColumn("Status"),
    },
    use_container_width=True,
    hide_index=True
)

# Export Buttons
st.subheader("Export Results")
col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    excel_data = export_to_excel(df_display)
    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="shortlist.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with col_exp2:
    csv_data = export_to_csv(df_display)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="shortlist.csv",
        mime="text/csv"
    )
