import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files = [
    DATA_DIR / "career_dataset_large.xlsx",
    DATA_DIR / "job_recommendation_dataset.csv",
]

for file in files:
    print("\n" + "=" * 70)
    print(f"DATASET: {file.name}")
    print("=" * 70)

    try:
        if file.suffix.lower() == ".xlsx":
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)

        print(f"\nRows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")

        print("\nColumn names and data types:")
        print(df.dtypes.to_string())

        print("\nMissing values per column:")
        print(df.isnull().sum().to_string())

        print(f"\nDuplicate rows: {df.duplicated().sum()}")

        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False, max_cols=12))

        print("\nUnique values per column:")
        print(df.nunique(dropna=False).to_string())

    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 70)
print("DATASET ANALYSIS COMPLETED")
print("=" * 70)
