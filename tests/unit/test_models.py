import pytest
from datetime import datetime, timezone, timedelta
from models.user_model import User
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken
from utils.user_utils import hash_password
from sqlalchemy.exc import IntegrityError

class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            name="New User",
            email="newuser@example.com",
            role="user",
            is_verified=False,
            password_hash=hash_password("Password123!")
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.name == "New User"
        assert user.email == "newuser@example.com"
        assert user.role == "user"
        assert user.is_verified is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_default_role(self, db_session):
        """Test that default role is 'user'"""
        user = User(
            name="Test User",
            email="defaultrole@example.com",
            is_verified=False,
            password_hash=hash_password("Password123!")
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.role == "user"
    
    def test_user_default_not_verified(self, db_session):
        """Test that default is_verified is False"""
        user = User(
            name="Test User",
            email="notverified@example.com",
            role="user",
            password_hash=hash_password("Password123!")
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.is_verified is False
    
    def test_user_repr(self, sample_user):
        """Test user string representation"""
        assert repr(sample_user) == f'<User {sample_user.email}>'
    
    def test_user_to_dict(self, sample_user):
        """Test user to_dict method"""
        user_dict = sample_user.to_dict()
        
        assert user_dict['id'] == sample_user.id
        assert user_dict['name'] == sample_user.name
        assert user_dict['email'] == sample_user.email
        assert user_dict['role'] == sample_user.role
        assert user_dict['is_verified'] == sample_user.is_verified
        assert 'created_at' in user_dict
        assert 'password_hash' not in user_dict  # PASSWORD SHOULD NOT BE EXPOSED
    
    def test_user_unique_email(self, db_session, sample_user):
        """Test that email must be unique"""
        duplicate_user = User(
            name="Duplicate",
            email=sample_user.email,  # SAME EMAIL
            role="user",
            is_verified=False,
            password_hash=hash_password("Password123!")
        )
        
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_updated_at_changes(self, db_session, sample_user):
        """Test that updated_at changes when user is modified"""
        original_updated_at = sample_user.updated_at
        
        # MODIFY USER
        sample_user.name = "Updated Name"
        db_session.commit()
        
        assert sample_user.updated_at > original_updated_at

class TestVerificationTokenModel:
    """Test VerificationToken model"""
    
    def test_create_verification_token(self, db_session, sample_user):
        """Test creating a verification token"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        token = VerificationToken(
            user_id=sample_user.id,
            token="test-token-abc123",
            token_type="email",
            expires_at=expires_at
        )
        
        db_session.add(token)
        db_session.commit()
        
        assert token.id is not None
        assert token.user_id == sample_user.id
        assert token.token == "test-token-abc123"
        assert token.token_type == "email"
        assert token.expires_at == expires_at
        assert token.created_at is not None
    
    def test_verification_token_types(self, db_session, sample_user):
        """Test different verification token types"""
        email_token = VerificationToken(
            user_id=sample_user.id,
            token="email-token",
            token_type="email",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        
        reset_token = VerificationToken(
            user_id=sample_user.id,
            token="reset-token",
            token_type="password_reset",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        db_session.add(email_token)
        db_session.add(reset_token)
        db_session.commit()
        
        assert email_token.token_type == "email"
        assert reset_token.token_type == "password_reset"
    
    def test_verification_token_unique(self, db_session, sample_user):
        """Test that token must be unique"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        token1 = VerificationToken(
            user_id=sample_user.id,
            token="duplicate-token",
            token_type="email",
            expires_at=expires_at
        )
        
        token2 = VerificationToken(
            user_id=sample_user.id,
            token="duplicate-token",
            token_type="email",
            expires_at=expires_at
        )
        
        db_session.add(token1)
        db_session.commit()
        
        db_session.add(token2)
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestRefreshTokenModel:
    """Test RefreshToken model"""
    
    def test_create_refresh_token(self, db_session, sample_user):
        """Test creating a refresh token"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        token = RefreshToken(
            token="test-refresh-token-xyz",
            user_id=sample_user.id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            expires_at=expires_at,
            is_revoked=False
        )
        
        db_session.add(token)
        db_session.commit()
        
        assert token.id is not None
        assert token.user_id == sample_user.id
        assert token.ip_address == "192.168.1.1"
        assert token.user_agent == "Mozilla/5.0"
        assert token.is_revoked is False
        assert token.created_at is not None
    
    def test_refresh_token_default_not_revoked(self, db_session, sample_user):
        """Test that default is_revoked is False"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        token = RefreshToken(
            token="test-token",
            user_id=sample_user.id,
            expires_at=expires_at
        )
        
        db_session.add(token)
        db_session.commit()
        
        assert token.is_revoked is False
    
    def test_refresh_token_unique(self, db_session, sample_user):
        """Test that refresh token must be unique"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        
        token1 = RefreshToken(
            token="duplicate-refresh",
            user_id=sample_user.id,
            expires_at=expires_at
        )
        
        token2 = RefreshToken(
            token="duplicate-refresh",
            user_id=sample_user.id,
            expires_at=expires_at
        )
        
        db_session.add(token1)
        db_session.commit()
        
        db_session.add(token2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_refresh_token_revocation(self, db_session, sample_user):
        """Test revoking a refresh token"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        token = RefreshToken(
            token="revoke-test-token",
            user_id=sample_user.id,
            expires_at=expires_at,
            is_revoked=False
        )
        
        db_session.add(token)
        db_session.commit()
        
        # REVOKE TOKEN
        token.is_revoked = True
        db_session.commit()
        
        assert token.is_revoked is True
    
    def test_multiple_refresh_tokens_per_user(self, db_session, sample_user):
        """Test that a user can have multiple refresh tokens"""
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        
        token1 = RefreshToken(
            token="token-1",
            user_id=sample_user.id,
            ip_address="192.168.1.1",
            expires_at=expires_at
        )
        
        token2 = RefreshToken(
            token="token-2",
            user_id=sample_user.id,
            ip_address="192.168.1.2",
            expires_at=expires_at
        )
        
        db_session.add(token1)
        db_session.add(token2)
        db_session.commit()
        
        user_tokens = RefreshToken.query.filter_by(user_id=sample_user.id).all()
        assert len(user_tokens) >= 2