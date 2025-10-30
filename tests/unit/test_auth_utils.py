import pytest
from datetime import datetime, timezone, timedelta
from utils.auth_utils import (
    generate_verification_token,
    validate_verification_token,
    create_refresh_token,
    validate_refresh_token,
    revoke_refresh_token
)
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken

class TestVerificationTokenUtils:
    """Test verification token utilities"""
    
    def test_generate_verification_token(self, app, db_session, sample_user):
        """Test generating a verification token"""
        with app.app_context():
            token = generate_verification_token(
                user_id=sample_user.id,
                token_type='email',
                expiration_hours=24
            )
            
            assert isinstance(token, str)
            assert len(token) > 0
            
            # VERIFY TOKEN WAS SAVED IN DATABASE
            token_record = VerificationToken.query.filter_by(token=token).first()
            assert token_record is not None
            assert token_record.user_id == sample_user.id
            assert token_record.token_type == 'email'
            assert token_record.expires_at > datetime.now(timezone.utc)
    
    def test_generate_token_invalidates_old_tokens(self, app, db_session, sample_user):
        """Test that generating new token invalidates old ones"""
        with app.app_context():
            # GENERATE FIRST TOKEN
            token1 = generate_verification_token(
                user_id=sample_user.id,
                token_type='email',
                expiration_hours=24
            )
            
            # GENERATE SECOND TOKEN
            token2 = generate_verification_token(
                user_id=sample_user.id,
                token_type='email',
                expiration_hours=24
            )
            
            # FIRST TOKEN SHOULD BE DELETED
            old_token = VerificationToken.query.filter_by(token=token1).first()
            assert old_token is None
            
            # SECOND TOKEN SHOULD EXIST
            new_token = VerificationToken.query.filter_by(token=token2).first()
            assert new_token is not None
    
    def test_generate_different_token_types_coexist(self, app, db_session, sample_user):
        """Test that different token types for same user can coexist"""
        with app.app_context():
            email_token = generate_verification_token(
                user_id=sample_user.id,
                token_type='email',
                expiration_hours=24
            )
            
            reset_token = generate_verification_token(
                user_id=sample_user.id,
                token_type='password_reset',
                expiration_hours=1
            )
            
            # BOTH TOKENS SHOULD EXIST
            email_record = VerificationToken.query.filter_by(token=email_token).first()
            reset_record = VerificationToken.query.filter_by(token=reset_token).first()
            
            assert email_record is not None
            assert reset_record is not None
    
    def test_validate_verification_token_valid(self, app, verification_token):
        """Test validating a valid verification token"""
        with app.app_context():
            user_id = validate_verification_token(
                verification_token.token,
                'email'
            )
            
            assert user_id == verification_token.user_id
            
            # TOKEN SHOULD BE DELETED AFTER USE
            token_record = VerificationToken.query.filter_by(
                token=verification_token.token
            ).first()
            assert token_record is None
    
    def test_validate_verification_token_expired(self, app, expired_verification_token):
        """Test validating an expired verification token"""
        with app.app_context():
            user_id = validate_verification_token(
                expired_verification_token.token,
                'email'
            )
            
            assert user_id is None
            
            # EXPIRED TOKEN SHOULD BE DELETED
            token_record = VerificationToken.query.filter_by(
                token=expired_verification_token.token
            ).first()
            assert token_record is None
    
    def test_validate_verification_token_wrong_type(self, app, verification_token):
        """Test validating token with wrong type"""
        with app.app_context():
            user_id = validate_verification_token(
                verification_token.token,
                'password_reset'  # WRONG TYPE
            )
            
            assert user_id is None
    
    def test_validate_verification_token_nonexistent(self, app):
        """Test validating non-existent token"""
        with app.app_context():
            user_id = validate_verification_token(
                'nonexistent-token-123',
                'email'
            )
            
            assert user_id is None

class TestRefreshTokenUtils:
    """Test refresh token utilities"""
    
    def test_create_refresh_token(self, app, db_session, sample_user):
        """Test creating a refresh token"""
        with app.app_context():
            token = create_refresh_token(
                user_id=sample_user.id,
                expires_seconds=3600,
                ip_address="192.168.1.1",
                user_agent="Test Browser"
            )
            
            assert isinstance(token, str)
            assert len(token) > 0
            
            # VERIFY TOKEN WAS SAVED IN DATABASE
            token_record = RefreshToken.query.filter_by(token=token).first()
            assert token_record is not None
            assert token_record.user_id == sample_user.id
            assert token_record.ip_address == "192.168.1.1"
            assert token_record.user_agent == "Test Browser"
            assert token_record.is_revoked is False
            assert token_record.expires_at > datetime.now(timezone.utc)
    
    def test_create_refresh_token_without_device_info(self, app, db_session, sample_user):
        """Test creating refresh token without device info"""
        with app.app_context():
            token = create_refresh_token(
                user_id=sample_user.id,
                expires_seconds=3600
            )
            
            token_record = RefreshToken.query.filter_by(token=token).first()
            assert token_record is not None
            assert token_record.ip_address is None
            assert token_record.user_agent is None
    
    def test_validate_refresh_token_valid(self, app, refresh_token):
        """Test validating a valid refresh token"""
        with app.app_context():
            is_valid, user_id = validate_refresh_token(refresh_token.token)
            
            assert is_valid is True
            assert user_id == refresh_token.user_id
    
    def test_validate_refresh_token_revoked(self, app, db_session, refresh_token):
        """Test validating a revoked refresh token"""
        with app.app_context():
            # REVOKE THE TOKEN PROPERLY
            token_to_revoke = RefreshToken.query.filter_by(token=refresh_token.token).first()
            token_to_revoke.is_revoked = True
            db_session.commit()
            
            # EXPIRE THE SESSION TO FORCE REFRESH FROM DB
            db_session.expire_all()
            
            is_valid, user_id = validate_refresh_token(refresh_token.token)
            
            assert is_valid is False
            assert user_id is None
    
    def test_validate_refresh_token_expired(self, app, db_session, sample_user):
        """Test validating an expired refresh token"""
        with app.app_context():
            # CREATE EXPIRED TOKEN
            expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
            expired_token = RefreshToken(
                token="expired-refresh-token",
                user_id=sample_user.id,
                expires_at=expires_at,
                is_revoked=False
            )
            db_session.add(expired_token)
            db_session.commit()
            
            is_valid, user_id = validate_refresh_token(expired_token.token)
            
            assert is_valid is False
            assert user_id is None
    
    def test_validate_refresh_token_nonexistent(self, app):
        """Test validating non-existent token"""
        with app.app_context():
            is_valid, user_id = validate_refresh_token('nonexistent-token')
            
            assert is_valid is False
            assert user_id is None
    
    def test_revoke_refresh_token(self, app, db_session, refresh_token):
        """Test revoking a refresh token"""
        with app.app_context():
            result = revoke_refresh_token(refresh_token.token)
            
            assert result is True
            
            # VERIFY TOKEN WAS REVOKED
            token_record = RefreshToken.query.filter_by(token=refresh_token.token).first()
            assert token_record.is_revoked is True
    
    def test_revoke_nonexistent_token(self, app):
        """Test revoking non-existent token"""
        with app.app_context():
            result = revoke_refresh_token('nonexistent-token')
            
            assert result is False
    
    def test_revoke_already_revoked_token(self, app, db_session, refresh_token):
        """Test revoking an already revoked token"""
        with app.app_context():
            # REVOKE ONCE
            revoke_refresh_token(refresh_token.token)
            
            # TRY TO REVOKE AGAIN
            result = revoke_refresh_token(refresh_token.token)
            
            assert result is True  # SHOULD STILL RETURN TRUE