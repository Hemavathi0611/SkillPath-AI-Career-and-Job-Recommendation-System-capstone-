from pathlib import Path
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "career_dataset_large.xlsx"
CAREER_COLUMN = "Recommended Career"
SKILLS_COLUMN = "Skills"

CAREER_SKILLS = {
    "Business Analyst": {"sql", "data analysis", "excel", "power bi", "tableau", "business analysis", "communication"},
    "Clerk": {"ms office", "data entry", "excel", "administration", "organization"},
    "Data Entry Operator": {"data entry", "typing", "ms office", "excel", "attention to detail"},
    "Financial Analyst": {"financial analysis", "accounting", "excel", "financial modelling", "sql", "data analysis"},
    "Junior Accountant": {"accounting", "tally erp", "bookkeeping", "financial reporting", "taxation", "excel"},
    "Marketing Executive": {"marketing", "digital marketing", "communication", "market research", "seo", "content creation"},
    "ML Engineer": {"python", "machine learning", "deep learning", "sql", "data analysis", "tensorflow", "pytorch", "model deployment", "statistics"},
    "Professor": {"teaching", "research", "communication", "subject knowledge", "mentoring"},
    "Research Scientist": {"research", "python", "machine learning", "statistics", "data analysis", "experimentation"},
    "Sales Assistant": {"sales", "communication", "customer service", "negotiation", "product knowledge"},
    "School Counselor": {"counseling", "communication", "psychology", "active listening", "student support"},
    "Software Engineer": {"python", "java", "c++", "programming", "software development", "data structures", "algorithms", "sql", "git"},
}

def normalize_skill(value):
    value = str(value).strip().casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9+#]", "", value)

def display_skill(skill):
    names = {"powerbi": "Power BI", "msoffice": "MS Office", "tallyerp": "Tally ERP",
             "c++": "C++", "seo": "SEO", "sql": "SQL", "python": "Python",
             "java": "Java", "git": "Git"}
    return names.get(normalize_skill(skill), skill.strip().title())

def load_career_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Career dataset not found: {DATA_PATH}. Put career_dataset_large.xlsx in data/raw/.")
    df = pd.read_excel(DATA_PATH)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in (CAREER_COLUMN, SKILLS_COLUMN) if c not in df.columns]
    if missing:
        raise ValueError(f"Career dataset missing columns: {missing}. Found: {df.columns.tolist()}")
    df = df[[CAREER_COLUMN, SKILLS_COLUMN]].drop_duplicates().copy()
    df[CAREER_COLUMN] = df[CAREER_COLUMN].fillna("").astype(str).str.strip()
    df[SKILLS_COLUMN] = df[SKILLS_COLUMN].fillna("").astype(str).str.strip()
    df = df[(df[CAREER_COLUMN] != "") & (df[SKILLS_COLUMN] != "")]
    if df.empty:
        raise ValueError("Career dataset has no usable rows.")
    return df.reset_index(drop=True)

def recommend_careers(user_skills, top_n=5):
    columns = ["Career", "Matched Skills", "Missing Skills", "Match Score (%)"]
    if top_n <= 0:
        return pd.DataFrame(columns=columns)
    user_set = {normalize_skill(s) for s in (user_skills or []) if str(s).strip()}
    if not user_set:
        return pd.DataFrame(columns=columns)

    dataset_careers = {c.casefold() for c in load_career_data()[CAREER_COLUMN].unique()}
    rows = []
    for career, required in CAREER_SKILLS.items():
        if career.casefold() not in dataset_careers:
            continue
        required_map = {normalize_skill(s): s for s in required}
        matched_keys = set(required_map) & user_set
        if not matched_keys:
            continue
        matched = sorted((display_skill(required_map[k]) for k in matched_keys), key=str.casefold)
        missing = sorted((display_skill(v) for k, v in required_map.items() if k not in matched_keys), key=str.casefold)
        rows.append({
            "Career": career,
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing) if missing else "None",
            "Match Score (%)": round(100 * len(matched_keys) / len(required_map), 2),
            "_matched": len(matched_keys),
        })
    if not rows:
        return pd.DataFrame(columns=columns)
    result = pd.DataFrame(rows).sort_values(
        ["Match Score (%)", "_matched", "Career"],
        ascending=[False, False, True], kind="stable"
    )
    return result[columns].head(top_n).reset_index(drop=True)
