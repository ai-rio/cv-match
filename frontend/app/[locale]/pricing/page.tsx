'use client';

import { formatBRLPrice, getPricingTier } from '@cv-match/shared-pricing-config';
import { Check, Loader2, Star, X } from 'lucide-react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

export default function PricingPage() {
  const t = useTranslations('pricing');
  const [processingTier, setProcessingTier] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePurchase = async (tierId: string) => {
    if (tierId === 'free') {
      // For free tier, redirect to signup
      window.location.href = '/auth/signup';
      return;
    }

    setProcessingTier(tierId);
    setError(null); // Clear any previous errors

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
        window.location.href = `/auth/login?callbackUrl=/pricing`;
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
          <Button
            className={`w-full mt-8 ${isPopular ? '' : ''}`}
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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4">{t('badge')}</Badge>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
            {t('hero.title')}
            <span className="block text-primary-600">{t('hero.highlight')}</span>
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600 max-w-3xl mx-auto">
            {t('hero.subtitle')}
          </p>
          <div className="mt-8 flex items-center justify-center gap-x-6">
            <Button size="lg" asChild>
              <Link href="/signup">{t('hero.getStarted')}</Link>
            </Button>
            <Button variant="outline" size="lg">
              {t('hero.buyLifetime')}
            </Button>
          </div>
        </div>

        {/* Social Proof */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:gap-8 mb-16">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600">10,000+</div>
            <div className="text-sm text-gray-600">{t('socialProof.resumesOptimized')}</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600">87%</div>
            <div className="text-sm text-gray-600">{t('socialProof.successRate')}</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary-600">5,000+</div>
            <div className="text-sm text-gray-600">{t('socialProof.happyUsers')}</div>
          </div>
        </div>

        {/* Features */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900">{t('features.title')}</h2>
            <p className="mt-4 text-lg text-gray-600">{t('features.subtitle')}</p>
          </div>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
                <Star className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900">
                {t('features.aiPowered.title')}
              </h3>
              <p className="mt-2 text-base text-gray-600">{t('features.aiPowered.description')}</p>
            </div>
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
                <Check className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900">
                {t('features.atsOptimized.title')}
              </h3>
              <p className="mt-2 text-base text-gray-600">
                {t('features.atsOptimized.description')}
              </p>
            </div>
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
                <Star className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900">
                {t('features.realResults.title')}
              </h3>
              <p className="mt-2 text-base text-gray-600">
                {t('features.realResults.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-8">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <Check className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Erro no pagamento</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
                <div className="ml-auto pl-3">
                  <div className="-mx-1.5 -my-1.5">
                    <button
                      onClick={() => setError(null)}
                      className="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100"
                    >
                      <span className="sr-only">Dismiss</span>
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Plans */}
        <div className="mb-16">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {renderPricingCard('free')}
            {renderPricingCard('basic')}
            {renderPricingCard('pro')}
            {renderPricingCard('enterprise')}
          </div>
        </div>

        {/* Brazilian Features */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900">{t('brazilianFeatures.title')}</h2>
            <p className="mt-4 text-lg text-gray-600">{t('brazilianFeatures.subtitle')}</p>
          </div>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('brazilianFeatures.lgpd.title')}
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                {t('brazilianFeatures.lgpd.description')}
              </p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('brazilianFeatures.localPayment.title')}
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                {t('brazilianFeatures.localPayment.description')}
              </p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('brazilianFeatures.localContent.title')}
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                {t('brazilianFeatures.localContent.description')}
              </p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">
                {t('brazilianFeatures.localSupport.title')}
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                {t('brazilianFeatures.localSupport.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="text-center">
          <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-600">
            <span>{t('trust.moneyBack')}</span>
            <span>{t('trust.cancelAnytime')}</span>
            <span>{t('trust.securePayment')}</span>
            <span>{t('trust.brazilianPayment')}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
