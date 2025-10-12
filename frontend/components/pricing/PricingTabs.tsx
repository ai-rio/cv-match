'use client';

import { useTranslations } from 'next-intl';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

import { CreditCards } from './CreditCards';
import { SubscriptionCards } from './SubscriptionCards';

export function PricingTabs() {
  const t = useTranslations('subscriptions');

  return (
    <Tabs defaultValue="subscriptions" className="w-full">
      <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
        <TabsTrigger value="credits">{t('tabs.credits')}</TabsTrigger>
        <TabsTrigger value="subscriptions">{t('tabs.subscriptions')}</TabsTrigger>
      </TabsList>

      <TabsContent value="credits" className="mt-8">
        <CreditCards />
      </TabsContent>

      <TabsContent value="subscriptions" className="mt-8">
        <SubscriptionCards />
      </TabsContent>
    </Tabs>
  );
}
