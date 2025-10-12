'use client';

import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { createClient } from '@/lib/supabase/client';

import { CancelSubscriptionDialog } from './CancelSubscriptionDialog';

interface SubscriptionData {
  id: string;
  tier_id: string;
  tier_name: string;
  analyses_used_this_period: number;
  analyses_per_month: number;
  analyses_rollover: number;
  current_period_end: string;
  status: string;
  cancel_at_period_end: boolean;
}

export function SubscriptionDashboard() {
  const t = useTranslations('subscriptions.manage');
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      setLoading(true);
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        setError('Você precisa estar logado para ver sua assinatura');
        return;
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/subscriptions/current`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          // No active subscription
          setSubscription(null);
          return;
        }
        throw new Error('Erro ao buscar assinatura');
      }

      const data = await response.json();
      setSubscription(data);
      setError(null);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
      setError(error instanceof Error ? error.message : 'Erro ao carregar assinatura');
      setSubscription(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={fetchSubscription} variant="outline">
            Tentar novamente
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!subscription) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center space-y-4">
            <p className="text-muted-foreground">Você não possui uma assinatura ativa.</p>
            <Button asChild>
              <a href="/pricing">Ver Planos</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const usagePercentage =
    subscription.analyses_per_month > 0
      ? (subscription.analyses_used_this_period / subscription.analyses_per_month) * 100
      : 0;

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'trialing':
        return 'secondary';
      case 'past_due':
        return 'destructive';
      case 'canceled':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Ativa';
      case 'trialing':
        return 'Teste';
      case 'past_due':
        return 'Em Atraso';
      case 'canceled':
        return 'Cancelada';
      default:
        return status;
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <CardTitle>{t('title')}</CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={getStatusBadgeVariant(subscription.status)}>
                {getStatusText(subscription.status)}
              </Badge>
              {subscription.cancel_at_period_end && (
                <Badge variant="outline">Cancela ao final do período</Badge>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">{t('current_plan')}</p>
            <p className="text-2xl font-bold">{subscription.tier_name}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground mb-2">{t('usage')}</p>
            <div className="space-y-2">
              <Progress value={usagePercentage} className="h-2" />
              <p className="text-sm">
                {t('analyses_used', {
                  used: subscription.analyses_used_this_period,
                  total: subscription.analyses_per_month,
                })}
              </p>
              {subscription.analyses_rollover > 0 && (
                <p className="text-sm text-muted-foreground">
                  {t('rollover', { count: subscription.analyses_rollover })}
                </p>
              )}
            </div>
          </div>

          <div>
            <p className="text-sm text-muted-foreground mb-1">{t('next_billing')}</p>
            <p className="font-medium">
              {new Date(subscription.current_period_end).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
              })}
            </p>
          </div>

          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" asChild>
              <a href="/pricing">{t('upgrade')}</a>
            </Button>
            {!subscription.cancel_at_period_end && subscription.status === 'active' && (
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowCancelDialog(true)}
              >
                {t('cancel')}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <CancelSubscriptionDialog
        open={showCancelDialog}
        onOpenChange={setShowCancelDialog}
        subscription={subscription}
        onCancel={fetchSubscription}
      />
    </>
  );
}
