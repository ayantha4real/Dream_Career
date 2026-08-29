import json

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required, current_user

from app import db
from app.models.alerts import JobAlert, EmailOutbox
from app.services.jobs.job_database import load_category_mapping


alerts = Blueprint("alerts", __name__)


@alerts.route("/alerts", methods=["GET"])
@login_required
def alerts_page():

    existing = JobAlert.query.filter_by(
        user_id=current_user.id
    ).first()

    mapping = load_category_mapping()

    groups = sorted(mapping["groups"].keys())

    selected = existing.group_list() if existing else []

    return render_template(
        "alerts.html",
        groups=groups,
        alert=existing,
        selected=selected
    )


@alerts.route("/alerts", methods=["POST"])
@login_required
def save_alert():

    email = request.form.get("email", "").strip().lower()

    if not email or "@" not in email:
        flash("Please provide a valid email address.", "error")

        return redirect(url_for("alerts.alerts_page"))

    selected_groups = request.form.getlist("groups")

    if not selected_groups:
        flash("Select at least one job field to watch.", "error")

        return redirect(url_for("alerts.alerts_page"))

    # Sensible default — kept out of the UI to stay simple.
    min_overlap = 3

    is_active = request.form.get("is_active") == "on"

    existing = JobAlert.query.filter_by(
        user_id=current_user.id
    ).first()

    if existing:

        existing.email = email
        existing.field_groups = json.dumps(selected_groups)
        existing.min_skill_overlap = min_overlap
        existing.is_active = is_active

        message = "Alert preferences updated."

    else:

        existing = JobAlert(
            user_id=current_user.id,
            email=email,
            field_groups=json.dumps(selected_groups),
            min_skill_overlap=min_overlap,
            is_active=is_active
        )

        db.session.add(existing)

        message = "Job alert created! You'll be emailed about new matches."

    db.session.commit()

    flash(message, "success")

    return redirect(url_for("alerts.alerts_page"))


@alerts.route("/alerts/outbox")
@login_required
def outbox():

    entries = EmailOutbox.query.filter_by(
        to_email=current_user.email
    ).order_by(
        EmailOutbox.created_at.desc()
    ).limit(20).all()

    return render_template(
        "outbox.html",
        entries=entries
    )
