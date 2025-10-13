# 🎯 P1.5 Phase 1.1: Subscription Pricing Configuration

**Agent**: payment-specialist
**Phase**: 1 (Parallel execution)
**Time Estimate**: 2 hours
**Dependencies**: None - can start immediately

**Why payment-specialist?** This task involves Stripe subscription products/pricing setup, which is payment infrastructure. The payment-specialist is the expert for all Stripe integration tasks.

---

## 📋 Mission

Create the subscription pricing configuration that defines the **Flow** subscription tiers for CV-Match. This builds on the existing credit-based (Flex) system to complete the Hybrid business model.

**What You're Building:**

- Subscription tier definitions (Flow Starter, Pro, Business, Enterprise)
- Pricing configuration aligned with business model
- Integration with existing pricing.py
- Stripe subscription product/price setup

---

## 🔍 Context

### Current State

- ✅ Credit-based pricing exists in `/backend/app/config/pricing.py`
- ✅ Stripe integration for one-time payments in `/backend/app/services/stripe_service.py`
- ❌ No subscription tiers defined
- ❌ No monthly recurring billing

### Target State

- ✅ Hybrid model: Credits (Flex) + Subscriptions (Flow)
- ✅ 4 subscription tiers: Starter, Pro, Business, Enterprise
- ✅ Monthly recurring billing via Stripe
- ✅ Usage limits per tier with rollover

### Reference Architecture

You're adapting **QuoteKit's advanced Stripe subscription system** to CV-Match:

- QuoteKit: `/home/carlos/projects/QuoteKit/src/constants/stripe-prices.ts`
- QuoteKit: `/home/carlos/projects/QuoteKit/src/features/account/actions/subscription-actions.ts`

---

## 🛠️ CRITICAL: Tools You MUST Use

### 1. Context7 - Library Documentation

**ALWAYS check documentation before implementing!**

```bash
# Get Stripe subscription documentation
context7:resolve-library-id --library-name="stripe"
context7:get-library-docs --library-id="/stripe/stripe-python" --topic="subscriptions"
context7:get-library-docs --library-id="/stripe/stripe-python" --topic="subscription pricing"
```

### 2. Python REPL Testing

Test your config as you build:

```bash
docker compose exec backend python -c "
from app.config.pricing import pricing_config
print(pricing_config.get_subscription_tiers())
"
```

---

## 📝 Implementation Tasks

### Task 1: Update Pricing Configuration (30 min)

**File**: `/backend/app/config/pricing.py`

**What to do:**

1. Add `is_subscription` field to `PricingTier` dataclass
2. Add `analyses_per_month` field (for subscription usage limits)
3. Add `rollover_limit` field (how many unused analyses can rollover)
4. Create subscription tier definitions

**Expected Result:**

```python
@dataclass
class PricingTier:
    """Pricing tier configuration for Brazilian market."""
    id: str
    name: str
    description: str
    price: int  # Price in cents (BRL) - monthly for subscriptions
    credits: int = 0  # For credit packages
    analyses_per_month: int = 0  # For subscriptions
    rollover_limit: int = 0  # For subscriptions
    is_subscription: bool = False  # True for Flow, False for Flex
    currency: str = "brl"
    stripe_price_id: str | None = None
    features: List[str] | None = None
    popular: bool = False
```

**Add subscription tiers to the config:**

```python
class BrazilianPricingConfig:
    def __init__(self):
        # ... existing code ...

        # Add subscription tiers (Flow)
        self.tiers.update({
            # FLEX PACKAGES (existing - keep these!)
            # "free", "basic", "pro", "enterprise" remain unchanged

            # FLOW SUBSCRIPTIONS (new!)
            "flow_starter": PricingTier(
                id="flow_starter",
                name="Flow Starter",
                description="Assinatura mensal para quem busca oportunidades regularmente",
                price=2490,  # R$ 24,90/month in cents
                analyses_per_month=15,
                rollover_limit=5,
                is_subscription=True,
                currency="brl",
                stripe_price_id=None,  # Will be set after Stripe setup
                features=[
                    "15 otimizações por mês",
                    "Rollover de até 5 análises",
                    "Análise avançada com IA",
                    "Suporte por email",
                    "Cancele quando quiser"
                ],
            ),
            "flow_pro": PricingTier(
                id="flow_pro",
                name="Flow Pro",
                description="Plano profissional para quem busca muitas oportunidades",
                price=4990,  # R$ 49,90/month in cents
                analyses_per_month=60,
                rollover_limit=30,
                is_subscription=True,
                currency="brl",
                stripe_price_id=None,
                popular=True,
                features=[
                    "60 otimizações por mês",
                    "Rollover de até 30 análises",
                    "Análise avançada com IA",
                    "Modelos de currículo profissionais",
                    "Suporte prioritário",
                    "Análise de mercado",
                    "Cancele quando quiser"
                ],
            ),
            "flow_business": PricingTier(
                id="flow_business",
                name="Flow Business",
                description="Para recrutadores e uso intensivo",
                price=12990,  # R$ 129,90/month in cents
                analyses_per_month=250,
                rollover_limit=100,
                is_subscription=True,
                currency="brl",
                stripe_price_id=None,
                features=[
                    "250 otimizações por mês",
                    "Rollover de até 100 análises",
                    "5 usuários incluídos",
                    "API de integração",
                    "Dashboard avançado",
                    "Suporte dedicado",
                    "Cancele quando quiser"
                ],
            ),
            "flow_enterprise": PricingTier(
                id="flow_enterprise",
                name="Flow Enterprise",
                description="Solução personalizada para grandes volumes",
                price=0,  # Custom pricing
                analyses_per_month=-1,  # Unlimited
                rollover_limit=-1,  # Unlimited
                is_subscription=True,
                currency="brl",
                stripe_price_id=None,
                features=[
                    "Otimizações ilimitadas",
                    "Usuários ilimitados",
                    "Integrações personalizadas",
                    "White-label disponível",
                    "SLA 99,9%",
                    "CSM dedicado",
                    "Suporte 24/7"
                ],
            ),
        })
```

### Task 2: Add Helper Methods (20 min)

Add utility methods to `BrazilianPricingConfig`:

```python
def get_subscription_tiers(self) -> Dict[str, PricingTier]:
    """Get only subscription tiers (Flow)."""
    return {
        tier_id: tier
        for tier_id, tier in self.tiers.items()
        if tier.is_subscription
    }

def get_credit_tiers(self) -> Dict[str, PricingTier]:
    """Get only credit tiers (Flex)."""
    return {
        tier_id: tier
        for tier_id, tier in self.tiers.items()
        if not tier.is_subscription
    }

def get_tier_by_type(self, tier_id: str, tier_type: str) -> PricingTier | None:
    """
    Get tier by ID with type validation.
    tier_type: 'credit' or 'subscription'
    """
    tier = self.get_tier(tier_id)
    if not tier:
        return None

    if tier_type == "subscription" and not tier.is_subscription:
        return None
    if tier_type == "credit" and tier.is_subscription:
        return None

    return tier

def validate_tier(self, tier_id: str) -> tuple[bool, str]:
    """
    Validate if a tier ID is valid and active.
    Returns: (is_valid, error_message)
    """
    tier = self.get_tier(tier_id)

    if not tier:
        return False, f"Invalid tier ID: {tier_id}"

    if tier.price == 0 and tier_id not in ["free", "flow_enterprise"]:
        return False, f"Invalid pricing for tier: {tier_id}"

    return True, ""

def get_tier_usage_limit(self, tier_id: str) -> int:
    """Get monthly usage limit for a tier (-1 = unlimited)."""
    tier = self.get_tier(tier_id)
    if not tier:
        return 0

    if tier.is_subscription:
        return tier.analyses_per_month
    else:
        return tier.credits
```

### Task 3: Create Stripe Products & Prices (45 min)

**Create a new script**: `/backend/scripts/setup_stripe_subscriptions.py`

```python
"""
Setup Stripe subscription products and prices for CV-Match.
Run this script to create Flow subscription tiers in Stripe.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import stripe
from dotenv import load_dotenv
from app.config.pricing import pricing_config

load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_subscription_products():
    """Create Stripe products and prices for Flow subscriptions."""

    print("🚀 Creating Stripe subscription products...")
    print(f"Mode: {'TEST' if stripe.api_key.startswith('sk_test_') else 'LIVE'}")
    print()

    # Get subscription tiers
    subscription_tiers = pricing_config.get_subscription_tiers()

    created_products = []
    created_prices = []

    for tier_id, tier in subscription_tiers.items():
        # Skip enterprise (custom pricing)
        if tier_id == "flow_enterprise":
            print(f"⏭️  Skipping {tier.name} (custom pricing)")
            continue

        print(f"📦 Creating product: {tier.name}")

        # Create product
        try:
            product = stripe.Product.create(
                name=tier.name,
                description=tier.description,
                metadata={
                    "tier_id": tier_id,
                    "market": "brazil",
                    "type": "subscription",
                    "analyses_per_month": str(tier.analyses_per_month),
                    "rollover_limit": str(tier.rollover_limit),
                }
            )

            print(f"  ✅ Product created: {product.id}")
            created_products.append(product)

            # Create recurring price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=tier.price,
                currency=tier.currency,
                recurring={"interval": "month"},
                metadata={
                    "tier_id": tier_id,
                    "market": "brazil",
                }
            )

            print(f"  ✅ Price created: {price.id} (R$ {tier.price/100:.2f}/mês)")
            created_prices.append(price)

            # Store price ID
            print(f"  💾 Update tier '{tier_id}' with stripe_price_id: {price.id}")
            print()

        except stripe.StripeError as e:
            print(f"  ❌ Error creating {tier.name}: {e}")
            print()

    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print(f"Products created: {len(created_products)}")
    print(f"Prices created: {len(created_prices)}")
    print()
    print("📝 Next steps:")
    print("1. Update pricing.py with the stripe_price_id values above")
    print("2. Commit the changes")
    print("3. Proceed to Phase 1.2 (Subscription Management Service)")
    print()

    return created_products, created_prices

if __name__ == "__main__":
    create_subscription_products()
```

**Run the script:**

```bash
cd /home/carlos/projects/cv-match/backend
python scripts/setup_stripe_subscriptions.py
```

**Update pricing.py with the generated price IDs** (copy from script output).

### Task 4: Add Pricing API Endpoint (25 min)

**Create**: `/backend/app/api/pricing.py`

```python
"""
Pricing API endpoints for CV-Match.
Returns both credit packages (Flex) and subscriptions (Flow).
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.config.pricing import pricing_config

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.get("/")
async def get_all_pricing() -> Dict[str, Any]:
    """
    Get all pricing tiers (credits + subscriptions).
    Returns organized structure for frontend.
    """
    all_tiers = pricing_config.get_all_tiers()

    # Separate into categories
    credit_tiers = {
        tier_id: tier
        for tier_id, tier in all_tiers.items()
        if not tier.get("is_subscription", False)
    }

    subscription_tiers = {
        tier_id: tier
        for tier_id, tier in all_tiers.items()
        if tier.get("is_subscription", False)
    }

    return {
        "success": True,
        "data": {
            "credits": credit_tiers,
            "subscriptions": subscription_tiers,
            "currency": "brl",
            "market": "brazil",
        }
    }


@router.get("/subscriptions")
async def get_subscription_pricing() -> Dict[str, Any]:
    """Get only subscription pricing (Flow tiers)."""
    subscription_tiers = pricing_config.get_subscription_tiers()

    return {
        "success": True,
        "data": {
            tier_id: {
                "id": tier.id,
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "analyses_per_month": tier.analyses_per_month,
                "rollover_limit": tier.rollover_limit,
                "currency": tier.currency,
                "stripe_price_id": tier.stripe_price_id,
                "features": tier.features or [],
                "popular": tier.popular,
            }
            for tier_id, tier in subscription_tiers.items()
        }
    }


@router.get("/credits")
async def get_credit_pricing() -> Dict[str, Any]:
    """Get only credit pricing (Flex packages)."""
    credit_tiers = pricing_config.get_credit_tiers()

    return {
        "success": True,
        "data": {
            tier_id: {
                "id": tier.id,
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "credits": tier.credits,
                "currency": tier.currency,
                "stripe_price_id": tier.stripe_price_id,
                "features": tier.features or [],
                "popular": tier.popular,
            }
            for tier_id, tier in credit_tiers.items()
        }
    }


@router.get("/tier/{tier_id}")
async def get_tier_details(tier_id: str) -> Dict[str, Any]:
    """Get details for a specific tier."""
    tier = pricing_config.get_tier(tier_id)

    if not tier:
        raise HTTPException(status_code=404, detail=f"Tier not found: {tier_id}")

    return {
        "success": True,
        "data": {
            "id": tier.id,
            "name": tier.name,
            "description": tier.description,
            "price": tier.price,
            "currency": tier.currency,
            "is_subscription": tier.is_subscription,
            "credits": tier.credits if not tier.is_subscription else None,
            "analyses_per_month": tier.analyses_per_month if tier.is_subscription else None,
            "rollover_limit": tier.rollover_limit if tier.is_subscription else None,
            "stripe_price_id": tier.stripe_price_id,
            "features": tier.features or [],
            "popular": tier.popular,
        }
    }
```

**Register the router in main.py:**

```python
# In app/main.py
from app.api.pricing import router as pricing_router

app.include_router(pricing_router)
```

---

## ✅ Verification Checklist

After completing all tasks:

### 1. Config Validation

```bash
cd /home/carlos/projects/cv-match/backend

# Test config loads correctly
docker compose exec backend python -c "
from app.config.pricing import pricing_config
print('Total tiers:', len(pricing_config.tiers))
print('Subscription tiers:', len(pricing_config.get_subscription_tiers()))
print('Credit tiers:', len(pricing_config.get_credit_tiers()))
print()
print('Flow Pro:')
tier = pricing_config.get_tier('flow_pro')
print('  Price:', tier.price, 'cents')
print('  Analyses/month:', tier.analyses_per_month)
print('  Rollover:', tier.rollover_limit)
print('  Is subscription:', tier.is_subscription)
"
```

**Expected output:**

```
Total tiers: 8
Subscription tiers: 4
Credit tiers: 4

Flow Pro:
  Price: 4990 cents
  Analyses/month: 60
  Rollover: 30
  Is subscription: True
```

### 2. Stripe Products Created

```bash
# List Stripe products
stripe products list --limit 10
```

Should see Flow Starter, Pro, Business products.

### 3. API Endpoint Working

```bash
# Test pricing endpoint
curl http://localhost:8000/api/pricing/subscriptions

# Should return JSON with flow_starter, flow_pro, flow_business, flow_enterprise
```

### 4. Type Checking

```bash
docker compose exec backend mypy app/config/pricing.py
docker compose exec backend mypy app/api/pricing.py
```

No errors should appear.

---

## 🚨 Common Issues & Solutions

### Issue 1: Stripe API Key Not Set

**Error**: `ValueError: STRIPE_SECRET_KEY environment variable is required`

**Solution**:

```bash
# Check .env file
cat backend/.env | grep STRIPE_SECRET_KEY

# Should show: STRIPE_SECRET_KEY=sk_test_...
```

### Issue 2: Import Errors

**Error**: `ModuleNotFoundError: No module named 'app.config.pricing'`

**Solution**:

```bash
# Restart backend
docker compose restart backend

# Check imports
docker compose exec backend python -c "from app.config.pricing import pricing_config; print('OK')"
```

### Issue 3: Stripe Products Already Exist

**Error**: `stripe.error.InvalidRequestError: A product with this ID already exists`

**Solution**:

```bash
# List existing products
stripe products list

# Either:
# 1. Use existing product IDs, OR
# 2. Archive old products: stripe products update <product_id> --active false
```

---

## 📊 Success Criteria

Phase 1.1 is complete when:

- ✅ All 4 subscription tiers defined in pricing.py
- ✅ Helper methods implemented and tested
- ✅ Stripe products and prices created
- ✅ Pricing API endpoint returns correct data
- ✅ Type checking passes
- ✅ All verification tests pass
- ✅ Code committed to git

---

## 🎯 Next Step

After completing Phase 1.1:
→ **Proceed to Phase 1.2**: Subscription Management Service
→ **Prompt**: `02-subscription-management-service.md`

---

## 💡 Tips

1. **Use Context7** for Stripe API documentation - don't guess!
2. **Test incrementally** after each task
3. **Keep pricing.py organized** - group Flex and Flow tiers clearly
4. **Save Stripe IDs** immediately after creation
5. **Commit after each task** - easier to rollback if needed

---

**Time check**: This should take ~2 hours. If taking longer, ask for help!

**Remember**: This is parallel with Phase 1.2, so another agent can start that while you work on this.

Good luck! 🚀
