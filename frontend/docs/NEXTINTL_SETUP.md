# Next-intl Internationalization Setup

## Overview

This document outlines the complete internationalization (i18n) setup for CV-Match using next-intl v4.3.6, configured specifically for the Brazilian market with PT-BR as the primary locale and EN as the secondary locale.

## Installation

### Dependencies

- **next-intl**: ^4.3.6
- **Package Manager**: Bun (not npm)

```bash
bun add next-intl@4.3.6
```

## Configuration Files

### 1. `i18n.ts` - Core Configuration

```typescript
import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => {
  return {
    messages: (await import(`./locales/${locale}/common.json`)).default,
  };
});
```

### 2. `middleware.ts` - Locale Detection

```typescript
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  locales: ['pt-br', 'en'],
  defaultLocale: 'pt-br',
  localePrefix: 'always',
});

export const config = {
  matcher: ['/', '/(pt-br|en)/:path*', '/((?!_next|_vercel|.*\\..*).*)'],
};
```

### 3. `next.config.mjs` - Next.js Integration

```javascript
import createNextIntlPlugin from 'next-intl/plugin';
const withNextIntl = createNextIntlPlugin('./i18n.ts');

export default withSentryConfig(withNextIntl(nextConfig), {
  // Sentry configuration
});
```

## Directory Structure

```
frontend/
├── app/
│   ├── [locale]/
│   │   ├── layout.tsx         # Locale-specific layout
│   │   ├── page.tsx           # Localized homepage
│   │   └── dashboard/         # Localized dashboard
│   ├── layout.tsx             # Root layout
│   └── middleware.ts          # Locale middleware
├── components/
│   ├── LanguageSwitcher.tsx   # Language switcher component
│   ├── LanguageSwitcherButton.tsx  # Toggle button version
│   └── Navigation.tsx         # Navigation with i18n
├── locales/
│   ├── pt-br/
│   │   ├── common.json        # Common translations
│   │   ├── auth.json          # Authentication translations
│   │   └── dashboard.json     # Dashboard translations
│   └── en/
│       ├── common.json        # English translations
│       ├── auth.json          # Authentication translations
│       └── dashboard.json     # Dashboard translations
├── i18n.ts                    # Core configuration
└── next.config.mjs           # Next.js config
```

## Translation Files

### Common Translations (`locales/pt-br/common.json`)

- Navigation items
- UI elements
- Actions and buttons
- Status messages
- Time and date formatting
- Units and currency

### Authentication Translations (`locales/pt-br/auth.json`)

- Login form
- Sign up form
- Password reset
- Email verification
- Error messages

### Dashboard Translations (`locales/pt-br/dashboard.json`)

- Dashboard overview
- Analytics and insights
- Settings and preferences
- Billing and subscriptions

## Components

### 1. Language Switcher Button

```typescript
'use client';
import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { useTransition } from 'react';

export default function LanguageSwitcherButton() {
  const [isPending, startTransition] = useTransition();
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLanguageChange = (newLocale: string) => {
    startTransition(() => {
      const newPathname = pathname.replace(`/${locale}`, `/${newLocale}`);
      router.push(newPathname);
    });
  };

  return (
    <button onClick={() => handleLanguageChange(otherLocale)}>
      {otherLocale === 'pt-br' ? '🇧🇷' : '🇺🇸'} {otherLocaleData?.name}
    </button>
  );
}
```

### 2. Navigation Component

```typescript
'use client';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import LanguageSwitcherButton from './LanguageSwitcherButton';

export default function Navigation() {
  const t = useTranslations('common');

  return (
    <nav>
      <Link href="/">{t('navigation.home')}</Link>
      <Link href="/dashboard">{t('navigation.dashboard')}</Link>
      <LanguageSwitcherButton />
    </nav>
  );
}
```

## Usage Examples

### 1. Basic Translation Usage

```typescript
'use client';
import { useTranslations } from 'next-intl';

export default function MyComponent() {
  const t = useTranslations('common');

  return (
    <div>
      <h1>{t('hero.title')}</h1>
      <p>{t('hero.subtitle')}</p>
      <button>{t('actions.getStarted')}</button>
    </div>
  );
}
```

### 2. Nested Translations

```typescript
const t = useTranslations('auth.login');
return (
  <form>
    <label>{t('email')}</label>
    <input placeholder={t('emailPlaceholder')} />
    <button>{t('submit')}</button>
  </form>
);
```

### 3. Parameterized Translations

```json
{
  "welcome": "Welcome back, {name}!",
  "itemsCount": "You have {count, plural, =0 {no items} =1 {one item} other {# items}}"
}
```

```typescript
const t = useTranslations('common');
t('welcome', { name: 'Carlos' });
t('itemsCount', { count: 5 });
```

## Routing Structure

### URL Patterns

- **Default locale**: `https://cv-match.com/pt-br/`
- **English**: `https://cv-match.com/en/`
- **Dashboard**: `https://cv-match.com/pt-br/dashboard`
- **Auth**: `https://cv-match.com/pt-br/auth/login`

### Route Generation

```typescript
export function generateStaticParams() {
  return [{ locale: 'pt-br' }, { locale: 'en' }];
}
```

## Brazilian Market Specifics

### 1. Currency Formatting

```json
{
  "units": {
    "currency": "R$",
    "currencyFormat": "R$ {value}"
  }
}
```

### 2. Date Formatting

- PT-BR: `DD/MM/YYYY` (e.g., "08/10/2025")
- EN: `MM/DD/YYYY` (e.g., "10/08/2025")

### 3. Number Formatting

- PT-BR: `1.234,56` (comma as decimal separator)
- EN: `1,234.56` (period as decimal separator)

## Best Practices

### 1. Translation Keys

- Use descriptive, hierarchical keys
- Group related translations together
- Avoid concatenating translated strings

### 2. Component Structure

- Keep translations close to components that use them
- Use `useTranslations` hook in client components
- Server components can use `getTranslations` directly

### 3. Performance

- Static generation is used for all locales
- Translation files are loaded on-demand
- Language switching is client-side without page reload

### 4. SEO Optimization

- Always include locale in URLs (`/pt-br/`, `/en/`)
- Set proper `lang` attribute in HTML
- Use `hreflang` tags for alternate languages

## Integration with Existing Systems

### 1. Supabase Authentication

- Works seamlessly with existing auth flow
- Language preference can be stored in user profile
- Auth callbacks respect locale routing

### 2. Stripe Payments

- Currency configured for BRL in PT-BR
- Payment forms use localized labels
- Error messages are translated

### 3. Sentry Error Tracking

- Error reports include current locale
- User feedback can be submitted in preferred language

## Testing

### 1. Development

```bash
bun run dev
```

Test URLs:

- http://localhost:3000/pt-br/
- http://localhost:3000/en/

### 2. Build

```bash
bun run build
```

### 3. Production

```bash
bun run start
```

## Adding New Translations

### 1. Add Translation Keys

```json
// locales/pt-br/common.json
{
  "newFeature": {
    "title": "Novo Recurso",
    "description": "Descrição do novo recurso"
  }
}
```

### 2. Add English Version

```json
// locales/en/common.json
{
  "newFeature": {
    "title": "New Feature",
    "description": "Description of the new feature"
  }
}
```

### 3. Use in Component

```typescript
const t = useTranslations('common.newFeature');
return <div>
  <h2>{t('title')}</h2>
  <p>{t('description')}</p>
</div>;
```

## Troubleshooting

### Common Issues

1. **Build Errors**
   - Ensure all translation files have matching keys
   - Check for invalid JSON syntax
   - Verify locale codes match configuration

2. **Missing Translations**
   - Check file names and directory structure
   - Verify i18n.ts configuration
   - Ensure middleware is properly configured

3. **Routing Issues**
   - Check middleware matcher patterns
   - Verify locale prefix settings
   - Ensure file structure matches routes

### Debug Mode

```typescript
// i18n.ts
export default getRequestConfig(async ({ locale }) => {
  console.log('Loading locale:', locale);
  return {
    messages: (await import(`./locales/${locale}/common.json`)).default,
  };
});
```

## Future Enhancements

1. **Dynamic Loading**: Load translations on-demand for better performance
2. **RTL Support**: Prepare for Arabic/Hebrew languages if needed
3. **Pluralization**: Enhanced pluralization rules for Portuguese
4. **Date/Time Libraries**: Integration with date-fns for advanced formatting
5. **Content Management**: CMS integration for translation management

## Support

For issues related to next-intl setup:

1. Check [next-intl documentation](https://next-intl-docs.vercel.app/)
2. Review this configuration guide
3. Contact the development team for CV-Match specific issues
