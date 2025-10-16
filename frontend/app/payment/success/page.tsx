'use client';

import { CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

export default function PaymentSuccess() {
  const [credits, setCredits] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCredits = async () => {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          return;
        }

        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/optimizations/credits/check`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setCredits(data.credits || 0);
        }
      } catch (error) {
        // Log error silently in production
        // TODO: Add proper error logging service
      } finally {
        setLoading(false);
      }
    };

    fetchCredits();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <Card className="text-center">
          <CardHeader>
            <div className="mx-auto mb-4">
              <CheckCircle className="w-16 h-16 text-green-500" />
            </div>
            <CardTitle className="text-2xl font-bold text-green-800">Pagamento Aprovado!</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-gray-600">
              Seus créditos foram adicionados com sucesso à sua conta.
            </p>

            {loading ? (
              <div className="py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-sm text-gray-500 mt-2">Carregando informações...</p>
              </div>
            ) : credits !== null ? (
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-600 font-medium">Seu Saldo Atual</p>
                <p className="text-3xl font-bold text-blue-800">{credits}</p>
                <p className="text-sm text-blue-600">créditos disponíveis</p>
              </div>
            ) : null}

            <div className="space-y-3">
              <Link href="/dashboard" className="block">
                <Button className="w-full">Ir para Dashboard</Button>
              </Link>
              <Link href="/optimize" className="block">
                <Button variant="outline" className="w-full">
                  Otimizar Currículo
                </Button>
              </Link>
            </div>

            <div className="text-xs text-gray-500 space-y-1">
              <p>• Você pode usar seus créditos para otimizar currículos</p>
              <p>• Cada otimização consome 1 crédito</p>
              <p>• Seus créditos não expiram</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
