import '../globals.css';

import { notFound } from 'next/navigation';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import Navigation from '@/components/Navigation';
import { AuthProvider } from '@/contexts/AuthContext';

interface LocaleLayoutProps {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}

export default async function LocaleLayout({ children, params }: LocaleLayoutProps) {
  const { locale } = await params;

  // Ensure that the incoming `locale` is valid
  if (!['en', 'pt-br'].includes(locale)) {
    notFound();
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <ErrorBoundary>
          <NextIntlClientProvider messages={messages}>
            <AuthProvider>
              <div className="min-h-screen bg-gray-50">
                <Navigation />
                <main>{children}</main>
              </div>
            </AuthProvider>
          </NextIntlClientProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'pt-br' }];
}
