# 🛠️ Agent Tools Guide - P1.5 Subscription System

**CRITICAL**: All agents MUST use these tools when appropriate. Don't reinvent the wheel!

---

## 🎯 Required Tools by Agent Type

### Backend Specialist Tools

#### 1. Context7 - Library Documentation
**When to use**: Before implementing ANY library integration
**How to use**:
```bash
# Step 1: Resolve library ID
context7:resolve-library-id --library-name="stripe"

# Step 2: Get documentation
context7:get-library-docs --library-id="/stripe/stripe-python" --topic="subscriptions"
```

**Use cases**:
- Stripe subscription creation → Search "stripe subscriptions python"
- FastAPI endpoints → Search "fastapi router dependencies"
- Pydantic models → Search "pydantic dataclass validation"
- Supabase queries → Search "supabase python client"

**Example**:
```python
# WRONG: Guessing Stripe API
stripe.create_subscription(...)  # ❌ Guessing

# RIGHT: Use Context7 first
# 1. context7:get-library-docs --library-id="/stripe/stripe-python" --topic="create subscription"
# 2. Read the docs
# 3. Implement correctly:
stripe.Subscription.create(
    customer=customer_id,
    items=[{"price": price_id}],
    metadata={"user_id": user_id}
)  # ✅ From documentation
```

#### 2. Python Environment Tools
**When to use**: Testing imports, running verification scripts

```bash
# Test imports
docker compose exec backend python -c "from app.config.pricing import pricing_config; print(pricing_config.get_subscription_tiers())"

# Run tests
docker compose exec backend pytest tests/unit/test_pricing.py -v

# Check type hints
docker compose exec backend mypy app/config/pricing.py
```

#### 3. Database Tools
**When to use**: Creating migrations, testing queries

```bash
# Create migration
supabase migration new add_subscription_fields

# Test query
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()
result = client.table('subscriptions').select('*').limit(5).execute()
print(result.data)
"
```

---

### Frontend Specialist Tools

#### 1. Shadcn/ui - UI Components
**When to use**: Building ANY UI component
**How to use**:

```bash
# Install component
cd frontend
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add dialog
```

**Use cases**:
- Subscription cards → Use `Card`, `CardHeader`, `CardContent`
- Pricing tiers → Use `Tabs` for Flex/Flow switching
- Popular badge → Use `Badge` component
- Subscribe button → Use `Button` with variants
- Cancel dialog → Use `Dialog`, `AlertDialog`

**Example**:
```tsx
// WRONG: Creating custom card from scratch
<div className="border rounded p-4">  // ❌ Don't do this

// RIGHT: Use Shadcn Card
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
<Card>
  <CardHeader>
    <CardTitle>Flow Pro</CardTitle>
  </CardHeader>
  <CardContent>...</CardContent>
</Card>  // ✅ Use Shadcn
```

#### 2. Shadcn Blocks - Pre-built Sections
**When to use**: Need common UI patterns
**Where to find**: https://ui.shadcn.com/blocks

**Available blocks**:
- Pricing sections → Use pricing block
- Dashboard layouts → Use dashboard block
- Authentication forms → Use auth block
- Settings pages → Use settings block

**How to copy**:
1. Go to https://ui.shadcn.com/blocks
2. Find "Pricing" or relevant block
3. Copy the code
4. Adapt for your needs

#### 3. Chrome DevTools
**When to use**: Debugging, testing, validation
**How to use**:

```javascript
// In browser console:

// Test API call
fetch('/api/payments/pricing')
  .then(r => r.json())
  .then(console.log)

// Test authentication
localStorage.getItem('supabase.auth.token')

// Debug component state
// In React DevTools: Select component → See state/props

// Test Stripe integration
// Network tab → Filter "stripe" → Check requests
```

**Use for**:
- Network requests (check API calls)
- Console errors (catch runtime errors)
- React DevTools (inspect component state)
- Performance profiling
- Responsive design testing

#### 4. Context7 - Library Documentation
**When to use**: Using any frontend library

```bash
# Next.js
context7:get-library-docs --library-id="/vercel/next.js" --topic="app router"

# React
context7:get-library-docs --library-id="/facebook/react" --topic="hooks"

# Stripe.js
context7:get-library-docs --library-id="/stripe/stripe-js" --topic="payment elements"
```

#### 5. Browser Testing
**When to use**: Validating UI works correctly

```bash
# Start dev server
cd frontend
bun run dev

# Open in browser
# http://localhost:3000/pt-br/pricing

# Test checklist:
# □ All tiers display correctly
# □ Buttons work
# □ Forms validate
# □ Responsive on mobile
# □ Portuguese text correct
# □ Stripe checkout opens
```

---

### Database Architect Tools

#### 1. Supabase Studio
**When to use**: Viewing data, testing queries
**How to access**: http://localhost:54323

**Use for**:
- View table schemas
- Test SQL queries
- Check RLS policies
- Inspect data
- Test migrations

#### 2. Migration Tools
```bash
# Create migration
supabase migration new description

# Test migration
supabase db reset

# Apply migration
supabase db push
```

#### 3. PostgreSQL Tools
```bash
# Connect to DB
supabase db remote psql

# Test query
psql -h localhost -p 54322 -U postgres -d postgres -c "SELECT * FROM subscriptions LIMIT 5;"

# Check table structure
\d subscriptions
```

---

### Test Writer Tools

#### 1. Pytest Tools
```bash
# Run specific test
docker compose exec backend pytest tests/unit/test_pricing.py -v

# Run with coverage
docker compose exec backend pytest --cov=app tests/

# Run specific test function
docker compose exec backend pytest tests/unit/test_pricing.py::test_subscription_tiers -v

# Debug test
docker compose exec backend pytest tests/unit/test_pricing.py -v -s --pdb
```

#### 2. Testing Libraries
**Use Context7 to understand**:
```bash
# Pytest
context7:get-library-docs --library-id="/pytest-dev/pytest" --topic="fixtures"

# Pytest-asyncio
context7:get-library-docs --library-id="/pytest-dev/pytest-asyncio" --topic="async tests"

# FastAPI TestClient
context7:get-library-docs --library-id="/tiangolo/fastapi" --topic="testing"
```

#### 3. Mock Tools
```python
# Use unittest.mock for mocking
from unittest.mock import Mock, patch, AsyncMock

# Mock Stripe API
with patch('app.services.stripe_service.stripe.Subscription.create') as mock_create:
    mock_create.return_value = {"id": "sub_123", "status": "active"}
    result = await create_subscription(...)
```

---

## 🎯 Tool Usage Workflow

### Before Starting ANY Task:

1. **Identify Required Libraries**
   ```
   Task: Create subscription endpoint
   Libraries: FastAPI, Stripe, Pydantic
   ```

2. **Use Context7 for Documentation**
   ```bash
   context7:resolve-library-id --library-name="stripe"
   context7:get-library-docs --library-id="/stripe/stripe-python" --topic="subscriptions"
   ```

3. **Use Existing Components**
   - Frontend: Check Shadcn/ui first
   - Backend: Check existing services
   - Database: Check existing patterns

4. **Test As You Build**
   - Backend: Use Python REPL tests
   - Frontend: Use browser + DevTools
   - Database: Use Supabase Studio

5. **Verify Before Committing**
   - Run tests
   - Check types
   - Test in browser
   - Verify API calls

---

## 🚨 CRITICAL Rules

### ❌ DON'T:
- ❌ Guess library APIs - USE Context7
- ❌ Create UI from scratch - USE Shadcn
- ❌ Skip testing - USE test tools
- ❌ Ignore errors - USE debugging tools
- ❌ Copy-paste without understanding - USE docs

### ✅ DO:
- ✅ Always check Context7 first
- ✅ Use Shadcn for all UI components
- ✅ Test with Chrome DevTools
- ✅ Verify with actual tools
- ✅ Read documentation before implementing
- ✅ Use existing patterns
- ✅ Test incrementally

---

## 📋 Tool Checklist by Phase

### Phase 1: Backend Services
- [ ] Context7: Stripe Python docs
- [ ] Context7: FastAPI docs
- [ ] Context7: Pydantic docs
- [ ] Python REPL for testing
- [ ] Type checker (mypy)

### Phase 2: Database
- [ ] Supabase Studio for schema
- [ ] Migration tools
- [ ] PostgreSQL CLI for testing
- [ ] Context7: Supabase docs

### Phase 3: API Endpoints
- [ ] Context7: FastAPI router docs
- [ ] Context7: Stripe webhook docs
- [ ] Pytest for testing
- [ ] Python REPL for verification

### Phase 4: Frontend
- [ ] Shadcn/ui components
- [ ] Shadcn blocks (pricing)
- [ ] Chrome DevTools
- [ ] React DevTools
- [ ] Context7: Next.js docs
- [ ] Context7: React docs
- [ ] Browser testing

### Phase 5: Testing
- [ ] Pytest
- [ ] Coverage tools
- [ ] Mock tools
- [ ] Chrome DevTools for E2E

---

## 🎓 Examples

### Example 1: Creating Subscription Endpoint

```python
# ❌ WRONG WAY - Guessing
@router.post("/subscribe")
async def subscribe(tier: str):
    subscription = stripe.create_subscription(tier)  # Wrong API!
    return subscription

# ✅ RIGHT WAY - Using Context7
# 1. context7:get-library-docs --library-id="/stripe/stripe-python" --topic="create subscription"
# 2. Read the actual API
# 3. Implement correctly:

@router.post("/subscribe")
async def create_subscription(
    tier: str,
    current_user: dict = Depends(get_current_user)
):
    # From Stripe docs via Context7:
    subscription = stripe.Subscription.create(
        customer=current_user["stripe_customer_id"],
        items=[{
            "price": pricing_config.get_tier(tier).stripe_price_id
        }],
        metadata={
            "user_id": current_user["id"],
            "tier": tier
        }
    )
    return subscription
```

### Example 2: Creating Pricing UI

```tsx
// ❌ WRONG WAY - Custom everything
<div className="border-2 rounded-lg p-6 shadow-md">
  <h3 className="text-2xl font-bold">Flow Pro</h3>
  <p className="text-gray-600">R$ 49,90/mês</p>
  <button className="bg-blue-500 text-white px-4 py-2 rounded">
    Assinar
  </button>
</div>

// ✅ RIGHT WAY - Using Shadcn components
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

<Card>
  <CardHeader>
    <div className="flex justify-between items-start">
      <CardTitle>Flow Pro</CardTitle>
      <Badge variant="secondary">Popular</Badge>
    </div>
    <CardDescription>
      Para quem busca muitas oportunidades
    </CardDescription>
  </CardHeader>
  <CardContent>
    <div className="text-3xl font-bold">
      R$ 49,90<span className="text-sm font-normal">/mês</span>
    </div>
  </CardContent>
  <CardFooter>
    <Button className="w-full">Assinar Agora</Button>
  </CardFooter>
</Card>
```

### Example 3: Testing with Tools

```python
# Use pytest with proper fixtures
import pytest
from app.config.pricing import pricing_config

def test_flow_pro_subscription():
    # Test subscription tier exists
    tier = pricing_config.get_tier("flow_pro")
    assert tier is not None
    assert tier.is_subscription == True
    
    # Test pricing
    assert tier.price == 4990  # R$ 49,90 in cents
    
    # Test analyses limit
    assert tier.analyses_per_month == 60
    
    # Test rollover
    assert tier.rollover_limit == 30

# Run with: docker compose exec backend pytest tests/unit/test_pricing.py::test_flow_pro_subscription -v
```

---

## 🎯 Success Criteria

Agent successfully uses tools when:
- [ ] Context7 consulted before implementing library code
- [ ] Shadcn components used for all UI
- [ ] Chrome DevTools used for debugging
- [ ] Tests written and passing
- [ ] Documentation followed, not guessed
- [ ] Existing patterns reused
- [ ] Tools mentioned in commit message

---

**Remember**: Tools exist to make you faster and produce better code. USE THEM! 🛠️
