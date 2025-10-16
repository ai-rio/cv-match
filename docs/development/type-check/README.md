# Type Checking Methodology - Bulk Fix Approach

**Purpose**: Systematic approach for identifying and fixing type errors in bulk
**Focus**: High-impact fixes using error classification and prioritization

---

## 🎯 Quick Start

```bash
# Check types
cd /home/carlos/projects/cv-match/frontend
bun run type-check  # Fast TypeScript type check only

cd /home/carlos/projects/cv-match/backend
docker compose exec backend python -m pytest  # Python type hints checked via tests

# Analyze errors
bun run type-check 2>&1 | grep "error TS" | wc -l  # Count TS errors
```

---

## 📊 Error Classification System

### Priority Levels

| Priority        | When to Fix   | Impact                  | Examples                        |
| --------------- | ------------- | ----------------------- | ------------------------------- |
| 🔴 **Critical** | Immediately   | Blocks builds           | Module not found, syntax errors |
| 🟡 **High**     | Within 1 day  | Affects multiple files  | Type mismatches in shared code  |
| 🟢 **Medium**   | Within 1 week | Local to file/component | Component prop types            |
| ⚪ **Low**      | Anytime       | Cosmetic                | Unused variables                |

---

## 🔧 Bulk Fixing Methodology

### Step 1: Count and Categorize (5 min)

```bash
# Get error count
bun run type-check 2>&1 | grep -E "error TS[0-9]+" | wc -l

# Group by error type
bun run type-check 2>&1 | grep -E "error TS[0-9]+" | \
  sed 's/.*error \(TS[0-9]*\).*/\1/' | sort | uniq -c | sort -nr
```

**Output example**:

```
45 TS2339  # Property does not exist
23 TS18047 # Possibly null/undefined
12 TS2345  # Argument not assignable
8  TS7006  # Implicit any
```

---

### Step 2: Prioritize by Impact (2 min)

**Critical** (Fix first):

- TS2307 - Cannot find module
- TS2304 - Cannot find name
- Build-blocking errors

**High Impact** (Fix second):

- TS2339 - Property does not exist on type
- TS2345 - Argument of type X not assignable to Y
- Errors in shared utilities/components

**Medium Impact** (Fix third):

- TS18047 - Object is possibly null/undefined
- TS2322 - Type X not assignable to type Y
- Component-specific errors

**Low Impact** (Fix last):

- TS7006 - Implicit 'any' parameter
- TS6133 - Declared but never used

---

### Step 3: Fix in Batches (Bulk approach)

#### Batch 1: Quick Wins (30 min)

Target: Simple, high-frequency errors

**Pattern: Null safety (TS18047)**

```typescript
// Before: Object is possibly 'null'
const email = user.email;

// Fix: Add null check
const email = user?.email ?? "unknown";
```

**Pattern: Type assertions (TS2339)**

```typescript
// Before: Property 'data' does not exist
const items = response.data;

// Fix: Type assertion (when you know the type)
const items = (response as { data: Item[] }).data;
```

**Count fixes**: `git diff | grep "^+" | wc -l`

---

#### Batch 2: Shared Code (1 hour)

Target: Types affecting multiple files

**Pattern: Interface updates**

```typescript
// Update interface once
interface ApiResponse<T> {
  data: T;
  error?: string;
  success: boolean;
}

// Use everywhere
const result: ApiResponse<User[]> = await fetchUsers();
```

**Verify**: Run build, count remaining errors

---

#### Batch 3: Component Props (1 hour)

Target: Component-specific errors

**Pattern: Props interface**

```typescript
interface ButtonProps {
  variant?: "primary" | "secondary";
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button({
  variant = "primary",
  onClick,
  children,
}: ButtonProps) {
  // Implementation
}
```

---

### Step 4: Verify Progress (5 min)

```bash
# Before fixes
echo "Before: X errors"

# After each batch
bun run type-check 2>&1 | grep "error TS" | wc -l
echo "After Batch 1: Y errors (X-Y fixed)"

# Track progress
echo "Progress: $((100 * Y / X))% remaining"
```

---

## 🚀 Speed Optimization Strategies

### 1. Use Global Find-Replace

For repeated patterns:

```bash
# Example: Add null checks to all `.email` accesses
find frontend/app -name "*.tsx" -exec sed -i 's/user\.email/user?.email ?? ""/g' {} +
```

### 2. Fix by File Impact

```bash
# Find files with most errors
bun run type-check 2>&1 | grep "error TS" | \
  cut -d'(' -f1 | sort | uniq -c | sort -nr | head -10
```

Focus on files with 5+ errors first.

### 3. Use TypeScript's `// @ts-expect-error`

For errors you'll fix later:

```typescript
// @ts-expect-error TODO: Fix type mismatch in next PR
const data = complexFunction(param);
```

---

## 📝 Common Patterns & Quick Fixes

### Pattern 1: Possibly Null/Undefined

```typescript
// Quick fix: Optional chaining + nullish coalescing
data?.field ?? defaultValue;
```

### Pattern 2: Union Type Issues

```typescript
// Quick fix: Type guard
if ("property" in object) {
  // TypeScript knows object has 'property' here
}
```

### Pattern 3: Any Parameters

```typescript
// Quick fix: Add basic type
function handler(event: React.FormEvent) {}
```

### Pattern 4: Missing Properties

```typescript
// Quick fix: Make property optional
interface User {
  email?: string; // Add ? if property might not exist
}
```

---

## 🎯 Success Metrics

Track your progress:

| Metric            | Target   | How to Measure             |
| ----------------- | -------- | -------------------------- |
| Error count       | < 50     | `grep "error TS" \| wc -l` |
| Critical errors   | 0        | Check build passes         |
| Files with errors | < 20%    | Count files with errors    |
| Time per batch    | < 1 hour | Track time spent           |

---

## 💡 Pro Tips

1. **Fix in order**: Critical → High → Medium → Low
2. **Batch similar errors**: Fix all TS2339 together
3. **Test after each batch**: Run build, ensure it works
4. **Commit frequently**: After each successful batch
5. **Document patterns**: For team consistency

---

## 🔄 Iterative Process

```
1. Count errors
2. Pick highest priority batch (5-10 errors)
3. Fix batch (30-60 min)
4. Run build
5. Count remaining errors
6. Repeat until target reached
```

**Goal**: Reduce errors by 50% per session

---

## 📋 Quick Reference

### Essential Commands

```bash
# Check types
bun run type-check

# Count errors
bun run type-check 2>&1 | grep "error TS" | wc -l

# Group errors
bun run type-check 2>&1 | grep "error TS" | \
  sed 's/.*\(TS[0-9]*\).*/\1/' | sort | uniq -c | sort -nr

# Find error in specific file
bun run type-check 2>&1 | grep "path/to/file.tsx"
```

### Priority Decision Tree

```
Is build broken? → Fix immediately (Critical)
   ↓ No
Affects shared code? → Fix today (High)
   ↓ No
Component-specific? → Fix this week (Medium)
   ↓ No
Cosmetic/warnings? → Fix anytime (Low)
```

---

## 🎉 Expected Results

After applying this methodology:

- ✅ Build passes without type errors
- ✅ 90% reduction in high-priority errors
- ✅ Reusable patterns established
- ✅ Team can maintain type safety

**Time investment**: 3-4 hours for typical codebase
**Long-term benefit**: Catch bugs early, better IDE support

---

_This methodology focuses on **rapid bulk fixing** through classification, prioritization, and batch processing._
