# 07 - Dashboard Implementation

**Agent**: `frontend-specialist`
**Phase**: 4
**Duration**: 4h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement stats and credit counter using Kokonut UI components following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Install and configure Kokonut UI components for dashboard
3. Implement dashboard stats with animated counters
4. Apply theme styling
5. Test responsive behavior
6. Verify accessibility

---

## 📚 Reference

- [Design System](../../design-system/README.md)
- [Wireframes](../../design-system/wireframes.md)
- [Components](../../design-system/components.md)
- [Kokonut UI Installation](04-kokonut-installation.md)
- [Kokonut UI Migration Guide](_design-reference/KOKONUT-UI-MIGRATION-GUIDE.md)

---

## 🛠️ Implementation Steps

### 1. Component Installation

```bash
# Install required Kokonut UI components for dashboard
bunx shadcn@latest add @kokonutui/card-flip
bunx shadcn@latest add @kokonutui/shimmer-text
bunx shadcn@latest add @kokonutui/type-writer

# Verify installation
ls frontend/components/ui/card-flip.tsx
ls frontend/components/ui/shimmer-text.tsx
ls frontend/components/ui/type-writer.tsx
```

### 2. Dashboard Stats Implementation

Create animated dashboard stats components:

```typescript
// frontend/components/dashboard/stats-card.tsx
import { CardFlip } from '@/components/ui/card-flip';
import { ShimmerText } from '@/components/ui/shimmer-text';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StatsCardProps {
  title: string;
  value: string | number;
  description: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
}

export function StatsCard({ title, value, description, trend, icon }: StatsCardProps) {
  return (
    <CardFlip
      frontContent={
        <Card className="h-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            {icon}
          </CardHeader>
          <CardContent>
            <ShimmerText className="text-2xl font-bold">
              {value}
            </ShimmerText>
            <p className="text-xs text-muted-foreground">
              {description}
            </p>
          </CardContent>
        </Card>
      }
      backContent={
        <Card className="h-full">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm space-y-2">
              <p>View detailed analytics and trends for {title.toLowerCase()}</p>
              <button className="text-primary text-sm hover:underline">
                View Full Report →
              </button>
            </div>
          </CardContent>
        </Card>
      }
    />
  );
}
```

### 3. Credit Counter Implementation

Create an animated credit counter:

```typescript
// frontend/components/dashboard/credit-counter.tsx
import { TypeWriter } from '@/components/ui/type-writer';
import { ParticleButton } from '@/components/ui/particle-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface CreditCounterProps {
  credits: number;
  onAddCredits: () => void;
}

export function CreditCounter({ credits, onAddCredits }: CreditCounterProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Credit Balance</span>
          <ParticleButton onClick={onAddCredits} size="sm">
            Add Credits
          </ParticleButton>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center py-4">
          <TypeWriter
            text={`${credits} credits`}
            className="text-4xl font-bold text-primary"
            speed={50}
          />
          <p className="text-sm text-muted-foreground mt-2">
            Credits available for CV optimization
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 4. Dashboard Integration

Update the dashboard page to use the new components:

```typescript
// frontend/app/[locale]/dashboard/page.tsx
import { StatsCard } from '@/components/dashboard/stats-card';
import { CreditCounter } from '@/components/dashboard/credit-counter';

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Optimizations"
          value="24"
          description="+2 from last month"
          trend="up"
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <StatsCard
          title="Success Rate"
          value="87%"
          description="+5% improvement"
          trend="up"
          icon={<Target className="h-4 w-4" />}
        />
        <StatsCard
          title="Active Jobs"
          value="12"
          description="3 new this week"
          trend="up"
          icon={<Briefcase className="h-4 w-4" />}
        />
        <StatsCard
          title="Profile Views"
          value="156"
          description="-2 from last week"
          trend="down"
          icon={<Eye className="h-4 w-4" />}
        />
      </div>
      
      <CreditCounter credits={50} onAddCredits={() => {}} />
      
      {/* Other dashboard content */}
    </div>
  );
}
```

---

## 🎨 Component Mapping

| Original Component | Kokonut UI Component | Usage |
|-------------------|----------------------|-------|
| 3D-Card-Hover | card-flip | Interactive stats cards |
| Text Reveal | shimmer-text, type-writer | Animated text for stats and credits |
| Moving Border | particle-button | Add credits button |

---

## 🔍 Type Checking Integration

### Post-Implementation Type Check Instructions

After implementing the dashboard components and stats, perform comprehensive type checking to ensure type safety across all dashboard-related code.

### Phase-Specific Type Validation Commands

Execute the following commands in sequence to validate types:

```bash
# Run the project's type check script
bun run type-check

# Strict type checking for dashboard app routes
npx tsc --noEmit src/app/dashboard/**/*.tsx --strict

# Strict type checking for dashboard components
npx tsc --noEmit src/components/dashboard/**/*.tsx --strict

# Type validation for Kokonut UI components
npx tsc --noEmit src/components/ui/kokonutui/**/*.tsx --strict

# Type validation for dashboard-specific types
npx tsc --noEmit src/types/dashboard.ts --strict
```

### Type Validation Checklist

- [ ] All dashboard app routes compile without type errors
- [ ] Dashboard components have proper prop types
- [ ] Dashboard type definitions are complete and accurate
- [ ] Stats and credit counter data flow is properly typed
- [ ] API responses match expected type interfaces
- [ ] State management hooks maintain type safety
- [ ] Kokonut UI components integrate without type conflicts

### Type Error Resolution Guidance

If encountering type errors:

1. **Missing Type Definitions**: Add missing interfaces to `src/types/dashboard.ts`
2. **API Response Types**: Ensure API responses match the defined interfaces
3. **Component Props**: Verify all component props are properly typed
4. **State Management**: Check that useState and useReducer hooks have explicit types
5. **Data Flow**: Trace data from API through components to ensure type consistency
6. **Kokonut UI Integration**: Resolve type conflicts between Kokonut UI and existing components

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] All type checks pass
- [ ] Card flip animations work smoothly
- [ ] Text animations render correctly
- [ ] Credit counter updates properly

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI
