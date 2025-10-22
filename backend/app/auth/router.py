from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from datetime import datetime

from ..db import get_session
from ..models.user import User
from .schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from .utils import hash_password, verify_password
from .jwt import create_access_token, create_refresh_token
from .dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        response: FastAPI response object for setting cookies
        session: Database session
    
    Returns:
        TokenResponse with user data and tokens set in httpOnly cookies
    
    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    statement = select(User).where(User.username == user_data.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Create access and refresh tokens
    token_data = {"sub": str(new_user.id), "email": new_user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(new_user.id)})
    
    # Set tokens in httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return TokenResponse(
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Login user and return tokens.
    
    Args:
        credentials: User login credentials (email and password)
        response: FastAPI response object for setting cookies
        session: Database session
    
    Returns:
        TokenResponse with user data and tokens set in httpOnly cookies
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Update last login timestamp
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create access and refresh tokens
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Set tokens in httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return TokenResponse(
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Currently authenticated user
    
    Returns:
        UserResponse with user data
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing authentication cookies.
    
    Args:
        response: FastAPI response object for clearing cookies
    
    Returns:
        Success message
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = None,
    response: Response = None,
    session: Session = Depends(get_session)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token from cookie
        response: FastAPI response object for setting cookies
        session: Database session
    
    Returns:
        TokenResponse with new access token
    
    Raises:
        HTTPException: If refresh token is invalid
    """
    # This endpoint would need to extract refresh_token from cookie
    # and generate a new access_token
    # Implementation left for future enhancement
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token endpoint not yet implemented"
    )
