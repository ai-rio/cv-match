'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState } from 'react';

import { supabase } from '@/services/supabase';

export default function ForgotPassword() {
  const params = useParams();
  const locale = (params?.locale as string) || 'en';

  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });

      if (error) {
        throw error;
      }

      setMessage({
        type: 'success',
        text: 'Se foi encontrada uma conta com este email, você receberá instruções para redefinir sua senha.',
      });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Ocorreu um erro. Por favor, tente novamente.';
      setMessage({
        type: 'error',
        text: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="max-w-md w-full mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Esqueceu a senha?</h1>
          <p className="mt-2 text-gray-600">
            Digite seu email abaixo e enviaremos instruções para redefinir sua senha.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {message && (
              <div
                className={`p-3 rounded ${
                  message.type === 'success'
                    ? 'bg-green-50 border border-green-200 text-green-700'
                    : 'bg-red-50 border border-red-200 text-red-700'
                }`}
              >
                {message.text}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="seu@email.com"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Enviando...' : 'Enviar instruções'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link
              href={`/${locale}/login`}
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              ← Voltar para o login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
