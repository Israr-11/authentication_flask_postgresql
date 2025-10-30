from datetime import datetime, timezone
from models.user_model import db

class VerificationToken(db.Model):
    """Model for email verification and password reset tokens"""
    __tablename__ = 'verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    token_type = db.Column(db.String(20), nullable=False)  # 'email' or 'password_reset'
    # ADD timezone=True TO STORE TIMEZONE-AWARE DATETIMES
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<VerificationToken {self.token_type} for user {self.user_id}>'
    
    def is_expired(self):
        """Check if token has expired"""
        now = datetime.now(timezone.utc)
        return now > self.expires_at