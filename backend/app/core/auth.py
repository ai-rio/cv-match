"""
Authentication dependencies for FastAPI endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.supabase.auth import SupabaseAuthService, get_auth_service

# Create HTTP Bearer scheme for JWT token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """
    Validate JWT token and return user information.

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        auth_service: Supabase authentication service

    Returns:
        Dictionary containing user information (id, email)

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Get user from JWT token
        user = await auth_service.get_user(credentials.credentials)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Return user information in a consistent format
        return {
            "id": user.get("id", ""),
            "email": user.get("email", ""),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
) -> dict[str, str] | None:
    """
    Optional authentication - returns user if authenticated, None otherwise.

    This is useful for endpoints that can work both with and without authentication.

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        auth_service: Supabase authentication service

    Returns:
        User information dictionary if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        user = await auth_service.get_user(credentials.credentials)

        if not user:
            return None

        return {
            "id": user.get("id", ""),
            "email": user.get("email", ""),
        }

    except Exception:
        return None
