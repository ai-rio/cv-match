# 06 - Landing Features Section

**Agent**: `frontend-specialist`
**Phase**: 3
**Duration**: 3h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement bento grid features using Kokonut UI bento-grid component following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Install and configure Kokonut UI bento-grid component
3. Implement features section with interactive cards
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
# Install bento-grid and card-flip components from Kokonut UI
bunx shadcn@latest add @kokonutui/bento-grid
bunx shadcn@latest add @kokonutui/card-flip

# Verify installation
ls frontend/components/ui/bento-grid.tsx
ls frontend/components/ui/card-flip.tsx
```

### 2. Features Section Implementation

Create the features section using the bento-grid component:

```typescript
// frontend/components/landing/features-section.tsx
import { BentoGrid } from '@/components/ui/bento-grid';
import { CardFlip } from '@/components/ui/card-flip';
import { DynamicText } from '@/components/ui/dynamic-text';

export function FeaturesSection() {
  const features = [
    {
      title: "AI-Powered Analysis",
      description: "Advanced algorithms analyze your CV against job requirements",
      icon: "🤖",
      className: "md:col-span-2"
    },
    {
      title: "Smart Optimization",
      description: "Get personalized suggestions to improve your resume",
      icon: "✨",
      className: "md:col-span-1"
    },
    {
      title: "Real-time Feedback",
      description: "Instant insights as you make changes to your CV",
      icon: "⚡",
      className: "md:col-span-1"
    },
    {
      title: "Industry Insights",
      description: "Compare your CV with industry standards and trends",
      icon: "📊",
      className: "md:col-span-2"
    }
  ];

  return (
    <section className="py-20 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-12">
          <DynamicText 
            texts={["Powerful Features", "Smart Tools", "Better Results"]}
            className="text-4xl md:text-5xl font-bold mb-4"
          />
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to create a standout resume that gets noticed by recruiters
          </p>
        </div>
        
        <BentoGrid className="max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <CardFlip
              key={index}
              className={feature.className}
              frontContent={
                <div className="p-6 h-full flex flex-col justify-center items-center text-center">
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </div>
              }
              backContent={
                <div className="p-6 h-full flex flex-col justify-center">
                  <h3 className="text-xl font-semibold mb-4">Learn More</h3>
                  <p className="text-muted-foreground mb-4">
                    Discover how this feature can transform your job search.
                  </p>
                  <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md">
                    Explore Feature
                  </button>
                </div>
              }
            />
          ))}
        </BentoGrid>
      </div>
    </section>
  );
}
```

### 3. Component Integration

Update the main page to include the features section:

```typescript
// frontend/app/[locale]/page.tsx
import { HeroSection } from '@/components/landing/hero-section';
import { FeaturesSection } from '@/components/landing/features-section';

export default function HomePage() {
  return (
    <main>
      <HeroSection />
      <FeaturesSection />
      {/* Other page sections */}
    </main>
  );
}
```

---

## 🎨 Component Mapping

| Original Component | Kokonut UI Component | Usage |
|-------------------|----------------------|-------|
| Bento Grid | bento-grid | Feature grid layout |
| 3D-Card-Hover | card-flip | Interactive feature cards |
| Text Reveal | dynamic-text | Section title animation |

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] Card flip animations work smoothly
- [ ] Bento grid layout is responsive
- [ ] Dynamic text animations render correctly

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI
