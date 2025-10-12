'use client';

import { Check, Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

const SUBSCRIPTION_TIERS = ['flow_starter', 'flow_pro', 'flow_business'];

export function SubscriptionCards() {
  const t = useTranslations('subscriptions');
  const [loading, setLoading] = useState<string | null>(null);

  const handleSubscribe = async (tierId: string) => {
    setLoading(tierId);

    try {
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

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${API_URL}/api/subscriptions/checkout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier_id: tierId,
          success_url: window.location.origin + '/payment/success',
          cancel_url: window.location.origin + '/payment/canceled',
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao processar pagamento');
      }

      const data = await response.json();

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error: unknown) {
      console.error('Checkout failed:', error);
      // TODO: Replace with proper toast notification when available
      // const errorMessage = error instanceof Error ? error.message : 'Erro ao processar pagamento. Tente novamente.';
      // alert(errorMessage);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
      {SUBSCRIPTION_TIERS.map((tierId) => {
        const isPopular = tierId === 'flow_pro'; // Flow Pro is the popular one

        return (
          <Card
            key={tierId}
            className={`relative ${isPopular ? 'border-primary-200 shadow-lg scale-105' : ''}`}
          >
            {isPopular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                <Badge className="bg-primary-600 text-white px-3 py-1">
                  {t(`${tierId}.popular`)}
                </Badge>
              </div>
            )}

            <CardHeader className={isPopular ? 'text-center pb-4' : ''}>
              <div className="flex justify-between items-start">
                <CardTitle className="text-xl">{t(`${tierId}.name`)}</CardTitle>
              </div>
              <CardDescription>{t(`${tierId}.description`)}</CardDescription>

              <div className="mt-4">
                <span
                  className={`text-4xl font-bold ${isPopular ? 'text-primary-600' : 'text-gray-900'}`}
                >
                  {t(`${tierId}.price`)}
                </span>
                <span className="text-gray-600 text-lg">/{t(`${tierId}.period`)}</span>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {t.raw(`${tierId}.features`).map((feature: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>

            <CardFooter>
              <Button
                className={`w-full ${isPopular ? 'bg-primary-600 hover:bg-primary-700' : ''}`}
                size="lg"
                onClick={() => handleSubscribe(tierId)}
                disabled={loading === tierId}
              >
                {loading === tierId ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processando...
                  </>
                ) : (
                  t(`${tierId}.cta`)
                )}
              </Button>
            </CardFooter>
          </Card>
        );
      })}
    </div>
  );
}
