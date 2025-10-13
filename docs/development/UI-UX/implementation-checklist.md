# ✅ CV-Match UI/UX Implementation Checklist

**Start Date:** October 12, 2025  
**Target Completion:** 4 weeks  
**Owner:** Development Team

---

## 🎯 Phase 1: Foundation & Auth Protection (Week 1)

### Task 1.1: Protect /optimize Route ⏰ 2 hours

**Priority:** 🔴 CRITICAL  
**Impact:** High - Fixes core user flow issue  
**Effort:** Low

**Implementation:**

```typescript
// File: frontend/middleware.ts

import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import createIntlMiddleware from 'next-intl/middleware';

// Create i18n middleware
const intlMiddleware = createIntlMiddleware({
  locales: ['pt-br', 'en'],
  defaultLocale: 'pt-br',
  localePrefix: 'always',
});

export async function middleware(req: NextRequest) {
  // 1. Handle i18n first
  const response = intlMiddleware(req);
  
  // 2. Define protected routes
  const protectedPaths = [
    '/optimize',
    '/dashboard', 
    '/history',
    '/settings',
    '/results'
  ];
  
  const path = req.nextUrl.pathname;
  const locale = path.split('/')[1]; // pt-br or en
  
  // Check if current path is protected
  const isProtected = protectedPaths.some(p => 
    path.includes(`/${locale}${p}`)
  );
  
  if (isProtected) {
    // 3. Check authentication
    const res = NextResponse.next();
    const supabase = createMiddlewareClient({ req, res });
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      // 4. Redirect to signup with return URL
      const signupUrl = new URL(`/${locale}/auth/signup`, req.url);
      signupUrl.searchParams.set('redirect', path);
      signupUrl.searchParams.set('message', 'signup_required');
      
      return NextResponse.redirect(signupUrl);
    }
  }
  
  return response;
}

export const config = {
  matcher: [
    '/',
    '/(pt-br|en)/:path*',
    '/((?!_next|_vercel|.*\\..*).*)',
  ],
};
```

**Checklist:**
- [ ] Update `middleware.ts` with auth checks
- [ ] Test protected routes redirect to signup
- [ ] Test authenticated users can access protected routes
- [ ] Test return URL works after signup/login
- [ ] Update any hardcoded `/optimize` links to use locale-aware routing

---

### Task 1.2: Remove Client-Side Auth from /optimize ⏰ 1 hour

**Priority:** 🟡 High  
**Impact:** Medium - Cleans up code  
**Effort:** Low

**Changes to make:**

```typescript
// File: frontend/app/[locale]/optimize/page.tsx

// ❌ REMOVE these lines (now handled by middleware):

const handleJobDescriptionSubmit = useCallback(
  async (data: JobDescriptionData) => {
    // ... existing code ...
    
    // DELETE THIS SECTION (lines ~255-276):
    /*
    try {
      const supabase = createClient();
      const { data: { user }, error: authError } = await supabase.auth.getUser();

      if (authError || !user) {
        setError(translations.errors.notAuthenticated);
        router.push('/auth/login');
        return;
      }
      
      // ... credit check code ...
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to check usage limits');
    }
    */
    
    // ✅ REPLACE with simple version:
    setJobDescription(data);
    setError(null);
    
    // Check credits
    const hasCredits = await checkUserCredits();
    if (hasCredits) {
      setCurrentStep('processing');
      await startOptimization();
    } else {
      setCurrentStep('payment');
    }
  },
  [router, startOptimization]
);
```

**Checklist:**
- [ ] Remove auth check from `handleJobDescriptionSubmit`
- [ ] Remove auth check from `handleResumeUploaded`
- [ ] Simplify error handling (no auth errors needed)
- [ ] Test workflow still works
- [ ] Verify middleware is catching unauthenticated users

---

### Task 1.3: Update Landing Page CTAs ⏰ 1 hour

**Priority:** 🟡 High  
**Impact:** High - Improves conversion  
**Effort:** Low

**Changes:**

```typescript
// File: frontend/app/[locale]/page.tsx

// Update hero section:
<div className="text-center">
  <h1 className="text-5xl font-bold">
    Otimize seu Currículo com IA
  </h1>
  <p className="text-xl mt-4">
    3 otimizações grátis • Sem cartão de crédito • Resultados em minutos
  </p>
  
  {/* Update CTA */}
  <div className="mt-8 flex gap-4 justify-center">
    <Button size="lg" asChild>
      <Link href="/auth/signup?plan=free">
        Começar Grátis (3 Créditos)
      </Link>
    </Button>
    <Button size="lg" variant="outline" asChild>
      <Link href="/pricing">
        Ver Planos
      </Link>
    </Button>
  </div>
  
  {/* Add trust badges */}
  <div className="mt-6 flex gap-6 justify-center text-sm text-gray-600">
    <span>✓ Sem cartão de crédito</span>
    <span>✓ 3 otimizações grátis</span>
    <span>✓ Cancele quando quiser</span>
  </div>
</div>
```

**Checklist:**
- [ ] Update hero CTA to "Começar Grátis"
- [ ] Add "3 créditos grátis" messaging
- [ ] Add trust badges below CTA
- [ ] Update secondary CTAs throughout page
- [ ] A/B test different copy variants

---

### Task 1.4: Add Credit Counter to Dashboard ⏰ 2 hours

**Priority:** 🟡 High  
**Impact:** High - Transparency  
**Effort:** Low

**Implementation:**

```typescript
// File: frontend/app/[locale]/dashboard/page.tsx

// Add to the Credits Card section (already exists, enhance it):

<Card>
  <CardHeader>
    <CardTitle className="flex items-center justify-between">
      <span>{t('credits.title')}</span>
      <Badge variant="secondary">
        {totalCredits} créditos disponíveis
      </Badge>
    </CardTitle>
  </CardHeader>
  <CardContent>
    {/* Large credit display */}
    <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg mb-6">
      <div className="text-5xl font-bold text-blue-600 mb-2">
        {totalCredits}
      </div>
      <div className="text-sm text-gray-600">
        {totalCredits === 0 
          ? 'Nenhum crédito disponível' 
          : `crédito${totalCredits > 1 ? 's' : ''} disponível${totalCredits > 1 ? 'eis' : ''}`
        }
      </div>
    </div>

    {/* Breakdown */}
    <div className="space-y-4">
      {/* Free credits */}
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Créditos Grátis</span>
          <span className="font-medium">
            {stats.free_optimizations_limit - stats.free_optimizations_used} / {stats.free_optimizations_limit}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full transition-all"
            style={{
              width: `${((stats.free_optimizations_limit - stats.free_optimizations_used) / stats.free_optimizations_limit) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Paid credits */}
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Créditos Comprados</span>
          <span className="font-medium">{stats.purchased_optimizations}</span>
        </div>
      </div>

      {/* CTA buttons */}
      <div className="pt-4 space-y-2">
        {totalCredits > 0 ? (
          <>
            <Button className="w-full" size="lg" onClick={() => router.push('/optimize')}>
              <Sparkles className="mr-2 h-4 w-4" />
              Usar Crédito Agora
            </Button>
            <Button variant="outline" className="w-full" onClick={() => router.push('/pricing')}>
              Comprar Mais Créditos
            </Button>
          </>
        ) : (
          <>
            <Button className="w-full" size="lg" onClick={() => router.push('/pricing')}>
              Comprar Créditos
            </Button>
            <p className="text-sm text-center text-gray-600">
              Seus créditos grátis acabaram. Compre mais para continuar!
            </p>
          </>
        )}
      </div>
    </div>
  </CardContent>
</Card>
```

**Checklist:**
- [ ] Add large credit counter
- [ ] Show free vs paid credits breakdown
- [ ] Add progress bars
- [ ] Conditional CTAs based on credit count
- [ ] Test with 0 credits, 1 credit, multiple credits
- [ ] Add loading states

---

### Task 1.5: Create Upgrade Modal Component ⏰ 3 hours

**Priority:** 🟡 High  
**Impact:** High - Key conversion point  
**Effort:** Medium

**New File:**

```typescript
// File: frontend/components/upgrade/UpgradeModal.tsx

'use client';

import { useState } from 'react';
import { Check, X, Sparkles, TrendingUp } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BRAZILIAN_PRICING, formatBRLPrice } from '@/lib/pricing-config';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  trigger: 'out_of_credits' | 'last_credit' | 'feature_gate';
  onUpgrade: (tierId: string) => void;
}

export function UpgradeModal({ isOpen, onClose, trigger, onUpgrade }: UpgradeModalProps) {
  const [selectedTier, setSelectedTier] = useState('pro');

  const getMessage = () => {
    switch (trigger) {
      case 'out_of_credits':
        return {
          title: '🎉 Parabéns! Você usou todos os créditos grátis',
          description: 'Você experimentou o poder da otimização com IA. Continue otimizando e aumente suas chances de contratação!',
          badge: 'Créditos Esgotados',
        };
      case 'last_credit':
        return {
          title: '⚠️ Este é seu último crédito grátis',
          description: 'Aproveite ao máximo! Considere fazer upgrade para continuar otimizando.',
          badge: 'Último Crédito',
        };
      case 'feature_gate':
        return {
          title: '✨ Recurso Premium',
          description: 'Este recurso está disponível apenas para usuários pagos.',
          badge: 'Premium',
        };
    }
  };

  const message = getMessage();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between mb-2">
            <Badge variant="secondary">{message.badge}</Badge>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <DialogTitle className="text-2xl">{message.title}</DialogTitle>
          <DialogDescription className="text-base">
            {message.description}
          </DialogDescription>
        </DialogHeader>

        {/* Social Proof */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 my-6">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <span className="font-semibold text-blue-900">
              Junte-se a 5.000+ profissionais
            </span>
          </div>
          <p className="text-sm text-blue-800">
            Usuários pagos têm 87% mais chances de conseguir entrevistas
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-4">
          {/* Basic */}
          <div
            className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
              selectedTier === 'basic'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedTier('basic')}
          >
            <h3 className="text-lg font-bold mb-2">{BRAZILIAN_PRICING.basic.name}</h3>
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {formatBRLPrice(BRAZILIAN_PRICING.basic.price)}
            </div>
            <p className="text-sm text-gray-600 mb-4">
              {BRAZILIAN_PRICING.basic.credits} créditos
            </p>
            <ul className="space-y-2 mb-6">
              {BRAZILIAN_PRICING.basic.features.slice(0, 3).map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Check className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Pro - Most Popular */}
          <div
            className={`border-2 rounded-lg p-6 cursor-pointer transition-all relative ${
              selectedTier === 'pro'
                ? 'border-blue-600 bg-blue-50'
                : 'border-blue-600 hover:border-blue-700'
            }`}
            onClick={() => setSelectedTier('pro')}
          >
            <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              Mais Popular
            </Badge>
            <h3 className="text-lg font-bold mb-2">{BRAZILIAN_PRICING.pro.name}</h3>
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {formatBRLPrice(BRAZILIAN_PRICING.pro.price)}
            </div>
            <p className="text-sm text-gray-600 mb-4">
              {BRAZILIAN_PRICING.pro.credits} créditos
            </p>
            <ul className="space-y-2 mb-6">
              {BRAZILIAN_PRICING.pro.features.slice(0, 4).map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Check className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Enterprise */}
          <div
            className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
              selectedTier === 'enterprise'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedTier('enterprise')}
          >
            <h3 className="text-lg font-bold mb-2">{BRAZILIAN_PRICING.enterprise.name}</h3>
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {formatBRLPrice(BRAZILIAN_PRICING.enterprise.price)}
            </div>
            <p className="text-sm text-gray-600 mb-4">
              {BRAZILIAN_PRICING.enterprise.credits} créditos
            </p>
            <ul className="space-y-2 mb-6">
              {BRAZILIAN_PRICING.enterprise.features.slice(0, 3).map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Check className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Testimonial */}
        <div className="bg-gray-50 rounded-lg p-4 my-6">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
              M
            </div>
            <div>
              <div className="font-semibold">Maria Silva</div>
              <div className="text-sm text-gray-600">Desenvolvedora Senior</div>
            </div>
          </div>
          <p className="text-sm text-gray-700 italic">
            "Depois de otimizar meu currículo, consegui 3 entrevistas em uma semana. 
            O investimento valeu muito a pena!"
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onClose}
          >
            Talvez Depois
          </Button>
          <Button
            className="flex-1"
            size="lg"
            onClick={() => onUpgrade(selectedTier)}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            Fazer Upgrade Agora
          </Button>
        </div>

        {/* Trust Footer */}
        <div className="text-center text-sm text-gray-600 mt-4">
          🔒 Pagamento seguro • 💳 Aceita PIX e Cartão • ↩️ Garantia de 7 dias
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

**Usage Example:**

```typescript
// In /optimize page or dashboard:
import { UpgradeModal } from '@/components/upgrade/UpgradeModal';

const [showUpgradeModal, setShowUpgradeModal] = useState(false);
const [upgradeTrigger, setUpgradeTrigger] = useState<'out_of_credits' | 'last_credit'>('out_of_credits');

// When user runs out of credits:
if (credits === 0) {
  setUpgradeTrigger('out_of_credits');
  setShowUpgradeModal(true);
}

// Before last credit:
if (credits === 1) {
  setUpgradeTrigger('last_credit');
  setShowUpgradeModal(true);
}

return (
  <>
    {/* Your page content */}
    
    <UpgradeModal
      isOpen={showUpgradeModal}
      onClose={() => setShowUpgradeModal(false)}
      trigger={upgradeTrigger}
      onUpgrade={(tierId) => {
        // Handle upgrade
        router.push(`/pricing?tier=${tierId}`);
      }}
    />
  </>
);
```

**Checklist:**
- [ ] Create UpgradeModal component
- [ ] Add to `/optimize` page
- [ ] Add to `/dashboard`
- [ ] Test with different triggers
- [ ] Add analytics tracking
- [ ] A/B test different copy
- [ ] Test on mobile

---

## 🎁 Phase 2: Onboarding & First-Time UX (Week 2-3)

### Task 2.1: Create Onboarding Flow ⏰ 8 hours

**Priority:** 🟢 Medium  
**Impact:** High - Better activation  
**Effort:** High

**New Files to Create:**

```
frontend/app/[locale]/onboarding/
  ├── page.tsx (main onboarding container)
  ├── steps/
  │   ├── WelcomeStep.tsx
  │   ├── QuickTutorialStep.tsx
  │   └── FirstOptimizationPrompt.tsx
  └── components/
      └── OnboardingProgress.tsx
```

**Implementation Outline:**

```typescript
// File: frontend/app/[locale]/onboarding/page.tsx

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { WelcomeStep } from './steps/WelcomeStep';
import { QuickTutorialStep } from './steps/QuickTutorialStep';
import { FirstOptimizationPrompt } from './steps/FirstOptimizationPrompt';

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  
  const steps = [
    <WelcomeStep key="welcome" onNext={() => setCurrentStep(1)} onSkip={handleSkip} />,
    <QuickTutorialStep key="tutorial" onNext={() => setCurrentStep(2)} onSkip={handleSkip} />,
    <FirstOptimizationPrompt key="prompt" onComplete={handleComplete} />,
  ];

  async function handleComplete() {
    // Mark onboarding as complete
    await markOnboardingComplete();
    router.push('/dashboard');
  }

  function handleSkip() {
    router.push('/dashboard');
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex gap-2 justify-center">
            {steps.map((_, i) => (
              <div
                key={i}
                className={`h-2 rounded-full transition-all ${
                  i === currentStep
                    ? 'w-12 bg-blue-600'
                    : i < currentStep
                    ? 'w-8 bg-blue-400'
                    : 'w-8 bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Current step */}
        {steps[currentStep]}
      </div>
    </div>
  );
}
```

**Checklist:**
- [ ] Create onboarding page structure
- [ ] Implement 3 steps (Welcome, Tutorial, Prompt)
- [ ] Add skip button (accessible)
- [ ] Add progress indicator
- [ ] Store `onboarding_completed` in user metadata
- [ ] Redirect to onboarding after signup if not completed
- [ ] Test on desktop and mobile
- [ ] Add animations (optional)

---

### Task 2.2: First-Time User Tooltips ⏰ 4 hours

**Priority:** 🟢 Medium  
**Impact:** Medium - Helps activation  
**Effort:** Medium

Use a library like **react-joyride** or **driver.js** for product tours.

**Example:**

```bash
bun install react-joyride
```

```typescript
// File: frontend/components/dashboard/DashboardTour.tsx

'use client';

import { useState, useEffect } from 'react';
import Joyride, { Step } from 'react-joyride';

const steps: Step[] = [
  {
    target: '[data-tour="credits"]',
    content: 'Aqui você pode ver quantos créditos você tem disponíveis. Você começa com 3 créditos grátis!',
    disableBeacon: true,
  },
  {
    target: '[data-tour="new-optimization"]',
    content: 'Clique aqui para começar sua primeira otimização de currículo com IA!',
  },
  {
    target: '[data-tour="history"]',
    content: 'Suas otimizações anteriores aparecerão aqui para você baixar novamente.',
  },
];

export function DashboardTour() {
  const [run, setRun] = useState(false);

  useEffect(() => {
    // Check if user is first-time visitor
    const hasSeenTour = localStorage.getItem('dashboard_tour_completed');
    if (!hasSeenTour) {
      setRun(true);
    }
  }, []);

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      styles={{
        options: {
          primaryColor: '#2563eb',
          zIndex: 10000,
        },
      }}
      callback={(data) => {
        if (data.status === 'finished' || data.status === 'skipped') {
          localStorage.setItem('dashboard_tour_completed', 'true');
        }
      }}
    />
  );
}
```

**Usage in Dashboard:**

```typescript
// Add data-tour attributes to elements
<Card data-tour="credits">
  {/* Credits card content */}
</Card>

<Button data-tour="new-optimization">
  Start New Optimization
</Button>

// Import and use tour
import { DashboardTour } from '@/components/dashboard/DashboardTour';

export default function Dashboard() {
  return (
    <>
      <DashboardTour />
      {/* Rest of dashboard */}
    </>
  );
}
```

**Checklist:**
- [ ] Install tour library
- [ ] Add data-tour attributes to key elements
- [ ] Create tour steps
- [ ] Store completion in localStorage
- [ ] Test on different screen sizes
- [ ] Make dismissible/skippable

---

### Task 2.3: Email Campaign Setup ⏰ 6 hours

**Priority:** 🟢 Medium  
**Impact:** High - Drives engagement  
**Effort:** Medium

**Tool:** Use Resend, SendGrid, or Mailgun

**Email Sequence:**

1. **Day 0 (Signup):** Welcome Email
2. **Day 1:** "Get Started" with tutorial link
3. **Day 3:** "2 credits left" reminder
4. **Day 7:** Success stories + upgrade offer
5. **Day 14:** "Are you still looking?" re-engagement

**Example using Resend:**

```typescript
// File: backend/app/services/email_service.py

from resend import Resend
import os

resend = Resend(os.getenv("RESEND_API_KEY"))

class EmailService:
    @staticmethod
    async def send_welcome_email(user_email: str, user_name: str):
        """Send welcome email to new user"""
        await resend.emails.send({
            "from": "CV-Match <noreply@cv-match.com>",
            "to": user_email,
            "subject": "Bem-vindo ao CV-Match! 🎉",
            "html": f"""
                <h1>Olá {user_name}!</h1>
                <p>Bem-vindo ao CV-Match. Você ganhou <strong>3 créditos grátis</strong> para otimizar seus currículos com IA.</p>
                <a href="https://cv-match.com/dashboard">Começar Agora</a>
            """
        })
    
    @staticmethod
    async def send_credit_reminder(user_email: str, credits_left: int):
        """Send reminder about remaining credits"""
        # Implementation...
    
    @staticmethod
    async def send_upgrade_offer(user_email: str):
        """Send upgrade offer after free credits exhausted"""
        # Implementation...
```

**Checklist:**
- [ ] Choose email service provider
- [ ] Set up API keys
- [ ] Create email templates
- [ ] Implement sending logic
- [ ] Set up automated triggers
- [ ] Add unsubscribe mechanism
- [ ] Test emails in different clients
- [ ] Track open rates and click-through rates

---

## 📊 Phase 3: Analytics & Tracking (Week 3)

### Task 3.1: Install Analytics ⏰ 3 hours

**Priority:** 🔴 CRITICAL  
**Impact:** High - Data-driven decisions  
**Effort:** Low

**Recommended:** PostHog (open-source, self-hostable)

```bash
bun install posthog-js
```

```typescript
// File: frontend/lib/analytics.ts

import posthog from 'posthog-js';

export const initAnalytics = () => {
  if (typeof window !== 'undefined') {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com',
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') posthog.debug();
      }
    });
  }
};

// Track events
export const analytics = {
  track: (event: string, properties?: Record<string, any>) => {
    posthog.capture(event, properties);
  },
  
  identify: (userId: string, traits?: Record<string, any>) => {
    posthog.identify(userId, traits);
  },
  
  page: () => {
    posthog.capture('$pageview');
  }
};
```

**Events to Track:**

```typescript
// User lifecycle
analytics.track('User Signed Up', { method: 'google', plan: 'free' });
analytics.track('Onboarding Started');
analytics.track('Onboarding Completed', { time_taken: 120 });

// Optimization flow
analytics.track('Optimization Started', { credits_left: 2 });
analytics.track('Resume Uploaded', { file_size: 1024, file_type: 'pdf' });
analytics.track('Job Description Submitted', { char_count: 500 });
analytics.track('Optimization Completed', { match_score: 85, time_taken: 180 });

// Conversion
analytics.track('Upgrade Modal Shown', { trigger: 'out_of_credits' });
analytics.track('Upgrade Clicked', { tier: 'pro' });
analytics.track('Payment Completed', { tier: 'pro', amount: 2990 });

// Engagement
analytics.track('Dashboard Viewed');
analytics.track('History Viewed');
analytics.track('Result Downloaded', { format: 'docx' });
```

**Checklist:**
- [ ] Install PostHog or similar
- [ ] Initialize in app
- [ ] Track key events
- [ ] Set up funnels in dashboard
- [ ] Create retention cohorts
- [ ] Set up alerts for drops in key metrics

---

### Task 3.2: Set Up A/B Testing ⏰ 4 hours

**Priority:** 🟢 Medium  
**Impact:** High - Optimization  
**Effort:** Medium

**Tests to Run:**

1. **CTA Copy Test**
   - A: "Começar Grátis"
   - B: "Experimentar Agora"
   
2. **Free Credit Amount**
   - A: 3 credits
   - B: 5 credits

3. **Upgrade Timing**
   - A: After 2nd optimization
   - B: After 3rd optimization

4. **Pricing Display**
   - A: Monthly pricing prominent
   - B: Annual pricing prominent

**Using PostHog Feature Flags:**

```typescript
// File: frontend/hooks/useFeatureFlag.ts

import { usePostHog } from 'posthog-js/react';

export function useFeatureFlag(flagKey: string): boolean | string {
  const posthog = usePostHog();
  return posthog.getFeatureFlag(flagKey);
}

// Usage:
const ctaCopy = useFeatureFlag('cta_copy_test') === 'variant_b' 
  ? 'Experimentar Agora' 
  : 'Começar Grátis';
```

**Checklist:**
- [ ] Set up feature flags
- [ ] Implement variant logic
- [ ] Track conversions for each variant
- [ ] Run test for 2+ weeks
- [ ] Analyze results
- [ ] Implement winning variant

---

## 🔄 Phase 4: Polish & Optimization (Week 4)

### Task 4.1: Mobile Optimization ⏰ 8 hours

**Priority:** 🟡 High  
**Impact:** High - 30-40% mobile traffic  
**Effort:** High

**Focus Areas:**
- [ ] Responsive navigation
- [ ] Touch-friendly buttons (min 44x44px)
- [ ] Optimize upload flow for mobile
- [ ] Test on iOS Safari and Android Chrome
- [ ] Reduce image sizes
- [ ] Lazy load components
- [ ] Test on slow 3G

---

### Task 4.2: Performance Audit ⏰ 4 hours

**Priority:** 🟡 High  
**Impact:** Medium - SEO & UX  
**Effort:** Low

**Tools:** Lighthouse, WebPageTest

**Targets:**
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 95
- SEO: > 90

**Checklist:**
- [ ] Run Lighthouse audit
- [ ] Optimize images (WebP, lazy load)
- [ ] Minimize JavaScript bundles
- [ ] Enable caching
- [ ] Add meta tags
- [ ] Fix accessibility issues

---

### Task 4.3: Error Handling & Edge Cases ⏰ 6 hours

**Priority:** 🟡 High  
**Impact:** Medium - User trust  
**Effort:** Medium

**Cases to Handle:**
- [ ] File upload fails
- [ ] API is down
- [ ] Payment fails
- [ ] Session expires mid-flow
- [ ] Invalid file formats
- [ ] Network timeout
- [ ] Database errors

**Example Error Boundary:**

```typescript
// File: frontend/components/ErrorBoundary.tsx

'use client';

import { Component, ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="text-center max-w-md">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold mb-2">Algo deu errado</h1>
            <p className="text-gray-600 mb-6">
              Desculpe, ocorreu um erro inesperado. Nossa equipe foi notificada.
            </p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => window.location.reload()}>
                Recarregar Página
              </Button>
              <Button variant="outline" onClick={() => window.location.href = '/dashboard'}>
                Ir para Dashboard
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 📈 Success Metrics Dashboard

Create a simple tracking dashboard to monitor:

```typescript
// File: frontend/app/[locale]/admin/metrics/page.tsx

export default function MetricsPage() {
  return (
    <div>
      <h1>Key Metrics</h1>
      
      {/* Acquisition */}
      <MetricCard title="Weekly Signups" value={450} change={+12} />
      <MetricCard title="Signup Conversion" value="15%" change={+3} />
      
      {/* Activation */}
      <MetricCard title="First Optimization %" value="68%" change={+8} />
      <MetricCard title="Time to First Optimization" value="4.2 min" change={-0.8} />
      
      {/* Monetization */}
      <MetricCard title="Free → Paid %" value="12%" change={+4} />
      <MetricCard title="MRR" value="R$ 12.450" change={+25} />
      
      {/* Retention */}
      <MetricCard title="30-day Retention" value="42%" change={+5} />
      <MetricCard title="Avg Credits Used" value="2.8/3" change={+0.3} />
    </div>
  );
}
```

---

## 🎯 Final Checklist

### Before Launch:
- [ ] All Phase 1 tasks complete
- [ ] Analytics tracking verified
- [ ] Error handling tested
- [ ] Mobile responsive
- [ ] Performance > 80 on Lighthouse
- [ ] Security audit passed
- [ ] Backup and rollback plan ready

### Launch Day:
- [ ] Monitor error rates
- [ ] Watch conversion funnels
- [ ] Be ready to rollback if issues
- [ ] Collect user feedback
- [ ] Monitor server load

### Week 1 Post-Launch:
- [ ] Review analytics daily
- [ ] Address critical bugs
- [ ] Collect qualitative feedback
- [ ] Start planning Phase 2

### Week 2-4 Post-Launch:
- [ ] Run A/B tests
- [ ] Optimize based on data
- [ ] Plan next features
- [ ] Celebrate wins! 🎉

---

## 📞 Questions to Answer Before Starting

1. **Free tier:** 3 or 5 credits? *Recommendation: 3*
2. **Credits reset?** Monthly or lifetime? *Recommendation: Lifetime for free tier*
3. **Onboarding:** Required or optional? *Recommendation: Optional with skip*
4. **Analytics:** PostHog, Amplitude, or custom? *Recommendation: PostHog*
5. **Email:** Resend, SendGrid, or other? *Recommendation: Resend*
6. **A/B testing:** Built-in or tool? *Recommendation: PostHog feature flags*

---

**Priority Legend:**
- 🔴 **CRITICAL** - Must have for MVP
- 🟡 **High** - Important for launch
- 🟢 **Medium** - Nice to have
- ⚪ **Low** - Future consideration

---

*This checklist is a living document. Update as tasks are completed and new requirements emerge.*

**Last Updated:** October 12, 2025  
**Next Review:** Weekly during implementation