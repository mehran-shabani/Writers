from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from uuid import UUID

# Secret key for JWT - should be in environment variables in production
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes for access token
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days for refresh token


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generates a short-lived JWT access token.

    Args:
        data (Dict[str, Any]): The payload to include in the token.
        expires_delta (Optional[timedelta]): The expiration time for the token.
                                              Defaults to 30 minutes.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generates a long-lived JWT refresh token.

    Args:
        data (Dict[str, Any]): The payload to include in the token.
        expires_delta (Optional[timedelta]): The expiration time for the token.
                                              Defaults to 7 days.

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and verifies a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        Optional[Dict[str, Any]]: The decoded payload if the token is valid,
                                 otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extracts the user ID from a JWT token.

    Args:
        token (str): The JWT token to process.

    Returns:
        Optional[str]: The user ID from the token payload if valid,
                       otherwise None.
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
