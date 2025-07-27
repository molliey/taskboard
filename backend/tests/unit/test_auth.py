import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from jose import jwt, JWTError

# Add the parent directory to the path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    get_current_user
)
from app.models.user import User
from fastapi import HTTPException
from sqlalchemy.orm import Session

class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hash_and_verify(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        
        # Hash the password
        hashed = get_password_hash(password)
        
        # Verify the password
        assert verify_password(password, hashed) is True
        
        # Verify wrong password
        assert verify_password("wrongpassword", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password123"
        password2 = "different123"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """Test that the same password produces different hashes (salt)"""
        password = "testpassword123"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify the same password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestJWTTokens:
    """Test JWT token creation and verification"""

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_create_access_token_with_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "testuser"

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        invalid_token = "invalid.token.here"
        
        payload = decode_access_token(invalid_token)
        assert payload is None

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_decode_expired_token(self):
        """Test decoding an expired token"""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        # Expired token should return None
        payload = decode_access_token(token)
        assert payload is None

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_decode_token_missing_subject(self):
        """Test decoding token without subject"""
        # Create token without 'sub' field
        data = {"user": "testuser"}  # Wrong field name
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") is None  # Missing 'sub' field
        assert payload.get("user") == "testuser"

class TestGetCurrentUser:
    """Test get_current_user dependency"""

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_success(self, mock_jwt_decode):
        """Test successful user retrieval"""
        # Mock JWT decode
        mock_jwt_decode.return_value = {"sub": "testuser"}
        
        # Mock user from database
        mock_user = User(id=1, username="testuser", email="test@example.com")
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Test (need to use async context)
        import asyncio
        result = asyncio.run(get_current_user("valid_token", mock_db))
        
        assert result == mock_user
        mock_jwt_decode.assert_called_once()

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_invalid_token(self, mock_jwt_decode):
        """Test user retrieval with invalid token"""
        from jose import JWTError
        # Mock JWT decode to raise JWTError (invalid token)
        mock_jwt_decode.side_effect = JWTError("Invalid token")
        
        mock_db = Mock(spec=Session)
        
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_user("invalid_token", mock_db))
        
        assert exc_info.value.status_code == 401
        mock_jwt_decode.assert_called_once()

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_user_not_found(self, mock_jwt_decode):
        """Test user retrieval when user doesn't exist in database"""
        # Mock JWT decode
        mock_jwt_decode.return_value = {"sub": "nonexistentuser"}
        
        # Mock database session - user not found
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None  # User not found
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_user("valid_token", mock_db))
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
        mock_jwt_decode.assert_called_once()

    @patch('app.utils.auth.jwt.decode')
    def test_get_current_user_with_user(self, mock_jwt_decode):
        """Test user retrieval successfully returns user"""
        # Mock JWT decode
        mock_jwt_decode.return_value = {"sub": "testuser"}
        
        # Mock user from database
        mock_user = User(
            id=1, 
            username="testuser", 
            email="test@example.com",
            is_active=True
        )
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        import asyncio
        result = asyncio.run(get_current_user("valid_token", mock_db))
        assert result == mock_user
        mock_jwt_decode.assert_called_once()

class TestTokenSecurity:
    """Test token security features"""

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_token_payload_integrity(self):
        """Test that token payload cannot be tampered with"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Tamper with the token
        parts = token.split('.')
        tampered_token = parts[0] + '.tampered.' + parts[2]
        
        payload = decode_access_token(tampered_token)
        assert payload is None

    @patch('app.utils.auth.SECRET_KEY', 'secret1')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_token_secret_key_verification(self):
        """Test that tokens signed with different keys are rejected"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Change secret key and try to verify
        with patch('app.utils.auth.SECRET_KEY', 'different_secret'):
            payload = decode_access_token(token)
            assert payload is None

class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_complete_auth_flow(self):
        """Test complete authentication flow from password to token to user"""
        # 1. Hash password
        password = "userpassword123"
        hashed_password = get_password_hash(password)
        
        # 2. Verify password (login)
        assert verify_password(password, hashed_password) is True
        
        # 3. Create token
        with patch('app.utils.auth.SECRET_KEY', 'test_secret'):
            token = create_access_token({"sub": "testuser"})
            
            # 4. Verify token and get payload
            payload = decode_access_token(token)
            assert payload["sub"] == "testuser"

    @patch('app.utils.auth.SECRET_KEY', 'test_secret_key')
    @patch('app.utils.auth.ALGORITHM', 'HS256')
    def test_end_to_end_auth(self):
        """Test end-to-end authentication"""
        # Mock user
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        
        # Create token
        token = create_access_token({"sub": "testuser"})
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # Get current user
        import asyncio
        current_user = asyncio.run(get_current_user(token, mock_db))
        
        assert current_user == mock_user
        assert current_user.username == "testuser"

class TestAuthenticationEdgeCases:
    """Test edge cases in authentication"""

    def test_empty_password(self):
        """Test handling of empty password"""
        # bcrypt actually accepts empty passwords, so let's test that it works
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True

    def test_very_long_password(self):
        """Test handling of very long password"""
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)
        assert verify_password(long_password, hashed) is True

    def test_unicode_password(self):
        """Test handling of unicode characters in password"""
        unicode_password = "пароль123🔒"
        hashed = get_password_hash(unicode_password)
        assert verify_password(unicode_password, hashed) is True

    @patch('app.utils.auth.SECRET_KEY', 'test_secret')
    def test_token_with_special_characters(self):
        """Test token creation with special characters in username"""
        data = {"sub": "user@domain.com"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload["sub"] == "user@domain.com"

    def test_malformed_token(self):
        """Test handling of malformed tokens"""
        malformed_tokens = [
            "",  # Empty token
            "not.a.token",  # Not enough parts
            "too.many.parts.here.error",  # Too many parts
            "invalid_base64.invalid_base64.invalid_base64",  # Invalid base64
        ]
        
        for token in malformed_tokens:
            payload = decode_access_token(token)
            assert payload is None