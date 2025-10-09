import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['pt-br', 'en'],

  // Used when no locale matches
  defaultLocale: 'pt-br',

  // Always show the locale prefix for better SEO
  localePrefix: 'always',
});

export const config = {
  // Match only internationalized pathnames
  matcher: [
    // Enable a redirect to a matching locale at the root
    '/',

    // Set a cookie to remember the previous locale for
    // all requests that have a locale prefix
    '/(pt-br|en)/:path*',

    // Enable redirects that add missing locales
    // (e.g. `/pathnames` -> `/pt-br/pathnames`)
    '/((?!_next|_vercel|.*\\..*).*)',
  ],
};
