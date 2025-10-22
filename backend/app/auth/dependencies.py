from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlmodel import Session, select
from uuid import UUID

from ..db import get_session
from ..models.user import User
from .jwt import verify_token


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    session: Session = Depends(get_session)
) -> User:
    """Retrieves and validates the current user from an httpOnly access token.

    This function is a FastAPI dependency that extracts a JWT from a cookie,
    verifies it, and fetches the corresponding user from the database. It raises
    an HTTPException if the token is missing, invalid, or the user is not found.

    Args:
        access_token (Optional[str]): The JWT access token from the httpOnly cookie.
        session (Session): The database session.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the access token is invalid, the user is not found,
                       or the user is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not access_token:
        raise credentials_exception
    
    # Verify and decode token
    payload = verify_token(access_token)
    if payload is None:
        raise credentials_exception
    
    # Check token type
    token_type = payload.get("type")
    if token_type != "access":
        raise credentials_exception
    
    # Extract user_id
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError):
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensures that the current user is active.

    This function is a FastAPI dependency that builds on `get_current_user` to
    provide an additional check for whether the user is active.

    Args:
        current_user (User): The user object obtained from `get_current_user`.

    Returns:
        User: The authenticated and active user object.

    Raises:
        HTTPException: If the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
