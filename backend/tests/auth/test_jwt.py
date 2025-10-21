import pytest
from datetime import timedelta
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_user_id_from_token,
)


class TestJWT:
    """Test cases for JWT token functions"""
    
    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_custom_expiration(self):
        """Test creating access token with custom expiration"""
        data = {"sub": "user123"}
        custom_expire = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expire)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token_with_custom_expiration(self):
        """Test creating refresh token with custom expiration"""
        data = {"sub": "user123"}
        custom_expire = timedelta(days=14)
        token = create_refresh_token(data, expires_delta=custom_expire)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_valid_token(self):
        """Test verifying valid token"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.string"
        
        payload = verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_token_types(self):
        """Test that access and refresh tokens have correct types"""
        access_data = {"sub": "user123"}
        refresh_data = {"sub": "user123"}
        
        access_token = create_access_token(access_data)
        refresh_token = create_refresh_token(refresh_data)
        
        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)
        
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
    
    def test_get_user_id_from_valid_token(self):
        """Test extracting user ID from valid token"""
        user_id = "user123"
        data = {"sub": user_id, "email": "test@example.com"}
        token = create_access_token(data)
        
        extracted_id = get_user_id_from_token(token)
        
        assert extracted_id == user_id
    
    def test_get_user_id_from_invalid_token(self):
        """Test extracting user ID from invalid token"""
        invalid_token = "invalid.token.string"
        
        extracted_id = get_user_id_from_token(invalid_token)
        
        assert extracted_id is None
    
    def test_get_user_id_from_token_without_sub(self):
        """Test extracting user ID from token without 'sub' claim"""
        data = {"email": "test@example.com"}  # No 'sub' field
        token = create_access_token(data)
        
        extracted_id = get_user_id_from_token(token)
        
        assert extracted_id is None
