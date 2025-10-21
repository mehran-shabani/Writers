import pytest
from app.auth.utils import hash_password, verify_password


class TestPasswordHashing:
    """Test cases for password hashing utilities"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0
    
    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Bcrypt uses random salt, so hashes should be different
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        is_valid = verify_password(password, hashed)
        
        assert is_valid is True
    
    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        correct_password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(correct_password)
        
        is_valid = verify_password(wrong_password, hashed)
        
        assert is_valid is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # Different case
        is_valid = verify_password("testpassword123", hashed)
        
        assert is_valid is False
    
    def test_hash_empty_password(self):
        """Test hashing empty password"""
        password = ""
        hashed = hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
    
    def test_hash_long_password(self):
        """Test hashing very long password"""
        password = "a" * 1000
        hashed = hash_password(password)
        
        assert hashed is not None
        assert verify_password(password, hashed) is True
