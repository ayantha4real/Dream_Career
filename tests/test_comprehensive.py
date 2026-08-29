import pytest
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.services.resume_parser import extract_text_from_pdf
from app.services.skill_extractor import extract_skills
from app.services.career_matcher import match_careers
from app.services.ml_predictor import predict_career
from app.services.nlp_analyzer import analyze_resume_text, estimate_experience_years
from app.services.qualification_recommender import recommend_qualifications
from app.services.skill_demand import get_skill_demand
from app.services.text_cleaner import clean_html_text
from app.services.jobs.job_database import (
    get_jobs, get_job, get_job_categories, split_category, get_category_group
)
from app.services.jobs.job_database import get_recommended_jobs


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(app):
    """Create a client with a logged-in user."""
    with app.app_context():
        from app import db
        from app.models.user import User
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    client = app.test_client()
    client.post("/login", data={
        "identifier": "test@example.com",
        "password": "password123"
    }, follow_redirects=True)
    return client


class TestResumeParser:
    def test_extract_text_from_valid_pdf(self):
        result = extract_text_from_pdf("app/static/uploads/test_resume.pdf")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_extract_text_from_nonexistent_file(self):
        result = extract_text_from_pdf("nonexistent.pdf")
        assert result == ""

    def test_extract_text_from_empty_string(self):
        result = extract_text_from_pdf("")
        assert result == ""


class TestSkillExtractor:
    def test_extract_skills_basic(self):
        text = "Python, SQL, Excel, Machine Learning, Pandas, Git"
        skills = extract_skills(text)
        assert "Python" in skills
        assert "SQL" in skills
        assert "Excel" in skills
        assert "Machine Learning" in skills

    def test_extract_skills_empty(self):
        skills = extract_skills("")
        assert skills == []

    def test_extract_skills_case_insensitive(self):
        skills = extract_skills("python SQL excel")
        assert "Python" in skills
        assert "SQL" in skills
        assert "Excel" in skills


class TestCareerMatcher:
    def test_match_careers_basic(self):
        skills = ["Python", "SQL", "Excel", "Power BI", "Pandas"]
        careers = match_careers(skills)
        assert len(careers) > 0
        assert careers[0]["career"] == "Data Analyst"
        assert careers[0]["score"] > 0

    def test_match_careers_empty_returns_zero_scores(self):
        careers = match_careers([])
        # All careers should have 0 score when no skills provided
        assert all(c["score"] == 0 for c in careers)


class TestMLPredictor:
    def test_predict_career_valid_sl_resume(self):
        # Use SL-format resume text that matches training data
        text = """Dilshan Herath

Systems Analyst

Badulla, Sri Lanka | +94 81 2645033 | dilshan67@gmail.com | linkedin.com/in/dilshan-herath

Professional Summary
Systems Analyst based in Badulla with 5+ years of experience in information technology related roles. Skilled in SQL, Linux, Agile. Known for delivering reliable results, working well in teams and continuously improving processes. Fluent in Sinhala and English.

Skills
- SQL
- Linux
- Agile
- Problem Solving
- Team Leadership
- System Design

Work Experience
Systems Analyst — MAS Holdings, Badulla
2019 - Present
- Designed and implemented system solutions for manufacturing operations
- Optimized database queries reducing response time by 40%
- Led agile team of 8 developers across multiple projects

Education
BSc (Hons) in Computer Science, University of Peradeniya (2018)"""
        result = predict_career(text)
        assert "predictions" in result
        assert len(result["predictions"]) > 0
        assert result["predictions"][0]["career"] == "INFORMATION-TECHNOLOGY"
        assert result["confidence"] > 80
        assert result["low_confidence"] is False

    def test_predict_career_short_text(self):
        result = predict_career("Python SQL")
        assert result["low_confidence"] is True

    def test_predict_career_empty(self):
        result = predict_career("")
        assert result["predictions"] == []
        assert result["low_confidence"] is True


class TestNLPAnalyzer:
    def test_analyze_resume_text(self):
        text = "John Perera worked at IFS Lanka since 2019 building Python systems"
        result = analyze_resume_text(text)
        assert "organizations" in result
        assert "keywords" in result
        assert "word_count" in result

    def test_estimate_experience_years(self):
        years = estimate_experience_years("Worked from 2019 - 2023 at Company X")
        assert years == 4


class TestQualificationRecommender:
    def test_recommend_qualifications(self):
        missing = ["TensorFlow", "Docker"]
        quals = recommend_qualifications(missing)
        assert isinstance(quals, list)

    def test_recommend_qualifications_empty(self):
        quals = recommend_qualifications([])
        assert quals == []


class TestSkillDemand:
    def test_get_skill_demand(self):
        demand = get_skill_demand(limit=5)
        assert "skills" in demand
        assert "jobs_scanned" in demand
        assert isinstance(demand["skills"], list)


class TestTextCleaner:
    def test_clean_html_text(self):
        dirty = '<p><strong>Test</strong></p><br><span>More</span>'
        clean = clean_html_text(dirty)
        assert "<" not in clean
        assert "Test" in clean
        assert "More" in clean

    def test_clean_empty(self):
        assert clean_html_text("") == ""
        assert clean_html_text(None) == ""


class TestJobDatabase:
    def test_get_jobs(self):
        jobs = get_jobs(limit=5)
        assert isinstance(jobs, list)
        assert len(jobs) <= 5

    def test_get_job_categories(self):
        cats = get_job_categories()
        assert isinstance(cats, list)
        assert len(cats) > 0

    def test_split_category(self):
        cats = split_category("IT-SWare / Internet, BPO/ KPO")
        assert "IT-SWare / Internet" in cats
        assert "BPO/ KPO" in cats

    def test_get_category_group(self):
        group = get_category_group("IT-SWare / Internet")
        assert group == "Information Technology"

    def test_get_recommended_jobs(self):
        skills = ["Python", "SQL", "Excel"]
        careers = [{"career": "Data Analyst", "score": 83}]
        jobs = get_recommended_jobs(skills=skills, careers=careers, limit=5)
        assert isinstance(jobs, list)
        if jobs:
            assert "match_score" in jobs[0]


class TestAuthRoutes:
    def test_register_get(self, client):
        r = client.get("/register")
        assert r.status_code == 200

    def test_login_get(self, client):
        r = client.get("/login")
        assert r.status_code == 200

    def test_register_post(self, client):
        import os
        uniq = os.urandom(3).hex()
        r = client.post("/register", data={
            "username": f"testuser_{uniq}",
            "email": f"test_{uniq}@test.com",
            "password": "secret123",
            "confirm_password": "secret123",
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_logout(self, client):
        # First register
        import os
        uniq = os.urandom(3).hex()
        client.post("/register", data={
            "username": f"loguser_{uniq}",
            "email": f"log_{uniq}@test.com",
            "password": "secret123",
            "confirm_password": "secret123",
        }, follow_redirects=True)

        # Then logout
        r = client.post("/logout", follow_redirects=True)
        assert r.status_code == 200


class TestMainRoutes:
    def test_home(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_jobs_page(self, client):
        r = client.get("/jobs")
        assert r.status_code == 200

    def test_job_details(self, client):
        r = client.get("/jobs/1")
        # May be 404 if job doesn't exist, but should not 500
        assert r.status_code in (200, 404)

    def test_analyze_flow(self, client):
        import io
        with open("app/static/uploads/test_resume.pdf", "rb") as f:
            pdf = f.read()
        r = client.post("/analyze", data={"resume": (io.BytesIO(pdf), "test.pdf")},
                        content_type="multipart/form-data")
        # Should redirect to results
        assert r.status_code in (200, 302)


class TestAdminRoutes:
    def test_admin_dashboard_requires_login(self, client):
        r = client.get("/admin/", follow_redirects=False)
        assert r.status_code == 302

    def test_admin_dashboard_after_login(self, authenticated_client):
        r = authenticated_client.get("/admin/")
        assert r.status_code == 200

    def test_admin_users_page(self, authenticated_client):
        r = authenticated_client.get("/admin/users")
        assert r.status_code == 200

    def test_admin_jobs(self, authenticated_client):
        r = authenticated_client.get("/admin/jobs")
        assert r.status_code == 200


class TestAlerts:
    def test_alerts_page(self, authenticated_client):
        r = authenticated_client.get("/alerts")
        assert r.status_code == 200

    def test_save_alert(self, authenticated_client):
        r = authenticated_client.post("/alerts", data={
            "email": "test@example.com",
            "groups": ["Information Technology"],
            "is_active": "on",
        }, follow_redirects=True)
        assert r.status_code == 200


class TestLanguageSwitching:
    def test_language_switch(self, client):
        r = client.get("/set-lang/si", follow_redirects=False)
        assert r.status_code == 302

    def test_sinhala_render(self, client):
        client.set_cookie("dc-lang", "si")
        r = client.get("/")
        html = r.get_data(as_text=True)
        assert "රැකියා බලන්න" in html

    def test_tamil_render(self, client):
        client.set_cookie("dc-lang", "ta")
        r = client.get("/")
        html = r.get_data(as_text=True)
        assert "வேலைவாய்ப்புகள்" in html


class TestFitCheck:
    def test_fit_page(self, client):
        r = client.get("/jobs/100/fit")
        assert r.status_code == 200

    def test_fit_analysis(self, client):
        import io
        with open("app/static/uploads/test_resume.pdf", "rb") as f:
            pdf = f.read()
        r = client.post("/analyze", data={
            "resume": (io.BytesIO(pdf), "fit.pdf"),
            "job_id": "100"
        }, content_type="multipart/form-data")
        if r.status_code == 302:
            r = client.get(r.headers["Location"])
        assert r.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])