import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.user import User
from app.auth.utils import hash_password


class TestRegister:
    """Test cases for user registration endpoint"""
    
    def test_register_success(self, client: TestClient, session: Session):
        """Test successful user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Verify user data
        user = data["user"]
        assert user["email"] == user_data["email"]
        assert user["username"] == user_data["username"]
        assert user["full_name"] == user_data["full_name"]
        assert user["is_active"] is True
        assert user["is_superuser"] is False
        assert "id" in user
        
        # Verify cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        
        # Verify user in database
        statement = select(User).where(User.email == user_data["email"])
        db_user = session.exec(statement).first()
        assert db_user is not None
        assert db_user.username == user_data["username"]
    
    def test_register_duplicate_email(self, client: TestClient, session: Session):
        """Test registration with duplicate email"""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            username="existinguser",
            hashed_password=hash_password("password123")
        )
        session.add(existing_user)
        session.commit()
        
        # Try to register with same email
        user_data = {
            "email": "existing@example.com",
            "username": "newuser",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client: TestClient, session: Session):
        """Test registration with duplicate username"""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            username="existinguser",
            hashed_password=hash_password("password123")
        )
        session.add(existing_user)
        session.commit()
        
        # Try to register with same username
        user_data = {
            "email": "new@example.com",
            "username": "existinguser",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password(self, client: TestClient):
        """Test registration with password too short"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test cases for user login endpoint"""
    
    def test_login_success(self, client: TestClient, session: Session):
        """Test successful user login"""
        # Create user
        password = "testpassword123"
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hash_password(password),
            full_name="Test User"
        )
        session.add(user)
        session.commit()
        
        # Login
        login_data = {
            "email": "test@example.com",
            "password": password
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "token_type" in data
        
        # Verify user data
        user_data = data["user"]
        assert user_data["email"] == "test@example.com"
        assert user_data["username"] == "testuser"
        
        # Verify cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
    
    def test_login_wrong_password(self, client: TestClient, session: Session):
        """Test login with incorrect password"""
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hash_password("correctpassword")
        )
        session.add(user)
        session.commit()
        
        # Login with wrong password
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client: TestClient, session: Session):
        """Test login with inactive user"""
        # Create inactive user
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=hash_password("password123"),
            is_active=False
        )
        session.add(user)
        session.commit()
        
        # Try to login
        login_data = {
            "email": "inactive@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 403
        assert "Inactive user" in response.json()["detail"]


class TestLogout:
    """Test cases for user logout endpoint"""
    
    def test_logout_success(self, client: TestClient):
        """Test successful logout"""
        response = client.post("/auth/logout")
        
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Successfully logged out"


class TestAuthentication:
    """Test cases for authentication dependency"""
    
    def test_access_protected_route_without_token(self, client: TestClient):
        """Test accessing protected route without token"""
        # This would need a protected route to test
        # For now, we'll skip this test
        pass
    
    def test_access_protected_route_with_valid_token(self, client: TestClient, session: Session):
        """Test accessing protected route with valid token"""
        # This would need a protected route to test
        # For now, we'll skip this test
        pass
    
    def test_access_protected_route_with_invalid_token(self, client: TestClient):
        """Test accessing protected route with invalid token"""
        # This would need a protected route to test
        # For now, we'll skip this test
        pass
