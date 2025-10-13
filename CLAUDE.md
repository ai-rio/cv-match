# CLAUDE.md

This file provides quick reference guidance for Claude Code (claude.ai/code) when working with code in this repository.

**📚 For detailed standards and patterns, see the [`.claude/` directory](.claude/GETTING_STARTED.md)** which contains:

- Complete project overview and architecture
- Business model and pricing strategy
- Backend and frontend development standards
- Development workflow and commands
- Templates for common patterns

**Quick Start**: Reference files in your prompts like `@.claude/project-overview.md` to give Claude full context.

## Project Overview

CV-Match is a full-stack SaaS application built on the Vinta Software template, featuring Next.js frontend with TypeScript, FastAPI backend with Python, and Supabase for database/authentication. The project targets the Brazilian market with Portuguese localization and BRL payment integration.

**Key Architecture:**

- **Frontend**: Next.js 15+ with App Router, TypeScript, Tailwind CSS, Bun package manager
- **Backend**: FastAPI with async/await patterns, Pydantic models, service layer architecture
- **Database**: Local Supabase PostgreSQL with Row Level Security (RLS)
- **Authentication**: Supabase Auth with Google, LinkedIn, Email/Password providers
- **Package Management**: Bun (not npm) for faster dependency installation

## Essential Commands

### Development Environment

```bash
# Start full development environment (Docker)
make dev

# Start individual services
make dev-frontend    # Frontend only: http://localhost:3000
make dev-backend     # Backend only: http://localhost:8000

# Install dependencies locally (when not using Docker)
make install-frontend    # Uses Bun, not npm
make install-backend     # Uses uv (fast Python package manager)

# Build for production
make build-frontend
```

### Database Operations

```bash
# Create new migration
make db-migration-new name=create_table_name

# Apply migrations to local Supabase
supabase db push

# Check migration status
make db-status

# List migrations
make db-list
```

### Production

```bash
# Start production environment
make prod

# Clean up containers and volumes
make clean
```

## Service Layer Architecture

### Backend Services Structure

```
backend/app/services/
├── supabase/
│   ├── database.py      # Generic SupabaseDatabaseService[T] for CRUD operations
│   ├── auth.py          # SupabaseAuthService for user management
│   └── storage.py       # SupabaseStorageService for file uploads
├── llm/
│   ├── llm_service.py   # LLM abstraction (OpenAI, Anthropic)
│   └── embedding_service.py  # Vector embeddings
└── vectordb/
    └── qdrant_service.py    # Vector database operations
```

**Key Service Patterns:**

- Use `SupabaseDatabaseService[T]` for generic CRUD operations with Pydantic models
- Always implement async/await patterns in services
- Service classes handle external API integrations (LLM, vector DB, storage)
- Use dependency injection in FastAPI endpoints

### FastAPI Endpoint Pattern

```python
@router.post("/items", response_model=ItemResponse)
async def create_item(
    request: CreateItemRequest,
    current_user: User = Depends(get_current_user)
) -> ItemResponse:
    try:
        service = SupabaseDatabaseService("items", ItemResponse)
        result = await service.create({**request.dict(), "user_id": current_user.id})
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Frontend Architecture

### Next.js App Router Structure

```
frontend/app/
├── layout.tsx          # Root layout with providers
├── page.tsx           # Landing page
├── dashboard/page.tsx # Protected dashboard
└── auth/
    ├── callback/      # Supabase auth callbacks
    └── reset-password/
```

**Key Frontend Patterns:**

- All components use `'use client'` directive when using hooks
- TypeScript interfaces for all props
- Tailwind CSS for styling with responsive design
- Error handling with try/catch and loading states

### Component Pattern

```tsx
"use client";
export default function ComponentName({ title, onAction }: Props) {
  const [loading, setLoading] = useState(false);

  const handleAction = async () => {
    try {
      setLoading(true);
      await onAction?.();
    } catch (error) {
      console.error("Action failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return <div className="p-4 rounded-lg border">{/* Component content */}</div>;
}
```

## Database Schema Patterns

### Table Structure with RLS

```sql
-- Standard table pattern with user association
CREATE TABLE public.table_name (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  -- Other columns...
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.table_name ENABLE ROW LEVEL SECURITY;

-- User-specific policy
CREATE POLICY "Users can manage own table_name"
  ON public.table_name
  USING (auth.uid() = user_id);
```

## Environment Configuration

### Required Environment Variables

```bash
# .env (backend)
SUPABASE_URL=http://localhost:54321  # Local Supabase
SUPABASE_SERVICE_KEY=your_local_service_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_local_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Local Development Setup

- Uses local Supabase instance (not remote)
- Bun package manager for frontend dependencies
- Docker Compose for service orchestration
- Environment files already configured for local development

## Brazilian Market Integration

The project includes comprehensive Resume-Matcher integration documentation for Brazilian market entry:

### Key Features Available

- **next-intl v4.3.6**: Brazilian Portuguese (pt-br) localization ready
- **Stripe BRL Integration**: Complete payment infrastructure for Brazilian market
- **Resume Matching**: Advanced cosine similarity algorithms with LLM improvement
- **SaaS Infrastructure**: Credit-based usage tracking, subscription management

### Integration Documentation

See `/docs/development/` for complete integration strategies:

- `resume-matcher-integration.md` - 4-week launch strategy with 90% development time reduction
- `implementation-guide.md` - Step-by-step integration instructions
- `next-intl-integration.md` - Brazilian Portuguese localization setup
- `stripe-integration-analysis.md` - BRL payment infrastructure analysis

## Development Workflow

1. **Initial Setup**: Environment files and local Supabase already configured
2. **Start Development**: `make dev` starts all services with hot reload
3. **Database Changes**: Create migrations with `make db-migration-new name=description`
4. **API Testing**: Backend docs available at http://localhost:8000/docs
5. **Frontend Testing**: Application available at http://localhost:3000

## Important Notes

- **Always use Bun** for frontend operations, not npm
- **Local Supabase** is configured and running by default
- **Service Layer**: Always use service classes for external integrations
- **Authentication**: All protected endpoints require `get_current_user` dependency
- **Error Handling**: Implement comprehensive error handling in all async functions
- **Type Safety**: Use TypeScript interfaces and Pydantic models throughout

## Testing Commands

```bash
# Backend API testing
curl http://localhost:8000/docs  # Interactive API documentation

# Frontend development server
http://localhost:3000           # Next.js development server

# Supabase local studio
http://localhost:54323         # Supabase dashboard for local instance
```

---

## 📖 Comprehensive Documentation

This file provides a quick reference. For comprehensive development standards and patterns:

### Core Documentation

- **[.claude/GETTING_STARTED.md](.claude/GETTING_STARTED.md)** - Start here for using Claude Code effectively
- **[.claude/project-overview.md](.claude/project-overview.md)** - Complete project context, tech stack, standards
- **[.claude/business-context.md](.claude/business-context.md)** - Pricing model, market strategy, KPIs
- **[.claude/development-workflow.md](.claude/development-workflow.md)** - Daily workflow, commands, debugging

### Development Standards

- **[.claude/backend/fastapi-standards.md](.claude/backend/fastapi-standards.md)** - Backend API patterns
- **[.claude/frontend/nextjs-standards.md](.claude/frontend/nextjs-standards.md)** - Frontend component patterns

### Business & Strategy

- **[docs/development/business-model-analysis.md](docs/development/business-model-analysis.md)** - Full business model analysis
- **[docs/development/stripe-integration-analysis.md](docs/development/stripe-integration-analysis.md)** - Brazilian payment strategy

**Pro Tip**: When asking Claude to build features, reference relevant `.claude/` files to ensure consistency with project standards:

```
@.claude/project-overview.md
@.claude/backend/fastapi-standards.md

Create a new API endpoint for analyzing resumes...
```
