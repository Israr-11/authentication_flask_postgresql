from datetime import datetime, timezone, timedelta
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken
from models.user_model import db
import secrets
import uuid

# VERIFICATION TOKEN UTILITIES
def generate_verification_token(user_id, token_type, expiration_hours=24):
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

def validate_verification_token(token, token_type):
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

# REFRESH TOKEN UTILITIES
def generate_refresh_token():
    """Generate a unique token string"""
    return str(uuid.uuid4())

def create_refresh_token(user_id, expires_seconds=2592000, ip_address=None, user_agent=None):
    """Create and store refresh token"""
    # GENERATE TOKEN
    token_str = generate_refresh_token()
    
    # SET EXPIRATION (DEFAULT 30 DAYS)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    
    # CREATE TOKEN RECORD
    token = RefreshToken(
        token=token_str,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at
    )
    
    db.session.add(token)
    db.session.commit()
    
    return token_str

def validate_refresh_token(token):
    """Check if a token is valid and not revoked"""
    token_record = RefreshToken.query.filter_by(token=token).first()
    
    if not token_record:
        return False, None
        
    if token_record.is_revoked:
        return False, None
        
    if token_record.expires_at < datetime.now(timezone.utc):
        return False, None
        
    return True, token_record.user_id

def revoke_refresh_token(token):
    """Revoke a refresh token"""
    token_record = RefreshToken.query.filter_by(token=token).first()
    
    if token_record:
        token_record.is_revoked = True
        db.session.commit()
        return True
    return False