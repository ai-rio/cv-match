# 🌍 Localization Guide - P1.5 Subscription System

**CRITICAL**: ALL text MUST use next-intl. NO hardcoded strings in UI!

---

## 🚨 CRITICAL RULES

### ❌ NEVER DO THIS:

```tsx
// ❌ WRONG - Hardcoded Portuguese
<Button>Assinar Agora</Button>
<h1>Flow Pro</h1>
<p>R$ 49,90 por mês</p>
```

### ✅ ALWAYS DO THIS:

```tsx
// ✅ RIGHT - Using next-intl
import { useTranslations } from 'next-intl';

const t = useTranslations('pricing');

<Button>{t('subscribe_now')}</Button>
<h1>{t('flow_pro.name')}</h1>
<p>{t('flow_pro.price', { amount: '49,90' })}</p>
```

---

## 📋 Next-Intl Best Practices

### 1. Translation File Structure

**Location**: `frontend/locales/{locale}/{namespace}.json`

**For P1.5, create**: `frontend/locales/pt-br/subscriptions.json`

```json
{
  "subscriptions": {
    "title": "Escolha seu plano",
    "subtitle": "Encontre o plano perfeito para suas necessidades",

    "tabs": {
      "credits": "Créditos (Flex)",
      "subscriptions": "Assinaturas (Flow)"
    },

    "flow_starter": {
      "name": "Flow Starter",
      "description": "Assinatura mensal para quem busca oportunidades regularmente",
      "price": "R$ 24,90",
      "period": "por mês",
      "analyses": "{count} otimizações por mês",
      "rollover": "Rollover de até {limit} análises",
      "cta": "Começar Agora"
    },

    "flow_pro": {
      "name": "Flow Pro",
      "description": "Plano profissional para quem busca muitas oportunidades",
      "price": "R$ 49,90",
      "period": "por mês",
      "analyses": "{count} otimizações por mês",
      "rollover": "Rollover de até {limit} análises",
      "cta": "Assinar Agora",
      "popular": "Mais Popular"
    },

    "features": {
      "ai_analysis": "Análise avançada com IA",
      "templates": "Modelos de currículo profissionais",
      "priority_support": "Suporte prioritário",
      "cancel_anytime": "Cancele quando quiser",
      "rollover": "Rollover de análises não usadas"
    },

    "cancel": {
      "title": "Cancelar Assinatura",
      "description": "Tem certeza que deseja cancelar?",
      "confirm": "Sim, cancelar",
      "keep": "Manter assinatura"
    },

    "manage": {
      "title": "Gerenciar Assinatura",
      "current_plan": "Plano atual",
      "next_billing": "Próxima cobrança",
      "usage": "Uso este mês",
      "upgrade": "Fazer upgrade",
      "downgrade": "Fazer downgrade",
      "cancel": "Cancelar"
    }
  }
}
```

**Also create**: `frontend/locales/en/subscriptions.json`

```json
{
  "subscriptions": {
    "title": "Choose your plan",
    "subtitle": "Find the perfect plan for your needs",

    "flow_pro": {
      "name": "Flow Pro",
      "description": "Professional plan for serious job seekers",
      "price": "$9.99",
      "period": "per month",
      "analyses": "{count} optimizations per month",
      "popular": "Most Popular"
    }
  }
}
```

---

### 2. Using Translations in Components

#### Basic Usage:

```tsx
"use client";

import { useTranslations } from "next-intl";

export function SubscriptionCard() {
  const t = useTranslations("subscriptions");

  return (
    <Card>
      <CardTitle>{t("flow_pro.name")}</CardTitle>
      <CardDescription>{t("flow_pro.description")}</CardDescription>
      <Button>{t("flow_pro.cta")}</Button>
    </Card>
  );
}
```

#### With Variables:

```tsx
const t = useTranslations('subscriptions');

// For "60 otimizações por mês"
<p>{t('flow_pro.analyses', { count: 60 })}</p>

// For "Rollover de até 30 análises"
<p>{t('flow_pro.rollover', { limit: 30 })}</p>
```

#### With Pluralization:

```json
{
  "remaining": {
    "zero": "Nenhuma análise restante",
    "one": "{count} análise restante",
    "other": "{count} análises restantes"
  }
}
```

```tsx
<p>{t("remaining", { count: analyses })}</p>
```

---

### 3. Currency Formatting

**Use next-intl's number formatting**:

```tsx
import { useFormatter } from "next-intl";

const format = useFormatter();

// Format currency
const price = format.number(49.9, {
  style: "currency",
  currency: "BRL",
});
// Output: R$ 49,90

// In component:
<p>{price}</p>;
```

**OR define in translations**:

```json
{
  "price_formatted": "R$ {amount}"
}
```

```tsx
<p>{t("price_formatted", { amount: "49,90" })}</p>
```

---

### 4. Date Formatting

```tsx
import { useFormatter } from "next-intl";

const format = useFormatter();

// Format date
const nextBilling = format.dateTime(new Date("2025-11-10"), {
  year: "numeric",
  month: "long",
  day: "numeric",
});
// Output: 10 de novembro de 2025

<p>
  {t("next_billing")}: {nextBilling}
</p>;
```

---

### 5. Feature Lists

**Translation file**:

```json
{
  "features": {
    "list": [
      "Análise avançada com IA",
      "Modelos de currículo profissionais",
      "Suporte prioritário",
      "Cancele quando quiser"
    ]
  }
}
```

**Component**:

```tsx
const t = useTranslations("subscriptions.features");

<ul>
  {t.raw("list").map((feature: string, index: number) => (
    <li key={index}>
      <Check className="w-4 h-4" />
      {feature}
    </li>
  ))}
</ul>;
```

---

### 6. Dynamic Content from API

**Problem**: API returns tier data with names/descriptions

**Solution**: Keep translations in frontend, use tier IDs as keys

```tsx
// API returns:
const tier = {
  id: 'flow_pro',
  price: 4990,
  analyses_per_month: 60
};

// Use ID to get translation:
const t = useTranslations('subscriptions');

<h3>{t(`${tier.id}.name`)}</h3>
<p>{t(`${tier.id}.description`)}</p>
<p>{t(`${tier.id}.analyses`, { count: tier.analyses_per_month })}</p>
```

---

### 7. Server Components

**For Server Components**, use different import:

```tsx
import { getTranslations } from "next-intl/server";

export default async function PricingPage() {
  const t = await getTranslations("subscriptions");

  return (
    <div>
      <h1>{t("title")}</h1>
      <p>{t("subtitle")}</p>
    </div>
  );
}
```

---

## 🎯 Complete Translation Structure for P1.5

### File: `frontend/locales/pt-br/subscriptions.json`

```json
{
  "title": "Escolha seu plano",
  "subtitle": "Preços simples e transparentes para todos",

  "tabs": {
    "credits": "Créditos",
    "subscriptions": "Assinaturas",
    "description_credits": "Pague por uso - créditos nunca expiram",
    "description_subscriptions": "Mensalidade com rollover de análises"
  },

  "free": {
    "name": "Gratuito",
    "description": "Para experimentar nossa plataforma",
    "cta": "Começar Grátis",
    "features": [
      "3 otimizações gratuitas",
      "Análise básica de ATS",
      "Exportação em texto"
    ]
  },

  "flex_10": {
    "name": "Flex 10",
    "description": "Pacote de 10 créditos",
    "price": "R$ 29,90",
    "credits": "10 créditos",
    "cta": "Comprar Agora",
    "features": [
      "10 otimizações de currículo",
      "Créditos nunca expiram",
      "Use quando quiser",
      "Análise avançada com IA",
      "Exportação PDF e DOCX"
    ]
  },

  "flex_25": {
    "name": "Flex 25",
    "description": "Pacote popular com melhor valor",
    "price": "R$ 59,90",
    "credits": "25 créditos",
    "popular": "Mais Popular",
    "cta": "Comprar Agora",
    "features": [
      "25 otimizações de currículo",
      "Créditos nunca expiram",
      "Melhor custo-benefício",
      "Análise avançada com IA",
      "Modelos profissionais",
      "Suporte prioritário"
    ]
  },

  "flex_50": {
    "name": "Flex 50",
    "description": "Para uso intensivo",
    "price": "R$ 99,90",
    "credits": "50 créditos",
    "cta": "Comprar Agora",
    "features": [
      "50 otimizações de currículo",
      "Créditos nunca expiram",
      "Análise avançada com IA",
      "Modelos profissionais",
      "Suporte prioritário",
      "Análise detalhada"
    ]
  },

  "flex_100": {
    "name": "Flex 100",
    "description": "Pacote empresarial",
    "price": "R$ 169,90",
    "credits": "100 créditos",
    "cta": "Comprar Agora",
    "features": [
      "100 otimizações de currículo",
      "Créditos nunca expiram",
      "API de integração",
      "Relatórios detalhados",
      "Suporte dedicado"
    ]
  },

  "flow_starter": {
    "name": "Flow Starter",
    "description": "Para buscas regulares",
    "price": "R$ 24,90",
    "period": "por mês",
    "analyses": "{count} otimizações/mês",
    "rollover": "Rollover de {limit} análises",
    "cta": "Assinar Agora",
    "features": [
      "15 otimizações por mês",
      "Rollover de 5 análises",
      "Análise avançada com IA",
      "Suporte por email",
      "Cancele quando quiser"
    ]
  },

  "flow_pro": {
    "name": "Flow Pro",
    "description": "Para profissionais ativos",
    "price": "R$ 49,90",
    "period": "por mês",
    "analyses": "{count} otimizações/mês",
    "rollover": "Rollover de {limit} análises",
    "popular": "Mais Popular",
    "cta": "Assinar Agora",
    "features": [
      "60 otimizações por mês",
      "Rollover de 30 análises",
      "Análise avançada com IA",
      "Modelos profissionais",
      "Suporte prioritário",
      "Análise de mercado",
      "Cancele quando quiser"
    ]
  },

  "flow_business": {
    "name": "Flow Business",
    "description": "Para recrutadores",
    "price": "R$ 129,90",
    "period": "por mês",
    "analyses": "{count} otimizações/mês",
    "rollover": "Rollover de {limit} análises",
    "cta": "Assinar Agora",
    "features": [
      "250 otimizações por mês",
      "Rollover de 100 análises",
      "5 usuários incluídos",
      "API de integração",
      "Dashboard avançado",
      "Suporte dedicado",
      "Cancele quando quiser"
    ]
  },

  "flow_enterprise": {
    "name": "Flow Enterprise",
    "description": "Solução personalizada",
    "price": "Sob consulta",
    "cta": "Falar com Vendas",
    "features": [
      "Otimizações ilimitadas",
      "Usuários ilimitados",
      "Integrações personalizadas",
      "White-label disponível",
      "SLA 99,9%",
      "CSM dedicado",
      "Suporte 24/7"
    ]
  },

  "comparison": {
    "title": "Compare os planos",
    "feature": "Recurso",
    "free": "Gratuito",
    "starter": "Starter",
    "pro": "Pro",
    "business": "Business"
  },

  "features_detailed": {
    "ai_analysis": "Análise avançada com IA",
    "ats_score": "Pontuação ATS",
    "templates": "Modelos profissionais",
    "priority_support": "Suporte prioritário",
    "api_access": "Acesso à API",
    "team_collaboration": "Colaboração em equipe",
    "analytics": "Dashboard de analytics",
    "white_label": "White-label",
    "sla": "SLA garantido",
    "csm": "Customer Success Manager"
  },

  "billing": {
    "monthly": "Mensal",
    "yearly": "Anual",
    "save": "Economize {percent}%",
    "billed_monthly": "Cobrado mensalmente",
    "billed_yearly": "Cobrado anualmente"
  },

  "actions": {
    "subscribe": "Assinar",
    "buy_credits": "Comprar Créditos",
    "upgrade": "Fazer Upgrade",
    "downgrade": "Fazer Downgrade",
    "cancel": "Cancelar",
    "manage": "Gerenciar",
    "contact_sales": "Falar com Vendas"
  },

  "status": {
    "active": "Ativa",
    "canceled": "Cancelada",
    "past_due": "Pagamento atrasado",
    "trialing": "Período de teste"
  },

  "manage_subscription": {
    "title": "Gerenciar Assinatura",
    "current_plan": "Plano atual",
    "next_billing_date": "Próxima cobrança",
    "payment_method": "Método de pagamento",
    "usage_this_month": "Uso este mês",
    "analyses_used": "{used} de {total} otimizações usadas",
    "rollover_available": "{count} análises acumuladas",
    "change_plan": "Trocar plano",
    "update_payment": "Atualizar pagamento",
    "cancel_subscription": "Cancelar assinatura"
  },

  "cancel_dialog": {
    "title": "Cancelar assinatura",
    "description": "Tem certeza que deseja cancelar sua assinatura?",
    "consequences": "Ao cancelar:",
    "lose_access": "Você perderá acesso aos recursos premium",
    "keep_until": "Sua assinatura permanecerá ativa até {date}",
    "can_resubscribe": "Você pode reativar a qualquer momento",
    "confirm": "Sim, cancelar",
    "keep": "Manter assinatura",
    "feedback": "Por que você está cancelando?",
    "feedback_placeholder": "Seu feedback nos ajuda a melhorar..."
  },

  "upgrade_dialog": {
    "title": "Fazer upgrade",
    "from": "De {current}",
    "to": "Para {new}",
    "benefits": "Você ganhará:",
    "confirm": "Confirmar upgrade",
    "cancel": "Voltar"
  },

  "success": {
    "subscribed": "Assinatura ativada com sucesso!",
    "upgraded": "Upgrade realizado com sucesso!",
    "downgraded": "Plano alterado com sucesso!",
    "canceled": "Assinatura cancelada"
  },

  "errors": {
    "payment_failed": "Falha no pagamento",
    "subscription_not_found": "Assinatura não encontrada",
    "already_subscribed": "Você já possui uma assinatura ativa",
    "try_again": "Tente novamente"
  }
}
```

---

## 🎯 Implementation Checklist

### Before Writing ANY Component:

- [ ] Create translation file in `locales/pt-br/`
- [ ] Create English version in `locales/en/`
- [ ] Import `useTranslations` at top of component
- [ ] Use `t('key')` for ALL text
- [ ] Use `format.number()` for currency
- [ ] Use `format.dateTime()` for dates
- [ ] Test with both locales (pt-br and en)

---

## 🚨 Common Mistakes to AVOID

### ❌ Mistake 1: Hardcoded Text

```tsx
<Button>Assinar Agora</Button> // WRONG!
```

### ✅ Solution:

```tsx
<Button>{t("flow_pro.cta")}</Button> // CORRECT!
```

---

### ❌ Mistake 2: Hardcoded Currency

```tsx
<p>R$ {price}</p> // WRONG!
```

### ✅ Solution:

```tsx
const format = useFormatter();
<p>{format.number(price, { style: "currency", currency: "BRL" })}</p>;
```

---

### ❌ Mistake 3: Inline Pluralization

```tsx
<p>{count === 1 ? "análise" : "análises"}</p> // WRONG!
```

### ✅ Solution:

```json
{
  "analyses": {
    "one": "{count} análise",
    "other": "{count} análises"
  }
}
```

```tsx
<p>{t("analyses", { count })}</p>
```

---

## 🎓 Testing Localization

```bash
# Start dev server
cd frontend
bun run dev

# Test Portuguese
http://localhost:3000/pt-br/pricing

# Test English
http://localhost:3000/en/pricing

# Check for hardcoded strings:
grep -r "Assinar\|Cancelar\|R\$" app/ components/ --include="*.tsx" --exclude="locales/*"
# Should return NO results!
```

---

## ✅ Success Criteria

Agent successfully implements i18n when:

- [ ] NO hardcoded Portuguese/English in components
- [ ] ALL text uses `useTranslations()`
- [ ] Currency uses `useFormatter()`
- [ ] Dates use `useFormatter()`
- [ ] Translation files in both pt-br and en
- [ ] Component works in both languages
- [ ] Grep test returns no hardcoded strings

---

**Remember**: If it's visible to the user, it MUST be in a translation file! 🌍
