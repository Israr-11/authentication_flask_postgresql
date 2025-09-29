from datetime import datetime, timezone, timedelta
from models.user_model import db

class RefreshToken(db.Model):
    """
    Model for storing refresh tokens
    """
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # STORE DEVICE INFORMATION FOR BETTER SECURITY
    device_info = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    
    def is_valid(self):
        """Check if the token is still valid based on expiry time"""
        return datetime.now(timezone.utc) < self.expires_at
    
    def invalidate(self):
        """Invalidate token by setting expiry to now"""
        self.expires_at = datetime.now(timezone.utc)
        db.session.commit()