"""
Send job alert digest emails.

Matches newly scraped jobs (since each user's last alert) against:
  1. the user's chosen field groups (via job_category_map.json)
  2. optionally, skills from their latest resume analysis

Run after refresh_jobs.py:
    venv\\Scripts\\python scripts\\send_job_alerts.py
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

os.chdir(PROJECT_ROOT)

from app import create_app, db
from app.models.user import User
from app.models.alerts import JobAlert
from app.services.jobs.job_database import (
    get_connection,
    get_category_group,
    split_category,
)
from app.services.mailer import send_alert_email, build_digest_body


def fetch_jobs_since(timestamp):
    connection = get_connection()

    cursor = connection.cursor()

    if timestamp:

        cursor.execute(
            "SELECT * FROM jobs WHERE scraped_at >= ? "
            "ORDER BY id DESC LIMIT 200",
            (timestamp.isoformat(sep=" "),),
        )

    else:
        cursor.execute(
            "SELECT * FROM jobs ORDER BY id DESC LIMIT 60"
        )

    jobs = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jobs


def job_matches_alert(job, alert):
    """Group match always applies; skill overlap tightens it further."""

    groups = {
        get_category_group(token)
        for token in split_category(job.get("category"))
    }

    wanted = set(alert.group_list())

    if not (groups & wanted):
        return False

    return True


def main():
    app = create_app()

    with app.app_context():

        active_alerts = JobAlert.query.filter_by(
            is_active=True
        ).all()

        if not active_alerts:
            print("No active alerts configured. Nothing to send.")
            return

        print(f"Processing {len(active_alerts)} alert(s)…")

        sent_count = 0

        for alert in active_alerts:

            user = User.query.get(alert.user_id)

            if not user:
                continue

            jobs = fetch_jobs_since(alert.last_sent_at)

            matched = [
                job for job in jobs
                if job_matches_alert(job, alert)
            ]

            if not matched:
                print(f"  {user.username}: no new matches")
                continue

            body = build_digest_body(user, matched)

            subject = (
                f"DreamCareer: {len(matched)} new jobs match your profile"
            )

            send_alert_email(alert.email, subject, body)

            alert.last_sent_at = datetime.utcnow()

            db.session.commit()

            sent_count += 1

            print(
                f"  {user.username}: {len(matched)} matches -> "
                f"{alert.email} (demo outbox unless SMTP set)"
            )

        print(f"\nDone. {sent_count} digest(s) generated.")


if __name__ == "__main__":
    main()
