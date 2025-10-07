# CV-Match Project Overview

## Business Model
CV-Match is a Brazilian-focused SaaS platform using a **Hybrid "Flex & Flow" Model**:
- **Flex** (Credits): R$ 29,90-169,90 for job seekers and occasional users
- **Flow** (Subscriptions): R$ 24,90-129,90/month for recruiters and power users
- **Target Market**: 220M+ Portuguese speakers in Brazil with high price sensitivity

## Key Business Metrics
- **Year 1 Goals**: 10K users, 3K paid users, R$ 634K revenue
- **Pricing Strategy**: 3 free analyses (lead gen), then Flex 25 (R$ 59,90) or Flow Pro (R$ 39,90/month)
- **KPIs**: CAC < R$ 75, LTV R$ 250-400, 25-35% conversion rate

## Technical Architecture
- **Frontend**: Next.js 15+ with TypeScript, Tailwind CSS, Bun package manager
- **Backend**: FastAPI with async/await, Pydantic models, service layer architecture
- **Database**: Supabase PostgreSQL with RLS policies
- **Payments**: Stripe with BRL support
- **Auth**: Supabase Auth (Google, LinkedIn, Email)

## Development Standards
- **Service Layer**: Generic SupabaseDatabaseService[T] for CRUD operations
- **API Pattern**: FastAPI endpoints with dependency injection
- **Frontend**: All components use 'use client', TypeScript interfaces
- **Database**: User-scoped tables with RLS policies
- **Localization**: next-intl for PT-BR translations

## Key Features
- Resume upload (PDF/DOCX) with AI-powered matching
- Job description analysis and improvement suggestions
- Credit-based usage tracking and subscription management
- Brazilian market optimized (PIX, boleto, BRL pricing)

## Development Workflow
- **Commands**: `make dev` (Docker), `make install-frontend` (Bun), `supabase db push`
- **Testing**: Backend at http://localhost:8000/docs, Frontend at http://localhost:3000
- **Database**: Local Supabase with migration management
- **Git**: Conventional commits, feature branches, pre-commit checks