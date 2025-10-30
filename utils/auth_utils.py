from datetime import datetime, timezone, timedelta
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken
from models.user_model import db
import secrets

def generate_verification_token(user_id, token_type, expiration_hours=24):
    """
    Generate a verification token for email verification or password reset
    
    Args:
        user_id: The user's ID
        token_type: 'email' or 'password_reset'
        expiration_hours: Hours until token expires
    
    Returns:
        str: The generated token
    """
    # DELETE OLD TOKENS OF SAME TYPE FOR THIS USER
    VerificationToken.query.filter_by(
        user_id=user_id,
        token_type=token_type
    ).delete()
    
    # GENERATE NEW TOKEN
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
    
    # SAVE TO DATABASE
    verification_token = VerificationToken(
        user_id=user_id,
        token=token,
        token_type=token_type,
        expires_at=expires_at
    )
    db.session.add(verification_token)
    db.session.commit()
    
    return token

def validate_verification_token(token, expected_type):
    """
    Validate a verification token
    
    Args:
        token: The token to validate
        expected_type: 'email' or 'password_reset'
    
    Returns:
        int or None: User ID if valid, None if invalid
    """
    token_record = VerificationToken.query.filter_by(token=token).first()
    
    # CHECK IF TOKEN EXISTS
    if not token_record:
        return None
    
    # CHECK IF EXPIRED - DELETE IF EXPIRED
    if token_record.expires_at < datetime.now(timezone.utc):
        db.session.delete(token_record)
        db.session.commit()
        return None
    
    # CHECK IF TOKEN TYPE MATCHES
    if token_record.token_type != expected_type:
        return None
    
    # TOKEN IS VALID - GET USER ID AND DELETE TOKEN (ONE-TIME USE)
    user_id = token_record.user_id
    db.session.delete(token_record)
    db.session.commit()
    
    return user_id

def create_refresh_token(user_id, expires_seconds=2592000, ip_address=None, user_agent=None):
    """
    Create a refresh token for a user
    
    Args:
        user_id: The user's ID
        expires_seconds: Seconds until token expires (default 30 days)
        ip_address: IP address of the request
        user_agent: User agent string
    
    Returns:
        str: The generated refresh token
    """
    # GENERATE TOKEN
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    
    # SAVE TO DATABASE
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        is_revoked=False
    )
    db.session.add(refresh_token)
    db.session.commit()
    
    return token

def validate_refresh_token(token_str):
    """
    Validate a refresh token
    
    Args:
        token_str: The refresh token to validate
    
    Returns:
        tuple: (is_valid: bool, user_id: int or None)
    """
    token_record = RefreshToken.query.filter_by(token=token_str).first()
    
    # CHECK IF TOKEN EXISTS
    if not token_record:
        return False, None
    
    # CHECK IF REVOKED
    if token_record.is_revoked:
        return False, None
    
    # CHECK IF EXPIRED
    if token_record.expires_at < datetime.now(timezone.utc):
        return False, None
    
    # TOKEN IS VALID
    return True, token_record.user_id

def revoke_refresh_token(token_str):
    """
    Revoke a refresh token
    
    Args:
        token_str: The refresh token to revoke
    
    Returns:
        bool: True if token was revoked, False if token not found
    """
    token_record = RefreshToken.query.filter_by(token=token_str).first()
    
    if not token_record:
        return False
    
    # MARK AS REVOKED
    token_record.is_revoked = True
    db.session.commit()
    
    return True