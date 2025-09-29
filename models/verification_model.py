from datetime import datetime, timedelta, timezone
from models.user_model import db
import secrets

class VerificationToken(db.Model):
    """Model for email verification and password reset tokens"""
    __tablename__ = 'verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    token_type = db.Column(db.String(20), nullable=False)  # 'email' or 'password_reset'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    
    @staticmethod
    def generate_token(user_id, token_type, expiration_hours=24):
        """Generate a new verification token"""
        # INVALIDATE ANY EXISTING TOKENS OF SAME TYPE FOR THIS USER
        VerificationToken.query.filter_by(
            user_id=user_id, token_type=token_type
        ).delete()
        
        # CREATE NEW TOKEN
        token = secrets.token_urlsafe(32)  # GENERATE SECURE RANDOM TOKEN
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
        
        new_token = VerificationToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
        
        db.session.add(new_token)
        db.session.commit()
        
        return token
    
    @staticmethod
    def validate_token(token, token_type):
        """Validate a token and return the associated user ID if valid"""
        token_record = VerificationToken.query.filter_by(
            token=token, 
            token_type=token_type
        ).first()
        
        # CHECK IF TOKEN EXISTS AND IS NOT EXPIRED
        if not token_record or token_record.expires_at < datetime.now(timezone.utc):
            return None
            
        user_id = token_record.user_id
        
        # DELETE THE USED TOKEN (ONE-TIME USE)
        db.session.delete(token_record)
        db.session.commit()
        
        return user_id