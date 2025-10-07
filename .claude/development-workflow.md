# Development Workflow with Claude Code

## Quick Reference Commands

### Backend Development
```bash
# Start backend server
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Create new migration
supabase migration new add_feature_name

# Apply migrations
supabase db push
```

### Frontend Development
```bash
# Start frontend server
cd frontend
bun install  # or npm install
bunx dev  # or npm run dev

# Run tests
bunx test

# Build for production
bunx build
```

## Project Setup

### First Time Setup

1. **Clone and Install**:
```bash
# Clone repository
git clone <repo-url>
cd cv-match

# Backend setup (using uv)
cd backend
uv venv  # Create virtual environment with uv
source .venv/bin/activate
uv pip install -e .  # Install from pyproject.toml

# Frontend setup
cd ../frontend
bun install

# Return to root
cd ..
```

2. **Environment Configuration**:
```bash
# Copy environment templates
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

# Edit .env with your keys:
# - SUPABASE_URL and SUPABASE_SERVICE_KEY (required)
# - OPENROUTER_API_KEY or OPENAI_API_KEY (for LLM)
# - STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET (for payments)
```

3. **Database Setup**:
```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Apply migrations
supabase db push
```

4. **Start Development**:
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
bunx dev
```

5. **Verify Setup**:
- Backend: http://localhost:8000/docs (API documentation)
- Frontend: http://localhost:3000
- Test auth flow and basic features

## Daily Development Workflow

### Starting Your Day

1. **Pull latest changes**:
```bash
git pull origin main
```

2. **Update dependencies** (if needed):
```bash
# Backend
cd backend
uv pip install -e .  # Install/update from pyproject.toml

# Frontend
cd frontend
bun install
```

3. **Check migrations**:
```bash
supabase db pull  # Pull remote migrations
supabase db push  # Apply local migrations
```

4. **Start servers**:
```bash
# Backend (Terminal 1)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend && bunx dev
```

### Creating New Features

#### 1. Backend API Endpoint

**Reference**: `@.claude/backend/fastapi-standards.md` and `@.claude/templates/api-endpoint-template.md`

```bash
# 1. Create service
touch backend/app/services/feature/feature_service.py

# 2. Create models
touch backend/app/models/feature.py

# 3. Create API endpoint
touch backend/app/api/router/v1/feature.py

# 4. Register router in main.py

# 5. Test at http://localhost:8000/docs
```

**Example with Claude**:
```
@.claude/templates/api-endpoint-template.md
@.claude/backend/fastapi-standards.md

Create a new API endpoint for analyzing job postings:
- POST /api/v1/jobs/analyze
- Accepts job description text
- Returns extracted requirements and keywords
- Requires authentication
- Deducts 1 credit from user
```

#### 2. Frontend Component

**Reference**: `@.claude/frontend/nextjs-standards.md` and `@.claude/templates/react-component-template.md`

```bash
# 1. Create component file
touch frontend/components/feature/FeatureComponent.tsx

# 2. Add translations
# Edit frontend/messages/pt-br.json
# Edit frontend/messages/en.json

# 3. Import and use in page
# Edit frontend/app/[locale]/feature/page.tsx
```

**Example with Claude**:
```
@.claude/templates/react-component-template.md
@.claude/frontend/nextjs-standards.md

Create a pricing card component for the Flex & Flow model:
- Display credit package options
- Show BRL pricing with proper formatting
- Include PT-BR translations
- Add "Most Popular" badge to Flex 25
- Handle purchase click with Stripe
```

#### 3. Database Changes

**Reference**: `@.claude/database-migrations.md`

```bash
# 1. Create migration
supabase migration new add_feature_table

# 2. Edit migration file
# supabase/migrations/YYYYMMDDHHMMSS_add_feature_table.sql

# 3. Apply migration
supabase db push

# 4. Verify in Supabase dashboard
```

**Example with Claude**:
```
@.claude/database-migrations.md

Create a migration for storing user preferences:
- Table: user_preferences
- Columns: id, user_id, language, currency, notifications_enabled
- RLS policies for user data isolation
- Indexes on user_id
```

## Testing Your Changes

### Backend Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/api/test_resumes.py -v

# Run with coverage
pytest --cov=app tests/

# Test specific endpoint manually
curl -X POST http://localhost:8000/api/v1/resumes/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"resume_text": "...", "job_description": "..."}'
```

### Frontend Testing

```bash
# Run tests
bunx test

# Run tests in watch mode
bunx test --watch

# Test specific component
bunx test ResumeAnalysis

# Manual testing
# Open http://localhost:3000
# Test user flows in browser
```

### Integration Testing

1. **Auth Flow**:
   - Sign up new user
   - Verify email
   - Login
   - Check token in localStorage

2. **Resume Analysis**:
   - Upload resume PDF
   - Verify file processed
   - Check analysis results
   - Verify credit deduction

3. **Payment Flow**:
   - Select Flex 25 package
   - Complete Stripe checkout
   - Verify webhook processed
   - Check credits added

## Debugging

### Backend Debugging

**View Logs**:
```bash
# In terminal running uvicorn
# Logs appear automatically

# Add debug prints
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")
```

**API Testing**:
- Use http://localhost:8000/docs for interactive API testing
- Check request/response in browser DevTools Network tab

**Database Issues**:
```bash
# Check connection
supabase db pull

# Inspect tables
supabase db dump --data-only

# Reset database (careful!)
supabase db reset
```

### Frontend Debugging

**Browser DevTools**:
- Console: Check for errors
- Network: Inspect API calls
- Application: Check localStorage/sessionStorage
- React DevTools: Inspect component state

**Next.js Debugging**:
```bash
# Run in debug mode
NODE_OPTIONS='--inspect' bunx dev

# Check build errors
bunx build
```

**Common Issues**:
- Translation missing: Check `messages/pt-br.json` and `messages/en.json`
- API not working: Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Auth issues: Check Supabase keys and token in localStorage

## Git Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/add-job-analysis

# Make changes and commit
git add .
git commit -m "feat(jobs): add job analysis endpoint"

# Push to remote
git push origin feature/add-job-analysis

# Create PR on GitHub
```

### Commit Message Format

Follow conventional commits:

```
feat(scope): add new feature
fix(scope): fix bug
docs(scope): update documentation
refactor(scope): refactor code
test(scope): add tests
chore(scope): update dependencies

Examples:
feat(resume): add PDF parsing with MarkItDown
fix(payment): handle failed BRL transactions
docs(api): update resume analysis endpoint docs
refactor(matching): extract similarity calculation
test(auth): add authentication tests
chore(deps): update next-intl to 4.3.6
```

### Pre-commit Checklist

- [ ] Code follows project standards (@.claude/project-overview.md)
- [ ] All tests pass
- [ ] PT-BR translations added for new text
- [ ] API endpoints tested
- [ ] No console.log() in production code
- [ ] No sensitive data (API keys, tokens) in code
- [ ] Environment variables documented

## Working with Claude Code

### Referencing Rules

Use `@` to reference specific rules:

```
@.claude/project-overview.md - Project context
@.claude/business-context.md - Business strategy
@.claude/backend/fastapi-standards.md - Backend patterns
@.claude/frontend/nextjs-standards.md - Frontend patterns
```

### Example Prompts

**Creating Features**:
```
@.claude/project-overview.md
@.claude/backend/fastapi-standards.md

Create a credit system that:
- Tracks user credit balance in database
- Deducts credits on resume analysis
- Prevents analysis if insufficient credits
- Returns clear error messages in PT-BR
```

**Debugging**:
```
I'm getting a 403 error when calling /api/v1/resumes/analyze
The user should have credits. Help me debug this.

@.claude/backend/fastapi-standards.md
```

**Refactoring**:
```
@.claude/frontend/nextjs-standards.md

Refactor this component to:
- Use proper TypeScript interfaces
- Add PT-BR translations with next-intl
- Implement loading and error states
- Follow Tailwind CSS best practices

[paste component code]
```

**Business Decisions**:
```
@.claude/business-context.md

Should we offer a 10% discount for annual Flex subscriptions?
Consider our pricing strategy and target market.
```

## Deployment Preparation

### Pre-deployment Checklist

#### Backend
- [ ] Environment variables set in production
- [ ] Database migrations applied to production DB
- [ ] Stripe webhook endpoint configured
- [ ] CORS origins set to production domain
- [ ] Error tracking configured (Sentry)
- [ ] Health check endpoint working
- [ ] Rate limiting configured

#### Frontend
- [ ] Environment variables set
- [ ] Build succeeds without errors
- [ ] All translations complete (PT-BR + EN)
- [ ] Stripe publishable key configured
- [ ] Supabase connection working
- [ ] Meta tags and SEO configured
- [ ] Error boundaries in place

#### Database
- [ ] Migrations applied
- [ ] RLS policies enabled and tested
- [ ] Indexes created for performance
- [ ] Backup strategy configured
- [ ] Connection pooling set up

### Deployment Commands

```bash
# Backend (Railway/Fly.io)
# Deploy via Git push or CLI

# Frontend (Vercel)
vercel --prod

# Database (Supabase)
# Migrations auto-apply via GitHub integration
# Or manually: supabase db push --linked
```

## Troubleshooting

### Common Issues

**"Module not found"**:
```bash
# Backend
pip install -r requirements.txt

# Frontend
bun install
```

**"Database connection failed"**:
```bash
# Check Supabase credentials
supabase status

# Verify .env has correct SUPABASE_URL and SUPABASE_SERVICE_KEY
```

**"API calls returning 401"**:
- Check authentication token in request headers
- Verify Supabase JWT is valid (not expired)
- Check user is logged in

**"Translations not showing"**:
- Verify `messages/pt-br.json` has the key
- Check `useTranslations('namespace')` matches JSON structure
- Restart dev server

**"Stripe payment not working"**:
- Check Stripe keys (test vs production)
- Verify webhook endpoint is accessible
- Check webhook signature secret
- Test with Stripe CLI: `stripe listen --forward-to localhost:8000/webhooks/stripe`

### Getting Help

1. **Check documentation**: `docs/development/`
2. **Ask Claude**: Reference relevant `.claude/` files for context
3. **Check logs**: Backend terminal, browser console
4. **Test in isolation**: API endpoint, component, service
5. **Verify environment**: Check `.env` files

---

**Quick tip**: Keep this file open in a tab when working with Claude. Reference the relevant sections to give Claude context about your workflow and standards.
