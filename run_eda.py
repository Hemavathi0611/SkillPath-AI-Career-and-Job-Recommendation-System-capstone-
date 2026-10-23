import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

career_path = Path("data/processed/career_dataset_cleaned.csv")
jobs_path = Path("data/processed/job_recommendation_dataset_cleaned.csv")

out = Path("outputs/reports/eda")
out.mkdir(parents=True, exist_ok=True)

career = pd.read_csv(career_path)
jobs = pd.read_csv(jobs_path)

def save_bar(series, title, xlabel, ylabel, filename, horizontal=True):
    plt.figure(figsize=(10, 6))
    if horizontal:
        series.sort_values().plot(kind="barh")
    else:
        series.plot(kind="bar")
        plt.xticks(rotation=35, ha="right")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(out / filename, dpi=150)
    plt.close()
    print(f"Saved: {out / filename}")

# Career dataset analysis
print("\n=== CAREER DATASET ===")
print("\nCareer counts:")
print(career["Recommended Career"].value_counts().to_string())

print("\nEducation level counts:")
print(career["Education Level"].value_counts().to_string())

save_bar(
    career["Recommended Career"].value_counts().head(10),
    "Top 10 Recommended Careers in Dataset",
    "Number of records", "Career",
    "top_careers.png"
)

save_bar(
    career["Education Level"].value_counts(),
    "Education Level Distribution",
    "Number of records", "Education level",
    "education_distribution.png"
)

# Job dataset analysis
print("\n=== JOB DATASET ===")
print("\nTop industries:")
print(jobs["industry"].value_counts().head(10).to_string())

print("\nTop job locations:")
print(jobs["location"].value_counts().head(10).to_string())

print("\nSalary summary (USD):")
print(jobs["salary_usd"].describe().round(2).to_string())

save_bar(
    jobs["industry"].value_counts().head(10),
    "Top 10 Industries by Job Listings",
    "Number of listings", "Industry",
    "top_industries.png"
)

save_bar(
    jobs["location"].value_counts().head(10),
    "Top 10 Job Locations",
    "Number of listings", "Location",
    "top_locations.png"
)

plt.figure(figsize=(9, 5))
jobs["salary_usd"].plot(kind="hist", bins=20, edgecolor="black")
plt.title("Job Salary Distribution")
plt.xlabel("Salary (USD)")
plt.ylabel("Number of listings")
plt.tight_layout()
plt.savefig(out / "salary_distribution.png", dpi=150)
plt.close()
print(f"Saved: {out / 'salary_distribution.png'}")

print("\nEDA COMPLETED")
print(f"Charts saved in: {out}")
