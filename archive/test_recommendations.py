#!/usr/bin/env python
"""Test script to validate job recommendations"""

from app.services.jobs.job_database import get_jobs, get_recommended_jobs
from pprint import pprint

print("=" * 80)
print("Testing Job Recommendation System")
print("=" * 80)

# First, check what jobs are in the database
all_jobs = get_jobs(limit=100)
print(f"\nTotal jobs in database: {len(all_jobs)}")

# Find genuine data science/analyst jobs
ds_jobs = [j for j in all_jobs if 'data scientist' in str(j['title']).lower()]
da_jobs = [j for j in all_jobs if 'data analyst' in str(j['title']).lower()]
ba_jobs = [j for j in all_jobs if 'business' in str(j['title']).lower() and 'support' in str(j['title']).lower()]

print(f"\nData Scientist jobs: {len(ds_jobs)}")
for j in ds_jobs[:3]:
    print(f"  - {j['title']}")

print(f"\nData Analyst jobs: {len(da_jobs)}")
for j in da_jobs[:3]:
    print(f"  - {j['title']}")

print(f"\nBusiness Support jobs: {len(ba_jobs)}")
for j in ba_jobs[:3]:
    print(f"  - {j['title']}")

# Test scenario from requirements
print("\n" + "=" * 80)
print("TEST SCENARIO: Candidate with strong Data Science profile")
print("=" * 80)
print("\nCandidate Skills: Python, SQL, Machine Learning, NumPy, Pandas, Power BI")
print("Predicted Careers: Data Scientist (83%), Data Analyst (67%)")
print("Education: Bachelor Degree")
print("Experience: 1 year")

jobs = get_recommended_jobs(
    skills=['Python', 'SQL', 'Machine Learning', 'NumPy', 'Pandas', 'Power BI'],
    careers=[
        {'career': 'Data Scientist', 'score': 83},
        {'career': 'Data Analyst', 'score': 67},
        {'career': 'Full StackDeveloper', 'score': 67},
        {'career': 'Backend Developer', 'score': 50},
        {'career': 'Frontend Developer', 'score': 50}
    ],
    candidate_education='Bachelor Degree',
    candidate_experience='1 year',
    limit=15
)

print(f"\nTop 15 Recommended Jobs: {len(jobs)}")
print("\n" + "-" * 80)

for idx, job in enumerate(jobs, 1):
    print(f"\n{idx}. {job['title']}")
    print(f"   Type: {job.get('recommendation_type', 'Unknown')}")
    print(f"   Match Score: {job.get('match_score', 0)}")
    print(f"   Career Matches: {job.get('career_matches', [])}")
    print(f"   Career Score: {job.get('career_score', 0)}")
    print(f"   Skill Score: {job.get('skill_score', 0)}")
    print(f"   Matched Skills: {job.get('matched_skills', [])}")
    
    # Only print career reasons if present
    if job.get('career_reasons'):
        print(f"   Career Reasons: {job.get('career_reasons', [])[:3]}")

print("\n" + "=" * 80)
print("Analysis:")
print("-" * 80)

# Count matches by career
data_scientist_matches = [j for j in jobs if 'data scientist' in str(j.get('career_matches', [])).lower()]
data_analyst_matches = [j for j in jobs if 'data analyst' in str(j.get('career_matches', [])).lower()]

print(f"Data Scientist career matches: {len(data_scientist_matches)}")
print(f"Data Analyst career matches: {len(data_analyst_matches)}")

# Check if "Senior Executive Business Support" appears as CAREER match
business_support = [j for j in jobs if 'business' in j['title'].lower() and 'support' in j['title'].lower()]
if business_support:
    has_career_match = any(j.get('career_matches') for j in business_support)
    if has_career_match:
        print(f"\n❌ CRITICAL: Business support jobs appearing with CAREER matches:")
        for j in business_support:
            if j.get('career_matches'):
                print(f"   - {j['title']} (Career: {j.get('career_matches', [])}, Type: {j.get('recommendation_type')})")
    else:
        print(f"\n✓ GOOD: Business support jobs NOT appearing as career matches")
        print(f"   (They appear as skill-based alternatives, which is acceptable)")
        for j in business_support:
            print(f"   - {j['title']} (Type: {j.get('recommendation_type')}, Career: {j.get('career_matches', [])})")
else:
    print(f"\n✓ Good: No business support jobs appearing in recommendations")

# Check if genuine data science jobs appear
print(f"\nGenuine data science jobs in recommendations:")
ds_in_results = [j for j in jobs if 'data scientist' in j['title'].lower()]
if ds_in_results:
    print(f"  ✓ Found {len(ds_in_results)} genuine data scientist jobs")
    for j in ds_in_results[:3]:
        print(f"    - {j['title']} (Score: {j.get('match_score', 0)})")
else:
    print(f"  ✗ No genuine data scientist jobs found")
