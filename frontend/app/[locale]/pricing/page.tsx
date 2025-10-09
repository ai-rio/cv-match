'use client';

import { Check, Star } from 'lucide-react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

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
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:gap-12">
            {/* Free Plan */}
            <Card className="relative">
              <CardHeader>
                <CardTitle className="text-xl">{t('plans.free.name')}</CardTitle>
                <CardDescription>{t('plans.free.description')}</CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-gray-900">{t('plans.free.price')}</span>
                  <span className="text-gray-600">{t('plans.free.period')}</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.free.features.basicAnalysis')}
                    </span>
                  </li>
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.free.features.limitedOptimizations')}
                    </span>
                  </li>
                </ul>
                <Button className="w-full mt-8" variant="outline" asChild>
                  <Link href="/signup">{t('plans.free.button')}</Link>
                </Button>
              </CardContent>
            </Card>

            {/* Pro Plan */}
            <Card className="relative border-primary-200 shadow-lg">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-primary-600 text-white">Popular</Badge>
              </div>
              <CardHeader className="text-center">
                <CardTitle className="text-xl">{t('plans.pro.name')}</CardTitle>
                <CardDescription>{t('plans.pro.description')}</CardDescription>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-primary-600">
                    {t('plans.pro.price')}
                  </span>
                  <span className="text-gray-600">{t('plans.pro.period')}</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.pro.features.unlimitedOptimizations')}
                    </span>
                  </li>
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.pro.features.advancedAnalysis')}
                    </span>
                  </li>
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.pro.features.professionalTemplates')}
                    </span>
                  </li>
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.pro.features.prioritySupport')}
                    </span>
                  </li>
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.pro.features.multipleFormats')}
                    </span>
                  </li>
                  <li className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-3" />
                    <span className="text-sm text-gray-700">
                      {t('plans.pro.features.brazilianMarket')}
                    </span>
                  </li>
                </ul>
                <Button className="w-full mt-8" asChild>
                  <Link href="/signup">{t('plans.pro.button')}</Link>
                </Button>
              </CardContent>
            </Card>
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
