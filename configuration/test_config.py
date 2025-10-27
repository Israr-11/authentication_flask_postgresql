import os
from configuration.config import Config

class TestConfig(Config):
    """Configuration specifically for testing environment"""
    
    # ENABLE TESTING MODE
    TESTING = True
    
    # USE IN-MEMORY SQLITE DATABASE FOR FASTER TESTS
    # THIS AVOIDS CONFLICTS WITH PRODUCTION DATABASE
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # DISABLE CSRF FOR API TESTING
    WTF_CSRF_ENABLED = False
    
    # USE SHORTER TOKEN EXPIRY FOR FASTER TESTS
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 MINUTES
    JWT_REFRESH_TOKEN_EXPIRES = 3006  # 1 HOUR
    
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