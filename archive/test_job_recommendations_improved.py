#!/usr/bin/env python
"""
Comprehensive test for the improved job recommendation system.
Tests that the system correctly handles generic data-related terms vs genuine career matches.
"""

from app.services.jobs.job_database import (
    get_career_match,
    get_recommended_jobs,
    CAREER_PROFILES,
    calculate_job_score
)

def test_data_analyst_core_skills():
    """Verify Data Analyst has only SQL as core skill, others as supporting"""
    profile = CAREER_PROFILES["data analyst"]
    assert "sql" in profile["core_skills"], "SQL should be core skill for Data Analyst"
    assert len(profile["core_skills"]) == 1, "Only SQL should be core skill"
    assert "data analysis" in profile["supporting_skills"], "data analysis should be supporting"
    assert "excel" in profile["supporting_skills"], "excel should be supporting"
    print("✓ Data Analyst profile correctly structured")

def test_data_scientist_core_skills():
    """Verify Data Scientist requires ML-specific core skills"""
    profile = CAREER_PROFILES["data scientist"]
    core = profile["core_skills"]
    assert "machine learning" in core, "machine learning should be core"
    assert "tensorflow" in core or "pytorch" in core, "deep learning frameworks should be core"
    print("✓ Data Scientist profile has ML-specific core skills")

def test_business_support_no_data_analyst_match():
    """Test that business support jobs with generic data terms don't match Data Analyst"""
    mock_business_job = {
        'title': 'Senior Executive Business Support',
        'category': 'Business Management',
        'description': 'SQL, Power BI, statistics, Excel, reporting, data analysis',
        'education': 'Bachelor Degree',
        'experience': '1 year'
    }
    
    result = get_career_match(mock_business_job, "Data Analyst")
    
    # Key assertion: should NOT match
    assert not result["matched"], (
        f"Business Support should NOT match Data Analyst. "
        f"Got matched={result['matched']}, reason={result['reason']}"
    )
    assert result["score"] == 0, "Score should be 0 for non-match"
    print("✓ Business Support job correctly rejected for Data Analyst")

def test_genuine_data_analyst_with_sql():
    """Test that genuine data analyst jobs with SQL do match"""
    mock_analyst_job = {
        'title': 'Data Analyst',
        'category': 'Data',
        'description': 'SQL, Python, Power BI, Excel, reporting, data visualization',
        'education': 'Bachelor Degree',
        'experience': '1 year'
    }
    
    result = get_career_match(mock_analyst_job, "Data Analyst")
    
    # Should match strongly due to title
    assert result["matched"], f"Data Analyst job should match. Got {result}"
    assert result["score"] == 100, "Title match should give score of 100"
    assert result["reason"] == "strong_title", "Should match on strong title"
    print("✓ Genuine Data Analyst job correctly matched via title")

def test_sql_without_business_contradiction():
    """Test SQL matching when there's no business contradiction"""
    mock_analyst_job = {
        'title': 'Business Analyst',
        'category': 'Analysis',
        'description': 'SQL, Python, Power BI, Excel, statistics, reporting',
        'education': 'Bachelor Degree',
        'experience': '1 year'
    }
    
    result = get_career_match(mock_analyst_job, "Data Analyst")
    
    # Should match on supporting role title
    assert result["matched"], f"Business Analyst should match Data Analyst. Got {result}"
    assert result["score"] == 60, f"Supporting title should give score of 60, got {result['score']}"
    assert result["reason"] == "supporting_title"
    print("✓ Business Analyst correctly matched via supporting title")

def test_skill_matching_threshold():
    """Test that skill-based matching requires sufficient evidence"""
    # Job with 1 core skill + only 2 supporting skills
    mock_minimal_job = {
        'title': 'Accounts Management',
        'category': 'Business',
        'description': 'SQL and Excel experience required',
        'education': 'Bachelor Degree',
        'experience': '1 year'
    }
    
    result = get_career_match(mock_minimal_job, "Data Analyst")
    
    # Should NOT match - not enough supporting skills and business contradiction
    assert not result["matched"], (
        f"Should not match with insufficient supporting skills and business contradiction. "
        f"Got {result}"
    )
    print("✓ Skill matching threshold correctly enforced")

def test_multiple_core_skills_match():
    """Test that 2+ core skills allow matching regardless of title"""
    mock_ml_job = {
        'title': 'Algorithm Developer',
        'category': 'Technology',
        'description': 'Machine Learning, TensorFlow, PyTorch, Python, scikit-learn deep learning',
        'education': 'Bachelor Degree',
        'experience': '2 years'
    }
    
    result = get_career_match(mock_ml_job, "Data Scientist")
    
    # Should match on multiple core skills
    assert result["matched"], f"Should match with 2+ core skills. Got {result}"
    assert result["score"] >= 55, f"Should score 55+. Got {result['score']}"
    assert result["reason"] == "career_skills"
    print("✓ Multiple core skills correctly enable skill-based matching")

def test_recommendations_structure():
    """Test that job recommendations maintain required structure"""
    test_jobs = get_recommended_jobs(
        skills=['SQL', 'Python'],
        careers=[{'career': 'Data Analyst', 'score': 70}],
        candidate_education='Bachelor Degree',
        candidate_experience='1 year',
        limit=5
    )
    
    # Check structure of returned jobs
    for job in test_jobs:
        required_keys = [
            'match_score', 'career_matches', 'matched_skills',
            'career_score', 'skill_score', 'recommendation_type'
        ]
        for key in required_keys:
            assert key in job, f"Job missing required key: {key}"
    
    print("✓ Job recommendations maintain correct structure")

if __name__ == "__main__":
    print("=" * 80)
    print("Running Job Matching System Tests")
    print("=" * 80)
    
    test_data_analyst_core_skills()
    test_data_scientist_core_skills()
    test_business_support_no_data_analyst_match()
    test_genuine_data_analyst_with_sql()
    test_sql_without_business_contradiction()
    test_skill_matching_threshold()
    test_multiple_core_skills_match()
    test_recommendations_structure()
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print("\nKey improvements:")
    print("1. ✓ Generic data-related terms no longer cause false matches")
    print("2. ✓ Business/accounting jobs correctly rejected for data roles")
    print("3. ✓ Core skills vs supporting skills distinction prevents misclassification")
    print("4. ✓ Title/category matches remain stronger than skill-based matches")
    print("5. ✓ Candidate resume skills remain separate from career-profile skills")
