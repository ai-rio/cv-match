'use client';

import { Check, Star } from 'lucide-react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';

import { PricingTabs } from '@/components/pricing/PricingTabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export default function PricingPage() {
  const t = useTranslations('pricing');

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

        {/* Pricing Plans */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900">
              {t('title')} - {t('subtitle')}
            </h2>
          </div>
          <PricingTabs />
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
