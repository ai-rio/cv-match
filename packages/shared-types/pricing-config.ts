/**
 * Centralized pricing configuration for CV-Match
 * Used by both frontend and backend to ensure consistency
 */

export interface PricingTier {
  id: string;
  name: string;
  description: string;
  price: number; // Price in cents (BRL)
  credits: number;
  currency: 'brl';
  stripePriceId?: string;
  features: string[];
  popular?: boolean;
}

export interface PricingConfig {
  tiers: Record<string, PricingTier>;
  currency: 'brl';
  country: 'BR';
  locale: 'pt-BR';
}

// Brazilian market pricing configuration
export const BRAZILIAN_PRICING: PricingConfig = {
  currency: 'brl',
  country: 'BR',
  locale: 'pt-BR',
  tiers: {
    free: {
      id: 'free',
      name: 'Gratuito',
      description: 'Perfeito para experimentar a otimização de currículo',
      price: 0,
      credits: 3,
      currency: 'brl',
      features: [
        '3 otimizações gratuitas',
        'Pontuação básica de compatibilidade ATS',
        'Exportação em formato .txt'
      ],
    },
    basic: {
      id: 'basic',
      name: 'Básico',
      description: 'Ideal para quem busca oportunidades ocasionalmente',
      price: 2990, // R$ 29,90 in cents
      credits: 10,
      currency: 'brl',
      stripePriceId: 'price_basic_brl',
      features: [
        '10 otimizações de currículo',
        'Pontuação básica de compatibilidade ATS',
        'Análise avançada com IA',
        'Exportação em PDF e DOCX',
        'Foco no mercado brasileiro'
      ],
    },
    pro: {
      id: 'pro',
      name: 'Pro',
      description: 'Para quem busca muitas oportunidades ou recrutadores',
      price: 7900, // R$ 79,00 in cents
      credits: 50,
      currency: 'brl',
      stripePriceId: 'price_pro_brl',
      popular: true,
      features: [
        '50 otimizações de currículo',
        'Análise avançada com IA',
        'Modelos de currículo profissionais',
        'Suporte prioritário',
        'Exportação em múltiplos formatos',
        'Foco no mercado brasileiro',
        'Análise detalhada de compatibilidade',
        'Otimização de palavras-chave',
        'LGPD Compliance'
      ],
    },
    enterprise: {
      id: 'enterprise',
      name: 'Empresarial',
      description: 'Solução completa para recrutamento no Brasil',
      price: 9990, // R$ 99,90 in cents
      credits: 1000,
      currency: 'brl',
      stripePriceId: 'price_enterprise_brl',
      features: [
        '1000 otimizações de currículo',
        'Recrutamento ilimitado',
        'Dashboard avançado',
        'API de integração',
        'Múltiplos usuários',
        'Relatórios detalhados',
        'Suporte dedicado',
        'LGPD Compliance completo'
      ],
    },
  },
};

// Helper functions for pricing calculations
export function formatBRLPrice(priceInCents: number): string {
  const reais = priceInCents / 100;
  return `R$ ${reais.toFixed(2).replace('.', ',')}`;
}

export function getPricingTier(tierId: string): PricingTier | null {
  return BRAZILIAN_PRICING.tiers[tierId] || null;
}

export function getCreditsForTier(tierId: string): number {
  const tier = getPricingTier(tierId);
  return tier?.credits || 0;
}

export function getPriceForTier(tierId: string): number {
  const tier = getPricingTier(tierId);
  return tier?.price || 0;
}

// Stripe mapping for backend
export function getStripePlanType(tierId: string): string {
  switch (tierId) {
    case 'basic':
      return 'basic'; // Use actual basic plan
    case 'pro':
      return 'pro';
    case 'enterprise':
      return 'enterprise';
    default:
      return 'basic';
  }
}