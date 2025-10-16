'use client';

import { Coins } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/lib/api';

interface CreditBalance {
  credits_remaining: number;
  total_credits: number;
  tier: string;
  is_pro: boolean;
  can_optimize: boolean;
  upgrade_prompt?: string;
}

interface CreditBalanceResponse {
  credits_remaining: number;
  total_credits: number;
  tier: string;
  is_pro: boolean;
  can_optimize: boolean;
  upgrade_prompt?: string;
}

export default function CreditBalance() {
  const { token, isAuthenticated } = useAuth();
  const [creditData, setCreditData] = useState<CreditBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const remainingOptimizations = creditData?.credits_remaining || 0;

  useEffect(() => {
    const fetchCreditBalance = async () => {
      if (!isAuthenticated || !token) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await apiService.get<CreditBalanceResponse>('/api/users/credits', token);
        setCreditData(response);
        setError(null);
      } catch (err) {
        // TODO: Add proper error logging service
        setError('Não foi possível carregar seus créditos. Tente novamente mais tarde.');
        setCreditData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchCreditBalance();
  }, [isAuthenticated, token]);

  if (!isAuthenticated) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5 text-yellow-600" />
            Créditos
          </CardTitle>
          <CardDescription>Faça login para ver seus créditos disponíveis</CardDescription>
        </CardHeader>
        <CardContent>
          <Link href="/auth/login">
            <Button className="w-full">Entrar</Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5 text-yellow-600 animate-pulse" />
            Créditos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/2 mx-auto mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
            </div>
            <div className="animate-pulse">
              <div className="h-9 bg-gray-200 rounded"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5 text-red-600" />
            Créditos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-red-600">{error}</p>
            <Button variant="outline" className="w-full" onClick={() => window.location.reload()}>
              Tentar Novamente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Coins className="h-5 w-5 text-yellow-600" />
          Seus Créditos
        </CardTitle>
        <CardDescription>Otimizações de currículo disponíveis</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center py-4">
          <div className="text-3xl font-bold text-primary mb-2">{remainingOptimizations}</div>
          <div className="text-sm text-muted-foreground">
            {remainingOptimizations === 1 ? 'otimização restante' : 'otimizações restantes'}
          </div>
          {creditData && (
            <div className="text-xs text-muted-foreground mt-1">
              Plano:{' '}
              {creditData.tier === 'pro'
                ? 'Pro'
                : creditData.tier === 'free'
                  ? 'Grátis'
                  : creditData.tier}
              {creditData.is_pro && (
                <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  PRO
                </span>
              )}
            </div>
          )}
        </div>

        {creditData?.upgrade_prompt && (
          <div className="text-center py-2 px-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-sm text-yellow-800">{creditData.upgrade_prompt}</p>
          </div>
        )}

        {!creditData?.can_optimize && (
          <div className="text-center py-2 px-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">Você não tem mais otimizações disponíveis</p>
          </div>
        )}

        <Link href="/pricing" className="block">
          <Button className="w-full" variant={!creditData?.can_optimize ? 'default' : 'outline'}>
            {!creditData?.can_optimize ? 'Comprar Créditos' : 'Comprar Mais Créditos'}
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
