'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { createClient } from '@/lib/supabase/client';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  subscription: any;
  onCancel: () => void;
}

export function CancelSubscriptionDialog({ open, onOpenChange, subscription, onCancel }: Props) {
  const t = useTranslations('subscriptions.cancel_dialog');
  const [loading, setLoading] = useState(false);

  const handleCancel = async () => {
    setLoading(true);

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error('Você precisa estar logado para cancelar a assinatura');
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/subscriptions/${subscription.id}/cancel`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao cancelar assinatura');
      }

      onCancel();
      onOpenChange(false);
    } catch (error) {
      console.error('Cancel failed:', error);
      // TODO: Replace with proper toast notification when available
      // alert(error instanceof Error ? error.message : 'Erro ao cancelar assinatura');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('title')}</AlertDialogTitle>
          <AlertDialogDescription>{t('description')}</AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-2 my-4">
          <p className="text-sm font-medium">{t('consequences')}</p>
          <ul className="text-sm text-muted-foreground space-y-1 ml-4">
            <li>• {t('lose_access')}</li>
            <li>
              •{' '}
              {t('keep_until', {
                date: new Date(subscription.current_period_end).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                }),
              })}
            </li>
          </ul>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>{t('keep')}</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleCancel}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700"
          >
            {loading ? 'Cancelando...' : t('confirm')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
