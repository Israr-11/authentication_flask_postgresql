from datetime import datetime, timezone
from models.user_model import db

class VerificationToken(db.Model):
    """Model for email verification and password reset tokens"""
    __tablename__ = 'verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    token_type = db.Column(db.String(20), nullable=False)  # 'email' or 'password_reset'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<VerificationToken {self.token_type} for user {self.user_id}>'