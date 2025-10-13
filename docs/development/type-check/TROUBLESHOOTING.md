# Type Checking Troubleshooting Guide

**Purpose**: Comprehensive guide for resolving common type errors in CV-Match Brazilian SaaS platform
**Focus**: Practical solutions for TypeScript and Python type issues

---

## 🚨 Critical Errors (Block Builds)

### TypeScript TS2307: Cannot find module

**Problem**: Module or type declaration not found

```typescript
// ❌ Error
import { SomeType } from 'missing-module';

// ✅ Solutions:
// 1. Install missing dependency
bun add missing-module

// 2. Add type declaration
declare module 'missing-module';

// 3. Check import path
import { SomeType } from './correct-path';
```

### TypeScript TS2304: Cannot find name

**Problem**: Variable, function, or type not defined

```typescript
// ❌ Error
const result = undefinedVariable;

// ✅ Solutions:
// 1. Define the variable
const undefinedVariable = 'value';

// 2. Import the variable
import { undefinedVariable } from './module';

// 3. Use type assertion
const result = (window as any).undefinedVariable;
```

### Python: Name not defined

**Problem**: Variable or function used before definition

```python
# ❌ Error
result = undefined_variable

# ✅ Solutions:
# 1. Define the variable
undefined_variable = "value"
result = undefined_variable

# 2. Import the variable
from module import undefined_variable
result = undefined_variable

# 3. Add type annotation
undefined_variable: str = "value"
```

---

## ⚠️ High Priority Errors

### TypeScript TS2339: Property does not exist on type

**Problem**: Accessing property that doesn't exist in type definition

```typescript
// ❌ Error
interface User {
  name: string;
}
const user: User = { name: "John" };
console.log(user.email); // Property 'email' does not exist

// ✅ Solutions:
// 1. Add property to interface
interface User {
  name: string;
  email?: string; // Optional property
}

// 2. Use optional chaining
console.log(user?.email);

// 3. Type assertion (when you know it exists)
console.log((user as any).email);

// 4. Extend interface
interface UserWithEmail extends User {
  email: string;
}
```

### TypeScript TS2345: Argument not assignable

**Problem**: Type mismatch in function arguments

```typescript
// ❌ Error
function processUser(user: { id: number; name: string }) {}
processUser({ id: "123", name: "John" }); // id should be number

// ✅ Solutions:
// 1. Fix the type
processUser({ id: 123, name: "John" });

// 2. Use type assertion
processUser({ id: "123" as any, name: "John" });

// 3. Make function more flexible
function processUser(user: { id: number | string; name: string }) {}
```

### Python: Incompatible types

**Problem**: Type mismatch in function calls or assignments

```python
# ❌ Error
def process_user(user_id: int, name: str) -> str:
    return f"{name}: {user_id}"

result = process_user("123", "John")  # user_id should be int

# ✅ Solutions:
# 1. Fix the type
result = process_user(123, "John")

# 2. Use Union type
def process_user(user_id: int | str, name: str) -> str:
    return f"{name}: {user_id}"

# 3. Add type conversion
result = process_user(int("123"), "John")
```

---

## 🔄 Medium Priority Errors

### TypeScript TS18047: Object is possibly null/undefined

**Problem**: Potential null/undefined access

```typescript
// ❌ Error
const user: User | null = getUser();
console.log(user.name); // user might be null

// ✅ Solutions:
// 1. Null check
if (user) {
  console.log(user.name);
}

// 2. Optional chaining
console.log(user?.name);

// 3. Nullish coalescing
const userName = user?.name ?? "Unknown";

// 4. Type assertion (when you know it's not null)
console.log((user!).name);

// 5. Non-null assertion operator
console.log(user!.name);
```

### TypeScript TS2322: Type not assignable

**Problem**: Type mismatch in assignment

```typescript
// ❌ Error
let value: string = 123; // Type 'number' not assignable to 'string'

// ✅ Solutions:
// 1. Fix the type
let value: string = "123";

// 2. Change the variable type
let value: number | string = 123;

// 3. Type conversion
let value: string = String(123);

// 4. Use generic type
let value = 123 as any;
```

### Python: Item has no attribute

**Problem**: Accessing attribute that doesn't exist on type

```python
# ❌ Error
class User:
    def __init__(self, name: str):
        self.name = name

user = User("John")
print(user.email)  # User has no attribute 'email'

# ✅ Solutions:
# 1. Add attribute to class
class User:
    def __init__(self, name: str, email: str = ""):
        self.name = name
        self.email = email

# 2. Use Optional type
from typing import Optional
class User:
    def __init__(self, name: str):
        self.name = name
        self.email: Optional[str] = None

# 3. Use hasattr check
if hasattr(user, 'email'):
    print(user.email)
```

---

## 🔧 Low Priority Errors

### TypeScript TS7006: Implicit 'any' parameter

**Problem**: Function parameter missing type annotation

```typescript
// ❌ Error
function processData(data) { // Parameter 'data' implicitly has 'any' type
  return data.length;
}

// ✅ Solutions:
// 1. Add type annotation
function processData(data: any[]) {
  return data.length;
}

// 2. Use generic type
function processData<T extends { length: number }>(data: T) {
  return data.length;
}

// 3. Use interface
interface DataContainer {
  length: number;
}
function processData(data: DataContainer) {
  return data.length;
}
```

### TypeScript TS6133: Declared but never used

**Problem**: Variable declared but not used

```typescript
// ❌ Error
const unusedVariable = "value"; // 'unusedVariable' is declared but never used

// ✅ Solutions:
// 1. Use the variable
console.log(unusedVariable);

// 2. Remove the variable
// const unusedVariable = "value";

// 3. Use underscore prefix (convention for unused)
const _unusedVariable = "value";

// 4. Add type-only import
import type { UnusedType } from './module';
```

---

## 🇧🇷 Brazilian Market Type Issues

### BRL Currency Types

```typescript
// ❌ Missing BRL currency types
interface Payment {
  amount: number; // Should be BRL-specific
  currency: string; // Too generic
}

// ✅ Brazilian-specific types
interface BRLPayment {
  amount: number; // In centavos (integers)
  currency: 'BRL';
  formattedAmount: string; // "R$ 1.234,56"
}

// Helper type for BRL values
type BRLAmount = number & { readonly __brand: 'BRL' };

function createBRLAmount(value: number): BRLAmount {
  return Math.round(value * 100) as BRLAmount;
}
```

### PT-BR Translation Types

```typescript
// ❌ Generic translation types
interface Translations {
  [key: string]: string;
}

// ✅ PT-BR specific types
interface PTBRTranslations {
  'payment.amount': string;
  'payment.method.pix': string;
  'payment.method.boleto': string;
  'user.cpf.invalid': string;
  'user.cnpj.invalid': string;
}

// Type-safe translation keys
type PTBRTranslationKey = keyof PTBRTranslations;

function getTranslation(key: PTBRTranslationKey): string {
  return translations[key];
}
```

### Brazilian Document Types

```typescript
// ✅ Brazilian CPF/CNPJ types
interface CPF {
  value: string;
  formatted: string; // "123.456.789-01"
  isValid: boolean;
}

interface CNPJ {
  value: string;
  formatted: string; // "12.345.678/0001-90"
  isValid: boolean;
}

type BrazilianDocument = CPF | CNPJ;

function validateBrazilianDocument(doc: BrazilianDocument): boolean {
  return doc.isValid;
}
```

---

## 🛠️ Common Fix Patterns

### Pattern 1: Add Optional Chaining

```typescript
// Before
const userEmail = user.profile.email;

// After
const userEmail = user?.profile?.email ?? 'no-email@example.com';
```

### Pattern 2: Use Type Guards

```typescript
// Before
function processValue(value: string | number) {
  return value.toUpperCase(); // Error on number
}

// After
function processValue(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return value.toString().toUpperCase();
}
```

### Pattern 3: Create Union Types

```typescript
// Before
interface ApiResponse {
  data: any; // Too generic
  error: any;
}

// After
type ApiSuccess<T> = {
  data: T;
  error: null;
};

type ApiError = {
  data: null;
  error: string;
};

type ApiResponse<T> = ApiSuccess<T> | ApiError;
```

### Pattern 4: Brazilian Market Types

```typescript
// Generic payment type
interface Payment {
  amount: number;
  currency: string;
}

// Brazilian-specific payment
interface BrazilianPayment extends Payment {
  currency: 'BRL';
  amountInCentavos: number;
  paymentMethod: 'pix' | 'boleto' | 'credit_card';
  installments?: number;
}
```

---

## 🚀 Quick Fix Commands

### TypeScript Bulk Fixes

```bash
# Fix common patterns
find frontend -name "*.ts" -o -name "*.tsx" | xargs sed -i 's/\.email/?.email ?? ""/g'

# Add optional chaining
find frontend -name "*.ts" -o -name "*.tsx" | xargs sed -i 's/\([a-zA-Z_]\+\)\.\([a-zA-Z_]\+\)/\1?.\2/g'

# Fix type assertions
find frontend -name "*.ts" -o -name "*.tsx" | xargs sed -i 's/as unknown as/as/g'
```

### Python Bulk Fixes

```bash
# Add type imports
find backend -name "*.py" -exec grep -l "def.*:" {} \; | xargs sed -i '1i from typing import Any, List, Dict, Optional'

# Add function type annotations
find backend -name "*.py" -exec sed -i 's/def \([a-zA-Z_]\+\)(\([^)]*\)):/def \1(\2: Any) -> Any:/g' {} \;
```

---

## 📊 Type Safety Monitoring

### Generate Type Safety Report

```bash
# Run comprehensive analysis
bun run type-safety:report

# Check specific priority levels
bun run type-fix:critical -- --dry-run
bun run type-fix:high -- --dry-run
bun run type-fix:medium -- --dry-run
bun run type-fix:low -- --dry-run
```

### Track Progress

```bash
# Before fixes
bun run type-analysis
# Note: Critical: 5, High: 23, Medium: 45, Low: 67

# After fixes
bun run type-analysis
# Note: Critical: 0, High: 5, Medium: 12, Low: 25
# Improvement: 73% reduction in errors
```

---

## 🎯 Best Practices

### Prevention

1. **Enable strict mode** in TypeScript configuration
2. **Use `unknown` instead of `any`** for better type safety
3. **Add type annotations** to all function parameters
4. **Create interfaces** for data structures
5. **Use type guards** for union types
6. **Validate Brazilian market types** regularly

### Code Review Checklist

- [ ] No critical type errors
- [ ] High priority errors under threshold
- [ ] Brazilian-specific types defined
- [ ] Type safety score above 80%
- [ ] Optional chaining used for nullable values
- [ ] Type guards implemented for union types

---

## 📞 Getting Help

### Internal Resources

- **Type checking methodology**: `/docs/development/type-check/README.md`
- **Automation script**: `./scripts/type-fix-automation.sh`
- **GitHub Actions**: `.github/workflows/type-checking-automation.yml`

### External Resources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)

---

## ✨ Summary

This troubleshooting guide provides:

- ✅ **Solutions for all error priority levels**
- ✅ **Brazilian market-specific type patterns**
- ✅ **Quick fix commands and automation**
- ✅ **Type safety monitoring and tracking**
- ✅ **Best practices for prevention**

Use this guide alongside the automated type checking system to maintain high code quality in the CV-Match Brazilian SaaS platform.