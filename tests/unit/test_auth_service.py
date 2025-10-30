import pytest
from unittest.mock import Mock, patch, MagicMock
from services.auth_service import AuthService
from models.user_model import User
from models.refresh_token_model import RefreshToken

class TestAuthServiceRegistration:
    """Test AuthService registration functionality"""
    
    def test_register_user_success(self, app, db_session):
        """Test successful user registration"""
        with app.app_context():
            auth_service = AuthService()
            
            with patch.object(auth_service, '_get_email_service') as mock_email:
                mock_email.return_value.send_verification_email = Mock()
                
                user, error = auth_service.register_user(
                    name="Test User",
                    email="newuser@test.com",
                    password="Password123!"
                )
                
                assert user is not None
                assert error is None
                assert user.email == "newuser@test.com"
                assert user.is_verified is False
                
                # VERIFY EMAIL WAS CALLED
                mock_email.return_value.send_verification_email.assert_called_once()
    
    def test_register_duplicate_email(self, app, db_session, sample_user):
        """Test registering with duplicate email"""
        with app.app_context():
            auth_service = AuthService()
            
            user, error = auth_service.register_user(
                name="Another User",
                email=sample_user.email,  # DUPLICATE
                password="Password123!"
            )
            
            assert user is None
            assert error == "Email already registered"
    
    def test_register_invalid_email(self, app, db_session):
        """Test registration with invalid email format"""
        with app.app_context():
            auth_service = AuthService()
            
            user, error = auth_service.register_user(
                name="Test User",
                email="invalid-email",  # NO @ OR DOMAIN
                password="Password123!"
            )
            
            assert user is None
            assert "Invalid email" in error
    
    def test_register_weak_password(self, app, db_session):
        """Test registration with weak password"""
        with app.app_context():
            auth_service = AuthService()
            
            user, error = auth_service.register_user(
                name="Test User",
                email="test@example.com",
                password="weak"  # TOO WEAK
            )
            
            assert user is None
            assert error is not None
    
    def test_register_email_failure_still_creates_user(self, app, db_session):
        """Test that user is created even if email fails"""
        with app.app_context():
            auth_service = AuthService()
            
            with patch.object(auth_service, '_get_email_service') as mock_email:
                mock_email.return_value.send_verification_email.side_effect = Exception("Email failed")
                
                user, error = auth_service.register_user(
                    name="Test User",
                    email="newuser@test.com",
                    password="Password123!"
                )
                
                # USER SHOULD STILL BE CREATED
                assert user is not None
                assert error is None

class TestAuthServiceEmailVerification:
    """Test AuthService email verification"""
    
    def test_verify_email_success(self, app, db_session, verification_token, unverified_user):
        """Test successful email verification"""
        with app.app_context():
            auth_service = AuthService()
            
            success, message = auth_service.verify_email(verification_token.token)
            
            assert success is True
            assert "verified successfully" in message.lower()
            
            # USER SHOULD NOW BE VERIFIED
            user = User.query.get(unverified_user.id)
            assert user.is_verified is True
    
    def test_verify_email_invalid_token(self, app, db_session):
        """Test verification with invalid token"""
        with app.app_context():
            auth_service = AuthService()
            
            success, message = auth_service.verify_email("invalid-token")
            
            assert success is False
            assert "invalid" in message.lower() or "expired" in message.lower()
    
    def test_verify_email_expired_token(self, app, db_session, expired_verification_token):
        """Test verification with expired token"""
        with app.app_context():
            auth_service = AuthService()
            
            success, message = auth_service.verify_email(expired_verification_token.token)
            
            assert success is False
            assert "expired" in message.lower() or "invalid" in message.lower()

class TestAuthServiceAuthentication:
    """Test AuthService authentication"""
    
    def test_authenticate_success(self, app, db_session, sample_user):
        """Test successful authentication"""
        with app.app_context():
            auth_service = AuthService()
            
            result, error = auth_service.authenticate_user(
                email=sample_user.email,
                password="Password123!",
                request_info={"ip": "127.0.0.1", "device": "Test Browser"}
            )
            
            assert result is not None
            assert error is None
            assert "access_token" in result
            assert "refresh_token" in result
            assert "user" in result
    
    def test_authenticate_wrong_password(self, app, db_session, sample_user):
        """Test authentication with wrong password"""
        with app.app_context():
            auth_service = AuthService()
            
            result, error = auth_service.authenticate_user(
                email=sample_user.email,
                password="WrongPassword123!",
                request_info=None
            )
            
            assert result is None
            assert "Invalid email or password" in error
    
    def test_authenticate_nonexistent_user(self, app, db_session):
        """Test authentication with non-existent user"""
        with app.app_context():
            auth_service = AuthService()
            
            result, error = auth_service.authenticate_user(
                email="nonexistent@example.com",
                password="Password123!",
                request_info=None
            )
            
            assert result is None
            assert "Invalid email or password" in error
    
    def test_authenticate_unverified_user(self, app, db_session, unverified_user):
        """Test authentication with unverified user"""
        with app.app_context():
            auth_service = AuthService()
            
            result, error = auth_service.authenticate_user(
                email=unverified_user.email,
                password="Password123!",
                request_info=None
            )
            
            assert result is None
            assert "verify your email" in error.lower()

class TestAuthServiceTokenRefresh:
    """Test AuthService token refresh"""
    
    def test_refresh_token_success(self, app, db_session, refresh_token, sample_user):
        """Test successful token refresh"""
        with app.app_context():
            auth_service = AuthService()
            
            result, error = auth_service.refresh_access_token(refresh_token.token)
            
            assert result is not None
            assert error is None
            assert "access_token" in result
    
    def test_refresh_invalid_token(self, app, db_session):
        """Test refresh with invalid token"""
        with app.app_context():
            auth_service = AuthService()
            
            result, error = auth_service.refresh_access_token("invalid-token")
            
            assert result is None
            assert "Invalid or expired" in error

class TestAuthServicePasswordReset:
    """Test AuthService password reset"""
    
    def test_request_password_reset_success(self, app, db_session, sample_user):
        """Test successful password reset request"""
        with app.app_context():
            auth_service = AuthService()
            
            with patch.object(auth_service, '_get_email_service') as mock_email:
                mock_email.return_value.send_password_reset_email = Mock()
                
                success, error = auth_service.request_password_reset(sample_user.email)
                
                assert success is True
                assert error is None
                mock_email.return_value.send_password_reset_email.assert_called_once()
    
    def test_request_password_reset_nonexistent_email(self, app, db_session):
        """Test password reset for non-existent email"""
        with app.app_context():
            auth_service = AuthService()
            
            success, error = auth_service.request_password_reset("nonexistent@example.com")
            
            # SHOULD NOT REVEAL IF EMAIL EXISTS
            assert success is True
            assert error is None
    
    def test_reset_password_success(self, app, db_session, reset_token, sample_user):
        """Test successful password reset"""
        with app.app_context():
            auth_service = AuthService()
            
            new_password = "NewPassword123!"
            success, message = auth_service.reset_password(reset_token.token, new_password)
            
            assert success is True
            
            # ALL REFRESH TOKENS SHOULD BE REVOKED
            tokens = RefreshToken.query.filter_by(user_id=sample_user.id).all()
            for token in tokens:
                assert token.is_revoked is True
    
    def test_reset_password_invalid_token(self, app, db_session):
        """Test password reset with invalid token"""
        with app.app_context():
            auth_service = AuthService()
            
            success, message = auth_service.reset_password("invalid-token", "NewPassword123!")
            
            assert success is False
            assert "invalid" in message.lower() or "expired" in message.lower()
    
    def test_reset_password_weak_password(self, app, db_session, reset_token):
        """Test password reset with weak password"""
        with app.app_context():
            auth_service = AuthService()
            
            success, message = auth_service.reset_password(reset_token.token, "weak")
            
            assert success is False
            assert message is not None

class TestAuthServiceLogout:
    """Test AuthService logout"""
    
    def test_logout_success(self, app, db_session, refresh_token):
        """Test successful logout"""
        with app.app_context():
            auth_service = AuthService()
            
            result = auth_service.logout(refresh_token.token)
            
            assert result is True
            
            # TOKEN SHOULD BE REVOKED
            token_record = RefreshToken.query.filter_by(token=refresh_token.token).first()
            assert token_record.is_revoked is True
    
    def test_logout_no_token(self, app, db_session):
        """Test logout without token"""
        with app.app_context():
            auth_service = AuthService()
            
            result = auth_service.logout(None)
            
            assert result is True