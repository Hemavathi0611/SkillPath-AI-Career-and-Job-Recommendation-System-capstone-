from pathlib import Path
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "job_recommendation_dataset.csv"
REQUIRED_COLUMNS = [
    "job_id", "job_title", "industry", "location", "salary_usd",
    "skills_required", "remote_option", "company_size", "posting_date"
]

def normalize_skill(value):
    value = str(value).strip().casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9+#]", "", value)

def split_skills(value):
    if pd.isna(value):
        return []
    return [part.strip() for part in re.split(r"[,;|]", str(value)) if part.strip()]

def load_job_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Job dataset not found: {DATA_PATH}. Put job_recommendation_dataset.csv in data/raw/."
        )
    df = pd.read_csv(DATA_PATH)
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Job dataset missing columns: {missing}. Found: {df.columns.tolist()}")
    df = df[REQUIRED_COLUMNS].copy()
    for col in ["job_title", "industry", "location", "skills_required", "remote_option", "company_size"]:
        df[col] = df[col].fillna("Not specified").astype(str).str.strip()
    df["salary_usd"] = pd.to_numeric(df["salary_usd"], errors="coerce")
    df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
    return df.drop_duplicates(subset=["job_id"], keep="first").reset_index(drop=True)

def recommend_jobs(user_skills, top_n=10, location=None, remote_only=False, industry=None):
    df = load_job_data()
    output_cols = ["matched_skills", "missing_skills", "match_score", "matched_skill_count"]
    user_map = {normalize_skill(s): str(s).strip() for s in (user_skills or []) if str(s).strip()}
    if top_n <= 0 or not user_map:
        for col in output_cols:
            df[col] = pd.Series(index=df.index, dtype="float64" if col in {"match_score", "matched_skill_count"} else "object")
        return df.head(0)

    if location and location.casefold() != "any":
        df = df[df["location"].str.casefold().str.contains(location.casefold(), na=False)]
    if industry and industry.casefold() != "any":
        df = df[df["industry"].str.casefold() == industry.casefold()]
    if remote_only:
        df = df[df["remote_option"].str.casefold().isin({"yes", "true", "remote", "1"})]

    rows = []
    for _, row in df.iterrows():
        required = {}
        for skill in split_skills(row["skills_required"]):
            required.setdefault(normalize_skill(skill), skill)
        if not required:
            continue
        matched_keys = set(required) & set(user_map)
        if not matched_keys:
            continue
        matched = sorted((required[k] for k in matched_keys), key=str.casefold)
        missing = sorted((v for k, v in required.items() if k not in matched_keys), key=str.casefold)
        item = row.to_dict()
        item["matched_skills"] = ", ".join(matched)
        item["missing_skills"] = ", ".join(missing) if missing else "None"
        item["match_score"] = round(100 * len(matched_keys) / len(required), 2)
        item["matched_skill_count"] = len(matched_keys)
        rows.append(item)

    if not rows:
        for col in output_cols:
            df[col] = pd.Series(index=df.index, dtype="float64" if col in {"match_score", "matched_skill_count"} else "object")
        return df.head(0)
    return pd.DataFrame(rows).sort_values(
        ["match_score", "matched_skill_count", "salary_usd"],
        ascending=[False, False, False], na_position="last", kind="stable"
    ).head(top_n).reset_index(drop=True)
