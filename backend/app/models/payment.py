"""
Payment models for CV-Match.

Defines Pydantic models for payment history and subscriptions.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PaymentHistoryBase(BaseModel):
    """Base model for payment history records."""

    user_id: str = Field(..., description="User ID who made the payment")
    stripe_checkout_session_id: str | None = Field(None, description="Stripe checkout session ID")
    stripe_payment_intent_id: str | None = Field(None, description="Stripe payment intent ID")
    amount: int = Field(..., description="Payment amount in cents")
    currency: str = Field(default="brl", description="Payment currency")
    status: str = Field(..., description="Payment status (succeeded, failed, pending)")
    payment_type: str = Field(..., description="Payment type (subscription, one_time)")
    description: str | None = Field(None, description="Payment description")
    error_message: str | None = Field(None, description="Error message if payment failed")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Additional metadata")


class PaymentHistoryCreate(PaymentHistoryBase):
    """Model for creating payment history records."""

    pass


class PaymentHistoryUpdate(BaseModel):
    """Model for updating payment history records."""

    status: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class PaymentHistory(PaymentHistoryBase):
    """Full payment history model with database fields."""

    id: str = Field(..., description="Payment record ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    """Base model for subscription records."""

    user_id: str = Field(..., description="User ID who owns the subscription")
    stripe_subscription_id: str | None = Field(None, description="Stripe subscription ID")
    stripe_customer_id: str | None = Field(None, description="Stripe customer ID")
    status: str = Field(..., description="Subscription status (active, canceled, past_due)")
    price_id: str | None = Field(None, description="Stripe price ID")
    product_id: str | None = Field(None, description="Stripe product ID")
    current_period_start: datetime | None = Field(None, description="Current period start")
    current_period_end: datetime | None = Field(None, description="Current period end")
    cancel_at_period_end: bool = Field(default=False, description="Whether to cancel at period end")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Additional metadata")


class SubscriptionCreate(SubscriptionBase):
    """Model for creating subscription records."""

    pass


class SubscriptionUpdate(BaseModel):
    """Model for updating subscription records."""

    status: str | None = None
    cancel_at_period_end: bool | None = None
    current_period_end: datetime | None = None
    metadata: dict[str, Any] | None = None


class Subscription(SubscriptionBase):
    """Full subscription model with database fields."""

    id: str = Field(..., description="Subscription record ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")

    class Config:
        from_attributes = True


class PaymentVerificationRequest(BaseModel):
    """Model for payment verification requests."""

    session_id: str = Field(..., description="Stripe checkout session ID")
    user_id: str = Field(..., description="User ID")


class PaymentVerificationResponse(BaseModel):
    """Model for payment verification responses."""

    success: bool = Field(..., description="Whether verification succeeded")
    payment_id: str | None = Field(None, description="Payment record ID")
    plan_type: str | None = Field(None, description="Plan type activated")
    credits_activated: int | None = Field(None, description="Number of credits activated")
    amount_paid: int | None = Field(None, description="Amount paid in cents")
    currency: str | None = Field(None, description="Payment currency")
    error: str | None = Field(None, description="Error message if verification failed")
    message: str | None = Field(None, description="Additional information")
