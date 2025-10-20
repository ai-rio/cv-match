# 05 - Landing Hero Implementation

**Agent**: `frontend-specialist`
**Phase**: 3
**Duration**: 3h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement hero with parallax effects using Kokonut UI shape-hero component following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Install and configure Kokonut UI shape-hero component
3. Implement hero section with parallax effects
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
# Install shape-hero component from Kokonut UI
bunx shadcn@latest add @kokonutui/shape-hero

# Verify installation
ls frontend/components/ui/shape-hero.tsx
```

### 2. Hero Implementation

Create the hero section using the shape-hero component:

```typescript
// frontend/components/landing/hero-section.tsx
import { ShapeHero } from '@/components/ui/shape-hero';
import { Button } from '@/components/ui/button';
import { GradientButton } from '@/components/ui/gradient-button';
import { ShimmerText } from '@/components/ui/shimmer-text';

export function HeroSection() {
  return (
    <ShapeHero className="relative min-h-screen flex items-center justify-center">
      <div className="container mx-auto px-4 text-center">
        <ShimmerText className="text-4xl md:text-6xl font-bold mb-6">
          Transform Your CV into Opportunities
        </ShimmerText>
        <p className="text-xl md:text-2xl mb-8 text-muted-foreground">
          AI-powered resume optimization that gets you noticed
        </p>
        <div className="flex gap-4 justify-center">
          <GradientButton size="lg">
            Get Started Free
          </GradientButton>
          <Button variant="outline" size="lg">
            View Demo
          </Button>
        </div>
      </div>
    </ShapeHero>
  );
}
```

### 3. Component Integration

Update the main page to use the new hero section:

```typescript
// frontend/app/[locale]/page.tsx
import { HeroSection } from '@/components/landing/hero-section';

export default function HomePage() {
  return (
    <main>
      <HeroSection />
      {/* Other page sections */}
    </main>
  );
}
```

---

## 🎨 Component Mapping

| Original Component | Kokonut UI Component | Usage |
|-------------------|----------------------|-------|
| Hero-Parallax | shape-hero | Main hero container with parallax effects |
| Text Reveal | shimmer-text | Hero title animation |
| Moving Border | gradient-button | Primary CTA button |

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] Parallax effects work smoothly
- [ ] Text animations render correctly
- [ ] Button interactions are responsive

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI
