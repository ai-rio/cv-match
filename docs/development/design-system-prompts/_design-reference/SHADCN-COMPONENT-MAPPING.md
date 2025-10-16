# 🎨 Shadcn Registry Component Mapping for CV-Match Design System

**Version:** 2.0
**Last Updated:** October 16, 2025
**Purpose:** Map shadcn + 3 registry components to wireframes with conflict prevention

---

## 📋 Table of Contents

1. [Component Analysis Summary](#component-analysis-summary)
2. [Public Pages Component Mapping](#public-pages-component-mapping)
3. [Dashboard/Protected Pages Component Mapping](#dashboardprotected-pages-component-mapping)
4. [Missing Components - Installation Plan](#missing-components---installation-plan)
5. [Additional Registries Research](#additional-registries-research)
6. [Component Usage Guidelines](#component-usage-guidelines)

---

## 📊 Component Analysis Summary

### Registry Configuration Strategy

**Four shadcn registries with specific usage domains:**

| Registry | Purpose | Target Pages | Component Types |
|----------|---------|--------------|-----------------|
| **@shadcn** | Base UI foundation | All pages | Forms, buttons, cards, navigation |
| **@aceternity-ui** | Premium animations | Public pages only | Hero sections, feature grids, interactive elements |
| **@kibo-ui** | Dashboard & analytics | Protected pages only | Charts, data tables, metrics |
| **@ai-sdk** | AI-powered interactions | AI features only | File upload, processing, smart forms |

### Current shadcn Components Installed:
✅ **Already Available (@shadcn registry):**
- alert-dialog.tsx
- alert.tsx
- badge.tsx
- button.tsx
- card.tsx
- dialog.tsx
- dropdown-menu.tsx
- input.tsx
- label.tsx
- progress.tsx
- table.tsx
- tabs.tsx
- textarea.tsx
- typography.tsx

### Key Radix Dependencies Already Installed:
- @radix-ui/react-alert-dialog
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-label
- @radix-ui/react-progress
- @radix-ui/react-slot
- @radix-ui/react-tabs

---

## 🌐 Public Pages Component Mapping

### Landing Page Components

| Wireframe Section | @shadcn Component | @aceternity-ui Component | Usage Notes |
|-------------------|------------------|-------------------------|-------------|
| Navigation Header | navigation-menu | - | Base navigation |
| Hero Section | button | Hero-Parallax | Premium hero animation |
| Social Proof | card + badge | - | Stats display |
| Features Grid | card | Bento Grid | 3D animated grid |
| How It Works | card + progress | - | Step indicators |
| CTA Section | button | - | Emphasis CTA |
| Footer | - | - | Simple layout |

### Pricing Page Components

| Wireframe Section | @shadcn Component | @aceternity-ui Component | Usage Notes |
|-------------------|------------------|-------------------------|-------------|
| Navigation Header | navigation-menu | - | Reusable component |
| Pricing Tabs | tabs | - | Credits vs Subscriptions |
| Pricing Cards | card + badge + button | - | 5-column grid |
| Features Grid | card | - | 4-column Brazilian features |
| Trust Indicators | badge | - | Payment security |

### Results Page Components

| Wireframe Section | @shadcn Component | @aceternity-ui Component | Usage Notes |
|-------------------|------------------|-------------------------|-------------|
| Match Score | progress + card | Text-Reveal | Animated score display |
| Improvements | card + badge | - | 3-column grid |
| Download Actions | button | - | Multiple CTAs |
| Next Steps | button | - | Navigation |
| Upsell Section | card + button | - | Conditional display |

---

## 🔒 Dashboard/Protected Pages Component Mapping

### Dashboard Layout

| Wireframe Section | @shadcn Component | @kibo-ui Component | @ai-sdk Component | Usage Notes |
|-------------------|------------------|-------------------|------------------|-------------|
| Navigation Header | navigation-menu | - | - | User menu |
| Quick Actions | card + button | - | 3D-Card-Hover | Interactive actions |
| Statistics Cards | card + progress | Analytics-Card | - | 2x2 grid |
| Credits Display | card + progress | Metric-Display | - | Prominent section |
| Recent Table | table + badge | DataTable | - | Status indicators |
| User Menu | dropdown-menu | - | - | Profile/settings |

### Optimize Flow Components

| Wireframe Section | @shadcn Component | @ai-sdk Component | Usage Notes |
|-------------------|------------------|------------------|-------------|
| Progress Indicator | progress | - | Step tracking |
| File Upload | input + card | File-Upload | Drag-drop zone |
| Job Details Form | form + input + textarea | Smart-Input | AI-enhanced form |
| Processing State | progress | Processing-Animation | Real-time feedback |

### Upgrade Modal

| Wireframe Section | @shadcn Component | @aceternity-ui Component | Usage Notes |
|-------------------|------------------|-------------------------|-------------|
| Modal Container | dialog | Moving Border | Overlay backdrop |
| Pricing Options | card + button | - | 3-column comparison |
| Testimonial | card | - | Social proof |
| CTAs | button | - | Primary/secondary |

---

## 🔧 Missing Components - Installation Plan

### Phase-Based Registry Installation Strategy

### Phase 1: @shadcn Foundation Components (All Pages)

```bash
# Navigation and layout
bunx shadcn@latest add @shadcn/navigation-menu
bunx shadcn@latest add @shadcn/separator
bunx shadcn@latest add @shadcn/sheet
bunx shadcn@latest add @shadcn/sidebar

# Form components
bunx shadcn@latest add @shadcn/select
bunx shadcn@latest add @shadcn/checkbox
bunx shadcn@latest add @shadcn/switch
bunx shadcn@latest add @shadcn/radio-group
bunx shadcn@latest add @shadcn/textarea

# Feedback and loading
bunx shadcn@latest add @shadcn/skeleton
bunx shadcn@latest add @shadcn/spinner
bunx shadcn@latest add @shadcn/toast
bunx shadcn@latest add @shadcn/sonner

# Data display
bunx shadcn@latest add @shadcn/avatar
bunx shadcn@latest add @shadcn/hover-card
bunx shadcn@latest add @shadcn/scroll-area
bunx shadcn@latest add @shadcn/resizable

# Advanced components
bunx shadcn@latest add @shadcn/command
bunx shadcn@latest add @shadcn/context-menu
bunx shadcn@latest add @shadcn/menubar
bunx shadcn@latest add @shadcn/collapsible
```

### Phase 2: @aceternity-ui Components (Public Pages Only)

```bash
# Hero and landing page components
bunx shadcn@latest add @aceternity-ui/hero-parallax
bunx shadcn@latest add @aceternity-ui/bento-grid
bunx shadcn@latest add @aceternity-ui/3d-card-hover
bunx shadcn@latest add @aceternity-ui/moving-border
bunx shadcn@latest add @aceternity-ui/text-reveal
bunx shadcn@latest add @aceternity-ui/sparkles
```

### Phase 3: @kibo-ui Components (Dashboard Only)

```bash
# Analytics and dashboard components
bunx shadcn@latest add @kibo-ui/analytics-chart
bunx shadcn@latest add @kibo-ui/data-table
bunx shadcn@latest add @kibo-ui/metric-card
bunx shadcn@latest add @kibo-ui/dashboard-layout
bunx shadcn@latest add @kibo-ui/stats-display
```

### Phase 4: @ai-sdk Components (AI Features Only)

```bash
# AI-powered components
bunx shadcn@latest add @ai-sdk/file-upload
bunx shadcn@latest add @ai-sdk/processing-animation
bunx shadcn@latest add @ai-sdk/smart-input
bunx shadcn@latest add @ai-sdk/ai-feedback
bunx shadcn@latest add @ai-sdk/result-display
```

### Additional Dependencies Needed:

```json
{
  "dependencies": {
    "@radix-ui/react-select": "^2.1.7",
    "@radix-ui/react-checkbox": "^1.1.7",
    "@radix-ui/react-switch": "^1.1.7",
    "@radix-ui/react-radio-group": "^1.2.7",
    "@radix-ui/react-hover-card": "^1.1.7",
    "@radix-ui/react-scroll-area": "^1.1.7",
    "@radix-ui/react-toast": "^1.2.7",
    "@radix-ui/react-context-menu": "^2.2.7",
    "@radix-ui/react-command": "^1.1.7",
    "@radix-ui/react-collapsible": "^1.1.7",
    "@hookform/resolvers": "^3.9.7",
    "react-hook-form": "^7.55.3",
    "zod": "^3.24.7",
    "cmdk": "^1.1.7",
    "sonner": "^2.1.7",
    "framer-motion": "^10.16.4",
    "recharts": "^2.8.0",
    "@tanstack/react-table": "^8.9.3"
  }
}
```

---

## 🔍 Registry-Specific Component Selection

### @aceternity-ui Registry Components (Public Pages Only)

| Component | Use Case | Page Location | Conflict Prevention |
|-----------|----------|---------------|---------------------|
| Hero-Parallax | Hero section animation | Landing page | Public pages only |
| Bento-Grid | Feature grid with 3D effects | Landing page | Public pages only |
| 3D-Card-Hover | Interactive card effects | Landing page | Public pages only |
| Moving-Border | Animated borders | Upgrade modal | Public pages only |
| Text-Reveal | Animated text appearance | Results page | Public pages only |
| Sparkles | Success animations | Results page | Public pages only |

### @kibo-ui Registry Components (Dashboard Only)

| Component | Use Case | Page Location | Conflict Prevention |
|-----------|----------|---------------|---------------------|
| Analytics-Chart | Data visualization | Dashboard | Dashboard only |
| Data-Table | Advanced data tables | Dashboard | Dashboard only |
| Metric-Card | Statistics display | Dashboard | Dashboard only |
| Dashboard-Layout | Dashboard structure | Dashboard | Dashboard only |
| Stats-Display | KPI visualization | Dashboard | Dashboard only |

### @ai-sdk Registry Components (AI Features Only)

| Component | Use Case | Page Location | Conflict Prevention |
|-----------|----------|---------------|---------------------|
| File-Upload | Resume upload with AI | Optimize flow | AI features only |
| Processing-Animation | AI processing feedback | Optimize flow | AI features only |
| Smart-Input | AI-enhanced forms | Optimize flow | AI features only |
| AI-Feedback | AI response display | Results page | AI features only |
| Result-Display | AI results visualization | Results page | AI features only |

### Registry Configuration Commands:

```bash
# Configure multiple registries
bunx shadcn@latest config set registries.aceternity-ui https://ui.aceternity.com
bunx shadcn@latest config set registries.kibo-ui https://ui.kibo-ui.com
bunx shadcn@latest config set registries.ai-sdk https://ui.ai-sdk.dev

# Verify registry configuration
bunx shadcn@latest registry list
```

---

## 📋 Component Usage Guidelines

### Public Pages Pattern:

1. **Hero Sections**: Use Aceternity components for visual impact
2. **Feature Cards**: Shadcn card + badge combinations
3. **CTAs**: Shadcn button with proper sizing
4. **Forms**: shadcn form components with validation
5. **Navigation**: shadcn navigation-menu for consistency

### Dashboard Pages Pattern:

1. **Layout**: shadcn sidebar + navigation
2. **Data Display**: kibo-ui charts + shadcn tables
3. **Interactions**: ai-sdk.dev 3D effects + animations
4. **Forms**: shadcn form + react-hook-form + zod validation
5. **Feedback**: shadcn toast + sonner for notifications

### Component Variations:

#### Button Variations:
```tsx
// Primary CTA (Landing pages)
<Button size="lg" className="brazilian-button">
  Começar Grátis
</Button>

// Secondary (Dashboard)
<Button variant="outline" size="default">
  Ver Histórico
</Button>

// Destructive (Actions)
<Button variant="destructive" size="sm">
  Excluir
</Button>
```

#### Card Variations:
```tsx
// Feature Card (Public)
<Card className="brazilian-card hover:shadow-lg transition-shadow">
  <CardHeader>
    <Badge variant="secondary">Novo</Badge>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>

// Stats Card (Dashboard)
<Card className="border-l-4 border-l-primary">
  <CardContent className="pt-6">
    <div className="text-2xl font-bold">87%</div>
    <p className="text-xs text-muted-foreground">Taxa de Sucesso</p>
  </CardContent>
</Card>
```

### Responsive Patterns:

1. **Mobile First**: All components must work at 320px
2. **Touch Targets**: Minimum 44x44px
3. **Spacing**: Use 4px grid system
4. **Typography**: Respect Brazilian Portuguese line heights

---

## 🎯 Implementation Priority

### Phase 2 Priority (Component Installation):
1. **Core shadcn components** - navigation, forms, feedback
2. **ai-sdk.dev components** - 3D effects, file upload
3. **kibo-ui components** - charts, data tables
4. **Custom components** - match score gauge, credit counter

### Phase 3 Priority (Landing Page):
1. **Hero section** with Aceternity parallax
2. **Feature grid** with card animations
3. **Pricing section** with tabs and cards
4. **CTA sections** with proper hierarchy

### Phase 4 Priority (Dashboard):
1. **Layout and navigation**
2. **Statistics cards** with charts
3. **Data tables** with status badges
4. **Form flows** with validation

---

## 📝 Next Steps

1. **Install missing shadcn components** (Phase 2)
2. **Add additional registries** (ai-sdk.dev, kibo-ui)
3. **Create custom components** (match gauge, credit counter)
4. **Implement component variations** (sizing, states)
5. **Test responsive behavior** across all breakpoints
6. **Validate accessibility** (WCAG 2.1 AA)

---

**Last Updated:** October 16, 2025
**Maintained by:** CV-Match Design System Team
**Status:** Ready for Implementation