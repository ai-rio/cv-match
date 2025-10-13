# Agent Prompt: API Payment Integration

**Agent**: backend-specialist
**Phase**: 3 - API Integration
**Priority**: P0
**Time**: 2.5 hours

## Mission

Integrate payment and credit system into existing API endpoints.

## Tasks

### Task 1: Create Payment Initiation Endpoint (1h)

```python
@router.post("/payments/create-checkout")
async def create_checkout(
    tier: str,
    user = Depends(get_current_user)
):
    # Get price from tier
    price_id = get_price_id(tier)

    # Create Stripe session
    session = await stripe_service.create_checkout_session(
        price_id=price_id,
        success_url=f"{frontend_url}/payment/success",
        cancel_url=f"{frontend_url}/payment/canceled",
        metadata={"user_id": user.id, "credits": get_credits(tier)}
    )

    return {"session_id": session.id}
```

### Task 2: Add Credit Check Middleware (30min)

```python
async def check_credits(user_id: str):
    credits = await usage_limit_service.check_credits(user_id)
    if credits <= 0:
        raise HTTPException(402, "Insufficient credits")
```

### Task 3: Update Optimization Endpoint (1h)

```python
@router.post("/optimizations/start")
async def start_optimization(
    request: OptimizationRequest,
    user = Depends(get_current_user)
):
    # Check credits first
    await check_credits(user.id)

    # Process optimization
    result = await optimize_resume(request)

    # Deduct credit atomically
    await usage_limit_service.deduct_credits(
        user_id=user.id,
        amount=1,
        operation_id=result.id
    )

    return result
```

## Success Criteria

- Can create Stripe checkout session
- Credits checked before operations
- Credits deducted after success
- Atomic operations prevent race conditions

Total: 2.5 hours
