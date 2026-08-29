#!/usr/bin/env python
"""Debug script to check actual job data"""

from app.services.jobs.job_database import get_jobs, get_career_match, CAREER_PROFILES, normalize_phrase

# Get all jobs
jobs = get_jobs(limit=100)

# Find the business support job
target_job = None
for job in jobs:
    if 'business' in str(job['title']).lower() and 'support' in str(job['title']).lower():
        target_job = job
        break

if target_job:
    print("=" * 80)
    print(f"Job: {target_job['title']}")
    print("=" * 80)
    print(f"Category: {target_job['category']}")
    print(f"\nDescription (first 500 chars):")
    desc = target_job['description'] or ""
    print(desc[:500] if len(desc) > 500 else desc)
    
    print("\n" + "=" * 80)
    print("Career Matching Analysis")
    print("=" * 80)
    
    # Check Data Analyst match
    data_analyst_match = get_career_match(target_job, "Data Analyst")
    print(f"\nData Analyst Match:")
    print(f"  Matched: {data_analyst_match['matched']}")
    print(f"  Score: {data_analyst_match['score']}")
    print(f"  Reason: {data_analyst_match['reason']}")
    print(f"  Matched Skills: {data_analyst_match['matched_skills']}")
    print(f"  Matches: {data_analyst_match['matches']}")
    
    # Get the data analyst profile
    da_profile = CAREER_PROFILES.get("data analyst", {})
    print(f"\nData Analyst Profile Skills:")
    print(f"  Core Skills: {da_profile.get('core_skills', [])}")
    print(f"  Supporting Skills: {da_profile.get('supporting_skills', [])}")
    
    # Check Data Scientist match
    data_scientist_match = get_career_match(target_job, "Data Scientist")
    print(f"\nData Scientist Match:")
    print(f"  Matched: {data_scientist_match['matched']}")
    print(f"  Score: {data_scientist_match['score']}")
    print(f"  Reason: {data_scientist_match['reason']}")
    print(f"  Matched Skills: {data_scientist_match['matched_skills']}")
    
    # Get the data scientist profile
    ds_profile = CAREER_PROFILES.get("data scientist", {})
    print(f"\nData Scientist Profile Skills:")
    print(f"  Core Skills: {ds_profile.get('core_skills', [])}")
    print(f"  Supporting Skills: {ds_profile.get('supporting_skills', [])}")
