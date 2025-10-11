"""
Centralized pricing configuration for CV-Match Brazilian market.
Used by both frontend and backend to ensure consistency.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PricingTier:
    """Pricing tier configuration for Brazilian market."""
    id: str
    name: str
    description: str
    price: int  # Price in cents (BRL)
    credits: int
    currency: str = "brl"
    stripe_price_id: str | None = None
    features: List[str] | None = None
    popular: bool = False

    def __post_init__(self):
        if self.features is None:
            self.features = []


class BrazilianPricingConfig:
    """Brazilian market pricing configuration."""

    def __init__(self):
        self.currency = "brl"
        self.country = "BR"
        self.locale = "pt-BR"

        # Brazilian pricing tiers
        self.tiers: Dict[str, PricingTier] = {
            "free": PricingTier(
                id="free",
                name="Plano Gratuito",
                description="Perfeito para experimentar a otimização de currículo",
                price=0,
                credits=3,
                currency="brl",
                features=[
                    "3 otimizações gratuitas",
                    "Pontuação básica de compatibilidade ATS",
                    "Exportação em formato .txt"
                ],
            ),
            "basic": PricingTier(
                id="basic",
                name="Plano Básico",
                description="Ideal para quem busca oportunidades ocasionalmente",
                price=2990,  # R$ 29,90 in cents
                credits=10,
                currency="brl",
                stripe_price_id="price_basic_brl",
                features=[
                    "10 otimizações de currículo",
                    "Pontuação básica de compatibilidade ATS",
                    "Análise avançada com IA",
                    "Exportação em PDF e DOCX",
                    "Foco no mercado brasileiro"
                ],
            ),
            "pro": PricingTier(
                id="pro",
                name="Plano Profissional",
                description="Para quem busca muitas oportunidades ou recrutadores",
                price=7900,  # R$ 79,00 in cents
                credits=50,
                currency="brl",
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
                    "LGPD Compliance"
                ],
            ),
            "enterprise": PricingTier(
                id="enterprise",
                name="Plano Empresarial",
                description="Solução completa para recrutamento no Brasil",
                price=9990,  # R$ 99,90 in cents
                credits=1000,
                currency="brl",
                stripe_price_id="price_enterprise_brl",
                features=[
                    "1000 otimizações de currículo",
                    "Recrutamento ilimitado",
                    "Dashboard avançado",
                    "API de integração",
                    "Múltiplos usuários",
                    "Relatórios detalhados",
                    "Suporte dedicado",
                    "LGPD Compliance completo"
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

    def get_all_tiers(self) -> Dict[str, Dict[str, Any]]:
        """Get all pricing tiers as dictionary for API responses."""
        return {
            tier_id: {
                "id": tier.id,
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "credits": tier.credits,
                "currency": tier.currency,
                "stripe_price_id": tier.stripe_price_id,
                "features": tier.features,
                "popular": tier.popular,
            }
            for tier_id, tier in self.tiers.items()
        }

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