'use client';

import { Check, Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { formatBRLPrice, getPricingTier } from '@/lib/pricing';
import { createClient } from '@/lib/supabase/client';

const CREDIT_TIERS = ['free', 'basic', 'pro', 'enterprise'];

export function CreditCards() {
  const t = useTranslations('pricing');
  const [processingTier, setProcessingTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePurchase = async (tierId: string) => {
    if (tierId === 'free') {
      // For free tier, redirect to signup
      window.location.href = '/pt-br/signup';
      return;
    }

    setProcessingTier(tierId);
    setError(null);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const tier = getPricingTier(tierId);

      if (!tier) {
        throw new Error('Plano inválido');
      }

      // Get Supabase session for auth token
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        // Redirect to login if not authenticated
        window.location.href = `/pt-br/login?callbackUrl=/pricing`;
        return;
      }

      const response = await fetch(`${API_URL}/api/payments/create-checkout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier: tier.id,
          success_url: window.location.origin + '/payment/success',
          cancel_url: window.location.origin + '/payment/canceled',
          metadata: {
            tier_id: tier.id,
            credits: tier.credits.toString(),
            price: tier.price.toString(),
          },
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao processar pagamento');
      }

      const data = await response.json();

      // Redirect to Stripe Checkout
      window.location.href = data.checkout_url;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erro ao processar pagamento. Tente novamente.';
      console.error('Payment failed:', error);
      setError(errorMessage);
    } finally {
      setProcessingTier(null);
    }
  };

  const renderPricingCard = (tierId: string) => {
    const tier = getPricingTier(tierId);
    if (!tier) return null;

    const isProcessing = processingTier === tierId;
    const isPopular = tier.popular;

    return (
      <Card key={tier.id} className={`relative ${isPopular ? 'border-primary-200 shadow-lg' : ''}`}>
        {isPopular && (
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <Badge className="bg-primary-600 text-white">Popular</Badge>
          </div>
        )}

        <CardHeader className={isPopular ? 'text-center' : ''}>
          <CardTitle className="text-xl">{tier.name}</CardTitle>
          <CardDescription>{tier.description}</CardDescription>
          <div className="mt-4">
            {tier.price === 0 ? (
              <span className="text-4xl font-bold text-gray-900">Gratuito</span>
            ) : (
              <>
                <span
                  className={`text-4xl font-bold ${isPopular ? 'text-primary-600' : 'text-blue-600'}`}
                >
                  {formatBRLPrice(tier.price)}
                </span>
                <span className="text-gray-600">/pacote</span>
              </>
            )}
            <div
              className={`text-sm font-medium mt-2 ${isPopular ? 'text-primary-600' : 'text-blue-600'}`}
            >
              {tier.credits} créditos
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <ul className="space-y-3">
            {tier.features.map((feature, index) => (
              <li key={index} className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-3" />
                <span className="text-sm text-gray-700">{feature}</span>
              </li>
            ))}
          </ul>

          {error && processingTier === tierId && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}

          <Button
            className={`w-full mt-6 ${isPopular ? '' : ''}`}
            variant={tier.id === 'free' ? 'outline' : 'default'}
            onClick={() => handlePurchase(tier.id)}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processando...
              </>
            ) : tier.id === 'free' ? (
              t('plans.free.button')
            ) : (
              `Comprar Plano ${tier.name}`
            )}
          </Button>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4 max-w-6xl mx-auto">
      {CREDIT_TIERS.map(renderPricingCard)}
    </div>
  );
}
