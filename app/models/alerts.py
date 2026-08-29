from datetime import datetime, timezone

from app import db


class JobAlert(db.Model):
    __tablename__ = 'job_alerts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        unique=True,
        index=True
    )

    email = db.Column(db.String(200), nullable=False)

    field_groups = db.Column(db.Text)      # JSON list of category groups
    min_skill_overlap = db.Column(db.Integer, default=2)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    last_sent_at = db.Column(db.DateTime)

    user = db.relationship(
        "User",
        backref=db.backref(
            "job_alert",
            uselist=False,
            cascade="all, delete-orphan"
        )
    )

    def group_list(self):
        import json

        try:
            return json.loads(self.field_groups or "[]")
        except ValueError:
            return []

    def __repr__(self):
        return f"<JobAlert user={self.user_id} active={self.is_active}>"


class EmailOutbox(db.Model):
    """
    Stores every alert email produced. When SMTP credentials are
    configured emails are sent directly AND logged here; without
    SMTP this acts as a demo outbox so nothing is lost.
    """

    __tablename__ = 'email_outbox'

    id = db.Column(db.Integer, primary_key=True)

    to_email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)

    sent_ok = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
