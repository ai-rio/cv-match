import { getRequestConfig } from 'next-intl/server';

export const locales = ['pt-br', 'en'] as const;
export const defaultLocale = 'pt-br' as const;

export default getRequestConfig(async ({ requestLocale }) => {
  // Provide a fallback locale if requestLocale is not available
  let locale = await requestLocale;

  if (!locale || !locales.includes(locale as (typeof locales)[number])) {
    locale = defaultLocale;
  }

  // Load all translation namespaces for the locale
  const messages: Record<string, unknown> = {};

  // Define all available namespaces
  const namespaces = [
    'common',
    'hero',
    'navigation',
    'auth',
    'pricing',
    'resume',
    'dashboard',
    'errors',
    'usage',
    'blog',
  ];

  // Load each namespace with fallback to pt-br
  for (const namespace of namespaces) {
    try {
      messages[namespace] = (await import(`./locales/${locale}/${namespace}.json`)).default;
    } catch {
      try {
        // Fallback to pt-br if locale-specific translation doesn't exist
        messages[namespace] = (
          await import(`./locales/${defaultLocale}/${namespace}.json`)
        ).default;
      } catch {
        // Final fallback - create empty object to prevent errors
        messages[namespace] = {};
      }
    }
  }

  return {
    locale,
    messages,
  };
});
