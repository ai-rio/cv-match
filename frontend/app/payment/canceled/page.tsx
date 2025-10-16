'use client';

import { XCircle } from 'lucide-react';
import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function PaymentCanceled() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <Card className="text-center">
          <CardHeader>
            <div className="mx-auto mb-4">
              <XCircle className="w-16 h-16 text-red-500" />
            </div>
            <CardTitle className="text-2xl font-bold text-red-800">Pagamento Cancelado</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-gray-600">
              Seu pagamento foi cancelado. Nenhum valor foi cobrado e você não foi cobrado.
            </p>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <strong>Pode tentar novamente quando quiser!</strong>
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                Se você encontrou algum problema durante o pagamento, nossa equipe de suporte está
                aqui para ajudar.
              </p>
            </div>

            <div className="space-y-3">
              <Link href="/pricing" className="block">
                <Button className="w-full">Ver Planos</Button>
              </Link>
              <Link href="/dashboard" className="block">
                <Button variant="outline" className="w-full">
                  Voltar ao Dashboard
                </Button>
              </Link>
            </div>

            <div className="text-xs text-gray-500 space-y-1">
              <p>• Pagamentos processados com segurança via Stripe</p>
              <p>• Suporte em português disponível</p>
              <p>• Pagamentos com PIX, Boleto e cartão brasileiro</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
