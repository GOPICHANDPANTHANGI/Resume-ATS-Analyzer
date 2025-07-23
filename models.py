from app import db
from datetime import datetime
from sqlalchemy import Text

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    job_description = db.Column(Text, nullable=False)
    resume_text = db.Column(Text, nullable=False)
    keyword_score = db.Column(db.Float, nullable=False)
    grammar_score = db.Column(db.Float, nullable=False)
    format_score = db.Column(db.Float, nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    matching_keywords = db.Column(Text)  # JSON string
    missing_keywords = db.Column(Text)   # JSON string
    ai_suggestions = db.Column(Text)     # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Analysis {self.id}: {self.filename}>'
