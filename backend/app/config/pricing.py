"""
Centralized pricing configuration for CV-Match Brazilian market.
Used by both frontend and backend to ensure consistency.
"""

from dataclasses import dataclass
from typing import Any


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
    features: list[str] | None = None
    popular: bool = False

    def __post_init__(self) -> None:
        if self.features is None:
            self.features = []


class BrazilianPricingConfig:
    """Brazilian market pricing configuration."""

    def __init__(self) -> None:
        self.currency = "brl"
        self.country = "BR"
        self.locale = "pt-BR"

        # Brazilian pricing tiers
        self.tiers: dict[str, PricingTier] = {
            # FLEX PACKAGES (credit-based - existing)
            "free": PricingTier(
                id="free",
                name="Plano Gratuito",
                description="Perfeito para experimentar a otimização de currículo",
                price=0,
                credits=3,
                currency="brl",
                is_subscription=False,
                features=[
                    "3 otimizações gratuitas",
                    "Pontuação básica de compatibilidade ATS",
                    "Exportação em formato .txt",
                ],
            ),
            "basic": PricingTier(
                id="basic",
                name="Flex Básico",
                description="Pacote de créditos para uso ocasional",
                price=2990,  # R$ 29,90 in cents
                credits=10,
                currency="brl",
                is_subscription=False,
                stripe_price_id="price_basic_brl",
                features=[
                    "10 otimizações de currículo",
                    "Pontuação básica de compatibilidade ATS",
                    "Análise avançada com IA",
                    "Exportação em PDF e DOCX",
                    "Foco no mercado brasileiro",
                    "Créditos não expiram",
                ],
            ),
            "pro": PricingTier(
                id="pro",
                name="Flex Profissional",
                description="Pacote maior para quem busca muitas oportunidades",
                price=7900,  # R$ 79,00 in cents
                credits=50,
                currency="brl",
                is_subscription=False,
                stripe_price_id="price_pro_brl",
                popular=True,
                features=[
                    "50 otimizações de currículo",
                    "Análise avançada com IA",
                    "Modelos de currículo profissionais",
                    "Suporte prioritário",
                    "Exportação em múltiplos formatos",
                    "Foco no mercado brasileiro",
                    "Análise detalhada de compatibilidade",
                    "Otimização de palavras-chave",
                    "LGPD Compliance",
                    "Créditos não expiram",
                ],
            ),
            "enterprise": PricingTier(
                id="enterprise",
                name="Flex Empresarial",
                description="Grande pacote para recrutamento intensivo",
                price=9990,  # R$ 99,90 in cents
                credits=1000,
                currency="brl",
                is_subscription=False,
                stripe_price_id="price_enterprise_brl",
                features=[
                    "1000 otimizações de currículo",
                    "Recrutamento ilimitado",
                    "Dashboard avançado",
                    "API de integração",
                    "Múltiplos usuários",
                    "Relatórios detalhados",
                    "Suporte dedicado",
                    "LGPD Compliance completo",
                    "Créditos não expiram",
                ],
            ),
            # FLOW SUBSCRIPTIONS (recurring - new!)
            "flow_starter": PricingTier(
                id="flow_starter",
                name="Flow Starter",
                description="Assinatura mensal para quem busca oportunidades regularmente",
                price=2490,  # R$ 24,90/month in cents
                credits=0,
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
                    "Cancele quando quiser",
                ],
            ),
            "flow_pro": PricingTier(
                id="flow_pro",
                name="Flow Pro",
                description="Plano profissional para quem busca muitas oportunidades",
                price=4990,  # R$ 49,90/month in cents
                credits=0,
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
                    "Cancele quando quiser",
                ],
            ),
            "flow_business": PricingTier(
                id="flow_business",
                name="Flow Business",
                description="Para recrutadores e uso intensivo",
                price=12990,  # R$ 129,90/month in cents
                credits=0,
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
                    "Cancele quando quiser",
                ],
            ),
            "flow_enterprise": PricingTier(
                id="flow_enterprise",
                name="Flow Enterprise",
                description="Solução personalizada para grandes volumes",
                price=0,  # Custom pricing
                credits=0,
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
                    "Suporte 24/7",
                ],
            ),
        }

    def get_tier(self, tier_id: str) -> PricingTier | None:
        """Get pricing tier by ID."""
        return self.tiers.get(tier_id)

    def get_credits_for_tier(self, tier_id: str) -> int:
        """Get credit amount for a pricing tier."""
        tier = self.get_tier(tier_id)
        return tier.credits if tier else 0

    def get_price_for_tier(self, tier_id: str) -> int:
        """Get price amount for a pricing tier."""
        tier = self.get_tier(tier_id)
        return tier.price if tier else 0

    def get_stripe_plan_type(self, tier_id: str) -> str:
        """Map pricing tiers to Stripe plan types."""
        tier_mapping = {
            "basic": "basic",
            "pro": "pro",
            "enterprise": "enterprise",
        }
        return tier_mapping.get(tier_id, "basic")

    def get_all_tiers(self) -> dict[str, dict[str, Any]]:
        """Get all pricing tiers as dictionary for API responses."""
        return {
            tier_id: {
                "id": tier.id,
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "credits": tier.credits,
                "analyses_per_month": tier.analyses_per_month,
                "rollover_limit": tier.rollover_limit,
                "is_subscription": tier.is_subscription,
                "currency": tier.currency,
                "stripe_price_id": tier.stripe_price_id,
                "features": tier.features,
                "popular": tier.popular,
            }
            for tier_id, tier in self.tiers.items()
        }

    def get_subscription_tiers(self) -> dict[str, PricingTier]:
        """Get only subscription tiers (Flow)."""
        return {tier_id: tier for tier_id, tier in self.tiers.items() if tier.is_subscription}

    def get_credit_tiers(self) -> dict[str, PricingTier]:
        """Get only credit tiers (Flex)."""
        return {tier_id: tier for tier_id, tier in self.tiers.items() if not tier.is_subscription}

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

    def format_brl_price(self, price_in_cents: int) -> str:
        """Format price in BRL currency."""
        reais = price_in_cents / 100
        return f"R$ {reais:.2f}".replace(".", ",")


# Global pricing configuration instance
pricing_config = BrazilianPricingConfig()


# Helper functions for backward compatibility
def get_pricing_tier(tier_id: str) -> PricingTier | None:
    """Get pricing tier by ID."""
    return pricing_config.get_tier(tier_id)


def get_credits_for_tier(tier_id: str) -> int:
    """Get credit amount for a pricing tier."""
    return pricing_config.get_credits_for_tier(tier_id)


def get_price_for_tier(tier_id: str) -> int:
    """Get price amount for a pricing tier."""
    return pricing_config.get_price_for_tier(tier_id)


def get_stripe_plan_type(tier_id: str) -> str:
    """Map pricing tiers to Stripe plan types."""
    return pricing_config.get_stripe_plan_type(tier_id)
