from src.career.recommender import recommend_careers
from src.jobs.job_recommender import load_job_data, recommend_jobs, split_skills

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

print("\n=== CAREER RECOMMENDER TESTS ===")

# A known combination of technical skills
career_results = recommend_careers(
    ["Python", "SQL", "Machine Learning"], top_n=5
)
check(
    "Technical skills return career recommendations",
    not career_results.empty,
    f"Results: {len(career_results)}"
)

if not career_results.empty:
    check(
        "Career match scores are between 0 and 100",
        career_results["Match Score (%)"].between(0, 100).all()
    )
    check(
        "Career results are sorted by match score",
        career_results["Match Score (%)"].is_monotonic_decreasing
    )
    print("\nCareer recommendations:")
    print(career_results.to_string(index=False))

check(
    "Empty skills return no career recommendations",
    recommend_careers([], top_n=5).empty
)

check(
    "Zero top_n returns no career recommendations",
    recommend_careers(["Python"], top_n=0).empty
)

check(
    "Unknown skills return no career recommendations",
    recommend_careers(["unknown_skill_xyz_987"], top_n=5).empty
)

print("\n=== JOB RECOMMENDER TESTS ===")

jobs = load_job_data()
check("Job dataset loads", not jobs.empty, f"Rows: {len(jobs)}")

# Use real skills from the first job to ensure the test is grounded
first_job = jobs.iloc[0]
test_skills = split_skills(first_job["skills_required"])

job_results = recommend_jobs(test_skills, top_n=10)
check(
    "Skills from a real job return recommendations",
    not job_results.empty,
    f"Test skills: {test_skills}"
)

if not job_results.empty:
    check(
        "Job match scores are between 0 and 100",
        job_results["match_score"].between(0, 100).all()
    )
    check(
        "Job results are sorted by match score",
        job_results["match_score"].is_monotonic_decreasing
    )
    check(
        "Job results include matched and missing skills",
        {"matched_skills", "missing_skills"}.issubset(job_results.columns)
    )
    print("\nTop job recommendations:")
    print(
        job_results[
            ["job_title", "industry", "location", "match_score", "salary_usd"]
        ].head(5).to_string(index=False)
    )

check(
    "Empty skills return no job recommendations",
    recommend_jobs([], top_n=5).empty
)

check(
    "Unknown skills return no job recommendations",
    recommend_jobs(["unknown_skill_xyz_987"], top_n=5).empty
)

check(
    "Zero top_n returns no job recommendations",
    recommend_jobs(["Python"], top_n=0).empty
)

print("\n" + "=" * 45)
print(f"TESTS PASSED: {passed}")
print(f"TESTS FAILED: {failed}")
print("=" * 45)
