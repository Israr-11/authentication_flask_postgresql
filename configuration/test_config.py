import os
from configuration.config import Config

class TestConfig(Config):
    """Configuration specifically for testing environment"""
    
    # ENABLE TESTING MODE
    TESTING = True
    
    # USE SEPARATE TEST POSTGRESQL DATABASE
    # IMPORTANT: USE A DIFFERENT DATABASE NAME FOR TESTING
    TEST_DB_USER = os.getenv('TEST_DB_USER', 'postgres')
    TEST_DB_PASSWORD = os.getenv('TEST_DB_PASSWORD', 'password')
    TEST_DB_HOST = os.getenv('TEST_DB_HOST', 'localhost')
    TEST_DB_PORT = os.getenv('TEST_DB_PORT', '5432')
    TEST_DB_NAME = os.getenv('TEST_DB_NAME', 'db_tests')  # DIFFERENT DATABASE NAME
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # DISABLE CSRF FOR API TESTING
    WTF_CSRF_ENABLED = False
    
    # USE SHORTER TOKEN EXPIRY FOR FASTER TESTS
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 MINUTES
    JWT_REFRESH_TOKEN_EXPIRES = 3600  # 1 HOUR (fixed typo from 3006)
    
    # MOCK EMAIL SENDING (DON'T ACTUALLY SEND EMAILS IN TESTS)
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = 'test@example.com'
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    
    # TEST-SPECIFIC SECRET KEYS
    SECRET_KEY = 'test-secret-key-do-not-use-in-production'
    JWT_SECRET_KEY = 'test-jwt-secret-key-do-not-use-in-production'
    
    # FRONTEND URL FOR TESTING
    FRONTEND_URL = 'http://localhost:3000'
    
    # PRESERVE EXCEPTIONS FOR BETTER ERROR MESSAGES IN TESTS
    PRESERVE_CONTEXT_ON_EXCEPTION = False