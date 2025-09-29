from datetime import datetime, timezone
from models.user_model import db
import uuid

class RefreshToken(db.Model):
    """Model for storing refresh tokens"""
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)  # IPV6 CAN BE UP TO 45 CHARS
    user_agent = db.Column(db.String(255), nullable=True)
    is_revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    
    @staticmethod
    def generate_token():
        """Generate a unique token string"""
        return str(uuid.uuid4())
    
    @staticmethod
    def is_valid(token):
        """Check if a token is valid and not revoked"""
        token_record = RefreshToken.query.filter_by(token=token).first()
        
        if not token_record:
            return False, None
            
        if token_record.is_revoked:
            return False, None
            
        if token_record.expires_at < datetime.now(timezone.utc):
            return False, None
            
        return True, token_record.user_id
    
    @staticmethod
    def revoke(token):
        """Revoke a refresh token"""
        token_record = RefreshToken.query.filter_by(token=token).first()
        
        if token_record:
            token_record.is_revoked = True
            db.session.commit()