# CV-Match Development Roadmap

**Last Updated**: 2025-10-07
**Current Status**: Integration Phase - Migrating Resume-Matcher components to cv-match

## 🎯 Executive Summary

This roadmap prioritizes migrating battle-tested code from Resume-Matcher (`/home/carlos/projects/Resume-Matcher/apps/`) to the cv-match project. The goal is to achieve a production-ready Brazilian market launch in **4 weeks** by leveraging existing assets.

### Current State Analysis

**Resume-Matcher Project (Source)**:

- ✅ 13 production-ready backend services (~3,264 lines of code)
- ✅ Complete SaaS infrastructure (Stripe, usage tracking, multi-tenancy)
- ✅ Full internationalization (PT-BR + EN with ~11 translation files)
- ✅ 30+ frontend pages including dashboard, optimization, pricing, blog
- ✅ Database schema with 6 migrations (auth, payments, usage tracking)
- ✅ Agent system for LLM orchestration

**cv-match Project (Target)**:

- ⚠️ Basic infrastructure only (3 backend service folders, 7 service files)
- ⚠️ Minimal frontend (4 pages: landing, dashboard, auth callbacks)
- ❌ No internationalization (no locales directory)
- ❌ No payment integration
- ❌ No resume matching services
- ❌ No usage tracking

**Gap Analysis**: ~90% of functionality needs to be migrated from Resume-Matcher to cv-match.

---

## 📋 Priority Tiers

### P0: MVP - Launch Blockers (Week 1-2)

**Must-have for first paying customer**

#### Backend Core Services (Week 1)

- [ ] **Copy resume processing services**
  - `resume_service.py` - PDF/DOCX parsing
  - `job_service.py` - Job description processing
  - `score_improvement_service.py` - Core matching algorithm
  - `text_extraction.py` - Document text extraction
  - Impact: Enables core product functionality
  - Effort: 2 days (copy + integration tests)

- [ ] **Copy agent system**
  - `app/agent/` directory - LLM orchestration
  - `app/agent/manager.py` - Multi-provider LLM abstraction
  - Impact: Enables AI-powered resume improvement
  - Effort: 1 day (minimal changes needed)

- [ ] **Database migrations**
  - Copy all 6 migrations from Resume-Matcher
  - Apply to cv-match Supabase instance
  - Verify RLS policies work
  - Impact: Required for all features
  - Effort: 1 day (testing critical)

- [ ] **API endpoints**
  - Create `/api/resume/upload` endpoint
  - Create `/api/resume/analyze` endpoint
  - Create `/api/jobs/analyze` endpoint
  - Impact: Connects frontend to backend
  - Effort: 2 days

#### Frontend Core Pages (Week 2)

- [ ] **Copy optimization workflow**
  - `app/[locale]/optimize/page.tsx` - Main optimization page
  - `app/[locale]/optimizations/page.tsx` - History view
  - `app/results/[id]/page.tsx` - Results display
  - Impact: Core user journey
  - Effort: 2 days

- [ ] **Copy UI components**
  - `components/ui/*` - shadcn/ui components
  - File upload components
  - Analysis display components
  - Impact: Required for all pages
  - Effort: 1 day (mostly copy-paste)

#### Internationalization Setup (Week 2)

- [ ] **Install next-intl**
  - `bun add next-intl@4.3.6`
  - Copy configuration from Resume-Matcher
  - Set up middleware for locale routing
  - Impact: Brazilian market targeting
  - Effort: 0.5 days

- [ ] **Copy PT-BR translations**
  - Copy `locales/pt-br/` directory (11 files)
  - Copy `locales/en/` directory (11 files)
  - Update `next.config.ts`
  - Impact: Enables Portuguese interface
  - Effort: 0.5 days

---

### P1: Revenue Enablement (Week 3)

**Required to charge customers**

#### Payment Infrastructure

- [ ] **Copy Stripe services**
  - `stripe_service.py` - Payment processing
  - `payment_verification.py` - AI-triggered verification
  - `usage_limit_service.py` - Credit tracking
  - Impact: Enables monetization
  - Effort: 2 days

- [ ] **Copy payment pages**
  - `app/[locale]/pricing/page.tsx` - Pricing page with BRL
  - `app/(default)/payment/success/page.tsx`
  - `app/(default)/payment/canceled/page.tsx`
  - Impact: Payment user flow
  - Effort: 1 day

- [ ] **Webhook integration**
  - Set up `/api/webhooks/stripe` endpoint
  - Copy webhook processing logic
  - Test idempotency and signature verification
  - Impact: Critical for payment security
  - Effort: 2 days

#### Usage Tracking

- [ ] **Copy usage services**
  - `usage_tracking_service.py` - Track API usage
  - `paid_resume_improvement_service.py` - Credit deduction
  - Impact: Prevents abuse, enables tiered pricing
  - Effort: 1 day

- [ ] **Dashboard integration**
  - Copy usage display components
  - Show credits remaining
  - Show optimization history
  - Impact: User transparency
  - Effort: 1 day

---

### P2: Growth & Optimization (Week 4+)

**Post-launch improvements**

#### Advanced Features

- [ ] **DOCX generation**
  - Copy `docx_generation.py` - Generate improved resumes
  - Add download functionality
  - Impact: Premium feature differentiation
  - Effort: 2 days

- [ ] **Blog system**
  - Copy blog infrastructure
  - Migrate content files
  - Set up analytics
  - Impact: SEO and content marketing
  - Effort: 3 days

#### User Experience

- [ ] **Onboarding flow**
  - Copy onboarding pages
  - Add progress indicators
  - Implement skip logic
  - Impact: Reduce time-to-value
  - Effort: 2 days

- [ ] **Settings page**
  - Copy `app/[locale]/settings/page.tsx`
  - Add profile management
  - Add notification preferences
  - Impact: User retention
  - Effort: 1 day

#### Testing & Quality

- [ ] **Integration tests**
  - Test resume upload → analysis → results flow
  - Test payment flow end-to-end
  - Test Portuguese translations
  - Impact: Reduce production bugs
  - Effort: 3 days

- [ ] **Performance optimization**
  - Implement caching for LLM responses
  - Optimize database queries
  - Add CDN for static assets
  - Impact: Better UX, lower costs
  - Effort: 2 days

#### Brazilian Market Specific

- [ ] **PIX payment integration**
  - Research Stripe PIX support
  - Add PIX as payment method
  - Impact: Higher conversion in Brazil
  - Effort: 3 days (research-heavy)

- [ ] **Boleto integration**
  - Add boleto payment method
  - Handle async payment confirmation
  - Impact: Reach unbanked population
  - Effort: 3 days

---

## 🗓️ 4-Week Timeline

### Week 1: Backend Foundation

**Goal**: Core resume matching works locally

- Days 1-2: Copy & test backend services
- Days 3-4: Set up database migrations
- Day 5: API endpoints and integration tests

**Milestone**: Can upload resume + job description, get match score via API

---

### Week 2: Frontend & i18n

**Goal**: Working UI in Portuguese

- Days 1-2: Copy frontend pages and components
- Days 3-4: Set up next-intl and translations
- Day 5: End-to-end testing of optimization flow

**Milestone**: Portuguese-speaking user can optimize resume through UI

---

### Week 3: Payments

**Goal**: Can charge first customer

- Days 1-2: Stripe service integration
- Days 3-4: Webhook + usage tracking setup
- Day 5: Payment flow testing with test cards

**Milestone**: User can purchase credits and use them

---

### Week 4: Polish & Launch

**Goal**: Production-ready deployment

- Days 1-2: Bug fixes from testing
- Day 3: Performance optimization
- Day 4: Production deployment
- Day 5: Soft launch to beta users

**Milestone**: First paying customer in Brazil

---

## 🚨 Critical Risks

### Technical Risks

1. **Database Migration Complexity**
   - Risk: RLS policies break during migration
   - Mitigation: Test on staging database first
   - Owner: Backend lead

2. **Stripe Webhook Reliability**
   - Risk: Missed webhooks = payment issues
   - Mitigation: Implement retry logic + manual reconciliation
   - Owner: Payment integration lead

3. **LLM API Rate Limits**
   - Risk: OpenRouter/Anthropic rate limits block users
   - Mitigation: Implement queueing + fallback providers
   - Owner: Backend lead

### Business Risks

1. **Brazilian Market Fit**
   - Risk: Pricing too high for Brazilian market
   - Mitigation: Start with proven Resume-Matcher pricing (R$ 49.90/mo)
   - Owner: Product lead

2. **Translation Quality**
   - Risk: PT-BR translations sound robotic
   - Mitigation: Native Brazilian review before launch
   - Owner: Content lead

---

## 📊 Success Metrics

### Technical KPIs (Week 4)

- [ ] Resume upload success rate > 95%
- [ ] Average analysis time < 30 seconds
- [ ] System uptime > 99%
- [ ] Zero payment processing errors

### Business KPIs (Month 1)

- [ ] 100 sign-ups
- [ ] 10 paying customers (10% conversion)
- [ ] R$ 500 MRR
- [ ] 4.0+ user satisfaction rating

### Business KPIs (Month 3)

- [ ] 500 sign-ups
- [ ] 75 paying customers (15% conversion)
- [ ] R$ 3,750 MRR
- [ ] 4.5+ user satisfaction rating

---

## 🔄 Migration Strategy

### Code Migration Process

1. **Copy files** from Resume-Matcher to cv-match
2. **Update imports** to match cv-match structure
3. **Run tests** to verify functionality
4. **Git commit** with descriptive message
5. **Deploy to staging** for integration testing

### Database Migration Process

1. **Backup** current cv-match database
2. **Apply migrations** one by one
3. **Verify RLS policies** with test users
4. **Run data validation** scripts
5. **Deploy to production** during low-traffic window

### Environment Variables

Copy these from Resume-Matcher to cv-match:

```bash
# Backend
RESUME_MATCHER_LLM_PROVIDER=openrouter
RESUME_MATCHER_LLM_MODEL=anthropic/claude-3.5-sonnet
RESUME_MATCHER_EMBEDDING_PROVIDER=openai
RESUME_MATCHER_EMBEDDING_MODEL=text-embedding-3-small
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...

# Frontend
NEXT_PUBLIC_DEFAULT_LOCALE=pt-br
NEXT_PUBLIC_SUPPORTED_LOCALES=en,pt-br
NEXT_PUBLIC_DEFAULT_CURRENCY=brl
NEXT_PUBLIC_MARKET=brasil
```

---

## 🎓 Documentation Links

- **Implementation Guide**: See `implementation-guide.md` for step-by-step migration
- **Architecture**: See `architecture-overview.md` for system design
- **Business Model**: See `business-model-analysis.md` for pricing strategy
- **Stripe Integration**: See `stripe-integration-analysis.md` for payment details
- **i18n Setup**: See `next-intl-integration.md` for translation infrastructure

---

## ✅ Definition of Done

### P0 (MVP) Complete When:

- [ ] User can upload resume in PT-BR interface
- [ ] User gets match score and improvement suggestions
- [ ] User can view optimization history
- [ ] All Portuguese translations are accurate
- [ ] Zero critical bugs in core flow

### P1 (Revenue) Complete When:

- [ ] User can purchase credits with credit card (BRL)
- [ ] Webhooks process payments reliably
- [ ] Credits deduct correctly per optimization
- [ ] User sees remaining credits in dashboard
- [ ] Payment reconciliation matches Stripe dashboard

### P2 (Growth) Complete When:

- [ ] DOCX generation works for all resume formats
- [ ] Blog has 10+ SEO-optimized articles
- [ ] Onboarding flow has >80% completion rate
- [ ] Performance benchmarks met (p95 < 30s)
- [ ] PIX or Boleto payment option available

---

**Next Actions**: Start with P0 Week 1 backend services migration. Track progress in this document.
