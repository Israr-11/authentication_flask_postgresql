from datetime import datetime, timezone
from models.user_model import db

class RefreshToken(db.Model):
    """Model for storing refresh tokens"""
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)  # IPV6 CAN BE UP TO 45 CHARS
    user_agent = db.Column(db.String(255), nullable=True)
    is_revoked = db.Column(db.Boolean, default=False)
    # ADD timezone=True TO STORE TIMEZONE-AWARE DATETIMES
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f'<RefreshToken {self.id} for user {self.user_id}>'
    
    def is_expired(self):
        """Check if token has expired"""
        now = datetime.now(timezone.utc)
        return now > self.expires_at