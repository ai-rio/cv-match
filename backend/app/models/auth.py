from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    """User profile information."""

    id: str
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: str
