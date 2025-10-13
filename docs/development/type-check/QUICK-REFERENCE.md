# Type Check Quick Reference

## Commands Cheat Sheet

```bash
# Full type check (both frontend and backend)
bun run type-check

# Individual checks
bun run type-check:frontend           # TypeScript only
bun run type-check:backend            # Python only

# Error analysis (with detailed breakdown)
bun run type-check:errors             # Both
bun run type-check:errors:frontend    # Frontend only
bun run type-check:errors:backend     # Backend only

# Linting
bun run lint                          # Both
bun run lint:frontend                 # TypeScript/JavaScript
bun run lint:backend                  # Python with Ruff
bun run lint:fix                      # Auto-fix both
bun run lint:fix:backend              # Auto-fix Python only
```

---

## Quick Fixes by Error Type

### TypeScript

| Error Code                  | Quick Fix                           |
| --------------------------- | ----------------------------------- |
| **TS2339** Property missing | `obj?.property` or add to interface |
| **TS2345** Wrong argument   | Cast: `value as Type`               |
| **TS18047** Possibly null   | Add `!` or `??` operator            |
| **TS7006** Implicit any     | Add type: `(param: Type)`           |
| **TS2322** Type mismatch    | Cast or fix type                    |
| **TS2304** Name not found   | Import or install package           |

### Python

| Error Type                     | Quick Fix                                    |
| ------------------------------ | -------------------------------------------- |
| **reportArgumentType**         | Add None check or change type hint           |
| **reportOptionalMemberAccess** | `if value is not None:` check                |
| **reportMissingImports**       | `uv add package-name`                        |
| **reportGeneralTypeIssues**    | Add type hints: `def func(x: Type) -> Type:` |
| **reportUnboundVariable**      | Initialize before use                        |

---

## Common Patterns

### TypeScript - Null Safety

```typescript
// Optional chaining
const email = user?.profile?.email;

// Nullish coalescing
const name = user?.name ?? "Anonymous";

// Type guard
if (user !== null) {
  console.log(user.name); // Safe
}
```

### TypeScript - Type Assertions

```typescript
// Safe assertion after check
const value = getValue();
if (typeof value === "string") {
  const upper = value.toUpperCase(); // Safe
}

// Type casting (use sparingly)
const data = response as MyType;
```

### Python - Optional Handling

```python
from typing import Optional

# Function with optional return
def find_user(id: str) -> Optional[User]:
    user = db.query(User).first()
    if user is None:
        return None
    return user

# Using walrus operator
if (user := find_user(id)) is not None:
    print(user.email)
```

### Python - Type Hints

```python
# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Generics
def get_items() -> list[dict[str, Any]]:
    return []

# Pydantic models
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str | None = None  # Optional in Python 3.10+
```

---

## Error Priority

**Fix in this order:**

1. 🔴 **Critical** - Build failures, imports, unbound variables
2. 🟡 **High** - Type mismatches in core logic, null safety in routes
3. 🟢 **Medium** - Component types, parameter annotations
4. ⚪ **Low** - Unused variables, cosmetic issues

---

## Configuration Files

### Frontend: `apps/frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2017",
    "module": "esnext"
  }
}
```

### Backend: `apps/backend/pyrightconfig.json`

```json
{
  "typeCheckingMode": "standard",
  "pythonVersion": "3.12",
  "reportGeneralTypeIssues": true
}
```

---

## Troubleshooting

| Problem             | Solution                                |
| ------------------- | --------------------------------------- |
| Pyright not found   | `cd apps/backend && uv sync`            |
| False import errors | Add to `ignore` in pyrightconfig.json   |
| VSCode not checking | Install Pylance, set Python interpreter |
| Too many errors     | Start with one file, fix incrementally  |

---

## Daily Workflow

```bash
# 1. Before starting work
bun run type-check

# 2. During development (as needed)
bun run type-check:backend  # or :frontend

# 3. Before committing
bun run type-check:errors

# 4. If errors found
# - Fix critical errors first
# - Run type-check again
# - Commit when clean (or document why skipping)
```

---

## Resources

- **Full Docs**: `/docs/development/type-check/README.md`
- **Implementation**: `/docs/development/type-check/IMPLEMENTATION-SUMMARY.md`
- **TypeScript**: https://www.typescriptlang.org/docs/
- **Pyright**: https://github.com/microsoft/pyright
- **FastAPI**: https://fastapi.tiangolo.com/python-types/
- **Pydantic**: https://docs.pydantic.dev/

---

**Last Updated**: 2025-09-29
