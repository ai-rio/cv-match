# CV-Match - Project Overview and Standards

## Project Description

CV-Match is a modern SaaS platform for AI-powered resume optimization and job matching, targeting the Brazilian market. Built on the Resume-Matcher foundation with a complete FastAPI/Next.js stack.

## Architecture Overview

- **Backend**: Python FastAPI with Supabase integration (auth, database, storage)
- **Frontend**: Next.js 15+ with Tailwind CSS, TypeScript, and App Router
- **Database**: Supabase PostgreSQL with pgvector for semantic search
- **LLM Integration**: OpenAI and OpenRouter (Claude) support
- **Payment Processing**: Stripe with BRL currency support for Brazilian market
- **Internationalization**: next-intl with PT-BR and EN support

## Core Principles

1. **Type Safety First**: Use TypeScript for frontend, Pydantic models for backend
2. **Service Layer Pattern**: Abstract external services (Supabase, LLM, Stripe)
3. **Environment-based Configuration**: Use .env files for all configuration
4. **Brazilian Market Focus**: BRL currency, PT-BR localization, local payment methods
5. **Migration-driven Database**: All schema changes through Supabase migrations
6. **Hybrid Monetization**: Credit-based + subscription model ("Flex & Flow")

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Database ORM**: SQLAlchemy with Supabase PostgreSQL
- **Authentication**: Supabase Auth with JWT
- **AI/ML**:
  - LLM: OpenAI GPT-4, Anthropic Claude (via OpenRouter)
  - Embeddings: OpenAI text-embedding-3-small
  - Vector Search: pgvector (built into Supabase)
- **Payment**: Stripe with Brazilian market configuration
- **Document Processing**: MarkItDown for PDF/DOCX parsing

### Frontend
- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React hooks + SWR for server state
- **Internationalization**: next-intl v4.3.6
- **Payment UI**: Stripe Elements

### Infrastructure
- **Database**: Supabase (PostgreSQL + pgvector)
- **Storage**: Supabase Storage for file uploads
- **Authentication**: Supabase Auth
- **Deployment**: Docker-ready, designed for Vercel (frontend) + Railway/Fly.io (backend)
- **CI/CD**: GitHub Actions ready

## File Organization Standards

### Backend Structure
```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Config, security, dependencies
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic services
│   │   ├── resume/   # Resume processing
│   │   ├── job/      # Job processing
│   │   ├── matching/ # AI matching logic
│   │   ├── stripe/   # Payment processing
│   │   └── supabase/ # Database/auth services
│   └── agent/        # LLM agent managers
```

### Frontend Structure
```
frontend/
├── app/              # Next.js App Router pages
├── components/       # React components
│   ├── ui/          # shadcn/ui components
│   ├── payment/     # Payment components
│   └── dashboard/   # Dashboard components
├── lib/             # Utilities and configs
│   ├── api/         # API client
│   └── stripe.ts    # Stripe client
├── messages/        # i18n translations (pt-br, en)
└── middleware.ts    # next-intl routing
```

### Database Structure
```
supabase/
├── migrations/      # SQL migration files
├── functions/       # PostgreSQL functions
└── seed.sql         # Initial data
```

## Naming Conventions

- **Python**: `snake_case` for functions, files, variables
- **TypeScript**: `camelCase` for functions, variables; `PascalCase` for components, types
- **Files**:
  - Backend: `user_service.py`, `auth_middleware.py`
  - Frontend: `ResumeUpload.tsx`, `payment-flow.tsx`
- **Database**: `snake_case` for tables, columns

## Development Workflow

### Starting Development
```bash
# Backend (using uv - fast Python package manager)
cd backend
uv venv  # Create virtual environment
source .venv/bin/activate  # Activate on WSL/Linux
uv pip install -e .  # Install from pyproject.toml
uvicorn app.main:app --reload

# Or use uv run (no activation needed)
cd backend
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
bun install
bun run dev

# Database
supabase db push
```

### Making Changes

#### Backend Changes
1. Create/modify service in `app/services/`
2. Define Pydantic models in `app/models/`
3. Create API endpoint in `app/api/`
4. Test via http://localhost:8000/docs

#### Frontend Changes
1. Create component in `components/`
2. Define TypeScript interfaces
3. Use Tailwind CSS for styling
4. Test at http://localhost:3000

#### Database Changes
```bash
# Create migration
supabase migration new description_of_change

# Edit SQL in supabase/migrations/YYYYMMDDHHMMSS_description.sql

# Apply migration
supabase db push
```

## Code Quality Standards

### Always Include

1. **Type Annotations**: All functions must have type hints (Python) or types (TypeScript)
2. **Error Handling**: Use try/catch blocks and proper HTTP status codes
3. **Authentication**: Protected endpoints must use `get_current_user` dependency
4. **Async/Await**: Use async patterns for I/O operations
5. **Documentation**: Docstrings for services, JSDoc for complex components
6. **Brazilian Localization**: Always provide PT-BR translations

### Error Handling Patterns

**Backend (Python)**:
```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail="Resume not found with the provided ID"
)
```

**Frontend (TypeScript)**:
```typescript
try {
  const response = await apiClient.post('/endpoint', data)
  // Handle success
} catch (error) {
  console.error('Operation failed:', error)
  toast.error(t('errors.operationFailed'))
}
```

## Key Services and Patterns

### Backend Services
- **ResumeService**: PDF/DOCX parsing, text extraction
- **JobService**: Job description processing
- **ScoreImprovementService**: Cosine similarity matching + LLM suggestions
- **AgentManager**: Multi-provider LLM abstraction
- **StripeService**: Payment processing with BRL support
- **UsageLimitService**: Credit-based usage tracking

### Frontend Components
- **FileUpload**: Drag-drop resume upload
- **ResumeAnalysis**: Score display with improvements
- **PaymentFlow**: Stripe checkout integration
- **PricingCards**: Flex & Flow pricing display
- **UsageTracker**: Credit consumption display

## Environment Variables

### Required (Backend)
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxx...
SUPABASE_ANON_KEY=eyJxxx...

# LLM Providers
OPENROUTER_API_KEY=sk-or-xxx
OPENAI_API_KEY=sk-xxx

# Stripe (Brazilian Market)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Configuration
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### Required (Frontend)
```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# Internationalization
NEXT_PUBLIC_DEFAULT_LOCALE=pt-br
NEXT_PUBLIC_SUPPORTED_LOCALES=en,pt-br

# Market Configuration
NEXT_PUBLIC_DEFAULT_CURRENCY=brl
NEXT_PUBLIC_DEFAULT_COUNTRY=BR
NEXT_PUBLIC_MARKET=brasil
```

## Security Best Practices

1. **Never commit secrets**: Use .env files (in .gitignore)
2. **Row Level Security**: All Supabase tables have RLS policies
3. **JWT Validation**: All protected routes validate Supabase JWT
4. **Input Validation**: Pydantic models validate all input
5. **CORS Configuration**: Whitelist specific origins only
6. **Stripe Webhooks**: Verify signatures with 300s tolerance
7. **File Upload**: Validate file types and sizes

## Testing Standards

### Backend Tests
```python
# Use pytest
pytest tests/

# Test API endpoints
pytest tests/api/test_resume.py -v

# Test with coverage
pytest --cov=app tests/
```

### Frontend Tests
```bash
# Run Jest tests
bun run test

# Run E2E tests (if configured)
bun run test:e2e
```

## Git Commit Standards

Follow conventional commits:
```bash
feat(resume): add PDF parsing with MarkItDown
fix(payment): handle failed BRL transactions
docs(readme): update Brazilian market setup
refactor(api): extract resume processing to service
test(matching): add cosine similarity tests
```

## Brazilian Market Specifics

### Currency Formatting
- Always use BRL: `R$ 49,90` (comma for decimal)
- Use Portuguese number formatting: `1.234,56` not `1,234.56`

### Translations
- All user-facing text must have PT-BR translations in `messages/pt-br.json`
- Use next-intl's `useTranslations()` hook in components
- Business terms: "créditos" (credits), "assinatura" (subscription), "análise" (analysis)

### Payment Methods
- Primary: Credit cards via Stripe
- Future: PIX (instant transfer), Boleto (bank slip)
- Always show prices in BRL with proper formatting

### Cultural Adaptations
- Use formal "você" in UI copy
- Job titles in Portuguese: "Desenvolvedor" not "Developer"
- Date format: DD/MM/YYYY
- Phone format: (11) 98765-4321

## Performance Optimization

1. **Backend**: Use async operations, cache LLM responses
2. **Frontend**: Use Next.js Image, lazy load components, SWR for caching
3. **Database**: Index frequently queried columns, use pgvector HNSW index
4. **API**: Implement rate limiting per subscription tier

## Deployment Checklist

- [ ] Environment variables configured for production
- [ ] Database migrations applied
- [ ] Supabase RLS policies tested
- [ ] Stripe webhooks endpoint configured
- [ ] CORS origins set to production domain
- [ ] Brazilian payment methods tested
- [ ] PT-BR translations complete
- [ ] Error monitoring configured (Sentry recommended)

---

When adding new features, **always** follow these established patterns and maintain consistency with existing code structure. Prioritize the Brazilian market experience in all user-facing features.
