# Stripe Test Mode Setup Guide for CV-Match Brazilian Market

## Overview

This guide provides comprehensive instructions for setting up and testing Stripe payments in test mode for the CV-Match Brazilian market SaaS application.

## 🎯 Objectives

- Configure Stripe test mode for Brazilian market (BRL currency)
- Set up webhook endpoints and signature verification
- Test all payment scenarios including Brazilian-specific requirements
- Validate security and error handling
- Ensure comprehensive test coverage

## 📋 Prerequisites

1. **Stripe Account**: Active Stripe account with test mode access
2. **Local Development**: CV-Match development environment running
3. **Database**: Local Supabase instance with payment tables
4. **Test Tools**: ngrok or similar for webhook testing

## 🚀 Quick Setup

### 1. Stripe Test Mode Configuration

```bash
# 1. Log into Stripe Dashboard
# https://dashboard.stripe.com/test/dashboard

# 2. Get your test keys
STRIPE_SECRET_KEY=sk_test_... (from Developers > API keys)
STRIPE_PUBLISHABLE_KEY=pk_test_... (from Developers > API keys)

# 3. Update your .env file
cp .env.example .env
# Edit .env with your test keys
```

### 2. Environment Configuration

```bash
# Required environment variables for test mode
STRIPE_SECRET_KEY=sk_test_51234567890abcdefghijklmnopqrstuvwxyz
STRIPE_WEBHOOK_SECRET=whsec_test_51234567890abcdefghijklmnopqrstuvwxyz
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51234567890abcdefghijklmnopqrstuvwxyz

# Brazilian market configuration
NEXT_PUBLIC_DEFAULT_CURRENCY=brl
NEXT_PUBLIC_DEFAULT_COUNTRY=BR
NEXT_PUBLIC_DEFAULT_LOCALE=pt-br
```

### 3. Database Setup

```bash
# Apply payment tables migration
supabase db push

# Verify tables were created
supabase db list
```

## 🛠️ Complete Test Mode Setup

### Step 1: Configure Stripe Account

1. **Enable Test Mode**
   - Go to Stripe Dashboard
   - Toggle "Viewing test data" ON
   - Confirm you're in test mode (URL shows `/test`)

2. **Set Up Brazilian Business Profile**

   ```bash
   # In Stripe Dashboard > Settings > Business details
   Business name: "CV-Match Brasil"
   Country: Brazil
   Currency: BRL (Brazilian Real)
   ```

3. **Configure Payment Methods**
   - Enable: Credit/Debit Cards
   - For future: PIX (when available in test mode)
   - For future: Boleto Bancário

### Step 2: Webhook Configuration

1. **Set Up Webhook Endpoint**

   ```bash
   # Start local development server
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Expose local server with ngrok
   ngrok http 8000

   # Get ngrok URL and configure in Stripe
   # Stripe Dashboard > Developers > Webhooks > Add endpoint
   # Endpoint URL: https://your-ngrok-url.ngrok.io/api/webhooks/stripe
   ```

2. **Configure Webhook Events**

   ```bash
   # Select these events for Brazilian market testing:
   - checkout.session.completed
   - invoice.payment_succeeded
   - invoice.payment_failed
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - payment_intent.succeeded
   - payment_intent.payment_failed
   ```

3. **Get Webhook Secret**
   ```bash
   # From webhook endpoint details
   # Copy "Signing secret" (starts with whsec_test_)
   # Add to .env file
   STRIPE_WEBHOOK_SECRET=whsec_test_...
   ```

### Step 3: Test Payment Products Setup

1. **Create Test Products**

   ```python
   # Use the Stripe CLI or Dashboard to create test products
   # Product 1: "CV-Match Plano Profissional"
   # - Price: R$ 29,90 (2990 cents)
   # - Currency: BRL
   # - Recurring: Monthly

   # Product 2: "CV-Match Plano Empresarial"
   # - Price: R$ 99,90 (9990 cents)
   # - Currency: BRL
   # - Recurring: Monthly

   # Product 3: "CV-Match Acesso Vitalício"
   # - Price: R$ 297,00 (29700 cents)
   # - Currency: BRL
   # - One-time payment
   ```

2. **Verify Test Products**
   ```bash
   # Test API endpoint to verify pricing
   curl http://localhost:8000/api/payments/pricing
   ```

## 🧪 Testing Scenarios

### 1. Basic Payment Flow Test

```bash
# Test 1: Create Checkout Session
curl -X POST "http://localhost:8000/api/payments/create-checkout-session" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "user_email": "test@exemplo.com.br",
    "plan_type": "pro"
  }'

# Expected Response:
{
  "success": true,
  "session_id": "cs_test_...",
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
  "plan_type": "pro",
  "currency": "brl",
  "amount": 2990
}
```

### 2. Webhook Processing Test

```bash
# Test 2: Health Check
curl http://localhost:8000/api/webhooks/stripe/health

# Expected Response:
{
  "status": "healthy",
  "stripe_configured": true,
  "test_mode": true,
  "currency": "brl",
  "country": "BR",
  "locale": "pt-BR"
}

# Test 3: Test Webhook Processing
curl -X POST "http://localhost:8000/api/webhooks/stripe/test"

# Expected Response:
{
  "success": true,
  "message": "Test webhook processed successfully",
  "test_event_id": "evt_test_1234567890",
  "processing_result": {
    "success": true,
    "payment_id": "payment_123"
  }
}
```

### 3. Brazilian Payment Methods Test

```bash
# Test 4: Get Test Payment Methods
curl http://localhost:8000/api/webhooks/stripe/test-payment-methods

# Expected Response:
{
  "success": true,
  "payment_methods": [
    {
      "type": "card",
      "name": "Cartão de Crédito",
      "test_cards": [
        {
          "number": "4242424242424242",
          "brand": "Visa",
          "status": "success",
          "description": "Visa sucesso"
        }
      ]
    }
  ],
  "currency": "brl",
  "country": "BR"
}
```

### 4. Comprehensive Test Suite

```bash
# Run the complete test suite
cd backend
python run_webhook_tests.py all

# Run Brazilian-specific tests
python run_webhook_tests.py brazilian

# Run with coverage
python run_webhook_tests.py coverage
```

## 🃏 Test Cards for Brazilian Market

### Successful Payment Cards

| Card Number      | Brand      | Description        |
| ---------------- | ---------- | ------------------ |
| 4242424242424242 | Visa       | Successful payment |
| 5555555555554444 | Mastercard | Successful payment |
| 4000002500003155 | Visa       | Requires 3D Secure |
| 4000000000000077 | Mastercard | Requires 3D Secure |

### Declined Payment Cards

| Card Number      | Brand | Decline Reason     |
| ---------------- | ----- | ------------------ |
| 4000000000000002 | Visa  | Generic decline    |
| 4000000000009995 | Visa  | Insufficient funds |
| 4000000000009987 | Visa  | Lost card          |
| 4000000000009979 | Visa  | Stolen card        |

### Special Test Scenarios

```bash
# Test 5: Payment Intent with 3D Secure
curl -X POST "http://localhost:8000/api/payments/create-payment-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "user_email": "test@exemplo.com.br",
    "amount": 2990,
    "metadata": {
      "test_scenario": "3d_secure",
      "card": "4000002500003155"
    }
  }'
```

## 🔍 Validation Checklist

### ✅ Configuration Validation

- [ ] Stripe API keys are test mode (start with `sk_test_`/`pk_test_`)
- [ ] Webhook secret configured (starts with `whsec_test_`)
- [ ] BRL currency set as default
- [ ] Brazilian locale (pt-br) configured
- [ ] Webhook endpoint accessible via ngrok
- [ ] Database tables created successfully

### ✅ Payment Flow Validation

- [ ] Checkout session creation works
- [ ] Brazilian pricing tiers are correct
- [ ] Payment forms display in Portuguese
- [ ] BRL currency formatting correct (R$ XX,XX)
- [ ] Test cards process successfully
- [ ] Declined cards handle errors gracefully

### ✅ Webhook Validation

- [ ] Webhook signature verification works
- [ ] All event types process correctly
- [ ] Idempotency protection prevents duplicates
- [ ] Error scenarios handled properly
- [ ] Audit trail logs all events

### ✅ Brazilian Market Validation

- [ ] Product names in Portuguese
- [ ] Descriptions localized for Brazil
- [ ] Pricing appropriate for Brazilian market
- [ ] Error messages in Portuguese
- [ ] Email templates localized

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "Invalid webhook signature" Error

```bash
# Solution: Verify webhook secret matches Stripe dashboard
# Check .env file:
echo $STRIPE_WEBHOOK_SECRET

# Recreate webhook if needed
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

#### 2. "No such customer" Error

```bash
# Solution: Create customer first
curl -X POST "http://localhost:8000/api/payments/create-customer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "user_email": "test@exemplo.com.br",
    "name": "João Silva"
  }'
```

#### 3. Currency not supported error

```bash
# Solution: Ensure BRL is configured in Stripe
# In Stripe Dashboard > Settings > Payments
# Verify BRL is enabled for your account
```

#### 4. Webhook not receiving events

```bash
# Solution: Check ngrok and webhook configuration
# Verify ngrok is running
curl http://localhost:4040/api/tunnels

# Test webhook endpoint directly
curl -X POST "http://localhost:8000/api/webhooks/stripe/test"
```

## 📊 Test Reports

### Automated Test Results

After running the test suite, you should see:

```bash
# Expected test results
tests/unit/test_webhook_service.py ....... [100%]
tests/integration/test_payment_webhooks.py ....... [100%]

8 passed in 2.34s
```

### Manual Test Results

Document your manual test results:

```markdown
## Test Results - [Date]

### Payment Flow Tests

- [x] Checkout session creation: ✅ PASS
- [x] Payment with Visa card: ✅ PASS
- [x] Payment with Mastercard: ✅ PASS
- [x] 3D Secure flow: ✅ PASS
- [x] Declined card handling: ✅ PASS

### Webhook Tests

- [x] checkout.session.completed: ✅ PASS
- [x] invoice.payment_succeeded: ✅ PASS
- [x] invoice.payment_failed: ✅ PASS
- [x] customer.subscription.created: ✅ PASS
- [x] customer.subscription.updated: ✅ PASS
- [x] customer.subscription.deleted: ✅ PASS

### Brazilian Market Tests

- [x] BRL currency display: ✅ PASS
- [x] Portuguese localization: ✅ PASS
- [x] Brazilian pricing: ✅ PASS
- [x] Error messages in Portuguese: ✅ PASS
```

## 🚀 Production Readiness

### Pre-Production Checklist

- [ ] All tests passing in test mode
- [ ] Error handling comprehensive
- [ ] Logging and monitoring configured
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Documentation complete

### Production Migration Steps

1. **Switch to Live Mode**

   ```bash
   # Get live keys from Stripe Dashboard
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```

2. **Update Webhook Endpoints**

   ```bash
   # Update webhook URLs to production
   # Configure live webhook endpoints
   # Test with small amounts first
   ```

3. **Monitor Initial Transactions**
   ```bash
   # Closely monitor first live transactions
   # Check webhook processing logs
   # Verify customer success
   ```

## 📚 Additional Resources

### Documentation

- [Stripe Brazil Documentation](https://stripe.com/docs/br)
- [Stripe Test Mode Cards](https://stripe.com/docs/testing#cards)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)

### Tools

- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [ngrok](https://ngrok.com/)
- [Postman](https://www.postman.com/) for API testing

### Support

- Stripe Developer Support
- CV-Match Development Team
- Brazilian Market Specialist

---

**Last Updated**: 2025-01-07
**Version**: 1.0
**Target Market**: Brazil
**Currency**: BRL (Brazilian Real)
