/**
 * Shared pricing configuration for Brazilian market
 */

// Brazilian pricing tiers configuration
export const BRAZILIAN_PRICING = {
  free: {
    id: 'free',
    name: 'Grátis',
    price: 0,
    currency: 'brl',
    credits: 5,
    description: 'Ideal para experimentar a plataforma',
    features: [
      '5 análises de currículo por mês',
      'Matching básico',
      'Download em PDF',
      'Suporte por email',
    ],
    popular: false,
  },
  basic: {
    id: 'basic',
    name: 'Básico',
    price: 1490, // R$ 14,90
    currency: 'brl',
    credits: 10,
    description: 'Perfeito para busca ocasional',
    features: [
      '10 análises de currículo por mês',
      'Matching intermediário',
      'Download em múltiplos formatos',
      'Templates brasileiros',
      'Suporte por email',
    ],
    popular: false,
  },
  pro: {
    id: 'pro',
    name: 'Profissional',
    price: 2990, // R$ 29,90
    currency: 'brl',
    credits: 50,
    description: 'O mais escolhido',
    features: [
      '50 análises de currículo por mês',
      'Matching avançado com IA',
      'Templates brasileiros premium',
      'Suporte prioritário',
      'Análise de compatibilidade com vagas',
      'Relatórios detalhados',
    ],
    popular: true,
  },
  enterprise: {
    id: 'enterprise',
    name: 'Empresarial',
    price: 9990, // R$ 99,90
    currency: 'brl',
    credits: 200,
    description: 'Para equipes e recrutadores',
    features: [
      'Análises ilimitadas',
      'Dashboard de recrutamento',
      'API de integração',
      'Múltiplos usuários',
      'Relatórios avançados',
      'Suporte dedicado',
      'Integração com ATS',
    ],
    popular: false,
  },
};

export interface PricingTier {
  id: string;
  name: string;
  price: number;
  currency: string;
  credits: number;
  description: string;
  features: string[];
  popular: boolean;
}

/**
 * Format price in Brazilian Reais
 * @param priceInCents Price in cents (integer)
 * @returns Formatted price string (e.g., "R$ 29,90")
 */
export function formatBRLPrice(priceInCents: number): string {
  const reais = priceInCents / 100;
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(reais);
}

/**
 * Get pricing tier configuration by ID
 * @param tierId The tier ID to retrieve
 * @returns Pricing tier configuration or null if not found
 */
export function getPricingTier(tierId: string): PricingTier | null {
  return BRAZILIAN_PRICING[tierId as keyof typeof BRAZILIAN_PRICING] || null;
}

/**
 * Get all available pricing tiers
 * @returns Array of all pricing tiers
 */
export function getAllPricingTiers(): PricingTier[] {
  return Object.values(BRAZILIAN_PRICING);
}

/**
 * Check if a tier exists
 * @param tierId The tier ID to check
 * @returns True if tier exists, false otherwise
 */
export function hasPricingTier(tierId: string): boolean {
  return tierId in BRAZILIAN_PRICING;
}
