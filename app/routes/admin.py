from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.analysis import AnalysisHistory
from app.models.alerts import JobAlert, EmailOutbox
from app.services.jobs.job_database import get_jobs, get_job
import json
from datetime import datetime, timedelta

admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access the admin panel.", "error")
            return redirect(url_for("auth.login"))
        if not getattr(current_user, "is_admin", False):
            flash("Admin access required.", "error")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function


@admin.route("/")
@login_required
@admin_required
def dashboard():
    # Stats
    total_users = User.query.count()
    total_analyses = AnalysisHistory.query.count()
    total_jobs = get_jobs(limit=10000).__len__()
    active_alerts = JobAlert.query.filter_by(is_active=True).count()

    # Recent analyses
    recent_analyses = AnalysisHistory.query.order_by(
        AnalysisHistory.created_at.desc()
    ).limit(10).all()

    # User growth (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = User.query.filter(User.id > 0).count()  # placeholder

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_analyses=total_analyses,
        total_jobs=total_jobs,
        active_alerts=active_alerts,
        recent_analyses=recent_analyses,
        new_users_30d=new_users,
    )


@admin.route("/users")
@login_required
@admin_required
def users():
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/users.html", users=users)


@admin.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "error")
        return redirect(url_for("admin.users"))
    user.is_admin = not getattr(user, "is_admin", False)
    db.session.commit()
    flash(f"Admin status updated for {user.username}.", "success")
    return redirect(url_for("admin.users"))


@admin.route("/jobs")
@login_required
@admin_required
def jobs():
    page = request.args.get("page", 1, type=int)
    jobs_raw = get_jobs(limit=10000)
    # Simple pagination
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    jobs_paginated = jobs_raw[start:end]
    total = len(jobs_raw)
    pages = (total + per_page - 1) // per_page
    return render_template(
        "admin/jobs.html",
        jobs=jobs_paginated,
        page=page,
        pages=pages,
        total=total,
    )


@admin.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_job(job_id):
    from app.services.jobs.job_database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    flash("Job deleted.", "success")
    return redirect(url_for("admin.jobs"))


@admin.route("/analytics")
@login_required
@admin_required
def analytics():
    # Category distribution
    from app.services.jobs.job_database import get_job_categories
    categories = get_job_categories()

    # Analysis trends (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    analyses = AnalysisHistory.query.filter(
        AnalysisHistory.created_at >= thirty_days_ago
    ).all()

    # Top careers
    career_counts = {}
    for a in analyses:
        if a.top_career:
            career_counts[a.top_career] = career_counts.get(a.top_career, 0) + 1
    top_careers = sorted(career_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Alert stats
    total_alerts = JobAlert.query.count()
    active_alerts = JobAlert.query.filter_by(is_active=True).count()
    emails_sent = EmailOutbox.query.filter_by(sent_ok=True).count()
    emails_failed = EmailOutbox.query.filter_by(sent_ok=False).count()

    return render_template(
        "admin/analytics.html",
        categories=categories,
        top_careers=top_careers,
        total_analyses=len(analyses),
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        emails_sent=emails_sent,
        emails_failed=emails_failed,
    )


@admin.route("/dataset")
@login_required
@admin_required
def dataset():
    from app.services.jobs.job_database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    # Source breakdown
    cursor.execute("SELECT source, COUNT(*) FROM jobs GROUP BY source")
    source_stats = cursor.fetchall()

    # Category breakdown
    from app.services.jobs.job_database import get_job_categories
    categories = get_job_categories()

    conn.close()

    return render_template(
        "admin/dataset.html",
        source_stats=source_stats,
        categories=categories,
    )


@admin.route("/outbox")
@login_required
@admin_required
def outbox():
    page = request.args.get("page", 1, type=int)
    entries = EmailOutbox.query.order_by(
        EmailOutbox.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/outbox.html", entries=entries)