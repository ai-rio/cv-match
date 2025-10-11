# 🎯 P1.5 Phase 4.1: Frontend Subscription UI

**Agent**: frontend-specialist  
**Phase**: 4 (Parallel execution with Prompt 06)  
**Time Estimate**: 3 hours  
**Dependencies**: Phase 3 must be complete

**Why frontend-specialist?** This task involves Next.js components, React hooks, TypeScript, next-intl localization, and Shadcn UI - core frontend development.

**⚠️ CRITICAL**: 
- DO NOT start until Phase 3 (API Endpoints) is complete!
- ✅ CAN RUN IN PARALLEL with Prompt 06 (Testing)

---

## 📋 Mission

Create the frontend UI for subscription management including pricing page, subscription dashboard, and Stripe Checkout integration.

---

## 🛠️ CRITICAL: Required Tools

### 1. Shadcn Components
```bash
cd frontend
npx shadcn-ui@latest add card badge tabs dialog button alert
```

### 2. Check Shadcn Blocks
Visit: https://ui.shadcn.com/blocks (Use "Pricing" blocks as reference)

---

## 📝 Implementation Tasks

### Task 1: Translations (20 min)

**Create**: `/frontend/locales/pt-br/subscriptions.json`

```json
{
  "title": "Escolha seu plano",
  "subtitle": "Preços simples e transparentes",
  "tabs": {"credits": "Créditos (Flex)", "subscriptions": "Assinaturas (Flow)"},
  "flow_pro": {
    "name": "Flow Pro",
    "price": "R$ 49,90",
    "period": "por mês",
    "analyses": "{count} otimizações/mês",
    "popular": "Mais Popular",
    "cta": "Assinar Agora"
  },
  "manage": {
    "title": "Gerenciar Assinatura",
    "current_plan": "Plano atual",
    "cancel": "Cancelar assinatura"
  }
}
```

---

### Task 2: Pricing Page (60 min)

**Create**: `/frontend/components/pricing/PricingTabs.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SubscriptionCards } from './SubscriptionCards';
import { CreditCards } from './CreditCards';

export function PricingTabs() {
  const t = useTranslations('subscriptions');
  
  return (
    <Tabs defaultValue="subscriptions" className="w-full">
      <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
        <TabsTrigger value="credits">{t('tabs.credits')}</TabsTrigger>
        <TabsTrigger value="subscriptions">{t('tabs.subscriptions')}</TabsTrigger>
      </TabsList>
      
      <TabsContent value="credits" className="mt-8">
        <CreditCards />
      </TabsContent>
      
      <TabsContent value="subscriptions" className="mt-8">
        <SubscriptionCards />
      </TabsContent>
    </Tabs>
  );
}
```

---

### Task 3: Subscription Cards (60 min)

**Create**: `/frontend/components/pricing/SubscriptionCards.tsx`

```typescript
'use client';

import { useTranslations } from 'next-intl';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check } from 'lucide-react';
import { useState } from 'react';

const SUBSCRIPTION_TIERS = ['flow_starter', 'flow_pro', 'flow_business'];

export function SubscriptionCards() {
  const t = useTranslations('subscriptions');
  const [loading, setLoading] = useState<string | null>(null);
  
  const handleSubscribe = async (tierId: string) => {
    setLoading(tierId);
    
    try {
      const response = await fetch('/api/subscriptions/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier_id: tierId })
      });
      
      const data = await response.json();
      
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error) {
      console.error('Checkout failed:', error);
    } finally {
      setLoading(null);
    }
  };
  
  return (
    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
      {SUBSCRIPTION_TIERS.map((tierId) => {
        const isPopular = t(`${tierId}.popular`) !== `${tierId}.popular`;
        
        return (
          <Card key={tierId} className={isPopular ? 'border-primary shadow-lg' : ''}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle>{t(`${tierId}.name`)}</CardTitle>
                {isPopular && (
                  <Badge variant="secondary">{t(`${tierId}.popular`)}</Badge>
                )}
              </div>
              <CardDescription>{t(`${tierId}.description`)}</CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="mb-6">
                <span className="text-4xl font-bold">{t(`${tierId}.price`)}</span>
                <span className="text-muted-foreground">/{t(`${tierId}.period`)}</span>
              </div>
              
              <ul className="space-y-3">
                {t.raw(`${tierId}.features`).map((feature: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            
            <CardFooter>
              <Button
                className="w-full"
                size="lg"
                onClick={() => handleSubscribe(tierId)}
                disabled={loading === tierId}
              >
                {loading === tierId ? 'Processando...' : t(`${tierId}.cta`)}
              </Button>
            </CardFooter>
          </Card>
        );
      })}
    </div>
  );
}
```

---

### Task 4: Subscription Dashboard (60 min)

**Create**: `/frontend/components/account/SubscriptionDashboard.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { CancelSubscriptionDialog } from './CancelSubscriptionDialog';

interface SubscriptionData {
  tier_id: string;
  tier_name: string;
  analyses_used_this_period: number;
  analyses_per_month: number;
  analyses_rollover: number;
  current_period_end: string;
  status: string;
}

export function SubscriptionDashboard() {
  const t = useTranslations('subscriptions.manage');
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  
  useEffect(() => {
    fetchSubscription();
  }, []);
  
  const fetchSubscription = async () => {
    try {
      const response = await fetch('/api/subscriptions/current');
      const data = await response.json();
      setSubscription(data);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    }
  };
  
  if (!subscription) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-muted-foreground">Você não possui uma assinatura ativa.</p>
        </CardContent>
      </Card>
    );
  }
  
  const usagePercentage = (subscription.analyses_used_this_period / subscription.analyses_per_month) * 100;
  
  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <CardTitle>{t('title')}</CardTitle>
            <Badge variant={subscription.status === 'active' ? 'default' : 'secondary'}>
              {subscription.status}
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">{t('current_plan')}</p>
            <p className="text-2xl font-bold">{subscription.tier_name}</p>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground mb-2">{t('usage')}</p>
            <div className="space-y-2">
              <Progress value={usagePercentage} className="h-2" />
              <p className="text-sm">
                {t('analyses_used', {
                  used: subscription.analyses_used_this_period,
                  total: subscription.analyses_per_month
                })}
              </p>
              {subscription.analyses_rollover > 0 && (
                <p className="text-sm text-muted-foreground">
                  {t('rollover', { count: subscription.analyses_rollover })}
                </p>
              )}
            </div>
          </div>
          
          <div>
            <p className="text-sm text-muted-foreground mb-1">{t('next_billing')}</p>
            <p className="font-medium">
              {new Date(subscription.current_period_end).toLocaleDateString('pt-BR')}
            </p>
          </div>
          
          <div className="flex gap-3">
            <Button variant="outline" className="flex-1">
              {t('upgrade')}
            </Button>
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={() => setShowCancelDialog(true)}
            >
              {t('cancel')}
            </Button>
          </div>
        </CardContent>
      </Card>
      
      <CancelSubscriptionDialog
        open={showCancelDialog}
        onOpenChange={setShowCancelDialog}
        subscription={subscription}
        onCancel={fetchSubscription}
      />
    </>
  );
}
```

---

### Task 5: Cancel Dialog (20 min)

**Create**: `/frontend/components/account/CancelSubscriptionDialog.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  subscription: any;
  onCancel: () => void;
}

export function CancelSubscriptionDialog({ open, onOpenChange, subscription, onCancel }: Props) {
  const t = useTranslations('subscriptions.cancel_dialog');
  const [loading, setLoading] = useState(false);
  
  const handleCancel = async () => {
    setLoading(true);
    
    try {
      await fetch(`/api/subscriptions/${subscription.id}/cancel`, {
        method: 'POST'
      });
      
      onCancel();
      onOpenChange(false);
    } catch (error) {
      console.error('Cancel failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('title')}</AlertDialogTitle>
          <AlertDialogDescription>{t('description')}</AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="space-y-2 my-4">
          <p className="text-sm font-medium">{t('consequences')}</p>
          <ul className="text-sm text-muted-foreground space-y-1 ml-4">
            <li>• {t('lose_access')}</li>
            <li>• {t('keep_until', { date: new Date(subscription.current_period_end).toLocaleDateString('pt-BR') })}</li>
          </ul>
        </div>
        
        <AlertDialogFooter>
          <AlertDialogCancel>{t('keep')}</AlertDialogCancel>
          <AlertDialogAction onClick={handleCancel} disabled={loading}>
            {loading ? 'Cancelando...' : t('confirm')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

---

## ✅ Verification Checklist

### 1. Components Render
```bash
cd frontend
bun run dev

# Open browser
open http://localhost:3000/pt-br/pricing
```

**Check:**
- [ ] Tabs switch between Flex/Flow
- [ ] Subscription cards display correctly
- [ ] "Popular" badge shows on Flow Pro
- [ ] All text in Portuguese

### 2. Checkout Flow
- [ ] Click "Assinar Agora"
- [ ] Redirects to Stripe Checkout
- [ ] Can complete test payment

### 3. Dashboard
```bash
# Navigate to account page
open http://localhost:3000/pt-br/account
```

**Check:**
- [ ] Subscription status displays
- [ ] Usage progress bar works
- [ ] Cancel button opens dialog

### 4. Responsive Design
- [ ] Test on mobile (DevTools)
- [ ] Cards stack vertically
- [ ] Buttons are touch-friendly

### 5. No Hardcoded Text
```bash
# Search for hardcoded Portuguese
grep -r "Assinar\|Cancelar" components/pricing --include="*.tsx"

# Should return NO results (all text via useTranslations)
```

---

## 🚨 Common Issues

### Issue 1: Shadcn Components Not Found
**Error**: `Module not found: @/components/ui/card`

**Solution**:
```bash
npx shadcn-ui@latest add card badge tabs dialog button
```

### Issue 2: Translation Keys Not Found
**Error**: `subscriptions.flow_pro.name not found`

**Solution**:
- Verify `/frontend/locales/pt-br/subscriptions.json` exists
- Check JSON structure matches `t('flow_pro.name')` calls

### Issue 3: API Calls Fail
**Error**: `Failed to fetch`

**Solution**:
```typescript
// Add error handling
try {
  const response = await fetch('/api/subscriptions/status');
  if (!response.ok) throw new Error('API failed');
  const data = await response.json();
} catch (error) {
  console.error(error);
}
```

---

## 📊 Success Criteria

Phase 4.1 is complete when:
- ✅ Pricing page with tabs works
- ✅ All subscription tiers display
- ✅ Checkout redirects to Stripe
- ✅ Dashboard shows subscription
- ✅ Cancel dialog functions
- ✅ All text via next-intl
- ✅ Responsive design
- ✅ No hardcoded strings
- ✅ Code committed

---

## 🎯 Next Step

**Can run in parallel**: Prompt 06 (Testing) can execute simultaneously!

After BOTH Phase 4.1 AND 4.2 complete:
→ **P1.5 is complete!** 🎉
→ Review, test end-to-end, deploy

---

**Time check**: ~3 hours. If longer, ask for help!

Good luck! 🚀
