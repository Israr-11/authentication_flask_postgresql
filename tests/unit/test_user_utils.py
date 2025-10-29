import pytest
from utils.user_utils import hash_password, check_password, validate_password_strength

class TestPasswordHashing:
    """Test password hashing utilities"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
    
    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes"""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # BCRYPT USES RANDOM SALT SO HASHES SHOULD BE DIFFERENT
        assert hash1 != hash2
    
    def test_check_password_correct(self):
        """Test checking correct password"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert check_password(password, hashed) is True
    
    def test_check_password_incorrect(self):
        """Test checking incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)
        
        assert check_password(wrong_password, hashed) is False
    
    def test_check_password_empty(self):
        """Test checking empty password"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert check_password("", hashed) is False
    
    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters"""
        password = "Pässwörd123!你好"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert check_password(password, hashed) is True

class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_valid_password(self):
        """Test valid password passes all checks"""
        is_valid, message = validate_password_strength("Password123!")
        
        assert is_valid is True
        assert message is None
    
    def test_password_too_short(self):
        """Test password shorter than 8 characters"""
        is_valid, message = validate_password_strength("Pass1!")
        
        assert is_valid is False
        assert "8 characters" in message
    
    def test_password_no_uppercase(self):
        """Test password without uppercase letter"""
        is_valid, message = validate_password_strength("password123!")
        
        assert is_valid is False
        assert "uppercase" in message.lower()
    
    def test_password_no_lowercase(self):
        """Test password without lowercase letter"""
        is_valid, message = validate_password_strength("PASSWORD123!")
        
        assert is_valid is False
        assert "lowercase" in message.lower()
    
    def test_password_no_digit(self):
        """Test password without digit"""
        is_valid, message = validate_password_strength("Password!")
        
        assert is_valid is False
        assert "digit" in message.lower()
    
    def test_password_no_special_char(self):
        """Test password without special character"""
        is_valid, message = validate_password_strength("Password123")
        
        assert is_valid is False
        assert "special character" in message.lower()
    
    def test_password_edge_cases(self):
        """Test password validation edge cases"""
        # EXACTLY 8 CHARACTERS
        is_valid, _ = validate_password_strength("Pass123!")
        assert is_valid is True
        
        # ALL REQUIREMENTS WITH MINIMUM LENGTH
        is_valid, _ = validate_password_strength("Aa1!")
        assert is_valid is False  # TOO SHORT
    
    def test_password_all_special_chars_accepted(self):
        """Test that various special characters are accepted"""
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        for char in special_chars:
            is_valid, _ = validate_password_strength(f"Password123{char}")
            assert is_valid is True, f"Special char '{char}' should be valid"