from datetime import datetime
from app import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Add sentiment scores
    sentiment_pos = db.Column(db.Float, default=0.0)
    sentiment_neg = db.Column(db.Float, default=0.0)
    sentiment_neu = db.Column(db.Float, default=0.0)
    sentiment_compound = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"