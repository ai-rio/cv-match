## Overview
This project uses **next-intl** for comprehensive internationalization (i18n) supporting **Portuguese (pt-BR)** and **English (en)** locales. All user-facing strings MUST be internationalized - NO hard-coded text in any language.

## Core Principles

### 1. Zero Hard-Coded Strings
- **NEVER** hard-code user-facing text in components
- **ALWAYS** use translation keys via `useTranslations()` or `getTranslations()`
- Even technical terms, labels, and placeholders MUST be translated
- Exception: Internal constants, config values, API keys (non-user-facing)

### 2. Locale Configuration
- **Supported Locales**: `['pt-BR', 'en']`
- **Default Locale**: `pt-BR` (Brazilian Portuguese)
- Locale is determined by URL prefix: `/pt-BR/*` or `/en/*`

### 3. File Structure
```
src/
├── i18n/
│   ├── routing.ts              # Routing configuration
│   └── request.ts              # Server-side i18n config
├── messages/
│   ├── pt-BR.json              # Portuguese translations
│   └── en.json                 # English translations
├── app/
│   ├── [locale]/               # Locale-based routing
│   │   ├── layout.tsx          # Root layout with provider
│   │   └── page.tsx            # Pages
│   └── middleware.ts           # Locale detection middleware
```

---

## Implementation Guidelines

### A. Server Components (Preferred)

Server Components are the **default and preferred** approach for i18n in Next.js App Router.

#### ✅ DO: Use `getTranslations` in async Server Components
```tsx
import {getTranslations} from 'next-intl/server';

export default async function ProfilePage() {
  const t = await getTranslations('ProfilePage');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

#### ✅ DO: Use `useTranslations` in non-async Server Components
```tsx
import {useTranslations} from 'next-intl';

export default function UserCard({user}) {
  const t = useTranslations('UserCard');
  
  return (
    <div>
      <h2>{t('title')}</h2>
      <p>{t('followers', {count: user.followers})}</p>
    </div>
  );
}
```

#### ✅ DO: Pass translated content as props to Client Components
```tsx
// Server Component
import {useTranslations} from 'next-intl';
import InteractiveButton from './InteractiveButton'; // Client Component

export default function FAQSection() {
  const t = useTranslations('FAQ');
  
  return (
    <InteractiveButton 
      label={t('submitButton')}
      successMessage={t('successMessage')}
    />
  );
}
```

### B. Client Components

Use Client Components **only when necessary** for interactivity (useState, useEffect, event handlers).

#### ✅ DO: Wrap with NextIntlClientProvider and pass specific messages
```tsx
// Parent Server Component
import {useTranslations, useMessages} from 'next-intl';
import {NextIntlClientProvider} from 'next-intl';
import pick from 'lodash/pick';
import InteractiveForm from './InteractiveForm';

export default function ContactSection() {
  const messages = useMessages();
  
  return (
    <NextIntlClientProvider 
      messages={pick(messages, 'ContactForm')}
    >
      <InteractiveForm />
    </NextIntlClientProvider>
  );
}
```

#### ✅ DO: Use `useTranslations` inside Client Components
```tsx
'use client';

import {useTranslations} from 'next-intl';
import {useState} from 'react';

export default function InteractiveForm() {
  const t = useTranslations('ContactForm');
  const [submitted, setSubmitted] = useState(false);
  
  return (
    <form>
      <label>{t('nameLabel')}</label>
      <input placeholder={t('namePlaceholder')} />
      <button type=\"submit\">{t('submitButton')}</button>
      {submitted && <p>{t('successMessage')}</p>}
    </form>
  );
}
```

#### ❌ DON'T: Pass all messages to client (bad for performance)
```tsx
// BAD - Sends entire message bundle to client
<NextIntlClientProvider>
  <HeavyClientComponent />
</NextIntlClientProvider>

// GOOD - Only pass needed messages
<NextIntlClientProvider messages={pick(messages, 'HeavyClientComponent')}>
  <HeavyClientComponent />
</NextIntlClientProvider>
```

### C. Configuration Files

#### `src/i18n/routing.ts`
```typescript
import {defineRouting} from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['pt-BR', 'en'],
  defaultLocale: 'pt-BR'
});
```

#### `src/i18n/request.ts`
```typescript
import {getRequestConfig} from 'next-intl/server';
import {routing} from './routing';

export default getRequestConfig(async ({requestLocale}) => {
  // Validate and get locale
  let locale = await requestLocale;
  
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
    timeZone: 'America/Sao_Paulo',
    now: new Date()
  };
});
```

#### `next.config.ts`
```typescript
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const nextConfig = {
  // Your Next.js config
};

export default withNextIntl(nextConfig);
```

#### `src/middleware.ts`
```typescript
import createMiddleware from 'next-intl/middleware';
import {routing} from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: [
    '/((?!api|_next|_vercel|.*\\\\..*).*)',
    '/',
    '/(pt-BR|en)/:path*'
  ]
};
```

### D. Root Layout Configuration

#### `app/[locale]/layout.tsx`
```tsx
import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import {notFound} from 'next/navigation';
import {routing} from '@/i18n/routing';

type Props = {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
};

export default async function LocaleLayout({children, params}: Props) {
  const {locale} = await params;
  
  // Validate locale
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  // Get messages for this locale
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider 
          locale={locale}
          messages={messages}
          timeZone=\"America/Sao_Paulo\"
        >
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

// Generate static params for both locales
export function generateStaticParams() {
  return routing.locales.map((locale) => ({locale}));
}
```

---

## Translation Message Organization

### Message File Structure (`messages/pt-BR.json` & `messages/en.json`)

```json
{
  \"Common\": {
    \"loading\": \"Carregando...\",
    \"error\": \"Erro\",
    \"success\": \"Sucesso\",
    \"cancel\": \"Cancelar\",
    \"save\": \"Salvar\",
    \"delete\": \"Excluir\",
    \"edit\": \"Editar\",
    \"back\": \"Voltar\",
    \"next\": \"Próximo\",
    \"submit\": \"Enviar\"
  },
  \"Navigation\": {
    \"home\": \"Início\",
    \"dashboard\": \"Painel\",
    \"profile\": \"Perfil\",
    \"settings\": \"Configurações\",
    \"logout\": \"Sair\"
  },
  \"CVUpload\": {
    \"title\": \"Upload de Currículo\",
    \"description\": \"Faça upload do seu CV para análise\",
    \"dragDropText\": \"Arraste e solte seu arquivo aqui ou clique para selecionar\",
    \"supportedFormats\": \"Formatos suportados: PDF, DOCX\",
    \"maxSize\": \"Tamanho máximo: {size}MB\",
    \"uploadButton\": \"Fazer Upload\",
    \"uploadSuccess\": \"Upload realizado com sucesso!\",
    \"uploadError\": \"Erro ao fazer upload. Tente novamente.\"
  },
  \"JobMatching\": {
    \"title\": \"Correspondência de Vagas\",
    \"matchScore\": \"Pontuação: {score}%\",
    \"noMatches\": \"Nenhuma vaga encontrada\",
    \"viewDetails\": \"Ver Detalhes\",
    \"applyNow\": \"Candidatar-se Agora\"
  },
  \"Forms\": {
    \"validation\": {
      \"required\": \"Este campo é obrigatório\",
      \"email\": \"Email inválido\",
      \"minLength\": \"Mínimo de {min} caracteres\",
      \"maxLength\": \"Máximo de {max} caracteres\"
    }
  }
}
```

### Naming Conventions for Translation Keys

1. **Organize by Feature/Component**: `ComponentName.keyName`
2. **Use camelCase for keys**: `uploadButton`, `successMessage`
3. **Group related keys**: `Forms.validation.required`
4. **Be descriptive**: `dragDropText` not `text1`
5. **Include interpolation variables**: `\"Maximum size: {size}MB\"`

---

## Best Practices & Patterns

### 1. ICU Message Format for Dynamic Content

#### Pluralization
```json
{
  \"items\": \"{count, plural, =0 {No items} =1 {One item} other {# items}}\"
}
```

```tsx
const t = useTranslations('Cart');
<p>{t('items', {count: cartItems.length})}</p>
```

#### Select/Switch
```json
{
  \"status\": \"{status, select, pending {Pending} approved {Approved} rejected {Rejected} other {Unknown}}\"
}
```

#### Rich Text
```tsx
const t = useTranslations('Profile');

<p>{t.rich('bio', {
  strong: (chunks) => <strong>{chunks}</strong>,
  link: (chunks) => <a href=\"/terms\">{chunks}</a>
})}</p>
```

### 2. Type-Safe Translations (TypeScript)

Create types for your message keys:

```typescript
// types/translations.ts
import type ptBR from '@/messages/pt-BR.json';

type Messages = typeof ptBR;

declare global {
  interface IntlMessages extends Messages {}
}
```

This enables autocomplete and type checking:

```tsx
const t = useTranslations('CVUpload');
t('title') // ✅ Type-safe
t('nonExistent') // ❌ TypeScript error
```

### 3. Shared Components with Translations

```tsx
// components/Button.tsx
import {useTranslations} from 'next-intl';

type ButtonProps = {
  translationKey: string;
  namespace: string;
  onClick?: () => void;
};

export default function Button({translationKey, namespace, onClick}: ButtonProps) {
  const t = useTranslations(namespace);
  
  return (
    <button onClick={onClick}>
      {t(translationKey)}
    </button>
  );
}

// Usage
<Button namespace=\"Common\" translationKey=\"save\" onClick={handleSave} />
```

### 4. Date & Number Formatting

```tsx
import {useFormatter} from 'next-intl';

export default function Stats() {
  const format = useFormatter();
  const now = new Date();
  
  return (
    <div>
      <p>{format.dateTime(now, {dateStyle: 'long'})}</p>
      <p>{format.number(1234.56, {style: 'currency', currency: 'BRL'})}</p>
      <p>{format.relativeTime(now, 'hour')}</p>
    </div>
  );
}
```

### 5. Navigation with Locale

```typescript
// lib/navigation.ts
import {createNavigation} from 'next-intl/navigation';
import {routing} from '@/i18n/routing';

export const {Link, redirect, usePathname, useRouter} = 
  createNavigation(routing);
```

```tsx
import {Link} from '@/lib/navigation';

// Automatically includes locale prefix
<Link href=\"/dashboard\">Dashboard</Link>
// Renders: /pt-BR/dashboard or /en/dashboard
```

---

## Testing Translations

### Check for Missing Translations

```typescript
// scripts/check-translations.ts
import en from '../messages/en.json';
import ptBR from '../messages/pt-BR.json';

function checkKeys(obj1: any, obj2: any, path: string = '') {
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  keys1.forEach(key => {
    const currentPath = path ? `${path}.${key}` : key;
    
    if (!keys2.includes(key)) {
      console.error(`Missing key in pt-BR: ${currentPath}`);
    } else if (typeof obj1[key] === 'object') {
      checkKeys(obj1[key], obj2[key], currentPath);
    }
  });
}

checkKeys(en, ptBR);
checkKeys(ptBR, en);
```

### Testing Component Translations

```tsx
// __tests__/CVUpload.test.tsx
import {render, screen} from '@testing-library/react';
import {NextIntlClientProvider} from 'next-intl';
import CVUpload from '@/components/CVUpload';

const messages = {
  CVUpload: {
    title: 'Upload de Currículo'
  }
};

test('renders translated title', () => {
  render(
    <NextIntlClientProvider locale=\"pt-BR\" messages={messages}>
      <CVUpload />
    </NextIntlClientProvider>
  );
  
  expect(screen.getByText('Upload de Currículo')).toBeInTheDocument();
});
```

---

## Common Mistakes to Avoid

### ❌ DON'T: Hard-code any user-facing text
```tsx
// BAD
<button>Submit</button>
<h1>Welcome to CV Match</h1>
```

### ✅ DO: Always use translations
```tsx
// GOOD
const t = useTranslations('Common');
<button>{t('submit')}</button>

const t = useTranslations('HomePage');
<h1>{t('welcome')}</h1>
```

### ❌ DON'T: Use translations in API routes or server actions directly
```tsx
// BAD - Server actions don't have access to locale by default
export async function submitCV() {
  const t = useTranslations(); // ❌ Won't work
}
```

### ✅ DO: Pass translated messages from components
```tsx
// GOOD
export default function CVForm() {
  const t = useTranslations('CVForm');
  
  async function handleSubmit() {
    await submitCV({
      successMessage: t('success'),
      errorMessage: t('error')
    });
  }
}
```

### ❌ DON'T: Import wrong translation functions
```tsx
// BAD
import {useTranslations} from 'next-intl'; // ❌ In async Server Component

export default async function Page() {
  const t = useTranslations(); // Won't work
}
```

### ✅ DO: Use correct function for component type
```tsx
// GOOD
import {getTranslations} from 'next-intl/server'; // ✅ Correct import

export default async function Page() {
  const t = await getTranslations(); // Works!
}
```

---

## Error Handling

Configure custom error handlers in `src/i18n/request.ts`:

```typescript
import {getRequestConfig} from 'next-intl/server';
import {IntlErrorCode} from 'next-intl';

export default getRequestConfig(async ({requestLocale}) => {
  // ...
  
  return {
    locale,
    messages,
    onError(error) {
      if (error.code === IntlErrorCode.MISSING_MESSAGE) {
        console.warn(`Missing translation: ${error.message}`);
      } else {
        console.error('Translation error:', error);
      }
    },
    getMessageFallback({namespace, key}) {
      return `${namespace}.${key}`; // Shows missing key path
    }
  };
});
```

---

## Quick Reference Checklist

When creating ANY new component, page, or feature:

- [ ] NO hard-coded strings in any language
- [ ] All user-facing text uses `useTranslations()` or `getTranslations()`
- [ ] Message keys added to BOTH `messages/pt-BR.json` AND `messages/en.json`
- [ ] Use Server Components by default (more performant)
- [ ] Only use Client Components when interactivity is needed
- [ ] Pass specific messages to Client Components (use `pick()`)
- [ ] Use proper imports: `next-intl` for Client, `next-intl/server` for Server
- [ ] Test in both locales: `/pt-BR/...` and `/en/...`
- [ ] Use ICU format for pluralization, variables, and rich text
- [ ] Utilize `useFormatter()` for dates, numbers, currencies
- [ ] Use locale-aware navigation from `@/lib/navigation`

---

## Additional Resources

- **Official Docs**: https://next-intl-docs.vercel.app/
- **ICU Message Format**: https://unicode-org.github.io/icu/userguide/format_parse/messages/
- **Migration Guide**: Check docs if upgrading from older versions

---

## Questions to Ask When Reviewing Code

1. \"Can I see any hard-coded user-facing text?\" → Should be NO
2. \"Are all translations present in both locale files?\" → Should be YES
3. \"Is this component using the right translation hook?\" → Check async/sync
4. \"Could this be a Server Component instead of Client?\" → Prefer Server
5. \"Are we passing all messages to the client?\" → Only pass what's needed
