# Agent Prompt: Webhook Implementation

**Agent**: payment-specialist
**Phase**: 2 - Webhooks (After database tables)
**Priority**: P0 - CRITICAL
**Time**: 1 hour

## Mission

Implement secure Stripe webhook endpoint with signature verification and idempotency.

## Tasks

1. Create webhook endpoint in webhooks.py
2. Verify signature using StripeService
3. Check idempotency via payment_events table
4. Handle checkout.session.completed
5. Add credits on successful payment
6. Log all events for audit

## Key Code

```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    event = stripe_service.verify_webhook_signature(payload, sig)
    if not event:
        raise HTTPException(401, "Invalid signature")

    # Check idempotency
    if check_already_processed(event.id):
        return {"already_processed": True}

    # Process and log
    await handle_event(event)
```

## Success Criteria

- Signature verification works
- Idempotency prevents duplicates
- Credits added on payment success
- All events logged

Total: 1 hour
