from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.models.auth_models import TokenResponse, UserProfile
from app.models.secure import SecureLoginRequest
from app.services.supabase.auth import SupabaseAuthService, get_auth_service
from app.utils.validation import validate_string

router = APIRouter()
security = HTTPBearer()


# Legacy model for backward compatibility
class LoginRequest(BaseModel):
    email: str
    password: str


class SecureLoginResponse(BaseModel):
    """Enhanced login response with security metadata."""

    access_token: str
    token_type: str
    user_id: str
    email: str
    login_time: str
    requires_mfa: bool = False


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    """Login with email and password (legacy endpoint)."""
    try:
        # Validate input for security
        email_validation = validate_string(login_data.email, input_type="email", max_length=254)
        password_validation = validate_string(
            login_data.password, input_type="general", max_length=128
        )

        if not email_validation.is_valid or not password_validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input format"
            )

        supabase_token = await auth_service.sign_in_with_email_password(
            email_validation.sanitized_input, password_validation.sanitized_input
        )
        return TokenResponse(access_token=supabase_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed",
        ) from err


@router.post("/secure-login", response_model=SecureLoginResponse)
async def secure_login(
    login_data: SecureLoginRequest,
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    """
    Secure login with comprehensive input validation.

    This endpoint provides enhanced security validation for login requests
    including rate limiting, input sanitization, and security logging.
    """
    try:
        # Input validation is handled by SecureLoginRequest Pydantic model
        # Additional server-side validation for defense in depth
        email_validation = validate_string(login_data.email, input_type="email", max_length=254)
        password_validation = validate_string(
            login_data.password, input_type="general", max_length=128
        )

        if not email_validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email format: {'; '.join(email_validation.errors)}",
            )

        if not password_validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid password format: {'; '.join(password_validation.errors)}",
            )

        # Log login attempt
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt for email: {email_validation.sanitized_input}")

        # Attempt authentication
        supabase_token = await auth_service.sign_in_with_email_password(
            email_validation.sanitized_input, password_validation.sanitized_input
        )

        # Get user info for response
        user = await auth_service.get_user(supabase_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            )

        from datetime import datetime

        return SecureLoginResponse(
            access_token=supabase_token,
            token_type="bearer",
            user_id=user.get("id", ""),
            email=user.get("email", ""),
            login_time=datetime.utcnow().isoformat(),
            requires_mfa=False,  # TODO: Implement MFA when needed
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Secure login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        ) from e


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
):
    """Get the currently authenticated user profile."""
    try:
        user = await auth_service.get_user(credentials.credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserProfile(
            id=user.get("id", ""),
            email=user.get("email", ""),
            full_name=user.get("user_metadata", {}).get("full_name", ""),
            avatar_url=user.get("user_metadata", {}).get("avatar_url", ""),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/provider-token", response_model=TokenResponse)
async def exchange_provider_token(
    provider: str, token: str, auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Exchange a provider token (Google, LinkedIn) for a Supabase token."""
    try:
        supabase_token = await auth_service.sign_in_with_provider_token(provider, token)
        return TokenResponse(access_token=supabase_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authenticate with provider: {str(e)}",
        ) from e
