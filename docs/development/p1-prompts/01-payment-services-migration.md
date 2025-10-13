# Agent Prompt: Payment Services Migration

**Agent**: payment-specialist (primary) + backend-specialist (supporting)
**Phase**: 1 - Payment Services (Parallel with usage services)
**Priority**: P0 - CRITICAL (Financial security)
**Estimated Time**: 2 hours
**Dependencies**: None (can start immediately after P0 merge)

---

## 🎯 Mission

Copy and adapt Stripe payment services from Resume-Matcher to cv-match, ensuring secure payment processing, webhook handling, and BRL (Brazilian Real) support.

**⚠️ CRITICAL**: This involves financial transactions. Triple-check all security measures.

---

## 📋 Tasks

### Task 1: Copy Stripe Service (1 hour)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/stripe_service.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/stripe_service.py`

**Actions**:

1. Copy the file:

   ```bash
   cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/stripe_service.py \
      /home/carlos/projects/cv-match/backend/app/services/stripe_service.py
   ```

2. Update imports to match cv-match structure

3. Verify Stripe package is installed:

   ```bash
   cd /home/carlos/projects/cv-match/backend
   grep "stripe" pyproject.toml || echo "stripe>=5.0.0" >> pyproject.toml
   docker compose exec backend uv sync
   ```

4. Add environment variables to `.env`:

   ```bash
   # Add to backend/.env
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
   STRIPE_PRICE_ID_BASIC=price_basic_id
   STRIPE_PRICE_ID_PRO=price_pro_id
   ```

5. Test import:
   ```bash
   docker compose exec backend python -c "
   from app.services.stripe_service import StripeService
   print('✅ StripeService imported')
   "
   ```

**Success Criteria**:

- [x] File copied and adapted
- [x] Imports working
- [x] Stripe package installed
- [x] Environment variables documented
- [x] Can instantiate StripeService

---

### Task 2: Copy Payment Verification Service (30 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/payment_verification.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/payment_verification.py`

**Actions**:

1. Copy the file:

   ```bash
   cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/payment_verification.py \
      /home/carlos/projects/cv-match/backend/app/services/payment_verification.py
   ```

2. Update imports

3. Ensure it integrates with Stripe service

4. Test import:
   ```bash
   docker compose exec backend python -c "
   from app.services.payment_verification import PaymentVerificationService
   print('✅ PaymentVerificationService imported')
   "
   ```

**Success Criteria**:

- [x] File copied
- [x] Imports working
- [x] Integrates with StripeService
- [x] Can verify payment status

---

### Task 3: Verify Security Configuration (30 min)

**Critical Security Checklist**:

1. **Webhook Signature Verification**:

   ```python
   # Verify this exists in stripe_service.py
   def verify_webhook_signature(self, payload: str, sig_header: str) -> bool:
       try:
           event = stripe.Webhook.construct_event(
               payload, sig_header, self.webhook_secret
           )
           return True
       except stripe.error.SignatureVerificationError:
           return False
   ```

2. **Idempotency Key Usage**:

   ```python
   # Verify idempotency keys are used
   stripe.PaymentIntent.create(
       idempotency_key=f"optimization_{optimization_id}",
       # ... other params
   )
   ```

3. **No Sensitive Data in Logs**:

   ```python
   # Check that card details are NEVER logged
   logger.info(f"Payment succeeded for user {user_id}")  # ✅ OK
   logger.info(f"Card: {card_number}")  # ❌ NEVER DO THIS
   ```

4. **HTTPS Only**:
   - Verify webhook endpoint will use HTTPS in production
   - Document this requirement

**Success Criteria**:

- [x] Webhook signature verification present
- [x] Idempotency keys used
- [x] No sensitive data logging
- [x] HTTPS requirement documented

---

## 🔧 Technical Details

### Stripe Service Key Methods

The stripe_service.py should have these critical methods:

```python
class StripeService:
    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        stripe.api_key = self.api_key

    async def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: str,
        metadata: dict
    ) -> str:
        """Create Stripe Checkout session"""
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata=metadata
        )
        return session.id

    async def verify_payment(self, session_id: str) -> bool:
        """Verify payment was successful"""
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == "paid"

    def verify_webhook_signature(
        self,
        payload: str,
        sig_header: str
    ) -> Optional[stripe.Event]:
        """Verify webhook signature and return event"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return None
```

---

### Payment Verification Pattern

```python
class PaymentVerificationService:
    def __init__(self):
        self.stripe_service = StripeService()

    async def verify_and_activate(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """Verify payment and activate credits"""
        # Verify payment succeeded
        if not await self.stripe_service.verify_payment(session_id):
            return False

        # Add credits to user (handled in usage_limit_service)
        # Log for audit trail
        logger.info(f"Payment verified for user {user_id}, session {session_id}")

        return True
```

---

## 🚨 Security Requirements (CRITICAL)

### 1. Never Trust Client

```python
# ❌ BAD - Trusting client
@router.post("/process-payment")
async def process_payment(amount: float, user_id: str):
    # Client could send fake amount!
    pass

# ✅ GOOD - Verify with Stripe
@router.post("/process-payment")
async def process_payment(session_id: str):
    session = stripe.checkout.Session.retrieve(session_id)
    amount = session.amount_total  # Trust Stripe, not client
    pass
```

### 2. Always Verify Webhooks

```python
# ❌ BAD - Processing unverified webhook
@router.post("/webhooks/stripe")
async def webhook(request: Request):
    data = await request.json()
    # Process directly - DANGEROUS!
    await process_payment(data)

# ✅ GOOD - Verify signature first
@router.post("/webhooks/stripe")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe_service.verify_webhook_signature(payload, sig_header)
    if not event:
        raise HTTPException(401, "Invalid signature")

    await process_payment(event.data.object)
```

### 3. Use Idempotency

```python
# ✅ GOOD - Prevents double-charging
def add_credits(user_id: str, amount: int, payment_id: str):
    # Check if already processed
    existing = db.query(CreditTransaction).filter_by(payment_id=payment_id).first()
    if existing:
        logger.info(f"Payment {payment_id} already processed")
        return existing

    # Process payment
    transaction = CreditTransaction(
        user_id=user_id,
        amount=amount,
        payment_id=payment_id
    )
    db.add(transaction)
    db.commit()
    return transaction
```

---

## 📊 Verification Checklist

```bash
cd /home/carlos/projects/cv-match/backend

# 1. Verify files exist
ls -la app/services/stripe_service.py
ls -la app/services/payment_verification.py

# 2. Test imports
docker compose exec backend python -c "
from app.services.stripe_service import StripeService
from app.services.payment_verification import PaymentVerificationService
print('✅ All payment services import')
"

# 3. Verify Stripe package
docker compose exec backend python -c "
import stripe
print(f'✅ Stripe version: {stripe.__version__}')
"

# 4. Check environment variables
docker compose exec backend python -c "
import os
required = ['STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET']
for var in required:
    value = os.getenv(var, 'NOT_SET')
    status = '✅' if value != 'NOT_SET' else '❌'
    print(f'{status} {var}: {value[:20]}...' if value != 'NOT_SET' else f'{status} {var}: NOT_SET')
"

# 5. Test Stripe API connection (use test key)
docker compose exec backend python -c "
import stripe
import os
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
try:
    stripe.Account.retrieve()
    print('✅ Stripe API connection successful')
except Exception as e:
    print(f'❌ Stripe API error: {e}')
"
```

---

## 📝 Deliverables

### Files to Create:

1. `/backend/app/services/stripe_service.py`
2. `/backend/app/services/payment_verification.py`

### Files to Update:

1. `/backend/.env` - Add Stripe keys
2. `/backend/pyproject.toml` - Add stripe dependency (if missing)
3. `/backend/app/services/__init__.py` - Export new services

### Documentation to Create:

- `PAYMENT_SETUP.md` - How to configure Stripe
- Security checklist for payment handling

### Git Commit:

```bash
git add backend/app/services/stripe_service.py
git add backend/app/services/payment_verification.py
git add backend/.env.example  # Don't commit real .env!
git add backend/pyproject.toml
git commit -m "feat(payments): Add Stripe payment services

- Add StripeService for payment processing
- Add PaymentVerificationService for security
- Configure webhook signature verification
- Add idempotency key support
- Support BRL currency
- Implement security best practices

Security:
- Webhook signature verification ✅
- Idempotency keys ✅
- No sensitive data logging ✅
- HTTPS requirement documented ✅

Related: P1 Payment Integration Phase 1
Tested: Imports verified, Stripe API connected"
```

---

## ⏱️ Timeline

- **00:00-01:00**: Task 1 (Copy Stripe service)
- **01:00-01:30**: Task 2 (Copy payment verification)
- **01:30-02:00**: Task 3 (Security verification)

**Total**: 2 hours

---

## 🎯 Success Definition

Mission complete when:

1. Both services copied and working
2. Stripe package installed
3. Environment variables configured
4. Can connect to Stripe API (test mode)
5. Security checklist verified
6. All imports working
7. Ready for webhook implementation (Phase 2)

---

## 🔄 Handoff to Next Phase

After completion, notify:

- **database-architect**: Payment services ready, need tables for usage tracking
- **backend-specialist**: Services ready for API endpoint integration

**Provide**:

- ✅ StripeService interface
- ✅ PaymentVerificationService interface
- ✅ Environment variables needed
- ✅ Security requirements documented

---

## ⚠️ Critical Warnings

1. **Never commit `.env` file** - Use `.env.example` instead
2. **Test mode only initially** - Use `sk_test_` keys until production
3. **Verify BRL support** - Ensure Stripe account supports Brazilian Real
4. **HTTPS required** - Webhooks won't work with HTTP in production
5. **Idempotency is not optional** - Financial integrity depends on it

---

**Status**: Ready for deployment 🚀
**Risk Level**: 🔴 HIGH (Financial)
**Review Required**: YES (Security review before production)
