# Next-Intl Integration for Brazilian Market

## Overview

This document covers the comprehensive next-intl internationalization implementation from Resume-Matcher that must be preserved and enhanced for targeting the Brazilian market. The implementation is already production-ready with Brazilian Portuguese (pt-BR) as a primary locale.

## Current Implementation Analysis

### **✅ Production-Ready Features Found**

#### **1. Core Internationalization Setup**
- **next-intl v4.3.6**: Latest stable version
- **Multi-locale support**: English (en) + Brazilian Portuguese (pt-br)
- **Automatic locale detection**: Based on browser preferences and URL prefixes
- **Locale-specific routing**: `/pt-br/*` and `/en/*` paths
- **Fallback system**: English as default locale with error handling

#### **2. Translation Infrastructure**
```
locales/
├── en/                     # English translations
│   ├── auth.json          # Authentication pages
│   ├── blog.json          # Blog content
│   ├── common.json        # Common UI elements
│   ├── dashboard.json     # Dashboard interface
│   ├── errors.json        # Error messages
│   ├── hero.json          # Landing page hero
│   ├── navigation.json    # Navigation elements
│   ├── pricing.json       # Pricing pages
│   ├── resume.json        # Resume-related UI
│   └── usage.json         # Usage tracking
└── pt-br/                 # Brazilian Portuguese translations
    ├── auth.json          # Complete auth translations
    ├── blog.json          # Localized blog content
    ├── common.json        # Brazilian Portuguese UI terms
    ├── dashboard.json     # Dashboard with cultural adaptations
    ├── errors.json        # Localized error messages
    ├── hero.json          # Brazilian-optimized hero content
    ├── navigation.json    # Navigation in Portuguese
    ├── pricing.json       # Localized pricing (BRL currency)
    ├── resume.json        # Resume-specific translations
    └── usage.json         # Usage tracking in Portuguese
```

#### **3. Advanced Features**
- **Modular translation loading**: Separate JSON files per feature
- **Deep merge functionality**: Combines translation modules properly
- **Error handling**: Fallback to English if locale loading fails
- **Type safety**: TypeScript integration with locale types
- **Server-side rendering**: Full SSR support with locale detection
- **Middleware integration**: Combines auth and i18n middleware

#### **4. Brazilian Market Optimizations**
- **Currency formatting**: Brazilian Real (R$) with proper locale formatting
- **Date/time formatting**: Brazilian format (DD/MM/YYYY)
- **Cultural adaptations**: Uses formal "você" instead of "tu"
- **Payment integration**: Stripe configured for Brazilian market
- **Content localization**: Job market-specific terminology

## Integration Strategy for CV-Match

### **Step 1: Core Internationalization Setup**

#### **1.1 Install Required Dependencies**
```bash
cd /home/carlos/projects/cv-match/frontend
bun install next-intl@4.3.6
```

#### **1.2 Create i18n Directory Structure**
```bash
mkdir -p /home/carlos/projects/cv-match/frontend/src/i18n
mkdir -p /home/carlos/projects/cv-match/frontend/locales/{en,pt-br}
```

#### **1.3 Copy Core Configuration Files**
```bash
# Copy routing configuration
cp /home/carlos/projects/Resume-Matcher/apps/frontend/src/i18n/routing.ts \
   /home/carlos/projects/cv-match/frontend/src/i18n/

# Copy request configuration
cp /home/carlos/projects/Resume-Matcher/apps/frontend/src/i18n/request.ts \
   /home/carlos/projects/cv-match/frontend/src/i18n/
```

#### **1.4 Update Next.js Configuration**
```typescript
// /home/carlos/projects/cv-match/frontend/next.config.ts
const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const nextConfig = {
  // Your existing config...
  transpilePackages: ['next-intl'],
};

export default withNextIntl(nextConfig);
```

### **Step 2: Translation File Migration**

#### **2.1 Copy Translation Files**
```bash
# Copy all translation files
cp -r /home/carlos/projects/Resume-Matcher/apps/frontend/locales/* \
   /home/carlos/projects/cv-match/frontend/locales/
```

#### **2.2 Enhance for CV-Match Specific Features**

**Create enhanced auth.json for cv-match:**
```json
{
  "auth": {
    "login": {
      "title": "Entrar na sua Conta CV-Match",
      "subtitle": "Otimize seu currículo com IA para o mercado brasileiro",
      "email": "E-mail",
      "emailPlaceholder": "seu@email.com.br",
      "password": "Senha",
      "passwordPlaceholder": "Digite sua senha segura",
      "submit": "Entrar",
      "forgotPassword": "Esqueceu sua senha?",
      "noAccount": "Não tem uma conta?",
      "signUp": "Criar conta gratuita"
    }
  }
}
```

**Create cv-match specific dashboard.json:**
```json
{
  "dashboard": {
    "title": "Painel CV-Match",
    "subtitle": "Otimize suas chances de contratação",
    "uploadResume": "Enviar Currículo",
    "jobAnalysis": "Análise de Vaga",
    "matchScore": "Pontuação de Compatibilidade",
    "improvements": "Sugestões de Melhoria",
    "downloadOptimized": "Baixar Currículo Otimizado"
  }
}
```

### **Step 3: Brazilian Market Enhancements**

#### **3.1 Currency and Number Formatting**
```typescript
// /home/carlos/projects/cv-match/frontend/src/lib/pt-br-formatters.ts

export function formatCurrencyBRL(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatPercentageBRL(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatFileSizePT(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB'];
  const size = bytes / 1024;
  const unitIndex = Math.floor(Math.log(size) / Math.log(1024));
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}
```

#### **3.2 Date and Time Formatting**
```typescript
// Enhanced date formatting for Brazilian market
export function formatDateBrazil(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(dateObj);
}

export function formatDateTimeBrazil(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj);
}
```

#### **3.3 Brazilian Market-Specific Content**
```json
{
  "pricing": {
    "title": "Planos CV-Match Brasil",
    "free": {
      "name": "Grátis",
      "price": "R$ 0",
      "description": "Comece gratuito com 5 análises",
      "features": [
        "5 análises de currículo por mês",
        "Upload de PDF/DOCX",
        "Análise básica de compatibilidade"
      ]
    },
    "pro": {
      "name": "Profissional",
      "price": "R$ 29,90/mês",
      "description": "Ideal para profissionais em busca ativa",
      "features": [
        "Análises ilimitadas",
        "Otimização avançada com IA",
        "Templates brasileiros",
        "Suporte prioritário"
      ]
    },
    "enterprise": {
      "name": "Empresarial",
      "price": "R$ 99,90/mês",
      "description": "Para recrutadores e empresas",
      "features": [
        "Análises em lote",
        "Dashboard de recrutamento",
        "API de integração",
        "Suporte dedicado"
      ]
    }
  }
}
```

### **Step 4: Middleware Integration**

#### **4.1 Enhanced Middleware**
```typescript
// /home/carlos/projects/cv-match/frontend/middleware.ts
import createMiddleware from 'next-intl/middleware';
import { routing } from './src/i18n/routing';

const intlMiddleware = createMiddleware(routing);

export default intlMiddleware;

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
```

#### **4.2 Route Structure Setup**
```typescript
// /home/carlos/projects/cv-match/frontend/src/i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'pt-br'],
  defaultLocale: 'en',
  localePrefix: 'always', // Always show locale in URL
});

export type Locale = (typeof routing.locales)[number];
```

### **Step 5: Component Integration**

#### **5.1 Layout Setup**
```typescript
// /home/carlos/projects/cv-match/frontend/app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  // Validate locale
  if (!['en', 'pt-br'].includes(locale)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### **5.2 Component Usage Example**
```tsx
// /home/carlos/projects/cv-match/frontend/components/resume-upload.tsx
import { useTranslations } from 'next-intl';

export default function ResumeUpload() {
  const t = useTranslations('upload');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('subtitle')}</p>
      <button>{t('button')}</button>
    </div>
  );
}
```

## Brazilian Market Specific Optimizations

### **1. Cultural Adaptations**

#### **Formal Language Guidelines**
- Use "você" instead of "tu" for formal communication
- Proper job market terminology (currículo instead of resumo)
- Brazilian Portuguese grammar and spelling

#### **Job Market Specific Terms**
```json
{
  "resume": {
    "jobTitle": "Cargo",
    "experience": "Experiência Profissional",
    "skills": "Habilidades",
    "education": "Formação Acadêmica",
    "certifications": "Certificações",
    "languages": "Idiomas",
    "projects": "Projetos"
  },
  "analysis": {
    "jobDescription": "Descrição da Vaga",
    "requirements": "Requisitos",
    "qualifications": "Qualificações",
    "responsibilities": "Responsabilidades",
    "benefits": "Benefícios",
    "salary": "Salário"
  }
}
```

### **2. Payment Integration**

#### **Brazilian Payment Methods**
```json
{
  "payment": {
    "methods": {
      "credit": "Cartão de Crédito",
      "debit": "Cartão de Débito",
      "pix": "PIX",
      "boleto": "Boleto Bancário"
    },
    "installments": "Parcelado em {count}x de {value}",
    "currency": "BRL"
  }
}
```

### **3. SEO Optimization for Brazil**

#### **Meta Tags and Descriptions**
```typescript
// Dynamic SEO for Brazilian market
export function getBrazilianSEOMetadata(pathname: string) {
  return {
    title: 'CV-Match Brasil: Otimizador de Currículos com IA',
    description: 'Aumente suas chances de contratação no mercado brasileiro com análise de currículo inteligente',
    keywords: 'currículo, emprego, brasil, otimização, ia, recrutamento',
    locale: 'pt-BR',
  };
}
```

## Testing and Validation

### **1. Locale Testing Strategy**
```typescript
// Test locale-specific functionality
describe('Brazilian Portuguese Localization', () => {
  test('Currency formatting', () => {
    expect(formatCurrencyBRL(29.90)).toBe('R$ 29,90');
  });

  test('Date formatting', () => {
    expect(formatDateBrazil('2024-01-15')).toBe('15/01/2024');
  });

  test('Translation loading', async () => {
    const messages = await getMessages('pt-br');
    expect(messages.dashboard.title).toBe('Painel CV-Match');
  });
});
```

### **2. User Acceptance Testing**
- Test all user flows in Brazilian Portuguese
- Validate payment flows with BRL currency
- Check form validations with Brazilian-specific inputs
- Test email templates in Portuguese

## Deployment Configuration

### **1. Environment Variables**
```bash
# Frontend .env.local
NEXT_PUBLIC_DEFAULT_LOCALE=pt-br
NEXT_PUBLIC_SUPPORTED_LOCALES=en,pt-br
NEXT_PUBLIC_MARKET=brasil
```

### **2. Build Configuration**
```json
{
  "scripts": {
    "build": "next build",
    "build:en": "next build --locale en",
    "build:pt-br": "next build --locale pt-br",
    "start": "next start"
  }
}
```

## Migration Checklist

### **✅ Must-Have Features**
- [ ] next-intl v4.3.6+ installed
- [ ] Locale routing configured
- [ ] Brazilian Portuguese translations copied
- [ ] Middleware for locale detection
- [ ] Currency formatting for BRL
- [ ] Date/time formatting for Brazilian locale
- [ ] SEO optimization for Brazilian market

### **🎯 Brazilian Market Enhancements**
- [ ] PIX payment method integration
- [ ] Brazilian job market terminology
- [ ] Cultural adaptations (formal language)
- [ ] Localized error messages
- [ ] Brazilian-specific legal pages
- [ ] Portuguese email templates

### **🔧 Technical Requirements**
- [ ] Type-safe locale definitions
- [ ] Fallback system working
- [ ] SSR with locale detection
- [ ] Static generation for SEO
- [ ] Client-side navigation with locale preservation

This comprehensive next-intl implementation ensures that CV-Match can effectively target the Brazilian market with proper localization, cultural adaptations, and market-specific features.
