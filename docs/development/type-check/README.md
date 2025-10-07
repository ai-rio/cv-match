# Type Checking Methodology

This document outlines the comprehensive type checking approach for the Resume-Matcher monorepo, covering both TypeScript (frontend) and Python (backend).

## Overview

Our type checking strategy ensures type safety across the entire stack:

- **Frontend**: TypeScript with `tsc` for Next.js 15+ application
- **Backend**: Python 3.12+ with Pyright for FastAPI application
- **Unified Interface**: Root-level scripts for checking both simultaneously

## Quick Start

```bash
# Check both frontend and backend
bun run type-check

# Check frontend only
bun run type-check:frontend

# Check backend only
bun run type-check:backend

# Analyze errors with detailed breakdown
bun run type-check:errors

# Analyze frontend errors only
bun run type-check:errors:frontend

# Analyze backend errors only
bun run type-check:errors:backend
```

## Methodology

Our approach follows a **high-impact, systematic methodology** that prioritizes fixes based on:

1. **Impact** - Errors that block builds or affect multiple files
2. **Frequency** - Most common error types first
3. **Complexity** - Simple fixes before complex refactoring
4. **Incremental Adoption** - Balanced strictness for gradual improvement

---

## TypeScript Error Classification

### By Error Code

| Error Code  | Description             | Priority | Strategy                                   |
| ----------- | ----------------------- | -------- | ------------------------------------------ |
| **TS2339**  | Property does not exist | High     | Type guards, assertions, interface updates |
| **TS2345**  | Argument not assignable | High     | Type casting, interface alignment          |
| **TS18047** | Possibly null/undefined | Medium   | Null assertions, optional chaining         |
| **TS7006**  | Implicit any parameter  | Low      | Explicit type annotations                  |
| **TS2322**  | Type not assignable     | Medium   | Type casting, interface updates            |
| **TS18046** | Possibly undefined      | Medium   | Default values, type guards                |
| **TS2304**  | Cannot find name        | High     | Import fixes, declaration files            |
| **TS2307**  | Cannot find module      | Critical | Module resolution, install deps            |

### By Impact Level

#### 🔴 Critical (Fix First)

- Build-blocking errors (TS2304, TS2307)
- Type generation failures
- Import/export issues
- Core infrastructure types

#### 🟡 High Impact (Fix Second)

- Errors affecting multiple files (TS2339, TS2345)
- Database relationship types
- Common utility functions
- Shared component interfaces

#### 🟢 Medium Impact (Fix Third)

- Component-specific errors (TS2322)
- Null safety issues (TS18047, TS18046)
- Parameter type annotations (TS7006)
- Local type mismatches

---

## Python Error Classification

### By Pyright Error Type

| Error Type                           | Description                     | Priority | Strategy                               |
| ------------------------------------ | ------------------------------- | -------- | -------------------------------------- |
| **reportGeneralTypeIssues**          | General type inconsistencies    | High     | Add type hints, fix type mismatches    |
| **reportOptionalMemberAccess**       | Accessing possibly None values  | High     | Add None checks, use Optional properly |
| **reportUnboundVariable**            | Variable used before assignment | Critical | Fix logic flow, add initialization     |
| **reportMissingImports**             | Import cannot be resolved       | Critical | Fix imports, install packages          |
| **reportIncompatibleMethodOverride** | Method override incompatible    | High     | Fix signatures, align with parent      |
| **reportPrivateImportUsage**         | Using private module exports    | Medium   | Use public APIs, refactor imports      |
| **reportOptionalCall**               | Calling possibly None function  | High     | Add None checks before calling         |
| **reportDeprecated**                 | Using deprecated features       | Low      | Update to modern APIs                  |

### By Impact Level

#### 🔴 Critical (Fix First)

- Unbound variables (runtime errors)
- Missing imports (import failures)
- Type generation failures
- Core infrastructure types

#### 🟡 High Impact (Fix Second)

- General type issues affecting logic
- Optional access without checks
- Method override incompatibilities
- Pydantic model validation errors

#### 🟢 Medium Impact (Fix Third)

- Private import usage
- Unused imports/variables
- Optional parameter issues
- Local type annotations

---

## Fixing Strategies

### TypeScript Patterns

#### 1. Type Assertions (Quick Wins)

```typescript
// Before: Property 'success' does not exist on union type
(result?.success !==
  false(
    // After: Use type assertion for complex unions
    result as any
  )?.success) !==
  false;

// Better: Use type narrowing
if (result && 'success' in result) {
  result.success !== false;
}
```

#### 2. Null Safety Patterns

```typescript
// Before: 'session' is possibly null
userId: session.user.id;

// After: Use null assertion after null check
userId: session!.user.id;

// Better: Handle null case
userId: session?.user.id ?? 'anonymous';
```

#### 3. Supabase Relationship Types

```typescript
// Before: Missing relationship types
subscriptions: {
  Row: {
    id: string
    price_id: string | null
  }
}

// After: Add optional relationship types
subscriptions: {
  Row: {
    id: string
    price_id: string | null
    // Relationships (optional for queries with joins)
    prices?: {
      id: string
      unit_amount: number | null
      products?: {
        name: string | null
      }
    }
  }
}
```

#### 4. Parameter Type Annotations

```typescript
// Before: Parameter 'price' implicitly has 'any' type
prices.map(price => ({ ... }))

// After: Explicit type annotation
prices.map((price: Price) => ({ ... }))

// Or: Use inference with proper types
prices.map((price) => ({
  id: price.id as string,
  amount: price.amount as number,
}))
```

### Python Patterns

#### 1. FastAPI Route Type Hints

```python
# Before: Missing type hints
@app.post("/optimize")
async def optimize_resume(resume, job_description):
    return {"status": "success"}

# After: Full type hints with Pydantic
from app.schemas.pydantic.resume import ResumeOptimizationRequest
from app.schemas.pydantic.resume import ResumeOptimizationResponse

@app.post("/optimize", response_model=ResumeOptimizationResponse)
async def optimize_resume(request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
    return ResumeOptimizationResponse(status="success")
```

#### 2. Pydantic Model Type Safety

```python
# Before: Missing field types
class User(BaseModel):
    id: int
    name = "John Doe"  # Type inferred but not explicit
    email = None  # Type unclear

# After: Explicit types with Optional
from typing import Optional

class User(BaseModel):
    id: int
    name: str = "John Doe"
    email: Optional[str] = None

# Python 3.10+: Use union syntax
class User(BaseModel):
    id: int
    name: str = "John Doe"
    email: str | None = None
```

#### 3. Optional Parameter Handling

```python
# Before: Not handling None case
def get_user_email(user_id: int) -> str:
    user = find_user(user_id)  # Returns Optional[User]
    return user.email  # Error: user is possibly None

# After: Proper None handling
def get_user_email(user_id: int) -> Optional[str]:
    user = find_user(user_id)
    if user is None:
        return None
    return user.email

# Or: Use walrus operator with type narrowing
def get_user_email(user_id: int) -> Optional[str]:
    if (user := find_user(user_id)) is not None:
        return user.email
    return None
```

#### 4. Generic Type Annotations

```python
# Before: Generic types without parameters
def get_items() -> list:
    return []

# After: Specific generic types
def get_items() -> list[dict[str, Any]]:
    return []

# Better: Use Pydantic models
from app.models.resume import Resume

def get_resumes() -> list[Resume]:
    return []
```

#### 5. Type Narrowing with TYPE_CHECKING

```python
# Use for type hints that are only needed for checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.models.user import User

def get_user(db: "Session", user_id: int) -> "User | None":
    return db.query(User).filter(User.id == user_id).first()
```

---

## Configuration Files

### TypeScript: `apps/frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,
    "noEmit": true,
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "moduleResolution": "bundler"
  }
}
```

Key settings:

- `strict: true` - Enables all strict type checking options
- `noEmit: true` - Only check types, don't generate files
- `moduleResolution: "bundler"` - Modern module resolution for Next.js

### Python: `apps/backend/pyrightconfig.json`

```json
{
  "typeCheckingMode": "standard",
  "pythonVersion": "3.12",
  "reportGeneralTypeIssues": true,
  "reportOptionalMemberAccess": true,
  "reportUnboundVariable": true,
  "reportMissingImports": true
}
```

Key settings:

- `typeCheckingMode: "standard"` - Balanced strictness for incremental adoption
- `reportGeneralTypeIssues: true` - Catch basic type errors
- `reportOptionalMemberAccess: true` - Enforce None checks
- `analyzeUnannotatedFunctions: true` - Check functions without type hints

---

## Tools and Commands

### Error Analysis

```bash
# Get comprehensive error analysis
bun run type-check:errors

# TypeScript error count
bun run type-check:frontend 2>&1 | grep -c "error TS" || echo "0"

# Python error count
bun run type-check:backend 2>&1 | grep -c "error:" || echo "0"

# TypeScript error breakdown by type
bun run type-check:frontend 2>&1 | grep -E "error TS[0-9]+" | \
  sed 's/.*error \(TS[0-9]*\).*/\1/' | sort | uniq -c | sort -nr

# Find specific TypeScript error type
bun run type-check:frontend 2>&1 | grep "TS2339" | head -5

# Find specific Python error type
bun run type-check:backend 2>&1 | grep "reportGeneralTypeIssues" | head -5
```

### File-Specific Checks

```bash
# Check specific TypeScript file
cd apps/frontend
bunx tsc --noEmit src/path/to/file.ts

# Check specific Python file
cd apps/backend
uv run pyright app/path/to/file.py

# Find related TypeScript files
find apps/frontend/src -name "*.ts" -o -name "*.tsx" | \
  xargs grep -l "problematic_type"

# Find related Python files
find apps/backend/app -name "*.py" | \
  xargs grep -l "problematic_type"
```

### Integration with Development

```bash
# Check before committing
bun run type-check

# Watch mode for TypeScript (in frontend directory)
cd apps/frontend
bun run type-check -- --watch

# Auto-fix some TypeScript issues with ts-migrate (install if needed)
# npx ts-migrate migrate .
```

---

## Common Patterns

### Frontend (TypeScript)

#### Next.js Page Components

```typescript
import { type Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Resume Optimizer',
  description: 'Optimize your resume for ATS',
}

interface PageProps {
  params: { id: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

export default async function Page({ params, searchParams }: PageProps) {
  // Type-safe implementation
  const id = params.id
  return <div>Resume {id}</div>
}
```

#### React Component Props

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  onClick
}: ButtonProps) {
  return (
    <button className={`btn-${variant} btn-${size}`} onClick={onClick}>
      {children}
    </button>
  )
}
```

#### Supabase Client Types

```typescript
import { createClient } from '@/lib/supabase/client';
import type { Database } from '@/types/supabase';

type Resume = Database['public']['Tables']['resumes']['Row'];
type ResumeInsert = Database['public']['Tables']['resumes']['Insert'];

async function getResume(id: string): Promise<Resume | null> {
  const supabase = createClient();
  const { data, error } = await supabase.from('resumes').select('*').eq('id', id).single();

  if (error) return null;
  return data;
}
```

### Backend (Python)

#### FastAPI Route Handlers

```python
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.pydantic.resume import (
    ResumeCreateRequest,
    ResumeResponse,
)
from app.services.resume_service import ResumeService
from app.core.dependencies import get_resume_service

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

@router.post("/", response_model=ResumeResponse)
async def create_resume(
    request: ResumeCreateRequest,
    service: ResumeService = Depends(get_resume_service),
) -> ResumeResponse:
    """Create a new resume with full type safety."""
    try:
        resume = await service.create(request)
        return ResumeResponse.from_orm(resume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Pydantic Models

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        return v

class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

#### Service Layer

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.schemas.pydantic.resume import ResumeCreateRequest

class ResumeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def create(self, request: ResumeCreateRequest) -> Resume:
        resume = Resume(**request.model_dump())
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def get_by_id(self, resume_id: str) -> Optional[Resume]:
        return self.db.query(Resume).filter(Resume.id == resume_id).first()

    async def list_by_user(self, user_id: str, limit: int = 10) -> List[Resume]:
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .limit(limit)
            .all()
        )
```

---

## Best Practices

### 1. Prioritize by Impact

- Fix build-blocking errors first (TS2307, unbound variables)
- Address high-frequency errors next (TS2339, reportGeneralTypeIssues)
- Leave cosmetic issues for last (unused variables)

### 2. Use Temporary Solutions Strategically

**TypeScript:**

- `any` type for complex union scenarios (document why)
- Type assertions for known-safe operations
- `// @ts-expect-error` with explanation for edge cases

**Python:**

- `type: ignore` comments with reason
- `Any` type for truly dynamic data
- Gradual typing for legacy code

### 3. Maintain Momentum

- Fix errors in batches of 5-10
- Run `bun run type-check` frequently
- Use `bun run type-check:errors` for progress tracking
- Document patterns for team consistency

### 4. Balance Speed vs. Quality

- Quick fixes for development velocity
- Proper types for long-term maintainability
- Refactor incrementally as understanding improves
- Use strict mode for new files only initially

### 5. Leverage Tools

**TypeScript:**

- VSCode IntelliSense for type hints
- ESLint with TypeScript rules
- Prettier for formatting
- ts-migrate for bulk migrations

**Python:**

- Pyright VSCode extension
- Ruff for linting and formatting
- mypy for additional checking (if needed)
- pydantic for runtime validation

---

## Integration with CI/CD

### Pre-commit Hook

Add to `.husky/pre-commit`:

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run type checks
bun run type-check || {
  echo "❌ Type check failed. Fix errors before committing."
  exit 1
}
```

### GitHub Actions

Add to `.github/workflows/type-check.yml`:

```yaml
name: Type Check

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  type-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: bun install

      - name: Type check frontend
        run: bun run type-check:frontend

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install UV
        run: pip install uv

      - name: Type check backend
        run: bun run type-check:backend

      - name: Generate error report
        if: failure()
        run: bun run type-check:errors
```

---

## Troubleshooting

### TypeScript Issues

**Issue**: `Cannot find module '@/...'`

```bash
# Solution: Check tsconfig.json paths
{
  "paths": {
    "@/*": ["./*"]
  }
}
```

**Issue**: `Property does not exist on type 'never'`

```typescript
// Solution: Initialize with proper type
const [state, setState] = useState<MyType[]>([]); // Not: useState([])
```

**Issue**: Module not found after installation

```bash
# Solution: Restart TypeScript server in VSCode
# Cmd/Ctrl + Shift + P -> "TypeScript: Restart TS Server"
```

### Python Issues

**Issue**: `Import could not be resolved`

```bash
# Solution: Install dependencies
cd apps/backend
uv sync

# Or: Check pyrightconfig.json venv settings
{
  "venvPath": ".",
  "venv": ".venv"
}
```

**Issue**: `reportGeneralTypeIssues` everywhere

```python
# Solution: Add type hints incrementally
# Start with function signatures
def process_resume(data: dict[str, Any]) -> Resume:
    ...
```

**Issue**: Pyright not finding packages

```bash
# Solution: Ensure virtual environment is activated
cd apps/backend
source .venv/bin/activate  # Unix
# or
.venv\Scripts\activate  # Windows

# Reinstall with UV
uv sync
```

---

## Monorepo-Specific Considerations

### Shared Types Between Frontend and Backend

Consider creating a shared types package:

```bash
# Future enhancement
packages/
  shared-types/
    src/
      resume.ts
      job.ts
```

Use code generation to keep types in sync:

- Generate TypeScript types from Pydantic models
- Use tools like `pydantic-to-typescript`

### Cross-Stack Type Safety

When frontend calls backend:

```typescript
// Frontend API client with typed responses
import type { ResumeResponse } from '@/types/api';

async function getResume(id: string): Promise<ResumeResponse> {
  const response = await fetch(`/api/v1/resumes/${id}`);
  return response.json(); // Type-safe
}
```

```python
# Backend ensures response matches TypeScript expectations
from app.schemas.pydantic.resume import ResumeResponse

@router.get("/{id}", response_model=ResumeResponse)
async def get_resume(id: str) -> ResumeResponse:
    # FastAPI validates response matches schema
    ...
```

---

## Quick Reference

### Error Priority Matrix

| Error Type                     | Priority    | Fix Time  | Impact |
| ------------------------------ | ----------- | --------- | ------ |
| Build-blocking                 | 🔴 Critical | Immediate | High   |
| Type mismatches in core logic  | 🔴 Critical | < 1 day   | High   |
| Null safety in routes/services | 🟡 High     | < 2 days  | Medium |
| Missing type annotations       | 🟡 High     | < 3 days  | Medium |
| Component prop types           | 🟢 Medium   | < 1 week  | Low    |
| Unused variables               | 🟢 Low      | Anytime   | Low    |

### Commands Cheat Sheet

```bash
# Full checks
bun run type-check                    # Both frontend and backend
bun run type-check:errors             # With detailed analysis

# Individual checks
bun run type-check:frontend           # TypeScript only
bun run type-check:backend            # Python only

# Error analysis
bun run type-check:errors:frontend    # TS error breakdown
bun run type-check:errors:backend     # Python error breakdown

# During development
cd apps/frontend && bun run type-check    # Quick frontend check
cd apps/backend && uv run pyright         # Quick backend check
```

---

## Additional Resources

### TypeScript

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- [Next.js TypeScript](https://nextjs.org/docs/app/building-your-application/configuring/typescript)

### Python

- [Pyright Documentation](https://github.com/microsoft/pyright/blob/main/docs/configuration.md)
- [FastAPI Type Hints](https://fastapi.tiangolo.com/python-types/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

### Monorepo

- [Monorepo Type Safety](https://turbo.build/repo/docs/handbook/linting/typescript)
- [Shared Types in Monorepos](https://vercel.com/blog/turborepo-typescript-shared-packages)

---

_This methodology provides a systematic approach for type checking across the entire Resume-Matcher stack while maintaining development velocity and code quality._
