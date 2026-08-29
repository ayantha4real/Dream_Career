"""
Alert email delivery.

Uses SMTP credentials from environment variables when available:

    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

Without configuration every message is recorded in the
EmailOutbox table (demo mode) so the feature remains fully
testable locally.
"""

import os
import smtplib
from email.mime.text import MIMEText

from flask import current_app

from app import db
from app.models.alerts import EmailOutbox


def _smtp_config():
    return {
        "host": os.environ.get("SMTP_HOST", ""),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
    }


def send_alert_email(to_email, subject, body):
    """
    Sends the email if SMTP is configured. Always stores it in
    the outbox. Returns True when actually sent via SMTP.
    """

    config = _smtp_config()

    sent_ok = False

    if config["host"] and config["user"]:

        try:

            message = MIMEText(body, "plain", "utf-8")

            message["Subject"] = subject

            message["From"] = "DreamCareer <{}>".format(config["user"])

            message["To"] = to_email

            with smtplib.SMTP(
                config["host"],
                config["port"],
                timeout=20
            ) as server:

                server.starttls()

                server.login(
                    config["user"],
                    config["password"]
                )

                server.send_message(message)

            sent_ok = True

        except Exception as exc:

            current_app.logger.warning(
                "SMTP send failed (%s): %s",
                to_email,
                exc
            )

    outbox_entry = EmailOutbox(
        to_email=to_email,
        subject=subject,
        body=body,
        sent_ok=sent_ok
    )

    db.session.add(outbox_entry)

    db.session.commit()

    return sent_ok


def build_digest_body(user, matched_jobs):
    """Plain-text digest of matched job listings."""

    lines = [
        f"Hi {user.username},",
        "",
        "New jobs matching your alert preferences:",
        "",
    ]

    for job in matched_jobs[:10]:

        lines.append(
            f"* {job['title']} — {job.get('company') or 'Company not specified'}"
        )

        lines.append(f"  {job.get('location') or 'Sri Lanka'}")

        lines.append(f"  {job['url'] or 'View on DreamCareer'}")

        lines.append("")

    lines.append(
        "Manage your alerts at http://localhost:5000/alerts"
    )

    lines.append("")
    lines.append("-- DreamCareer")

    return "\n".join(lines)
