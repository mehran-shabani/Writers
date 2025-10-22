from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration.

    Attributes:
        email (EmailStr): The user's email address.
        username (str): The user's username.
        password (str): The user's password.
        full_name (Optional[str]): The user's full name.
    """
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for the response when a user is returned.

    Attributes:
        id (UUID): The user's unique ID.
        email (str): The user's email address.
        username (str): The user's username.
        full_name (Optional[str]): The user's full name.
        is_active (bool): Whether the user's account is active.
        is_superuser (bool): Whether the user has superuser privileges.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user was last updated.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Schema for the response when tokens are returned.

    Attributes:
        user (UserResponse): The user's information.
        token_type (str): The type of token (defaults to "bearer").
    """
    user: UserResponse
    token_type: str = "bearer"
