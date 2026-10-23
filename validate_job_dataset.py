import pandas as pd
from pathlib import Path

raw_path = Path("data/raw/job_recommendation_dataset.csv")
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(raw_path)
df.columns = df.columns.str.strip()

# Clean whitespace in text columns
for col in df.select_dtypes(include=["object", "str"]).columns:
    df[col] = df[col].str.strip()

# Validate posting dates
dates = pd.to_datetime(df["posting_date"], errors="coerce")
invalid_dates = int(dates.isna().sum())
df["posting_date"] = dates.dt.strftime("%Y-%m-%d")

# Check salaries
salary = pd.to_numeric(df["salary_usd"], errors="coerce")
invalid_salary = int(salary.isna().sum())
nonpositive_salary = int((salary <= 0).sum())

# Check missing and duplicate records
missing_before = int(df.isna().sum().sum())
duplicates_before = int(df.duplicated().sum())

# Save a cleaned copy without silently deleting invalid records
df.to_csv(
    output_dir / "job_recommendation_dataset_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)

print("JOB DATASET VALIDATION COMPLETE")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Missing values before cleaning: {missing_before}")
print(f"Duplicate rows: {duplicates_before}")
print(f"Invalid posting dates: {invalid_dates}")
print(f"Invalid salary values: {invalid_salary}")
print(f"Non-positive salaries: {nonpositive_salary}")
print(f"Minimum salary: {salary.min()}")
print(f"Maximum salary: {salary.max()}")
print(f"Saved to: {output_dir / 'job_recommendation_dataset_cleaned.csv'}")
