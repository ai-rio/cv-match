"""
Payment endpoints for CV-Match Brazilian market.
Handles checkout sessions, payment processing, and subscription management.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from app.services.stripe_service import stripe_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


class CreateCheckoutSessionRequest(BaseModel):
    """Request model for creating a checkout session."""
    user_id: str
    user_email: EmailStr
    plan_type: str = "pro"  # free, pro, enterprise, lifetime
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class CreatePaymentIntentRequest(BaseModel):
    """Request model for creating a payment intent."""
    user_id: str
    user_email: EmailStr
    amount: int  # Amount in cents (BRL)
    metadata: Optional[Dict[str, str]] = None


class CreateCustomerRequest(BaseModel):
    """Request model for creating a customer."""
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    address: Optional[Dict[str, str]] = None


@router.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest) -> JSONResponse:
    """
    Create a Stripe checkout session for Brazilian market.

    This endpoint creates a checkout session with Brazilian Real (BRL) currency
    and appropriate pricing tiers for the Brazilian market.

    Plans available:
    - free: R$ 0,00 (5 análises por mês)
    - pro: R$ 29,90/mês (análises ilimitadas, IA avançada)
    - enterprise: R$ 99,90/mês (recrutamento ilimitado, dashboard)
    - lifetime: R$ 297,00 (acesso vitalício)

    Args:
        request: Checkout session creation request

    Returns:
        Checkout session data with URL and session ID
    """
    try:
        result = await stripe_service.create_checkout_session(
            user_id=request.user_id,
            user_email=request.user_email,
            plan_type=request.plan_type,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata=request.metadata
        )

        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "session_id": result["session_id"],
                    "checkout_url": result["checkout_url"],
                    "plan_type": result["plan_type"],
                    "currency": result["currency"],
                    "amount": result["amount"]
                }
            )
        else:
            logger.error(f"Checkout session creation failed: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating checkout session"
        )


@router.post("/create-payment-intent")
async def create_payment_intent(request: CreatePaymentIntentRequest) -> JSONResponse:
    """
    Create a payment intent for one-time payments.

    This endpoint creates a payment intent for Brazilian market transactions
    using BRL currency and appropriate payment methods.

    Args:
        request: Payment intent creation request

    Returns:
        Payment intent data with client secret
    """
    try:
        result = await stripe_service.create_payment_intent(
            amount=request.amount,
            user_id=request.user_id,
            user_email=request.user_email,
            metadata=request.metadata
        )

        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "client_secret": result["client_secret"],
                    "payment_intent_id": result["payment_intent_id"],
                    "amount": result["amount"],
                    "currency": result["currency"]
                }
            )
        else:
            logger.error(f"Payment intent creation failed: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating payment intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating payment intent"
        )


@router.post("/create-customer")
async def create_customer(request: CreateCustomerRequest) -> JSONResponse:
    """
    Create a Stripe customer for Brazilian market.

    This endpoint creates a customer record with Brazilian market
    configuration and metadata.

    Args:
        request: Customer creation request

    Returns:
        Customer creation result
    """
    try:
        result = await stripe_service.create_customer(
            user_id=request.user_id,
            email=request.email,
            name=request.name,
            address=request.address
        )

        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "customer_id": result["customer_id"],
                    "customer": result["customer"]
                }
            )
        else:
            logger.error(f"Customer creation failed: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating customer"
        )


@router.get("/retrieve-session/{session_id}")
async def retrieve_checkout_session(session_id: str) -> JSONResponse:
    """
    Retrieve a checkout session.

    This endpoint retrieves the details of a checkout session
    for payment status verification.

    Args:
        session_id: Stripe checkout session ID

    Returns:
        Checkout session details
    """
    try:
        result = await stripe_service.retrieve_checkout_session(session_id)

        if result["success"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "session": result["session"]
                }
            )
        else:
            logger.error(f"Session retrieval failed: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving session"
        )


@router.get("/pricing")
async def get_brazilian_pricing() -> JSONResponse:
    """
    Get Brazilian pricing configuration.

    Returns:
        Available pricing tiers for Brazilian market
    """
    try:
        pricing = stripe_service._get_brazilian_pricing()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "pricing": pricing,
                "currency": "brl",
                "country": "BR",
                "locale": "pt-BR"
            }
        )
    except Exception as e:
        logger.error(f"Error getting pricing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting pricing"
        )


@router.get("/health")
async def payments_health_check() -> JSONResponse:
    """
    Health check endpoint for payment services.

    Returns:
        Health status of payment processing system
    """
    try:
        stripe_configured = bool(stripe_service.api_key)
        test_mode = stripe_service.api_key.startswith("sk_test_") if stripe_service.api_key else False

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "stripe_configured": stripe_configured,
                "test_mode": test_mode,
                "currency": stripe_service.default_currency,
                "country": stripe_service.default_country,
                "locale": stripe_service.default_locale
            }
        )
    except Exception as e:
        logger.error(f"Payments health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )