"""
Authentication dependencies for FastAPI endpoints.
"""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.supabase.auth import get_auth_service, SupabaseAuthService

# Create HTTP Bearer scheme for JWT token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
) -> Dict[str, str]:
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
            "id": user.id,
            "email": user.email,
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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
) -> Optional[Dict[str, str]]:
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
            "id": user.id,
            "email": user.email,
        }

    except Exception:
        return None