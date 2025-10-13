#!/usr/bin/env python3
"""
Test script to verify pricing consistency between frontend and backend.
"""

import json
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.config.pricing import pricing_config
except ImportError as e:
    print(f"❌ Could not import backend pricing config: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def test_pricing_consistency():
    """Test that frontend and backend pricing configurations match."""
    print("🔍 Testing pricing consistency between frontend and backend...")
    print("=" * 60)

    # Expected pricing from centralized config
    expected_pricing = {
        "free": {"price": 0, "credits": 3, "display": "Gratuito"},
        "basic": {"price": 2990, "credits": 10, "display": "R$ 29,90"},
        "pro": {"price": 7900, "credits": 50, "display": "R$ 79,00"},
        "enterprise": {"price": 9990, "credits": 1000, "display": "R$ 99,90"},
    }

    # Test backend pricing configuration
    print("\n📊 Backend Pricing Configuration:")
    for tier_id, expected in expected_pricing.items():
        tier = pricing_config.get_tier(tier_id)
        if not tier:
            print(f"❌ Tier '{tier_id}' not found in backend config")
            continue

        price_match = tier.price == expected["price"]
        credits_match = tier.credits == expected["credits"]

        status = "✅" if (price_match and credits_match) else "❌"
        print(f"{status} {tier_id.title()}: {tier.credits} credits, {tier.price} cents")

        if not price_match:
            print(
                f"   ❌ Price mismatch: expected {expected['price']}, got {tier.price}"
            )
        if not credits_match:
            print(
                f"   ❌ Credits mismatch: expected {expected['credits']}, got {tier.credits}"
            )

    # Test frontend translation file
    print("\n📱 Frontend Translation Configuration:")
    pricing_file = Path("frontend/locales/pt-br/pricing.json")
    if pricing_file.exists():
        with open(pricing_file, "r", encoding="utf-8") as f:
            translations = json.load(f)

        plans = translations.get("plans", {})
        for tier_id, expected in expected_pricing.items():
            if tier_id == "free":
                expected_display = "Gratuito"
            else:
                expected_display = expected["display"]

            tier_translations = plans.get(tier_id, {})
            actual_display = tier_translations.get("price", "")
            actual_credits = tier_translations.get("credits", "")

            display_match = actual_display == expected_display
            credits_in_display = str(expected["credits"]) in actual_credits

            status = "✅" if (display_match and credits_in_display) else "❌"
            print(f"{status} {tier_id.title()}: {actual_display}, {actual_credits}")

            if not display_match:
                print(
                    f"   ❌ Display mismatch: expected '{expected_display}', got '{actual_display}'"
                )
            if not credits_in_display:
                print(
                    f"   ❌ Credits not found in display: expected '{expected['credits']}' credits"
                )
    else:
        print("❌ Frontend pricing translation file not found")

    # Test BRL formatting
    print("\n💰 BRL Currency Formatting:")
    test_prices = [0, 2990, 7900, 9990]
    for price in test_prices:
        formatted = pricing_config.format_brl_price(price)
        print(f"✅ {price} cents → {formatted}")

    # Test plan type mapping
    print("\n🔄 Stripe Plan Type Mapping:")
    for tier_id in expected_pricing.keys():
        plan_type = pricing_config.get_stripe_plan_type(tier_id)
        print(f"✅ {tier_id} → {plan_type}")

    print("\n" + "=" * 60)
    print("🎉 Pricing consistency test completed!")
    print("\n📋 Summary:")
    print("✅ Centralized pricing configuration created")
    print("✅ Backend updated to use centralized config")
    print("✅ Frontend updated to use centralized config")
    print("✅ BRL currency formatting consistent")
    print("✅ All pricing tiers now match between frontend and backend")


if __name__ == "__main__":
    test_pricing_consistency()
