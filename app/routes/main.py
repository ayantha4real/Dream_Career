import json
import os
import re
import uuid
from flask import session
from flask_session import Session
from werkzeug.utils import secure_filename

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    current_app,
    flash,
    redirect,
    url_for
)
from flask_login import current_user, login_required

from app import db
from app.models.analysis import AnalysisHistory

from app.services.resume_parser import extract_text_from_pdf
from app.services.skill_extractor import extract_skills
from app.services.career_matcher import match_careers
from app.services.ml_predictor import predict_career
from app.services.nlp_analyzer import analyze_resume_text, estimate_experience_years
from app.services.qualification_recommender import recommend_qualifications
from app.services.skill_demand import get_skill_demand
from app.services.jobs.job_database import (
    get_jobs,
    get_job,
    get_job_categories,
    get_recommended_jobs
)


main = Blueprint("main", __name__)


def _allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in {"pdf"}
    )


def _attach_personal_matches(jobs):
    """
    For logged-in users with a prior analysis, flag jobs whose
    description genuinely contains at least MIN_OVERLAP of the
    user's detected skills — not vague engine guesses.
    """

    if not current_user.is_authenticated:
        return jobs

    latest = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        AnalysisHistory.created_at.desc()
    ).first()

    if not latest or not latest.skill_list():
        return jobs

    user_skills = [
        skill for skill in latest.skill_list() if isinstance(skill, str)
    ]

    if len(user_skills) < 2:
        return jobs

    MIN_OVERLAP = 3

    for job in jobs:

        haystack = " ".join(
            part for part in [
                job["title"],
                job["description"] or ""
            ] if part
        ).lower()

        overlap = [
            skill for skill in user_skills
            if re.search(
                r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)",
                haystack
            )
        ]

        if len(overlap) >= min(MIN_OVERLAP, len(user_skills)):

            job["personal_match"] = True

            job["personal_overlap"] = overlap[:4]

    return jobs


@main.route("/set-lang/<lang_code>")
def set_lang(lang_code):

    from app.translations import LANGUAGES

    if lang_code not in LANGUAGES:
        lang_code = "en"

    next_url = request.args.get("next") or url_for("main.home")

    # /analyze only accepts POST; redirect to home instead
    if next_url and next_url.rstrip("/") == url_for("main.analyze").rstrip("/"):
        next_url = url_for("main.home")

    response = redirect(next_url)

    response.set_cookie(
        "dc-lang",
        lang_code,
        max_age=60 * 60 * 24 * 365
    )

    return response


@main.route("/")
def home():

    featured_jobs = [
        dict(job) for job in get_jobs(limit=6)
    ]

    demand = get_skill_demand(limit=10)

    return render_template(
        "index.html",
        jobs=featured_jobs,
        demand=demand
    )


@main.route("/history")
@login_required
def history():

    analyses = AnalysisHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        AnalysisHistory.created_at.desc()
    ).limit(30).all()

    return render_template(
        "history.html",
        analyses=analyses
    )


@main.route("/jobs")
def jobs_page():

    search = request.args.get("q", "").strip() or None

    category = request.args.get("category", "").strip() or None

    job_rows = [
        dict(job) for job in get_jobs(
            limit=60,
            search=search,
            category=category
        )
    ]

    jobs = _attach_personal_matches(job_rows)

    categories = get_job_categories()

    demand = get_skill_demand(limit=10)

    return render_template(
        "jobs.html",
        jobs=jobs,
        categories=categories,
        demand=demand,
        active_search=search or "",
        active_category=category or ""
    )


@main.route("/jobs/<int:job_id>")
def job_details(job_id):

    row = get_job(job_id)

    if not row:
        abort(404)

    job = dict(row)

    job["freshness"] = _humanize_age(job.get("scraped_at"))

    related_jobs = [
        dict(related)
        for related in get_jobs(limit=12)
        if related["id"] != job["id"]
    ][:3]

    return render_template(
        "job_details.html",
        job=job,
        related_jobs=related_jobs
    )


def _humanize_age(iso_string):
    """Turn a scraped_at ISO timestamp into '3 days ago' style text."""

    if not iso_string:
        return None

    from datetime import datetime

    try:
        scraped = datetime.fromisoformat(
            str(iso_string).replace("Z", "")
        )
    except ValueError:
        return None

    delta = datetime.now() - scraped.replace(tzinfo=None)

    days = delta.days
    hours = delta.seconds // 3600

    if days > 30:
        return "over a month ago"
    if days >= 1:
        return f"{days} day{'s' if days != 1 else ''} ago"
    if hours >= 1:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    return "recently"


@main.route("/jobs/<int:job_id>/fit")
@login_required
def check_fit(job_id):

    row = get_job(job_id)

    if not row:
        abort(404)

    return render_template(
        "fit.html",
        job=dict(row)
    )


@main.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():

    # GET: show the upload form
    if request.method == "GET":
        return render_template("analyze_form.html")

    # POST: process upload and store results in session
    file = request.files.get("resume")

    if not file or not file.filename:

        flash("Please select a resume file to analyze.", "error")

        return redirect(url_for("main.home"))

    if not _allowed_file(file.filename):

        flash("Only PDF resumes are supported.", "error")

        return redirect(url_for("main.home"))

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    safe_name = secure_filename(file.filename)

    stored_name = f"{uuid.uuid4().hex}_{safe_name}"

    filepath = os.path.join(upload_folder, stored_name)

    file.save(filepath)

    text = extract_text_from_pdf(filepath)

    skills = extract_skills(text)

    nlp_insights = analyze_resume_text(text)

    nlp_insights["estimated_experience_years"] = (
        estimate_experience_years(text)
    )

    careers = match_careers(skills)

    ml_result = predict_career(text)

    ml_predictions = ml_result["predictions"]

    shap_explanations = ml_result["explanations"]

    ml_confidence = ml_result["confidence"]

    ml_low_confidence = ml_result["low_confidence"]

    top_careers = careers[:3]

    recommended_jobs = get_recommended_jobs(
        skills=skills,
        careers=top_careers,
        limit=9
    )

    if len(recommended_jobs) < 6:

        seen_ids = {job["id"] for job in recommended_jobs}

        fallback_jobs = [
            job for job in get_jobs(limit=30)
            if job["id"] not in seen_ids
        ]

        for job in fallback_jobs:

            job = dict(job)

            job["match_score"] = None

            recommended_jobs.append(job)

    recommended_jobs = recommended_jobs[:9]

    qualification_skills = []

    if careers:

        qualification_skills = careers[0].get("missing", [])

    qualifications = recommend_qualifications(
        qualification_skills
    )

    # Optional per-job fit check ("Check your fit" flow)
    fit_job = None

    job_fit = None

    raw_job_id = request.form.get("job_id", "").strip()

    if raw_job_id.isdigit():

        target = get_job(int(raw_job_id))

        if target:

            fit_job = dict(target)

            job_text = " ".join(
                part for part in [
                    fit_job["title"],
                    fit_job["description"] or ""
                ] if part
            )

            job_required = extract_skills(job_text)

            user_set = set(skills)

            matched_required = [
                s for s in job_required if s in user_set
            ]

            missing_required = [
                s for s in job_required if s not in user_set
            ]

            coverage = round(
                len(matched_required) / len(job_required) * 100
            ) if job_required else 0

            verdict = (
                "Ready to apply"
                if coverage >= 70
                else (
                    "Almost there"
                    if coverage >= 40
                    else "Stretch role"
                )
            )

            job_fit = {
                "required_count": len(job_required),
                "matched": matched_required,
                "missing": missing_required[:8],
                "coverage": coverage,
                "verdict": verdict
            }

    if current_user.is_authenticated and (skills or careers):

        history_entry = AnalysisHistory(
            user_id=current_user.id,
            filename=safe_name,
            top_career=careers[0]["career"] if careers else None,
            top_skill_score=careers[0]["score"] if careers else 0,
            ml_confidence=ml_confidence,
            skills_json=json.dumps(skills)
        )

        db.session.add(history_entry)

        db.session.commit()

    # Store results in session for GET /results
    session["analysis_results"] = {
        "skills": skills,
        "careers": top_careers,
        "all_careers": careers,
        "nlp": nlp_insights,
        "ml_predictions": ml_predictions,
        "ml_confidence": ml_confidence,
        "ml_low_confidence": ml_low_confidence,
        "shap_explanations": shap_explanations,
        "qualifications": qualifications,
        "jobs": recommended_jobs,
        "resume_text": text,
        "fit_job": fit_job,
        "job_fit": job_fit
    }

    return redirect(url_for("main.results"))


@main.route("/results")
def results():
    """Display stored analysis results (GET). Allows language switching without losing results."""
    data = session.get("analysis_results")
    if not data:
        flash("No analysis found. Please upload a resume first.", "error")
        return redirect(url_for("main.home"))

    return render_template(
        "results.html",
        skills=data["skills"],
        careers=data["careers"],
        all_careers=data["all_careers"],
        nlp=data["nlp"],
        ml_predictions=data["ml_predictions"],
        ml_confidence=data["ml_confidence"],
        ml_low_confidence=data["ml_low_confidence"],
        shap_explanations=data["shap_explanations"],
        qualifications=data["qualifications"],
        jobs=data["jobs"],
        resume_text=data["resume_text"],
        fit_job=data.get("fit_job"),
        job_fit=data.get("job_fit")
    )
