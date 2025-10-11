"""
Subscription models for CV-Match.
Represents user subscriptions and their usage.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """Base subscription model."""
    user_id: str
    tier_id: str  # e.g., "flow_pro"
    status: Literal["active", "canceled", "past_due", "paused"] = "active"


class SubscriptionCreate(SubscriptionBase):
    """Model for creating a new subscription."""
    stripe_subscription_id: str
    stripe_customer_id: str
    stripe_price_id: str


class SubscriptionUpdate(BaseModel):
    """Model for updating a subscription."""
    tier_id: Optional[str] = None
    status: Optional[Literal["active", "canceled", "past_due", "paused"]] = None
    cancel_at_period_end: Optional[bool] = None


class SubscriptionUsage(BaseModel):
    """Model for subscription usage tracking."""
    subscription_id: str
    user_id: str
    analyses_used_this_period: int = 0
    analyses_rollover: int = 0
    period_start: datetime
    period_end: datetime


class SubscriptionDetails(SubscriptionBase):
    """Complete subscription details with usage."""
    id: str
    stripe_subscription_id: str
    stripe_customer_id: str
    stripe_price_id: str

    # Period info
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None

    # Usage tracking
    analyses_used_this_period: int = 0
    analyses_rollover: int = 0
    analyses_available: int  # Computed: tier limit + rollover - used

    # Tier info (from pricing config)
    tier_name: str
    analyses_per_month: int
    rollover_limit: int

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionStatus(BaseModel):
    """Quick subscription status check."""
    has_active_subscription: bool
    tier_id: Optional[str] = None
    analyses_remaining: int = 0
    can_use_service: bool  # True if has subscription OR has credits