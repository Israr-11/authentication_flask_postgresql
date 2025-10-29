import pytest
from app import create_app
from models.user_model import db, User
from models.verification_model import VerificationToken
from models.refresh_token_model import RefreshToken
from configuration.test_config import TestConfig
from utils.user_utils import hash_password
from datetime import datetime, timezone, timedelta

@pytest.fixture(scope='session')
def app():
    """Create and configure a test app instance for entire test session"""
    app = create_app(TestConfig)
    
    with app.app_context():
        # CREATE ALL TABLES ONCE FOR THE SESSION
        db.create_all()
        yield app
        # DROP ALL TABLES AFTER ALL TESTS ARE DONE
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for each test function with automatic cleanup"""
    with app.app_context():
        # START A TRANSACTION
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # BIND THE SESSION TO THE TRANSACTION
        session = db.session
        session.bind = connection
        
        yield session
        
        # ROLLBACK TRANSACTION AFTER TEST (CLEANUP)
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for each test"""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(db_session):
    """Create a sample verified user for testing"""
    user = User(
        name="Test User",
        email="test@example.com",
        role="user",
        is_verified=True,
        password_hash=hash_password("Password123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)  # REFRESH TO GET ID
    return user

@pytest.fixture
def unverified_user(db_session):
    """Create an unverified user for testing"""
    user = User(
        name="Unverified User",
        email="unverified@example.com",
        role="user",
        is_verified=False,
        password_hash=hash_password("Password123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        name="Admin User",
        email="admin@example.com",
        role="admin",
        is_verified=True,
        password_hash=hash_password("AdminPass123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def verification_token(db_session, unverified_user):
    """Create a verification token for testing"""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    token = VerificationToken(
        user_id=unverified_user.id,
        token="test-verification-token-123",
        token_type="email",
        expires_at=expires_at
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    return token

@pytest.fixture
def expired_verification_token(db_session, unverified_user):
    """Create an expired verification token for testing"""
    expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    token = VerificationToken(
        user_id=unverified_user.id,
        token="expired-token-123",
        token_type="email",
        expires_at=expires_at
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    return token

@pytest.fixture
def reset_token(db_session, sample_user):
    """Create a password reset token for testing"""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    token = VerificationToken(
        user_id=sample_user.id,
        token="test-reset-token-123",
        token_type="password_reset",
        expires_at=expires_at
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    return token

@pytest.fixture
def refresh_token(db_session, sample_user):
    """Create a refresh token for testing"""
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    token = RefreshToken(
        token="test-refresh-token-123",
        user_id=sample_user.id,
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        expires_at=expires_at,
        is_revoked=False
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    return token

@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers with access token"""
    from flask_jwt_extended import create_access_token
    
    with client.application.app_context():
        access_token = create_access_token(
            identity=str(sample_user.id),
            additional_claims={
                "email": sample_user.email,
                "role": sample_user.role
            }
        )
    
    return {
        'Authorization': f'Bearer {access_token}'
    }