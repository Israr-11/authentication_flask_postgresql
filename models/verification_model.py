from datetime import datetime, timezone, timedelta
import secrets
from models.user_model import db

class VerificationToken(db.Model):
    """
    Model for email verification and password reset tokens
    """
    __tablename__ = 'verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'email' or 'password_reset'
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def generate_token(cls, user_id, token_type, expiry_hours=24):
        """Generate a new verification token"""
        # CREATE A SECURE RANDOM TOKEN
        token = secrets.token_urlsafe(32)
        
        # SET EXPIRY TIME
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        # CREATE AND SAVE THE TOKEN
        verification_token = cls(
            user_id=user_id,
            token=token,
            type=token_type,
            expires_at=expires_at
        )
        
        db.session.add(verification_token)
        db.session.commit()
        
        return verification_token
    
    def is_valid(self):
        """Check if token is still valid"""
        return datetime.now(timezone.utc) < self.expires_at
    
    def use_token(self):
        """Invalidate token after use by deleting it"""
        db.session.delete(self)
        db.session.commit()