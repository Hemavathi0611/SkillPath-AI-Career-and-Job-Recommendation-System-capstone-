import pandas as pd
from pathlib import Path

raw_path = Path("data/raw/career_dataset_large.xlsx")
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(raw_path)

# Remove accidental spaces from column names and text values
df.columns = df.columns.str.strip()

for col in df.select_dtypes(include=["object", "str"]).columns:
    df[col] = df[col].str.strip()

# Preserve rows and replace missing certifications with a clear label
df["Certifications"] = (
    df["Certifications"]
    .fillna("Not specified")
    .replace("", "Not specified")
)

# Remove exact duplicate records
before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
removed = before - len(df)

output_path = output_dir / "career_dataset_cleaned.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("CAREER DATASET CLEANING COMPLETE")
print(f"Original rows: {before}")
print(f"Duplicates removed: {removed}")
print(f"Cleaned rows: {len(df)}")
print(f"Missing values remaining: {int(df.isna().sum().sum())}")
print(f"Saved to: {output_path}")
