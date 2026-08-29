from datetime import datetime, timezone

from app import db


class AnalysisHistory(db.Model):
    __tablename__ = 'analysis_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    filename = db.Column(db.String(260))
    top_career = db.Column(db.String(120))
    top_skill_score = db.Column(db.Integer)

    ml_confidence = db.Column(db.Float)
    skills_json = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "analyses",
            cascade="all, delete-orphan"
        )
    )

    def skill_list(self):
        import json

        try:
            return json.loads(self.skills_json or "[]")
        except ValueError:
            return []

    def __repr__(self):
        return f"<AnalysisHistory {self.id} user={self.user_id} {self.top_career}>"
