/**
 * Pricing utility functions for CV-Match frontend
 */

export interface PricingTier {
  id: string;
  name: string;
  description: string;
  price: number; // in cents
  credits: number;
  features: string[];
  popular?: boolean;
}

const PRICING_TIERS: Record<string, PricingTier> = {
  free: {
    id: 'free',
    name: 'Plano Gratuito',
    description: 'Perfeito para experimentar',
    price: 0,
    credits: 3,
    features: ['3 otimizações gratuitas', 'Pontuação básica ATS', 'Exportação em .txt'],
  },
  basic: {
    id: 'basic',
    name: 'Plano Básico',
    description: 'Ideal para buscas ocasionais',
    price: 2990, // R$ 29,90
    credits: 10,
    features: [
      '10 otimizações de currículo',
      'Análise avançada com IA',
      'Exportação PDF e DOCX',
      'Suporte por email',
    ],
  },
  pro: {
    id: 'pro',
    name: 'Plano Profissional',
    description: 'Para quem busca muitas oportunidades',
    price: 7900, // R$ 79,00
    credits: 50,
    popular: true,
    features: [
      '50 otimizações de currículo',
      'Análise avançada com IA',
      'Modelos profissionais',
      'Suporte prioritário',
      'Otimização de palavras-chave',
    ],
  },
  enterprise: {
    id: 'enterprise',
    name: 'Plano Empresarial',
    description: 'Solução completa para recrutamento',
    price: 9990, // R$ 99,90
    credits: 1000,
    features: [
      '1000 otimizações',
      'Dashboard avançado',
      'API de integração',
      'Múltiplos usuários',
      'Suporte dedicado',
    ],
  },
};

export function getPricingTier(tierId: string): PricingTier | null {
  return PRICING_TIERS[tierId] || null;
}

export function formatBRLPrice(priceInCents: number): string {
  const reais = priceInCents / 100;
  return `R$ ${reais.toFixed(2).replace('.', ',')}`;
}

export function getAllPricingTiers(): PricingTier[] {
  return Object.values(PRICING_TIERS);
}
