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
    """Handles user registration.

    This endpoint creates a new user, hashes their password, and stores it in
    the database. It then generates access and refresh tokens, which are set
    as httpOnly cookies.

    Args:
        user_data (UserRegister): The user's registration information.
        response (Response): The FastAPI response object.
        session (Session): The database session.

    Returns:
        TokenResponse: An object containing the user's information.

    Raises:
        HTTPException: If the email or username is already registered.
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
    """Handles user login.

    This endpoint authenticates a user by verifying their email and password.
    If successful, it generates new access and refresh tokens and sets them
    as httpOnly cookies.

    Args:
        credentials (UserLogin): The user's login credentials.
        response (Response): The FastAPI response object.
        session (Session): The database session.

    Returns:
        TokenResponse: An object containing the user's information.

    Raises:
        HTTPException: If the login credentials are invalid or the user is inactive.
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
    """Retrieves the information of the currently authenticated user.

    Args:
        current_user (User): The authenticated user object.

    Returns:
        UserResponse: An object containing the user's public information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(response: Response):
    """Handles user logout.

    This endpoint logs a user out by deleting their access and refresh tokens
    from the cookies.

    Args:
        response (Response): The FastAPI response object.

    Returns:
        dict: A message indicating successful logout.
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
    """Refreshes a user's access token.

    This endpoint uses a refresh token to generate a new access token.
    (Note: This is not yet implemented).

    Args:
        refresh_token (str): The refresh token.
        response (Response): The FastAPI response object.
        session (Session): The database session.

    Raises:
        HTTPException: Indicating that the endpoint is not implemented.
    """
    # This endpoint would need to extract refresh_token from cookie
    # and generate a new access_token
    # Implementation left for future enhancement
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token endpoint not yet implemented"
    )
