import html
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.career.recommender import CAREER_SKILLS, recommend_careers
from src.jobs.job_recommender import load_job_data, recommend_jobs

st.set_page_config(
    page_title="SkillPath AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp, [data-testid="stAppViewContainer"] {
    background: #0b1220 !important; color: #e5edf9 !important;
}
[data-testid="stHeader"] { background: rgba(11,18,32,.96) !important; }
[data-testid="stSidebar"] {
    background: #111c30 !important; border-right: 1px solid #263650 !important;
}
.stApp p, .stApp label, .stApp span, .stApp li,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li { color: #e5edf9; }
h1,h2,h3,h4,h5,h6 { color: #f8fafc !important; }
.hero {
    padding: 1.7rem 1.8rem; border-radius: 20px;
    background: linear-gradient(120deg,#102a56 0%,#1d4ed8 65%,#2563eb 100%);
    border: 1px solid #315aa6; margin-bottom: 1.3rem;
    box-shadow: 0 12px 32px rgba(0,0,0,.25);
}
.hero h1 { color:#fff !important; margin:0 0 .45rem 0; font-size:2.15rem; }
.hero p { color:#eaf2ff !important; margin:0; font-size:1rem; }
.result-card {
    background:#142137 !important; color:#e5edf9 !important;
    border:1px solid #2b4162 !important; border-radius:16px;
    padding:1.1rem 1.25rem; margin:.65rem 0 1rem 0;
    box-shadow:0 5px 18px rgba(0,0,0,.18);
}
.result-card h1,.result-card h2,.result-card h3,.result-card p,
.result-card li,.result-card strong { color:#f8fafc !important; }
.muted { color:#bdcbe0 !important; font-size:.92rem; }
div[data-testid="stMetric"] {
    background:#1b2b43 !important; border:1px solid #344b6b !important;
    padding:.85rem; border-radius:14px;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color:#f8fafc !important; }
[data-baseweb="select"] > div {
    background-color:#18263b !important; color:#f8fafc !important;
    border-color:#435875 !important;
}
[data-baseweb="select"] input,[data-baseweb="select"] span { color:#f8fafc !important; }
[data-baseweb="popover"],[data-baseweb="menu"],ul[role="listbox"] {
    background-color:#18263b !important; color:#f8fafc !important;
}
li[role="option"] { background-color:#18263b !important; color:#f8fafc !important; }
li[role="option"]:hover { background-color:#29415f !important; }
.stTextInput input,.stNumberInput input,.stDateInput input,.stTextArea textarea {
    background:#18263b !important; color:#f8fafc !important;
}
.stButton > button {
    background:#2563eb !important; color:#fff !important;
    border:1px solid #3b82f6 !important; border-radius:10px; font-weight:600;
}
.stButton > button:hover { background:#1d4ed8 !important; border-color:#60a5fa !important; }
[data-testid="stAlert"] { background:#18263b !important; color:#f8fafc !important; }
hr { border-color:#2b4162 !important; }
</style>
""", unsafe_allow_html=True)

CAREER_DETAILS = {
    "Business Analyst": ("Analyzes business requirements, processes, and data to support decisions.", ["Practice SQL queries", "Build Excel analyses", "Create a Power BI dashboard"]),
    "Clerk": ("Maintains records, documents, and routine administrative information.", ["Improve Excel skills", "Practice document management", "Build typing accuracy"]),
    "Data Entry Operator": ("Enters, checks, and updates information accurately in digital systems.", ["Practice typing", "Learn sorting and filtering", "Practice data cleaning and validation"]),
    "Financial Analyst": ("Evaluates financial information, budgets, and trends.", ["Practice advanced Excel", "Study financial statements", "Build a financial reporting model"]),
    "Junior Accountant": ("Supports bookkeeping, reconciliations, and financial reports.", ["Practice journal entries", "Learn ledger reconciliation", "Explore accounting software"]),
    "Marketing Executive": ("Supports campaigns and studies customer needs.", ["Learn digital marketing", "Track campaign metrics", "Practice market research"]),
    "ML Engineer": ("Builds, evaluates, and helps deploy machine-learning models.", ["Build an end-to-end ML project", "Evaluate models carefully", "Learn model deployment"]),
    "Professor": ("Teaches a subject, guides learners, and may conduct research.", ["Strengthen subject knowledge", "Practice presentations", "Review postgraduate qualifications"]),
    "Research Scientist": ("Investigates research questions, conducts experiments, and analyzes results.", ["Study statistics", "Learn experimental design", "Complete a research-style project"]),
    "Sales Assistant": ("Helps customers understand products and supports sales activities.", ["Practice customer communication", "Learn product demonstration", "Explore CRM basics"]),
    "School Counselor": ("Supports students with educational and personal concerns.", ["Explore counseling qualifications", "Practice active listening", "Learn student-support approaches"]),
    "Software Engineer": ("Designs, builds, tests, and maintains software applications.", ["Build a practical software project", "Practice data structures and algorithms", "Use Git and testing tools"]),
}

def safe(value):
    if value is None:
        return "Not specified"
    try:
        if pd.isna(value):
            return "Not specified"
    except (TypeError, ValueError):
        pass
    return html.escape(str(value))

def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{safe(title)}</h1><p>{safe(subtitle)}</p></div>', unsafe_allow_html=True)

def career_page():
    hero("Career Recommendation", "Explore career paths that overlap with your current skills, then identify what to learn next.")
    st.subheader("1. Select your skills")
    skill_options = sorted({s for group in CAREER_SKILLS.values() for s in group}, key=str.casefold)
    pretty = {"power bi": "Power BI", "ms office": "MS Office", "tally erp": "Tally ERP", "c++": "C++", "seo": "SEO", "sql": "SQL"}
    skill_options = [pretty.get(s, s.title()) for s in skill_options]
    selected = st.multiselect("Which skills do you currently have?", skill_options, placeholder="Choose one or more skills", key="career_skills")
    top_n = st.selectbox("Number of career suggestions", [3, 5, 8, 10, 12], index=1)
    st.caption("Scores show required-skill coverage, not the probability of getting hired.")
    if st.button("Find Matching Careers", type="primary", use_container_width=True):
        if not selected:
            st.warning("Please select at least one skill.")
        else:
            try:
                st.session_state["career_results"] = recommend_careers(selected, int(top_n))
                st.session_state["career_search_done"] = True
            except Exception as exc:
                st.error(f"Could not generate career recommendations: {exc}")
    if not st.session_state.get("career_search_done", False):
        st.info("Choose your skills and select **Find Matching Careers**.")
        return
    results = st.session_state.get("career_results", pd.DataFrame())
    if results.empty:
        st.warning("No matching careers found. Try selecting more skills.")
        return
    st.subheader("2. Your recommended career paths")
    st.caption("REQUIRED SKILL COVERAGE")
    for _, row in results.iterrows():
        career = str(row.get("Career", row.get("career", "Career option")))
        description, steps = CAREER_DETAILS.get(career, ("Career option based on your selected skills.", []))
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(f"### {safe(career)}")
        st.markdown(f'<div class="muted">{safe(description)}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 3])
        score = row.get("Match Score (%)", row.get("match_score", row.get("match_score_pct", 0)))
        c1.metric("Skill coverage", f"{float(score):.1f}%")
        with c2:
            st.markdown(f'**Matched skills:** {safe(row.get("Matched Skills", row.get("matched_skills", "Not specified")))}')
            st.markdown(f'**Skills to develop:** {safe(row.get("Missing Skills", row.get("missing_skills", "Not specified")))}')
        if steps:
            st.markdown("**Suggested next steps**")
            for step in steps:
                st.markdown(f"- {step}")
        st.markdown("</div>", unsafe_allow_html=True)

def job_page():
    hero("Job Recommendation", "Find job listings that match your skills and narrow them down with practical filters.")
    try:
        jobs = load_job_data()
    except Exception as exc:
        st.error(f"Could not load the job dataset: {exc}")
        return

    st.subheader("1. Choose skills and filters")
    all_skills = set()
    for value in jobs["skills_required"].dropna().astype(str):
        all_skills.update(s.strip() for s in value.replace(";", ",").replace("|", ",").split(",") if s.strip())
    selected_skills = st.multiselect("Skills you have", sorted(all_skills, key=str.casefold),
        placeholder="Choose skills such as Python or SQL", key="job_skills")
    industries = sorted(jobs["industry"].dropna().astype(str).unique(), key=str.casefold)
    locations = sorted(jobs["location"].dropna().astype(str).unique(), key=str.casefold)
    remote_options = sorted(jobs["remote_option"].dropna().astype(str).unique(), key=str.casefold)
    company_sizes = sorted(jobs["company_size"].dropna().astype(str).unique(), key=str.casefold)

    c1, c2, c3 = st.columns(3)
    industry = c1.selectbox("Industry", ["Any"] + industries)
    location = c2.selectbox("Location", ["Any"] + locations)
    remote = c3.selectbox("Remote option", ["Any"] + remote_options)
    c4, c5 = st.columns([2, 1])
    selected_sizes = c4.multiselect("Company size", company_sizes, placeholder="Any company size")
    salary_data = pd.to_numeric(jobs["salary_usd"], errors="coerce").dropna()
    salary_range = None
    if not salary_data.empty:
        low, high = int(salary_data.min()), int(salary_data.max())
        if low < high:
            salary_range = c5.slider("Annual salary range (USD)", min_value=low, max_value=high,
                value=(low, high), step=max(1, (high-low)//100), format="$%d")
        else:
            salary_range = (low, high)
            c5.caption(f"Salary available: ${low:,}")
    else:
        c5.caption("Salary data unavailable.")
    top_n = st.selectbox("Number of job results", [5, 10, 15, 20], index=1)

    if st.button("Find Matching Jobs", type="primary", use_container_width=True):
        if not selected_skills:
            st.warning("Please select at least one skill.")
        else:
            try:
                results = recommend_jobs(selected_skills, top_n=len(jobs))
                # Normalize the recommender's score column name to one stable name.
                if "match_score" not in results.columns:
                    alternatives = ["Match Score (%)", "match_score_pct", "score"]
                    found = next((c for c in alternatives if c in results.columns), None)
                    if found:
                        results = results.rename(columns={found: "match_score"})
                    elif not results.empty:
                        st.error(f"Recommendation output has no match-score column. Available columns: {', '.join(map(str, results.columns))}")
                        return
                    else:
                        results["match_score"] = pd.Series(dtype="float64")
                if industry != "Any":
                    results = results[results["industry"].astype(str).str.casefold() == industry.casefold()]
                if location != "Any":
                    results = results[results["location"].astype(str).str.casefold() == location.casefold()]
                if remote != "Any":
                    results = results[results["remote_option"].astype(str).str.casefold() == remote.casefold()]
                if selected_sizes:
                    results = results[results["company_size"].isin(selected_sizes)]
                if salary_range is not None:
                    results = results[pd.to_numeric(results["salary_usd"], errors="coerce").between(*salary_range, inclusive="both")]
                if not results.empty:
                    results = results.sort_values(["match_score", "salary_usd"], ascending=[False, False], na_position="last")
                results = results.head(int(top_n)).reset_index(drop=True)
                st.session_state["job_results"] = results
                st.session_state["job_search_done"] = True
            except Exception as exc:
                st.error(f"Could not generate job recommendations: {exc}")

    if not st.session_state.get("job_search_done", False):
        st.info("Choose your skills and optional filters, then select **Find Matching Jobs**.")
        return
    results = st.session_state.get("job_results", pd.DataFrame())
    if results.empty:
        st.warning("No jobs match those skills and filters. Try changing your selection.")
        return
    st.subheader("2. Matching job listings")
    st.caption("REQUIRED SKILL COVERAGE = matched required skills divided by all listed required skills.")
    st.write(f"Showing **{len(results)}** matching job(s).")
    for _, row in results.iterrows():
        salary = pd.to_numeric(pd.Series([row.get("salary_usd")]), errors="coerce").iloc[0]
        salary_text = f"${salary:,.0f} per year" if pd.notna(salary) else "Not specified"
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(f'### {safe(row.get("job_title", "Job title not specified"))}')
        st.markdown(f'<div class="muted">{safe(row.get("industry"))} · {safe(row.get("location"))}</div>', unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.metric("Skill coverage", f'{float(row.get("match_score", 0)):.1f}%')
        b.metric("Annual salary", salary_text)
        c.metric("Remote option", safe(row.get("remote_option")))
        st.markdown(f'**Company size:** {safe(row.get("company_size"))}')
        st.markdown(f'**Matched skills:** {safe(row.get("matched_skills"))}')
        st.markdown(f'**Other required skills:** {safe(row.get("missing_skills"))}')
        st.markdown(f'**All listed skills:** {safe(row.get("skills_required"))}')
        posting_date = row.get("posting_date")
        if pd.notna(posting_date):
            st.caption(f'Posting date: {pd.Timestamp(posting_date).date().isoformat()}')
        st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎯 SkillPath AI")
    st.caption("Career planning and job matching")
    page = st.radio("Navigate", ["Career Recommendation", "Job Recommendation"], label_visibility="collapsed")
    st.divider()
    st.markdown("### About")
    st.caption("SkillPath AI compares selected skills with career profiles and job listings from the project's datasets.")
    st.caption("Scores show skill overlap only; they do not predict hiring outcomes.")

if page == "Career Recommendation":
    career_page()
else:
    job_page()

st.markdown("---")
st.caption("SkillPath AI · Skill-based suggestions for learning and exploration.")
