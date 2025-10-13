"""
Pydantic models for usage tracking services.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UsageTrackingBase(BaseModel):
    """Base model for usage tracking."""

    user_id: UUID
    month_date: date
    free_optimizations_used: int = Field(default=0, ge=0)
    paid_optimizations_used: int = Field(default=0, ge=0)


class UsageTrackingCreate(UsageTrackingBase):
    """Model for creating usage tracking records."""

    pass


class UsageTrackingResponse(UsageTrackingBase):
    """Model for usage tracking response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsageLimitCheckResponse(BaseModel):
    """Response model for usage limit checks."""

    can_optimize: bool
    is_pro: bool
    free_optimizations_used: int
    free_optimizations_limit: int
    remaining_free_optimizations: int
    tier: str = "free"  # User's subscription tier
    reason: str | None = None
    upgrade_prompt: str | None = None


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics."""

    user_id: UUID
    current_month_date: date
    free_optimizations_used: int
    paid_optimizations_used: int
    free_optimizations_limit: int
    is_pro: bool
    can_optimize: bool
    remaining_free_optimizations: int
    total_optimizations_this_month: int


class UserCredits(BaseModel):
    """Model for user credits."""

    user_id: UUID
    credits_remaining: int
    total_credits: int
    is_pro: bool


class CreditTransaction(BaseModel):
    """Model for credit transactions."""

    id: UUID
    user_id: UUID
    amount: int
    type: str  # "credit" or "debit"
    source: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreditsResponse(BaseModel):
    """Response model for user credits endpoint."""

    credits_remaining: int = Field(..., description="Number of credits remaining")
    tier: str = Field(..., description="User's subscription tier")
    can_optimize: bool = Field(..., description="Whether user can perform optimizations")
    upgrade_prompt: str | None = Field(
        None, description="Upgrade prompt for users with insufficient credits"
    )
    is_pro: bool = Field(..., description="Whether user has Pro status")
    total_credits: int = Field(..., description="Total credits ever purchased/earned")
