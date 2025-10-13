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
                },
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
                },
            )

            print(f"  ✅ Price created: {price.id} (R$ {tier.price / 100:.2f}/mês)")
            created_prices.append(price)

            # Store price ID
            print(f"  💾 Update tier '{tier_id}' with stripe_price_id: {price.id}")
            print()

        except stripe.StripeError as e:
            print(f"  ❌ Error creating {tier.name}: {e}")
            print()

    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
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
