from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    """User profile information."""

    id: str
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None
    subscription_tier: str | None = None  # 'free', 'premium', 'enterprise'
    credits_remaining: int | None = None
    created_at: str | None = None
    updated_at: str | None = None


class TokenResponse(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: str
