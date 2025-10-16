# 🔧 Enhanced Component Configuration Plan

**Version:** 1.0
**Last Updated:** October 16, 2025
**Purpose:** Configure shadcn and additional registries for CV-Match design system

---

## 📋 Table of Contents

1. [Current Configuration Analysis](#current-configuration-analysis)
2. [Registry Configuration Strategy](#registry-configuration-strategy)
3. [Component Installation Sequence](#component-installation-sequence)
4. [Theme Configuration Updates](#theme-configuration-updates)
5. [Custom Component Extensions](#custom-component-extensions)
6. [Type Safety Configuration](#type-safety-configuration)

---

## 📊 Current Configuration Analysis

### Current components.json Status:
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
  }
}
```

### Current Dependencies Status:
✅ **Radix UI Components Installed:**
- @radix-ui/react-alert-dialog
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-label
- @radix-ui/react-progress
- @radix-ui/react-slot
- @radix-ui/react-tabs

❌ **Missing Radix UI Components:**
- @radix-ui/react-select
- @radix-ui/react-checkbox
- @radix-ui/react-switch
- @radix-ui/react-radio-group
- @radix-ui/react-hover-card
- @radix-ui/react-scroll-area
- @radix-ui/react-toast
- @radix-ui/react-context-menu
- @radix-ui/react-command
- @radix-ui/react-collapsible

---

## 🗂️ Registry Configuration Strategy

### Adding Additional Registries

Based on research, shadcn supports adding custom registries through the components.json configuration. Here's our strategy:

#### 1. Update components.json for Multiple Registries:

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
      "name": "@ai-sdk",
      "url": "https://ui.ai-sdk.dev",
      "type": "registry"
    },
    {
      "name": "@kibo-ui",
      "url": "https://ui.kibo-ui.com",
      "type": "registry"
    }
  ]
}
```

#### 2. Registry Installation Commands:

```bash
# Add ai-sdk.dev registry (if available)
# Note: These are hypothetical registries for our use case
bunx shadcn@latest registry add ai-sdk https://ui.ai-sdk.dev

# Add kibo-ui registry (if available)
bunx shadcn@latest registry add kibo-ui https://ui.kibo-ui.com

# List available registries
bunx shadcn@latest registry list

# View components from specific registry
bunx shadcn@latest view @ai-sdk
bunx shadcn@latest view @kibo-ui
```

#### 3. Alternative Approach - Manual Integration:

If custom registries are not available, we'll manually integrate these components:

```bash
# Create directories for additional components
mkdir -p frontend/components/ai-sdk
mkdir -p frontend/components/kibo-ui

# Install additional dependencies
bun add framer-motion
bun add @tanstack/react-table
bun add recharts
```

---

## 📦 Component Installation Sequence

### Phase 2.1: Core shadcn Components (Foundation)

```bash
# Navigation and Layout
bunx shadcn@latest add navigation-menu
bunx shadcn@latest add separator
bunx shadcn@latest add sheet
bunx shadcn@latest add sidebar

# Form Components
bunx shadcn@latest add select
bunx shadcn@latest add checkbox
bunx shadcn@latest add switch
bunx shadcn@latest add radio-group

# Feedback and Loading
bunx shadcn@latest add skeleton
bunx shadcn@latest add spinner
bunx shadcn@latest add toast
bunx shadcn@latest add sonner

# Data Display
bunx shadcn@latest add avatar
bunx shadcn@latest add hover-card
bunx shadcn@latest add scroll-area
```

### Phase 2.2: Advanced shadcn Components

```bash
# Advanced Components
bunx shadcn@latest add command
bunx shadcn@latest add context-menu
bunx shadcn@latest add menubar
bunx shadcn@latest add collapsible
bunx shadcn@latest add resizable

# Charts and Data
bunx shadcn@latest add chart

# Additional UI Elements
bunx shadcn@latest add accordion
bunx shadcn@latest add aspect-ratio
bunx shadcn@latest add breadcrumb
bunx shadcn@latest add calendar
bunx shadcn@latest add carousel
```

### Phase 2.3: Custom and Extended Components

```bash
# Install additional dependencies for custom components
bun add framer-motion
bun add @tanstack/react-table
bun add recharts
bun add react-hook-form
bun add @hookform/resolvers
bun add zod
bun add cmdk
bun add sonner
```

---

## 🎨 Theme Configuration Updates

### Update tailwind.config.js for New Components

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  darkMode: 'class',
  theme: {
    extend: {
      // Animation variants for new components
      animation: {
        // Existing animations...
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'carousel-scroll': 'carousel-scroll 20s linear infinite',
        'slide-in-from-bottom': 'slide-in-from-bottom 0.3s ease-out',
        'slide-in-from-top': 'slide-in-from-top 0.3s ease-out',
        'slide-in-from-left': 'slide-in-from-left 0.3s ease-out',
        'slide-in-from-right': 'slide-in-from-right 0.3s ease-out',
      },
      
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'carousel-scroll': {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        },
        'slide-in-from-bottom': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-from-top': {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-from-left': {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'slide-in-from-right': {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      
      // Component-specific shadows
      boxShadow: {
        'card-hover': '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'dialog': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'dropdown': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  plugins: [
    // Existing plugins...
    require('@tailwindcss/typography'),
    
    // Plugin for new component variants
    function ({ addUtilities, addComponents, theme }) {
      // Component-specific utilities
      addUtilities({
        '.card-hover': {
          '@media (prefers-reduced-motion: no-preference)': {
            transition: 'all 0.3s ease',
          },
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme('boxShadow.card-hover'),
          },
        },
        '.dialog-backdrop': {
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(4px)',
        },
        '.navigation-item': {
          '@media (prefers-reduced-motion: no-preference)': {
            transition: 'all 0.2s ease',
          },
          '&:hover': {
            backgroundColor: theme('colors.accent'),
          },
        },
      });
      
      // Component-specific components
      addComponents({
        '.feature-card': {
          borderRadius: theme('borderRadius.lg'),
          boxShadow: theme('boxShadow.md'),
          padding: theme('spacing.6'),
          backgroundColor: theme('colors.card'),
          border: `1px solid ${theme('colors.border')}`,
          '@media (prefers-reduced-motion: no-preference)': {
            transition: 'all 0.3s ease',
          },
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme('boxShadow.card-hover'),
          },
        },
        '.stats-card': {
          borderRadius: theme('borderRadius.md'),
          boxShadow: theme('boxShadow.sm'),
          padding: theme('spacing.4'),
          backgroundColor: theme('colors.card'),
          border: `1px solid ${theme('colors.border')}`,
          borderLeft: `4px solid ${theme('colors.primary.DEFAULT')}`,
        },
        '.pricing-card': {
          borderRadius: theme('borderRadius.lg'),
          boxShadow: theme('boxShadow.md'),
          padding: theme('spacing.6'),
          backgroundColor: theme('colors.card'),
          border: `2px solid ${theme('colors.border')}`,
          position: 'relative',
          '&.featured': {
            borderColor: theme('colors.primary.DEFAULT'),
            transform: 'scale(1.05)',
          },
        },
      });
    },
  ],
};
```

---

## 🎛️ Custom Component Extensions

### Custom Components for CV-Match

#### 1. Match Score Gauge Component
```tsx
// frontend/components/ui/match-gauge.tsx
import React from 'react';
import { Progress } from './progress';

interface MatchGaugeProps {
  score: number;
  previousScore?: number;
  size?: 'sm' | 'md' | 'lg';
}

export function MatchGauge({ score, previousScore, size = 'md' }: MatchGaugeProps) {
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-48 h-48'
  };
  
  return (
    <div className={`relative ${sizeClasses[size]}`}>
      <svg className="transform -rotate-90 w-full h-full">
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="currentColor"
          strokeWidth="10"
          fill="none"
          className="text-muted"
        />
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="currentColor"
          strokeWidth="10"
          fill="none"
          strokeDasharray={`${2 * Math.PI * 45}`}
          strokeDashoffset={`${2 * Math.PI * 45 * (1 - score / 100)}`}
          className={score >= 80 ? 'text-green-500' : score >= 60 ? 'text-yellow-500' : 'text-red-500'}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold">{score}%</span>
      </div>
    </div>
  );
}
```

#### 2. Credit Counter Component
```tsx
// frontend/components/ui/credit-counter.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { Progress } from './progress';
import { Badge } from './badge';

interface CreditCounterProps {
  total: number;
  used: number;
  type: 'free' | 'purchased' | 'subscription';
}

export function CreditCounter({ total, used, type }: CreditCounterProps) {
  const remaining = total - used;
  const percentage = (remaining / total) * 100;
  
  const typeColors = {
    free: 'bg-green-500',
    purchased: 'bg-blue-500',
    subscription: 'bg-purple-500'
  };
  
  return (
    <Card className="border-l-4 border-l-primary">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <span>Créditos {type === 'free' ? 'Grátis' : type === 'purchased' ? 'Comprados' : 'Assinatura'}</span>
          <Badge variant={remaining > 0 ? 'default' : 'destructive'}>
            {remaining} restantes
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Usados: {used}</span>
            <span>Total: {total}</span>
          </div>
          <Progress value={percentage} className="h-2" />
        </div>
      </CardContent>
    </Card>
  );
}
```

#### 3. Brazilian Payment Methods Component
```tsx
// frontend/components/ui/brazilian-payment-methods.tsx
import React from 'react';
import { Card, CardContent } from './card';
import { Badge } from './badge';

export function BrazilianPaymentMethods() {
  const methods = [
    { name: 'PIX', icon: '💳', available: true },
    { name: 'Cartão', icon: '💳', available: true },
    { name: 'Boleto', icon: '📄', available: true },
  ];
  
  return (
    <div className="flex gap-2">
      {methods.map((method) => (
        <Badge key={method.name} variant={method.available ? 'default' : 'secondary'}>
          {method.icon} {method.name}
        </Badge>
      ))}
    </div>
  );
}
```

---

## 🔒 Type Safety Configuration

### Enhanced TypeScript Configuration

#### 1. Component Props Types
```tsx
// frontend/components/ui/types.ts
export interface ComponentVariants {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  intent?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

export interface BrazilianComponentProps extends ComponentVariants {
  // Brazilian-specific props
  lang?: 'pt-BR' | 'en';
  region?: 'BR' | 'US';
  currency?: 'BRL' | 'USD';
}

export interface CreditSystemProps {
  credits: number;
  totalCredits: number;
  plan: 'free' | 'flex' | 'flow';
  onUpgrade?: () => void;
}
```

#### 2. Form Validation Types
```tsx
// frontend/components/ui/form-types.ts
import { z } from 'zod';

export const BrazilianDocumentSchema = z.object({
  type: z.enum(['cpf', 'cnpj']),
  number: z.string().min(11).max(14),
});

export const BrazilianAddressSchema = z.object({
  street: z.string().min(5),
  number: z.string().min(1),
  complement: z.string().optional(),
  neighborhood: z.string().min(3),
  city: z.string().min(3),
  state: z.string().length(2),
  zipCode: z.string().regex(/^\d{5}-\d{3}$/),
});

export const JobDetailsSchema = z.object({
  title: z.string().min(3),
  company: z.string().optional(),
  description: z.string().min(10).max(5000),
  location: z.string().optional(),
  remote: z.boolean().default(false),
  salary: z.string().optional(),
});
```

#### 3. Component Export Types
```tsx
// frontend/components/ui/index.ts
export { Button } from './button';
export { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './card';
export { Input } from './input';
export { Label } from './label';
export { Progress } from './progress';
export { Badge } from './badge';
export { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs';
export { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './dialog';
export { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './table';
export { Alert, AlertDescription, AlertTitle } from './alert';
export { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './alert-dialog';
export { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from './dropdown-menu';

// Custom components
export { MatchGauge } from './match-gauge';
export { CreditCounter } from './credit-counter';
export { BrazilianPaymentMethods } from './brazilian-payment-methods';

// Types
export type { ComponentVariants, BrazilianComponentProps, CreditSystemProps } from './types';
export type { BrazilianDocumentSchema, BrazilianAddressSchema, JobDetailsSchema } from './form-types';
```

---

## 📋 Installation Checklist

### Pre-Installation Requirements:
- [ ] Backup current components.json
- [ ] Update package.json with new dependencies
- [ ] Create component directories for additional registries
- [ ] Backup current tailwind.config.js

### Installation Steps:
1. **Phase 2.1**: Install core shadcn components
2. **Phase 2.2**: Install advanced shadcn components
3. **Phase 2.3**: Install custom components and dependencies
4. **Phase 2.4**: Update configuration files
5. **Phase 2.5**: Add custom components
6. **Phase 2.6**: Type checking and validation

### Post-Installation Validation:
- [ ] All components compile without errors
- [ ] TypeScript validation passes
- [ ] Theme system works correctly
- [ ] Responsive design tests pass
- [ ] Accessibility tests pass

---

**Last Updated:** October 16, 2025
**Maintained by:** CV-Match Design System Team
**Status:** Ready for Implementation