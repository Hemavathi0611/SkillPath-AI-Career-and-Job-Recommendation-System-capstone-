from src.jobs.job_recommender import load_job_data, recommend_jobs, split_skills

jobs = load_job_data()
first = jobs.iloc[0]
skills = split_skills(first["skills_required"])
location = first["location"]
industry = first["industry"]

passed = 0
failed = 0

def check(name, condition, details=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}")
    if details:
        print(f"      {details}")

# Location filter
result = recommend_jobs(skills, top_n=10000, location=location)
check(
    "Location filter",
    result.empty or result["location"].str.casefold().str.contains(
        location.casefold(), regex=False
    ).all(),
    f"Location tested: {location}; results: {len(result)}"
)

# Industry filter
result = recommend_jobs(skills, top_n=10000, industry=industry)
check(
    "Industry filter",
    result.empty or (result["industry"].str.casefold() == industry.casefold()).all(),
    f"Industry tested: {industry}; results: {len(result)}"
)

# Combined location and industry filters
result = recommend_jobs(
    skills, top_n=10000, location=location, industry=industry
)
check(
    "Combined location and industry filters",
    result.empty or (
        result["location"].str.casefold().str.contains(
            location.casefold(), regex=False
        ).all()
        and (result["industry"].str.casefold() == industry.casefold()).all()
    ),
    f"Results: {len(result)}"
)

# Remote-only filter
result = recommend_jobs(skills, top_n=10000, remote_only=True)
check(
    "Remote-only filter",
    result.empty or result["remote_option"].str.casefold().isin(
        {"yes", "true", "remote", "1"}
    ).all(),
    f"Results: {len(result)}"
)

print("\n" + "=" * 40)
print(f"FILTER TESTS PASSED: {passed}")
print(f"FILTER TESTS FAILED: {failed}")
print("=" * 40)
