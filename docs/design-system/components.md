# 🧩 CV-Match Component Inventory & Mapping

**Version:** 1.0  
**Last Updated:** October 12, 2025  
**Purpose:** Map UI needs from UX strategy to available components

---

## 📋 Table of Contents

1. [Component Inventory](#component-inventory)
2. [shadcn/ui Mapping](#shadcnui-mapping)
3. [Aceternity UI Mapping](#aceternity-ui-mapping)
4. [Custom Components Needed](#custom-components-needed)
5. [Installation Commands](#installation-commands)

---

## 📦 Component Inventory

Based on our [UX Strategy](/docs/development/UI-UX/ux-strategy.md), here are ALL components needed:

### Landing Page
- [ ] Hero section with animation
- [ ] Feature cards (3-column grid)
- [ ] Pricing comparison table
- [ ] Social proof badges
- [ ] Trust indicators
- [ ] CTA buttons
- [ ] Navigation header
- [ ] Footer

### Authentication
- [ ] Login form
- [ ] Signup form  
- [ ] OAuth buttons (Google, LinkedIn)
- [ ] Password reset form
- [ ] Email verification screen

### Dashboard
- [ ] Stats cards (4 metrics)
- [ ] Credit counter display
- [ ] Recent optimizations list
- [ ] Quick action cards
- [ ] Progress bars
- [ ] Charts (usage over time)
- [ ] Empty states

### Optimize Flow
- [ ] File upload dropzone
- [ ] Form inputs (job title, company, description)
- [ ] Character counter
- [ ] Progress stepper
- [ ] Processing animation
- [ ] Results display
- [ ] Download button
- [ ] Match score gauge

### Upgrade Modal
- [ ] Dialog/modal component
- [ ] Pricing cards comparison
- [ ] Feature checkmarks
- [ ] "Most Popular" badge
- [ ] Payment CTA buttons
- [ ] Social proof testimonials
- [ ] Trust badges

### Settings
- [ ] Profile form
- [ ] Billing information
- [ ] Plan upgrade/downgrade
- [ ] Theme toggle (light/dark)
- [ ] Language selector
- [ ] Delete account (dangerous action)

### Common UI Elements
- [ ] Buttons (variants)
- [ ] Input fields
- [ ] Textarea
- [ ] Select dropdowns
- [ ] Radio buttons
- [ ] Checkboxes
- [ ] Badges
- [ ] Alerts/Toasts
- [ ] Loading spinners
- [ ] Tooltips
- [ ] Breadcrumbs
- [ ] Pagination
- [ ] Skeleton loaders

---

## 🎨 shadcn/ui Mapping

Components already available via shadcn (installed or easy to add):

### ✅ Already Installed
Based on your `components/ui/` directory:

```bash
components/ui/
├── button.tsx           ✅
├── card.tsx             ✅
├── input.tsx            ✅
├── label.tsx            ✅
├── dialog.tsx           ✅
├── badge.tsx            ✅
├── alert.tsx            ✅
└── ...
```

### 📥 Need to Install

| Component | Usage | Install Command |
|-----------|-------|-----------------|
| **Form** | All forms | `bux shadcn@latest add form` |
| **Select** | Dropdowns | `bux shadcn@latest add select` |
| **Radio Group** | Payment options | `bux shadcn@latest add radio-group` |
| **Checkbox** | Feature lists | `bux shadcn@latest add checkbox` |
| **Progress** | Credit usage | `bux shadcn@latest add progress` |
| **Skeleton** | Loading states | `bux shadcn@latest add skeleton` |
| **Toast** | Notifications | `bux shadcn@latest add toast` |
| **Tooltip** | Help text | `bux shadcn@latest add tooltip` |
| **Tabs** | Dashboard sections | `bux shadcn@latest add tabs` |
| **Separator** | Visual dividers | `bux shadcn@latest add separator` |
| **Avatar** | User profiles | `bux shadcn@latest add avatar` |
| **Dropdown Menu** | User menu | `bux shadcn@latest add dropdown-menu` |
| **Sheet** | Mobile navigation | `bux shadcn@latest add sheet` |
| **Table** | Optimization history | `bux shadcn@latest add table` |
| **Breadcrumb** | Navigation | `bux shadcn@latest add breadcrumb` |
| **Command** | Search/command palette | `bux shadcn@latest add command` |

### Component Mapping Table

| UI Need | shadcn Component | Status | Notes |
|---------|------------------|--------|-------|
| **Login Form** | Form + Input + Button | ✅ Ready | Standard form layout |
| **Signup Form** | Form + Input + Button | ✅ Ready | Add OAuth buttons |
| **Stats Cards** | Card | ✅ Ready | 2x2 grid layout |
| **Credit Display** | Card + Progress | 📥 Need Progress | Large number + bar |
| **Upload Zone** | Input (file) | ✅ Ready | Add drag-drop logic |
| **Processing** | Skeleton + Spinner | 📥 Need Skeleton | Animated states |
| **Results Table** | Table + Badge | 📥 Need Table | Past optimizations |
| **Upgrade Modal** | Dialog + Card | ✅ Ready | Pricing comparison |
| **Alerts** | Alert + Toast | 📥 Need Toast | Success/error messages |
| **Settings Form** | Form + Tabs | 📥 Need Tabs | Organized settings |

---

## ✨ Aceternity UI Mapping

Premium animated components for visual appeal:

### 🌟 Recommended for CV-Match

| Page | Component | Usage | Priority |
|------|-----------|-------|----------|
| **Landing Hero** | `@aceternity/hero-parallax` | Stunning hero with depth | 🔴 High |
| **Landing Hero** | `@aceternity/spotlight` | Dramatic lighting effect | 🟡 Medium |
| **Landing Features** | `@aceternity/bento-grid` | Feature showcase | 🔴 High |
| **Landing Features** | `@aceternity/card-hover-effect` | Interactive cards | 🟡 Medium |
| **Landing** | `@aceternity/wavy-background` | Animated background | 🟢 Low |
| **Dashboard Cards** | `@aceternity/3d-card` | Elevated card effect | 🟡 Medium |
| **Dashboard Stats** | `@aceternity/moving-border` | Animated borders | 🟢 Low |
| **Dashboard** | `@aceternity/animated-tooltip` | Helpful tooltips | 🔴 High |
| **Optimize Flow** | `@aceternity/tracing-beam` | Progress indicator | 🟡 Medium |
| **Optimize Upload** | `@aceternity/file-upload` | Beautiful file upload | 🔴 High |
| **Results** | `@aceternity/sparkles` | Celebration effect | 🟡 Medium |
| **Results** | `@aceternity/text-generate-effect` | Animated text reveal | 🟢 Low |
| **Upgrade Modal** | `@aceternity/moving-border` | Premium feel | 🟡 Medium |
| **Pricing Page** | `@aceternity/bento-grid` | Pricing grid | 🔴 High |
| **Navigation** | `@aceternity/floating-navbar` | Modern navbar | 🟡 Medium |
| **All Pages** | `@aceternity/background-gradient` | Subtle backgrounds | 🟢 Low |

### Detailed Recommendations

#### **Landing Page Hero**

```bash
# Primary choice
bux shadcn@latest add @aceternity/hero-parallax

# Alternative/addition
bux shadcn@latest add @aceternity/spotlight
```

**Usage:**
```tsx
import { HeroParallax } from "@/components/ui/hero-parallax"

export function Hero() {
  const products = [
    { thumbnail: "/resume1.jpg" },
    { thumbnail: "/resume2.jpg" },
    // ... more examples
  ]

  return (
    <HeroParallax products={products}>
      <h1>Otimize seu Currículo com IA</h1>
      <p>3 otimizações grátis • Sem cartão de crédito</p>
      <Button>Começar Agora</Button>
    </HeroParallax>
  )
}
```

#### **Feature Showcase**

```bash
bux shadcn@latest add @aceternity/bento-grid
```

**Usage:**
```tsx
import { BentoGrid, BentoGridItem } from "@/components/ui/bento-grid"

const features = [
  {
    title: "Otimização com IA",
    description: "Algoritmos avançados analisam seu currículo",
    icon: <Sparkles />
  },
  // ... more features
]

<BentoGrid>
  {features.map(feature => (
    <BentoGridItem {...feature} />
  ))}
</BentoGrid>
```

#### **Dashboard Cards**

```bash
bux shadcn@latest add @aceternity/3d-card
bux shadcn@latest add @aceternity/animated-tooltip
```

**Usage:**
```tsx
import { CardContainer, CardBody } from "@/components/ui/3d-card"
import { AnimatedTooltip } from "@/components/ui/animated-tooltip"

<CardContainer>
  <CardBody>
    <AnimatedTooltip content="Seus créditos disponíveis">
      <div className="text-4xl font-bold">{credits}</div>
    </AnimatedTooltip>
  </CardBody>
</CardContainer>
```

#### **File Upload**

```bash
bux shadcn@latest add @aceternity/file-upload
```

**Usage:**
```tsx
import { FileUpload } from "@/components/ui/file-upload"

<FileUpload
  onChange={handleFileChange}
  accept=".pdf,.docx"
  maxSize={2 * 1024 * 1024}
/>
```

#### **Progress Indicator**

```bash
bux shadcn@latest add @aceternity/tracing-beam
```

**Usage:**
```tsx
import { TracingBeam } from "@/components/ui/tracing-beam"

<TracingBeam>
  <Step1 />
  <Step2 />
  <Step3 />
  <Step4 />
</TracingBeam>
```

---

## 🛠️ Custom Components Needed

Components we'll need to build (can't use library as-is):

### 1. **Credit Counter Widget**
**Complexity:** Low  
**Based on:** shadcn Card + Progress  
**Features:**
- Large number display
- Free vs Paid credits breakdown
- Progress bar
- CTAs based on credit count

```tsx
// components/dashboard/CreditCounter.tsx
export function CreditCounter({ 
  freeUsed, 
  freeLimit, 
  purchased 
}) {
  const total = (freeLimit - freeUsed) + purchased
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Créditos Disponíveis</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-5xl font-bold text-primary mb-4">
          {total}
        </div>
        <Progress value={(freeUsed / freeLimit) * 100} />
        <div className="mt-4 space-y-2">
          <div>Grátis: {freeLimit - freeUsed}/{freeLimit}</div>
          <div>Comprados: {purchased}</div>
        </div>
      </CardContent>
    </Card>
  )
}
```

### 2. **Upgrade Modal**
**Complexity:** Medium  
**Based on:** shadcn Dialog + Card + Aceternity Moving Border  
**Features:**
- Pricing comparison
- Social proof
- Feature checkmarks
- Payment CTAs

```tsx
// components/upgrade/UpgradeModal.tsx
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { MovingBorder } from "@/components/ui/moving-border"

export function UpgradeModal({ 
  isOpen, 
  onClose, 
  trigger 
}) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        {/* Pricing cards with MovingBorder for selected tier */}
        <div className="grid md:grid-cols-3 gap-6">
          {tiers.map(tier => (
            <MovingBorder key={tier.id}>
              <PricingCard {...tier} />
            </MovingBorder>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

### 3. **Match Score Gauge**
**Complexity:** Medium  
**Based on:** Custom SVG + shadcn Card  
**Features:**
- Circular progress indicator
- Animated score reveal
- Color-coded (red/yellow/green)

```tsx
// components/results/MatchScoreGauge.tsx
export function MatchScoreGauge({ score }: { score: number }) {
  const color = score >= 80 ? 'text-green-600' : 
                score >= 60 ? 'text-yellow-600' : 'text-red-600'
  
  return (
    <div className="relative w-48 h-48">
      <svg className="w-full h-full" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-muted"
        />
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeDasharray={`${score * 2.51} 251`}
          className={color}
          style={{ transition: 'stroke-dasharray 1s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`text-4xl font-bold ${color}`}>{score}%</span>
      </div>
    </div>
  )
}
```

### 4. **Optimization History Table**
**Complexity:** Low  
**Based on:** shadcn Table + Badge  
**Features:**
- Sortable columns
- Status badges
- Action buttons
- Pagination

```tsx
// components/history/OptimizationTable.tsx
import { Table } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

export function OptimizationTable({ optimizations }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Currículo</TableHead>
          <TableHead>Vaga</TableHead>
          <TableHead>Score</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Data</TableHead>
          <TableHead>Ações</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {optimizations.map(opt => (
          <TableRow key={opt.id}>
            <TableCell>{opt.resumeName}</TableCell>
            <TableCell>{opt.jobTitle}</TableCell>
            <TableCell>
              <Badge variant={opt.score >= 80 ? 'default' : 'secondary'}>
                {opt.score}%
              </Badge>
            </TableCell>
            <TableCell>
              <StatusBadge status={opt.status} />
            </TableCell>
            <TableCell>{formatDate(opt.createdAt)}</TableCell>
            <TableCell>
              <Button size="sm">Download</Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

### 5. **Onboarding Stepper**
**Complexity:** Medium  
**Based on:** Custom + Aceternity Tracing Beam  
**Features:**
- Multi-step wizard
- Progress indicator
- Skip functionality
- Animation between steps

```tsx
// components/onboarding/OnboardingStepper.tsx
import { TracingBeam } from "@/components/ui/tracing-beam"

export function OnboardingStepper({ currentStep, steps }) {
  return (
    <TracingBeam>
      {steps.map((Step, index) => (
        <div key={index} className={index === currentStep ? 'block' : 'hidden'}>
          <Step />
        </div>
      ))}
    </TracingBeam>
  )
}
```

---

## 📦 Installation Commands

### Phase 1: Essential Components (Install First)

```bash
# Forms and inputs
bux shadcn@latest add form
bux shadcn@latest add select
bux shadcn@latest add radio-group
bux shadcn@latest add checkbox

# Feedback
bux shadcn@latest add toast
bux shadcn@latest add progress
bux shadcn@latest add skeleton

# Navigation
bux shadcn@latest add tabs
bux shadcn@latest add dropdown-menu
bux shadcn@latest add breadcrumb

# Data display
bux shadcn@latest add table
bux shadcn@latest add avatar
bux shadcn@latest add separator

# Utilities
bux shadcn@latest add tooltip
bux shadcn@latest add sheet
bux shadcn@latest add command
```

### Phase 2: Aceternity UI (Landing Page)

```bash
# Hero section
bux shadcn@latest add @aceternity/hero-parallax
bux shadcn@latest add @aceternity/spotlight

# Features
bux shadcn@latest add @aceternity/bento-grid
bux shadcn@latest add @aceternity/card-hover-effect

# Background
bux shadcn@latest add @aceternity/background-gradient
```

### Phase 3: Aceternity UI (Dashboard & Flow)

```bash
# Dashboard
bux shadcn@latest add @aceternity/3d-card
bux shadcn@latest add @aceternity/animated-tooltip
bux shadcn@latest add @aceternity/moving-border

# Optimize flow
bux shadcn@latest add @aceternity/file-upload
bux shadcn@latest add @aceternity/tracing-beam

# Results
bux shadcn@latest add @aceternity/sparkles
bux shadcn@latest add @aceternity/text-generate-effect
```

### Phase 4: Nice-to-Have

```bash
# Advanced animations
bux shadcn@latest add @aceternity/floating-navbar
bux shadcn@latest add @aceternity/wavy-background
bux shadcn@latest add @aceternity/meteors
```

---

## ✅ Implementation Checklist

### Week 1: Core Components
- [ ] Install all Phase 1 shadcn components
- [ ] Test each component in isolation
- [ ] Create component playground/documentation page
- [ ] Build CreditCounter custom component
- [ ] Build basic UpgradeModal

### Week 2: Landing Page
- [ ] Install Phase 2 Aceternity components
- [ ] Build Hero section with parallax
- [ ] Build Feature section with bento grid
- [ ] Add animated backgrounds
- [ ] Test on mobile

### Week 3: Dashboard & Flow
- [ ] Install Phase 3 Aceternity components
- [ ] Build Dashboard with 3D cards
- [ ] Build Optimize flow with tracing beam
- [ ] Add file upload component
- [ ] Build Results display

### Week 4: Polish
- [ ] Add Phase 4 nice-to-have components
- [ ] Build MatchScoreGauge
- [ ] Build OptimizationTable
- [ ] Onboarding stepper
- [ ] Theme testing (light/dark)

---

## 🎨 Component Examples

### Landing Page Hero

```tsx
import { HeroParallax } from "@/components/ui/hero-parallax"
import { Spotlight } from "@/components/ui/spotlight"
import { Button } from "@/components/ui/button"

export function LandingHero() {
  return (
    <div className="relative">
      <Spotlight className="absolute top-0 left-0" />
      <HeroParallax products={resumeExamples}>
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-4">
            Otimize seu Currículo com IA
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            3 otimizações grátis • Sem cartão de crédito • Resultados em minutos
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="text-lg">
              Começar Grátis
            </Button>
            <Button size="lg" variant="outline">
              Ver Planos
            </Button>
          </div>
        </div>
      </HeroParallax>
    </div>
  )
}
```

### Dashboard Stats

```tsx
import { Card } from "@/components/ui/card"
import { CardContainer, CardBody } from "@/components/ui/3d-card"
import { AnimatedTooltip } from "@/components/ui/animated-tooltip"

export function StatsGrid({ stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map(stat => (
        <CardContainer key={stat.label}>
          <CardBody>
            <Card className="text-center p-6">
              <AnimatedTooltip content={stat.tooltip}>
                <div className="text-4xl font-bold text-primary mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">
                  {stat.label}
                </div>
              </AnimatedTooltip>
            </Card>
          </CardBody>
        </CardContainer>
      ))}
    </div>
  )
}
```

---

## 📚 Resources

- **shadcn/ui docs:** https://ui.shadcn.com
- **Aceternity UI docs:** https://ui.aceternity.com
- **Component examples:** See `/docs/design-system/wireframes.md`
- **Design system:** See `/docs/design-system/README.md`

---

**Last Updated:** October 12, 2025  
**Next Review:** After Phase 1 implementation