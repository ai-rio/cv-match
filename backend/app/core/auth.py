"""Authentication utilities for the CV-Match backend."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current user from the JWT token.

    Args:
        credentials: The HTTP authorization credentials

    Returns:
        The current user information

    Raises:
        HTTPException: If authentication fails
    """
    # This is a placeholder implementation
    # In a real application, you would validate the JWT token
    # and return the user information
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Placeholder user data
    return {"id": "user_id", "email": "user@example.com", "is_active": True}
