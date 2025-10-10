#!/usr/bin/env python3
"""
Stripe Test Mode Validation Script for CV-Match Brazilian Market

This script validates the complete Stripe test mode setup including:
- API configuration
- Webhook endpoints
- Brazilian market features
- Payment processing
- Error handling

Usage:
    python test_stripe_setup.py --all          # Run all tests
    python test_stripe_setup.py --config       # Test configuration only
    python test_stripe_setup.py --payments     # Test payment flows only
    python test_stripe_setup.py --webhooks     # Test webhooks only
    python test_stripe_setup.py --brazilian    # Test Brazilian features only
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from typing import Any, Dict

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class Colors:
    """Terminal colors for test output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class StripeTestValidator:
    """Validates Stripe test mode setup for Brazilian market."""

    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.start_time = datetime.now(UTC)

    def log_test(
        self, test_name: str, passed: bool, message: str = "", details: Dict[str, Any] = None
    ):
        """Log a test result."""
        status = (
            f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        )
        print(f"{status} {test_name}")
        if message:
            print(f"    {Colors.BLUE}{message}{Colors.END}")
        if details:
            for key, value in details.items():
                print(f"    {Colors.YELLOW}{key}:{Colors.END} {value}")

        self.test_results.append(
            {
                "test_name": test_name,
                "passed": passed,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    async def test_configuration(self) -> bool:
        """Test Stripe configuration and environment setup."""
        print(f"\n{Colors.BOLD}🔧 Testing Stripe Configuration{Colors.END}")

        config_passed = True

        # Test 1: Environment Variables
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        publishable_key = os.getenv("NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY")

        has_stripe_key = stripe_key and stripe_key.startswith("sk_test_")
        has_webhook_secret = webhook_secret and webhook_secret.startswith("whsec_test_")
        has_publishable_key = publishable_key and publishable_key.startswith("pk_test_")

        self.log_test(
            "Stripe Secret Key (Test Mode)",
            has_stripe_key,
            "Key exists and is in test mode" if has_stripe_key else "Missing or invalid test key",
            {"key_prefix": stripe_key[:7] + "..." if stripe_key else "None"},
        )

        self.log_test(
            "Webhook Secret (Test Mode)",
            has_webhook_secret,
            "Webhook secret configured" if has_webhook_secret else "Missing webhook secret",
            {"secret_prefix": webhook_secret[:8] + "..." if webhook_secret else "None"},
        )

        self.log_test(
            "Publishable Key (Test Mode)",
            has_publishable_key,
            "Frontend key configured" if has_publishable_key else "Missing publishable key",
            {"key_prefix": publishable_key[:7] + "..." if publishable_key else "None"},
        )

        # Test 2: Brazilian Market Configuration
        currency = os.getenv("NEXT_PUBLIC_DEFAULT_CURRENCY", "brl")
        country = os.getenv("NEXT_PUBLIC_DEFAULT_COUNTRY", "BR")
        locale = os.getenv("NEXT_PUBLIC_DEFAULT_LOCALE", "pt-br")

        self.log_test(
            "Brazilian Currency (BRL)",
            currency.lower() == "brl",
            f"Currency set to {currency}",
            {"currency": currency},
        )

        self.log_test(
            "Brazilian Country (BR)",
            country.upper() == "BR",
            f"Country set to {country}",
            {"country": country},
        )

        self.log_test(
            "Brazilian Locale (pt-br)",
            locale.lower() == "pt-br",
            f"Locale set to {locale}",
            {"locale": locale},
        )

        config_passed = all(
            [
                has_stripe_key,
                has_webhook_secret,
                has_publishable_key,
                currency.lower() == "brl",
                country.upper() == "BR",
                locale.lower() == "pt-br",
            ]
        )

        return config_passed

    async def test_api_health(self) -> bool:
        """Test API health and Stripe integration."""
        print(f"\n{Colors.BOLD}🏥 Testing API Health{Colors.END}")

        health_passed = True

        async with httpx.AsyncClient() as client:
            try:
                # Test Payments Health
                response = await client.get(f"{self.base_url}/api/payments/health", timeout=10)
                payments_healthy = response.status_code == 200

                if payments_healthy:
                    data = response.json()
                    stripe_configured = data.get("stripe_configured", False)
                    test_mode = data.get("test_mode", False)

                    self.log_test(
                        "Payments API Health",
                        True,
                        "Payments endpoint healthy",
                        {
                            "stripe_configured": stripe_configured,
                            "test_mode": test_mode,
                            "currency": data.get("currency"),
                            "country": data.get("country"),
                        },
                    )

                    if not stripe_configured:
                        health_passed = False
                    if not test_mode:
                        health_passed = False
                else:
                    self.log_test(
                        "Payments API Health",
                        False,
                        f"HTTP {response.status_code}",
                        {"response_text": response.text[:200]},
                    )
                    health_passed = False

                # Test Webhooks Health
                response = await client.get(
                    f"{self.base_url}/api/webhooks/stripe/health", timeout=10
                )
                webhooks_healthy = response.status_code == 200

                if webhooks_healthy:
                    data = response.json()
                    webhook_configured = data.get("stripe_configured", False)

                    self.log_test(
                        "Webhooks API Health",
                        True,
                        "Webhooks endpoint healthy",
                        {
                            "webhook_configured": webhook_configured,
                            "test_mode": data.get("test_mode"),
                            "currency": data.get("currency"),
                        },
                    )

                    if not webhook_configured:
                        health_passed = False
                else:
                    self.log_test(
                        "Webhooks API Health",
                        False,
                        f"HTTP {response.status_code}",
                        {"response_text": response.text[:200]},
                    )
                    health_passed = False

            except httpx.RequestError as e:
                self.log_test(
                    "API Connection",
                    False,
                    f"Connection error: {str(e)}",
                    {"base_url": self.base_url},
                )
                health_passed = False

        return health_passed

    async def test_pricing(self) -> bool:
        """Test Brazilian pricing configuration."""
        print(f"\n{Colors.BOLD}💰 Testing Brazilian Pricing{Colors.END}")

        pricing_passed = True

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/payments/pricing", timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    pricing = data.get("pricing", {})

                    # Check required plans
                    required_plans = ["free", "pro", "enterprise", "lifetime"]
                    has_all_plans = all(plan in pricing for plan in required_plans)

                    self.log_test(
                        "Brazilian Pricing Plans",
                        has_all_plans,
                        f"Found {len(pricing)} pricing plans",
                        {"plans": list(pricing.keys())},
                    )

                    # Check specific plan configurations
                    if "pro" in pricing:
                        pro_plan = pricing["pro"]
                        pro_price_correct = pro_plan.get("price") == 2990  # R$ 29,90
                        pro_currency_correct = pro_plan.get("currency") == "brl"

                        price = pro_plan.get("price", 0) / 100
                        currency = pro_plan.get("currency")
                        price_msg = f"Price: R$ {price:.2f}, Currency: {currency}"
                        self.log_test(
                            "Pro Plan Configuration",
                            pro_price_correct and pro_currency_correct,
                            price_msg,
                            pro_plan,
                        )

                        if not (pro_price_correct and pro_currency_correct):
                            pricing_passed = False

                    if "enterprise" in pricing:
                        enterprise_plan = pricing["enterprise"]
                        enterprise_price_correct = enterprise_plan.get("price") == 9990  # R$ 99,90

                        self.log_test(
                            "Enterprise Plan Configuration",
                            enterprise_price_correct,
                            f"Price: R$ {enterprise_plan.get('price', 0) / 100:.2f}",
                            {
                                "price": enterprise_plan.get("price"),
                                "currency": enterprise_plan.get("currency"),
                            },
                        )

                        if not enterprise_price_correct:
                            pricing_passed = False

                else:
                    self.log_test(
                        "Pricing API",
                        False,
                        f"HTTP {response.status_code}",
                        {"response_text": response.text[:200]},
                    )
                    pricing_passed = False

            except httpx.RequestError as e:
                self.log_test("Pricing API Connection", False, f"Connection error: {str(e)}")
                pricing_passed = False

        return pricing_passed

    async def test_checkout_session(self) -> bool:
        """Test checkout session creation."""
        print(f"\n{Colors.BOLD}🛒 Testing Checkout Session Creation{Colors.END}")

        checkout_passed = True

        async with httpx.AsyncClient() as client:
            try:
                # Test Pro Plan Checkout
                request_data = {
                    "user_id": "test_user_validation_123",
                    "user_email": "validacao@exemplo.com.br",
                    "plan_type": "pro",
                    "success_url": f"{FRONTEND_URL}/sucesso",
                    "cancel_url": f"{FRONTEND_URL}/cancelar",
                }

                response = await client.post(
                    f"{self.base_url}/api/payments/create-checkout-session",
                    json=request_data,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", False)

                    if success:
                        self.log_test(
                            "Pro Plan Checkout Session",
                            True,
                            "Checkout session created successfully",
                            {
                                "session_id": data.get("session_id", "")[:20] + "...",
                                "plan_type": data.get("plan_type"),
                                "currency": data.get("currency"),
                                "amount": data.get("amount"),
                            },
                        )
                    else:
                        self.log_test(
                            "Pro Plan Checkout Session",
                            False,
                            data.get("error", "Unknown error"),
                            data,
                        )
                        checkout_passed = False
                else:
                    self.log_test(
                        "Pro Plan Checkout Session",
                        False,
                        f"HTTP {response.status_code}",
                        {"response_text": response.text[:200]},
                    )
                    checkout_passed = False

                # Test Free Plan (should not require payment)
                free_request = {
                    "user_id": "test_user_free_123",
                    "user_email": "gratis@exemplo.com.br",
                    "plan_type": "free",
                }

                response = await client.post(
                    f"{self.base_url}/api/payments/create-checkout-session",
                    json=free_request,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("plan_type") == "free":
                        self.log_test(
                            "Free Plan Checkout", True, "Free plan activated without payment", data
                        )
                    else:
                        self.log_test(
                            "Free Plan Checkout", False, "Free plan checkout failed", data
                        )
                        checkout_passed = False
                else:
                    self.log_test("Free Plan Checkout", False, f"HTTP {response.status_code}")
                    checkout_passed = False

            except httpx.RequestError as e:
                self.log_test("Checkout Session API", False, f"Connection error: {str(e)}")
                checkout_passed = False

        return checkout_passed

    async def test_webhooks(self) -> bool:
        """Test webhook processing."""
        print(f"\n{Colors.BOLD}🔗 Testing Webhook Processing{Colors.END}")

        webhooks_passed = True

        async with httpx.AsyncClient() as client:
            try:
                # Test webhook health
                response = await client.get(
                    f"{self.base_url}/api/webhooks/stripe/health", timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Webhook Health Check",
                        True,
                        "Webhook system healthy",
                        {
                            "status": data.get("status"),
                            "stripe_configured": data.get("stripe_configured"),
                            "test_mode": data.get("test_mode"),
                        },
                    )
                else:
                    self.log_test("Webhook Health Check", False, f"HTTP {response.status_code}")
                    webhooks_passed = False

                # Test test webhook processing
                response = await client.post(
                    f"{self.base_url}/api/webhooks/stripe/test", timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", False)

                    if success:
                        self.log_test(
                            "Test Webhook Processing",
                            True,
                            "Test webhook processed successfully",
                            {
                                "test_event_id": data.get("test_event_id"),
                                "processing_success": data.get("processing_result", {}).get(
                                    "success"
                                ),
                            },
                        )
                    else:
                        self.log_test(
                            "Test Webhook Processing", False, data.get("message", "Unknown error")
                        )
                        webhooks_passed = False
                else:
                    self.log_test("Test Webhook Processing", False, f"HTTP {response.status_code}")
                    webhooks_passed = False

                # Test payment methods endpoint
                response = await client.get(
                    f"{self.base_url}/api/webhooks/stripe/test-payment-methods", timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    payment_methods = data.get("payment_methods", [])

                    self.log_test(
                        "Test Payment Methods",
                        True,
                        f"Found {len(payment_methods)} payment method types",
                        {
                            "currency": data.get("currency"),
                            "country": data.get("country"),
                            "methods": [pm.get("name") for pm in payment_methods],
                        },
                    )
                else:
                    self.log_test("Test Payment Methods", False, f"HTTP {response.status_code}")
                    webhooks_passed = False

            except httpx.RequestError as e:
                self.log_test("Webhook API Connection", False, f"Connection error: {str(e)}")
                webhooks_passed = False

        return webhooks_passed

    async def test_brazilian_features(self) -> bool:
        """Test Brazilian market specific features."""
        print(f"\n{Colors.BOLD}🇧🇷 Testing Brazilian Market Features{Colors.END}")

        brazilian_passed = True

        async with httpx.AsyncClient() as client:
            try:
                # Test pricing includes Portuguese names
                response = await client.get(f"{self.base_url}/api/payments/pricing", timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    pricing = data.get("pricing", {})

                    # Check Portuguese plan names
                    portuguese_names = {
                        "pro": "Plano Profissional",
                        "enterprise": "Plano Empresarial",
                        "lifetime": "Acesso Vitalício",
                        "free": "Plano Grátis",
                    }

                    for plan_key, expected_name in portuguese_names.items():
                        if plan_key in pricing:
                            actual_name = pricing[plan_key].get("name", "")
                            name_correct = expected_name.lower() in actual_name.lower()

                            self.log_test(
                                f"Portuguese Plan Name ({plan_key})",
                                name_correct,
                                f"Expected: {expected_name}, Got: {actual_name}",
                                {"expected": expected_name, "actual": actual_name},
                            )

                            if not name_correct:
                                brazilian_passed = False

                # Test Brazilian user data processing
                brazilian_user_request = {
                    "user_id": "user_brazilian_test_123",
                    "user_email": "usuario@exemplo.com.br",
                    "plan_type": "pro",
                    "metadata": {"market": "brazil", "language": "pt-br", "document_type": "CPF"},
                }

                response = await client.post(
                    f"{self.base_url}/api/payments/create-checkout-session",
                    json=brazilian_user_request,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test(
                            "Brazilian User Data Processing",
                            True,
                            "Brazilian user metadata processed correctly",
                            {
                                "user_email": brazilian_user_request["user_email"],
                                "metadata": brazilian_user_request["metadata"],
                            },
                        )
                    else:
                        self.log_test(
                            "Brazilian User Data Processing",
                            False,
                            data.get("error", "Unknown error"),
                        )
                        brazilian_passed = False
                else:
                    self.log_test(
                        "Brazilian User Data Processing", False, f"HTTP {response.status_code}"
                    )
                    brazilian_passed = False

            except httpx.RequestError as e:
                self.log_test("Brazilian Features API", False, f"Connection error: {str(e)}")
                brazilian_passed = False

        return brazilian_passed

    async def run_all_tests(self) -> bool:
        """Run all validation tests."""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 CV-Match Stripe Test Mode Validation{Colors.END}")
        print("Testing Brazilian market payment setup\n")

        results = {}

        # Run all test suites
        results["configuration"] = await self.test_configuration()
        results["api_health"] = await self.test_api_health()
        results["pricing"] = await self.test_pricing()
        results["checkout"] = await self.test_checkout_session()
        results["webhooks"] = await self.test_webhooks()
        results["brazilian"] = await self.test_brazilian_features()

        # Generate summary
        self.print_summary(results)

        # Save detailed report
        await self.save_report(results)

        return all(results.values())

    def print_summary(self, results: Dict[str, bool]):
        """Print test summary."""
        total_time = (datetime.now(UTC) - self.start_time).total_seconds()
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests

        print(f"\n{Colors.BOLD}📊 Test Summary{Colors.END}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.END}")
        print(f"Failed: {Colors.RED}{failed_tests}{Colors.END}")
        print(f"Duration: {total_time:.2f} seconds")

        print(f"\n{Colors.BOLD}📋 Test Suite Results:{Colors.END}")
        for suite_name, passed in results.items():
            status = f"{Colors.GREEN}✅{Colors.END}" if passed else f"{Colors.RED}❌{Colors.END}"
            print(f"{status} {suite_name.title()}")

        overall_passed = all(results.values())
        overall_status = (
            f"{Colors.GREEN}✅ ALL TESTS PASSED{Colors.END}"
            if overall_passed
            else f"{Colors.RED}❌ SOME TESTS FAILED{Colors.END}"
        )

        print(f"\n{Colors.BOLD}Overall Status: {overall_status}{Colors.END}")

    async def save_report(self, results: Dict[str, bool]):
        """Save detailed test report."""
        report = {
            "validation_summary": {
                "timestamp": datetime.now(UTC).isoformat(),
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r["passed"]),
                "failed_tests": sum(1 for r in self.test_results if not r["passed"]),
                "duration_seconds": (datetime.now(UTC) - self.start_time).total_seconds(),
                "overall_passed": all(results.values()),
                "test_suites": results,
            },
            "detailed_results": self.test_results,
            "environment": {
                "base_url": self.base_url,
                "frontend_url": FRONTEND_URL,
                "stripe_key_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
                "webhook_secret_configured": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
                "brazilian_currency": os.getenv("NEXT_PUBLIC_DEFAULT_CURRENCY"),
                "brazilian_country": os.getenv("NEXT_PUBLIC_DEFAULT_COUNTRY"),
                "brazilian_locale": os.getenv("NEXT_PUBLIC_DEFAULT_LOCALE"),
            },
        }

        report_filename = (
            f"stripe_validation_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(report_filename, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"\n{Colors.BLUE}📄 Detailed report saved: {report_filename}{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Failed to save report: {str(e)}{Colors.END}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CV-Match Stripe Test Mode Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_stripe_setup.py --all         # Run all tests
  python test_stripe_setup.py --config      # Test configuration only
  python test_stripe_setup.py --payments    # Test payment flows only
  python test_stripe_setup.py --webhooks    # Test webhooks only
  python test_stripe_setup.py --brazilian   # Test Brazilian features only
        """,
    )

    parser.add_argument("--all", action="store_true", help="Run all validation tests")
    parser.add_argument("--config", action="store_true", help="Test configuration only")
    parser.add_argument("--payments", action="store_true", help="Test payment flows only")
    parser.add_argument("--webhooks", action="store_true", help="Test webhooks only")
    parser.add_argument("--brazilian", action="store_true", help="Test Brazilian features only")

    args = parser.parse_args()

    if not any([args.all, args.config, args.payments, args.webhooks, args.brazilian]):
        args.all = True  # Default to running all tests

    validator = StripeTestValidator()

    try:
        if args.all:
            success = await validator.run_all_tests()
        else:
            success = True
            if args.config:
                success &= await validator.test_configuration()
            if args.payments:
                success &= await validator.test_checkout_session()
            if args.webhooks:
                success &= await validator.test_webhooks()
            if args.brazilian:
                success &= await validator.test_brazilian_features()

            validator.print_summary(
                {
                    "configuration": args.config,
                    "payments": args.payments,
                    "webhooks": args.webhooks,
                    "brazilian": args.brazilian,
                }
            )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Validation interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Validation failed with error: {str(e)}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
