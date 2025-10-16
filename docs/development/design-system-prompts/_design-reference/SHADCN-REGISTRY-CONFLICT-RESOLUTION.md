# 🔄 Shadcn Registry Conflict Resolution Strategy

**Version:** 1.0
**Last Updated:** October 16, 2025
**Purpose**: Prevent component redundancy and ensure proper usage of three shadcn registries

---

## 📋 Table of Contents

1. [Registry Overview](#registry-overview)
2. [Component Redundancy Prevention](#component-redundancy-prevention)
3. [Registry-Specific Usage Guidelines](#registry-specific-usage-guidelines)
4. [Installation & Configuration Strategy](#installation--configuration-strategy)
5. [Conflict Prevention Rules](#conflict-prevention-rules)
6. [Component Directory Structure](#component-directory-structure)
7. [Validation & Enforcement](#validation--enforcement)

---

## 🗂️ Registry Overview

### Three shadcn Registries Configuration

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  },
  "registries": [
    {
      "name": "@shadcn",
      "url": "https://ui.shadcn.com",
      "type": "registry"
    },
    {
      "name": "@aceternity-ui",
      "url": "https://ui.aceternity.com",
      "type": "registry"
    },
    {
      "name": "@kibo-ui",
      "url": "https://ui.kibo-ui.com",
      "type": "registry"
    },
    {
      "name": "@ai-sdk",
      "url": "https://ui.ai-sdk.dev",
      "type": "registry"
    }
  ]
}
```

### Registry Purpose & Scope

| Registry | Primary Use Case | Component Types | Target Pages |
|----------|------------------|-----------------|--------------|
| **@shadcn** | Base UI components | Forms, buttons, cards, tables | All pages (foundation) |
| **@aceternity-ui** | Premium animations | Hero sections, feature grids, interactive elements | Public pages only |
| **@kibo-ui** | Dashboard & data visualization | Charts, analytics, data tables | Protected/dashboard pages |
| **@ai-sdk** | AI-powered interactions | File upload, processing animations, AI feedback | Optimize flow & AI features |

---

## 🚫 Component Redundancy Prevention

### Overlapping Components Analysis

| Component Type | @shadcn | @aceternity-ui | @kibo-ui | @ai-sdk | Usage Decision |
|----------------|---------|----------------|----------|---------|----------------|
| Button | ✅ Base | ✅ Animated | ❌ | ❌ | Use @shadcn for consistency, @aceternity-ui for hero CTAs only |
| Card | ✅ Base | ✅ 3D effects | ✅ Data cards | ❌ | Use @shadcn for forms, @aceternity-ui for features, @kibo-ui for dashboard |
| Input | ✅ Base | ❌ | ✅ Advanced | ✅ AI-powered | Use @shadcn for standard forms, @kibo-ui for dashboard, @ai-sdk for file upload |
| Table | ✅ Base | ❌ | ✅ Data tables | ❌ | Use @shadcn for simple tables, @kibo-ui for analytics |
| Progress | ✅ Base | ✅ Animated | ❌ | ✅ AI processing | Use @shadcn for static, @aceternity-ui for animations, @ai-sdk for AI states |
| Navigation | ✅ Base | ❌ | ❌ | ❌ | Use @shadcn exclusively |
| Forms | ✅ Base | ❌ | ✅ Advanced | ✅ Smart forms | Use @shadcn for standard, @kibo-ui for dashboard, @ai-sdk for AI interactions |

### Redundancy Prevention Rules

1. **No Duplicate Components**: Never install the same component from multiple registries
2. **Purpose-Driven Selection**: Choose registry based on primary use case
3. **Fallback Strategy**: Use @shadcn as base, enhance with registry-specific components
4. **Explicit Imports**: Always use explicit registry imports to avoid confusion

---

## 📖 Registry-Specific Usage Guidelines

### @shadcn - Foundation Layer (All Pages)

**When to Use:**
- Basic form elements (buttons, inputs, labels)
- Standard UI components (cards, badges, dialogs)
- Navigation and layout components
- Anything not requiring special animations or AI features

**Installation Examples:**
```bash
# Base components - use everywhere
bunx shadcn@latest add @shadcn/button
bunx shadcn@latest add @shadcn/card
bunx shadcn@latest add @shadcn/input
bunx shadcn@latest add @shadcn/form
bunx shadcn@latest add @shadcn/navigation-menu
bunx shadcn@latest add @shadcn/table
```

**Usage Pattern:**
```tsx
// Use for all standard UI elements
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
```

### @aceternity-ui - Public Pages Only

**When to Use:**
- Hero sections with parallax effects
- Feature grids with 3D animations
- Interactive landing page elements
- Marketing-focused components

**Page Restrictions:**
- ✅ Landing page
- ✅ Pricing page
- ✅ About page
- ✅ Marketing pages
- ❌ Dashboard
- ❌ Optimize flow
- ❌ Protected routes

**Installation Examples:**
```bash
# Public page enhancements
bunx shadcn@latest add @aceternity-ui/hero-parallax
bunx shadcn@latest add @aceternity-ui/bento-grid
bunx shadcn@latest add @aceternity-ui/3d-card-hover
bunx shadcn@latest add @aceternity-ui/moving-border
bunx shadcn@latest add @aceternity-ui/text-reveal
```

**Usage Pattern:**
```tsx
// Use only in public page components
import { HeroParallax } from "@/components/aceternity-ui/hero-parallax";
import { BentoGrid } from "@/components/aceternity-ui/bento-grid";
```

### @kibo-ui - Dashboard/Protected Pages Only

**When to Use:**
- Analytics and data visualization
- Dashboard-specific components
- Advanced data tables
- Business intelligence components

**Page Restrictions:**
- ✅ Dashboard
- ✅ Analytics pages
- ✅ Reports
- ✅ Admin panels
- ❌ Public landing pages
- ❌ Marketing pages

**Installation Examples:**
```bash
# Dashboard and analytics
bunx shadcn@latest add @kibo-ui/chart
bunx shadcn@latest add @kibo-ui/data-table
bunx shadcn@latest add @kibo-ui/analytics-card
bunx shadcn@latest add @kibo-ui/metric-display
bunx shadcn@latest add @kibo-ui/dashboard-layout
```

**Usage Pattern:**
```tsx
// Use only in dashboard components
import { Chart } from "@/components/kibo-ui/chart";
import { DataTable } from "@/components/kibo-ui/data-table";
```

### @ai-sdk - AI Features Only

**When to Use:**
- File upload with AI processing
- AI-powered form interactions
- Processing animations and feedback
- AI result displays

**Feature Restrictions:**
- ✅ Resume upload (optimize flow)
- ✅ AI processing states
- ✅ Smart form suggestions
- ✅ AI-powered recommendations
- ❌ Standard forms
- ❌ Static content display

**Installation Examples:**
```bash
# AI-specific features
bunx shadcn@latest add @ai-sdk/file-upload
bunx shadcn@latest add @ai-sdk/processing-animation
bunx shadcn@latest add @ai-sdk/smart-input
bunx shadcn@latest add @ai-sdk/ai-feedback
bunx shadcn@latest add @ai-sdk/result-display
```

**Usage Pattern:**
```tsx
// Use only in AI feature components
import { FileUpload } from "@/components/ai-sdk/file-upload";
import { ProcessingAnimation } from "@/components/ai-sdk/processing-animation";
```

---

## ⚙️ Installation & Configuration Strategy

### Phase-Based Installation

#### Phase 1: Foundation (@shadcn only)
```bash
# Install all base components first
bunx shadcn@latest add @shadcn/button
bunx shadcn@latest add @shadcn/card
bunx shadcn@latest add @shadcn/input
bunx shadcn@latest add @shadcn/form
bunx shadcn@latest add @shadcn/navigation-menu
bunx shadcn@latest add @shadcn/table
bunx shadcn@latest add @shadcn/dialog
bunx shadcn@latest add @shadcn/tabs
bunx shadcn@latest add @shadcn/progress
bunx shadcn@latest add @shadcn/badge
```

#### Phase 2: Public Pages (@aceternity-ui)
```bash
# Install only after @shadcn is complete
bunx shadcn@latest add @aceternity-ui/hero-parallax
bunx shadcn@latest add @aceternity-ui/bento-grid
bunx shadcn@latest add @aceternity-ui/3d-card-hover
bunx shadcn@latest add @aceternity-ui/moving-border
bunx shadcn@latest add @aceternity-ui/text-reveal
```

#### Phase 3: Dashboard (@kibo-ui)
```bash
# Install only for dashboard features
bunx shadcn@latest add @kibo-ui/chart
bunx shadcn@latest add @kibo-ui/data-table
bunx shadcn@latest add @kibo-ui/analytics-card
bunx shadcn@latest add @kibo-ui/metric-display
bunx shadcn@latest add @kibo-ui/dashboard-layout
```

#### Phase 4: AI Features (@ai-sdk)
```bash
# Install only for AI-specific features
bunx shadcn@latest add @ai-sdk/file-upload
bunx shadcn@latest add @ai-sdk/processing-animation
bunx shadcn@latest add @ai-sdk/smart-input
bunx shadcn@latest add @ai-sdk/ai-feedback
bunx shadcn@latest add @ai-sdk/result-display
```

### Registry Configuration

```json
{
  "components.json": {
    "registry": "@shadcn",
    "style": "default",
    "rsc": false,
    "tsx": true,
    "tailwind": {
      "config": "tailwind.config.js",
      "css": "app/globals.css",
      "baseColor": "slate",
      "cssVariables": true
    },
    "aliases": {
      "components": "@/components",
      "utils": "@/lib/utils"
    },
    "registries": {
      "@aceternity-ui": {
        "style": "new-york",
        "tailwind": {
          "config": "tailwind.config.js",
          "css": "app/globals.css",
          "baseColor": "slate",
          "cssVariables": true
        }
      },
      "@kibo-ui": {
        "style": "default",
        "tailwind": {
          "config": "tailwind.config.js",
          "css": "app/globals.css",
          "baseColor": "slate",
          "cssVariables": true
        }
      },
      "@ai-sdk": {
        "style": "default",
        "tailwind": {
          "config": "tailwind.config.js",
          "css": "app/globals.css",
          "baseColor": "slate",
          "cssVariables": true
        }
      }
    }
  }
}
```

---

## 🚧 Conflict Prevention Rules

### 1. Explicit Registry Imports

```tsx
// ❌ WRONG - Ambiguous imports
import { Button } from "@/components/ui/button"; // Could be from any registry

// ✅ CORRECT - Explicit registry imports
import { Button } from "@/components/shadcn/button";
import { AnimatedButton } from "@/components/aceternity-ui/animated-button";
import { ChartButton } from "@/components/kibo-ui/chart-button";
import { AIButton } from "@/components/ai-sdk/ai-button";
```

### 2. Directory Structure Enforcement

```
frontend/components/
├── shadcn/           # Base components only
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── form.tsx
├── aceternity-ui/    # Public page animations only
│   ├── hero-parallax.tsx
│   ├── bento-grid.tsx
│   └── 3d-card-hover.tsx
├── kibo-ui/          # Dashboard components only
│   ├── chart.tsx
│   ├── data-table.tsx
│   └── analytics-card.tsx
├── ai-sdk/           # AI features only
│   ├── file-upload.tsx
│   ├── processing-animation.tsx
│   └── smart-input.tsx
└── ui/               # Re-export main components
    ├── button.tsx      # Re-exports from shadcn
    ├── card.tsx        # Re-exports from shadcn
    └── index.ts        # Main export file
```

### 3. Page-Level Import Rules

```tsx
// Public pages (app/(public)/page.tsx)
import { HeroParallax } from "@/components/aceternity-ui/hero-parallax"; // ✅
import { BentoGrid } from "@/components/aceternity-ui/bento-grid"; // ✅
import { Button } from "@/components/ui/button"; // ✅ (shadcn)
import { Chart } from "@/components/kibo-ui/chart"; // ❌ WRONG - Dashboard only

// Dashboard pages (app/(dashboard)/page.tsx)
import { Chart } from "@/components/kibo-ui/chart"; // ✅
import { DataTable } from "@/components/kibo-ui/data-table"; // ✅
import { Button } from "@/components/ui/button"; // ✅ (shadcn)
import { HeroParallax } from "@/components/aceternity-ui/hero-parallax"; // ❌ WRONG - Public only

// AI features (app/(dashboard)/optimize/page.tsx)
import { FileUpload } from "@/components/ai-sdk/file-upload"; // ✅
import { ProcessingAnimation } from "@/components/ai-sdk/processing-animation"; // ✅
import { Button } from "@/components/ui/button"; // ✅ (shadcn)
import { BentoGrid } from "@/components/aceternity-ui/bento-grid"; // ❌ WRONG - Public only
```

### 4. Component Naming Convention

```tsx
// shadcn components - standard names
export const Button = ...
export const Card = ...
export const Input = ...

// aceternity-ui components - descriptive animation names
export const HeroParallax = ...
export const BentoGrid = ...
export const TextReveal = ...

// kibo-ui components - data/analytics focused names
export const AnalyticsChart = ...
export const MetricCard = ...
export const DataTable = ...

// ai-sdk components - AI-focused names
export const AIFileUpload = ...
export const ProcessingAnimation = ...
export const SmartInput = ...
```

---

## 📁 Component Directory Structure

### Implementation Structure

```
frontend/components/
├── ui/                           # Main exports (backward compatibility)
│   ├── index.ts                  # Re-exports from appropriate registry
│   ├── button.tsx                # Re-exports from shadcn
│   ├── card.tsx                  # Re-exports from shadcn
│   └── form.tsx                  # Re-exports from shadcn
├── shadcn/                       # Base registry components
│   ├── button/
│   │   ├── button.tsx
│   │   └── index.ts
│   ├── card/
│   │   ├── card.tsx
│   │   └── index.ts
│   └── form/
│       ├── form.tsx
│       └── index.ts
├── aceternity-ui/                # Public page animations
│   ├── hero-parallax/
│   │   ├── hero-parallax.tsx
│   │   └── index.ts
│   ├── bento-grid/
│   │   ├── bento-grid.tsx
│   │   └── index.ts
│   └── 3d-card-hover/
│       ├── 3d-card-hover.tsx
│       └── index.ts
├── kibo-ui/                      # Dashboard components
│   ├── chart/
│   │   ├── chart.tsx
│   │   └── index.ts
│   ├── data-table/
│   │   ├── data-table.tsx
│   │   └── index.ts
│   └── analytics-card/
│       ├── analytics-card.tsx
│       └── index.ts
├── ai-sdk/                       # AI features
│   ├── file-upload/
│   │   ├── file-upload.tsx
│   │   └── index.ts
│   ├── processing-animation/
│   │   ├── processing-animation.tsx
│   │   └── index.ts
│   └── smart-input/
│       ├── smart-input.tsx
│       └── index.ts
└── lib/
    ├── utils.ts                  # Shared utilities
    ├── registry-config.ts        # Registry configuration
    └── component-rules.ts        # Usage rules and validation
```

### Re-export Strategy

```tsx
// frontend/components/ui/index.ts
// Main export file for backward compatibility

// Base components from shadcn
export { Button } from "../shadcn/button";
export { Card, CardContent, CardHeader, CardTitle } from "../shadcn/card";
export { Input } from "../shadcn/input";
export { Form } from "../shadcn/form";

// Registry-specific components (named exports)
export { HeroParallax } from "../aceternity-ui/hero-parallax";
export { BentoGrid } from "../aceternity-ui/bento-grid";
export { AnalyticsChart } from "../kibo-ui/chart";
export { DataTable } from "../kibo-ui/data-table";
export { AIFileUpload } from "../ai-sdk/file-upload";
export { ProcessingAnimation } from "../ai-sdk/processing-animation";
```

---

## ✅ Validation & Enforcement

### ESLint Rules for Registry Usage

```javascript
// .eslintrc.js
module.exports = {
  rules: {
    'no-restricted-imports': [
      'error',
      {
        patterns: [
          {
            group: ['@/components/kibo-ui/*'],
            message: 'kibo-ui components should only be used in dashboard pages',
            allowTypeImports: true
          },
          {
            group: ['@/components/aceternity-ui/*'],
            message: 'aceternity-ui components should only be used in public pages',
            allowTypeImports: true
          },
          {
            group: ['@/components/ai-sdk/*'],
            message: 'ai-sdk components should only be used in AI features',
            allowTypeImports: true
          }
        ]
      }
    ]
  }
};
```

### TypeScript Path Mapping

```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/components/ui/*": ["./components/shadcn/*"],
      "@/components/aceternity-ui/*": ["./components/aceternity-ui/*"],
      "@/components/kibo-ui/*": ["./components/kibo-ui/*"],
      "@/components/ai-sdk/*": ["./components/ai-sdk/*"]
    }
  }
}
```

### Pre-commit Hooks

```bash
#!/bin/sh
# .husky/pre-commit

# Check for registry misuse
echo "Checking registry usage compliance..."

# Ensure kibo-ui is not used in public pages
if grep -r "from.*kibo-ui" app/\(public\)/ --include="*.tsx" --include="*.ts"; then
  echo "❌ kibo-ui components found in public pages"
  exit 1
fi

# Ensure aceternity-ui is not used in dashboard
if grep -r "from.*aceternity-ui" app/\(dashboard\)/ --include="*.tsx" --include="*.ts"; then
  echo "❌ aceternity-ui components found in dashboard pages"
  exit 1
fi

# Ensure ai-sdk is not used in non-AI features
if grep -r "from.*ai-sdk" app/\(public\)/ --include="*.tsx" --include="*.ts"; then
  echo "❌ ai-sdk components found in public pages"
  exit 1
fi

echo "✅ Registry usage validation passed"
```

### Build-time Validation

```typescript
// scripts/validate-registry-usage.ts
import * as fs from 'fs';
import * as path from 'path';

const REGISTRY_RULES = {
  'app/(public)': {
    allowed: ['shadcn', 'aceternity-ui'],
    forbidden: ['kibo-ui', 'ai-sdk']
  },
  'app/(dashboard)': {
    allowed: ['shadcn', 'kibo-ui', 'ai-sdk'],
    forbidden: ['aceternity-ui']
  },
  'app/(dashboard)/optimize': {
    allowed: ['shadcn', 'ai-sdk'],
    forbidden: ['aceternity-ui', 'kibo-ui']
  }
};

function validateRegistryUsage() {
  // Implementation to validate registry usage
  console.log('Validating registry usage...');
  // Add validation logic
}

validateRegistryUsage();
```

---

## 📋 Quick Reference Checklist

### Before Installation:
- [ ] Review component requirements for each page type
- [ ] Identify potential component overlaps
- [ ] Plan registry-specific usage patterns

### During Installation:
- [ ] Install @shadcn components first (foundation)
- [ ] Install @aceternity-ui for public pages only
- [ ] Install @kibo-ui for dashboard pages only
- [ ] Install @ai-sdk for AI features only
- [ ] Use explicit registry prefixes in commands

### After Installation:
- [ ] Verify directory structure is correct
- [ ] Test component imports work properly
- [ ] Run ESLint validation
- [ ] Execute pre-commit hooks
- [ ] Test page-specific functionality

### Ongoing Maintenance:
- [ ] Regular audits of component usage
- [ ] Update documentation when adding new components
- [ ] Monitor for registry conflicts
- [ ] Enforce usage rules in code reviews

---

**Last Updated:** October 16, 2025
**Maintained by:** CV-Match Design System Team
**Status:** Ready for Implementation