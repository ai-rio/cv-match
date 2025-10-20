# 09 - Theme Testing

**Agent**: `frontend-specialist`
**Phase**: 5
**Duration**: 2h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement light/dark coverage for all Kokonut UI components following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Test theme switching across all Kokonut UI components
3. Verify consistent styling in light and dark modes
4. Test responsive behavior in both themes
5. Verify accessibility in both themes
6. Document any theme-specific issues

---

## 📚 Reference

- [Design System](../../design-system/README.md)
- [Wireframes](../../design-system/wireframes.md)
- [Components](../../design-system/components.md)
- [Kokonut UI Installation](04-kokonut-installation.md)
- [Kokonut UI Migration Guide](_design-reference/KOKONUT-UI-MIGRATION-GUIDE.md)

---

## 🛠️ Testing Steps

### 1. Theme Switching Test

```bash
# Navigate to frontend
cd frontend

# Start development server
bun run dev

# Test theme switching functionality
# 1. Click theme toggle in header
# 2. Verify system preference detection
# 3. Check localStorage persistence
```

### 2. Component Theme Testing

Test each Kokonut UI component in both themes:

```typescript
// frontend/components/test/theme-test-page.tsx
import { 
  ShapeHero, 
  BentoGrid, 
  CardFlip, 
  GradientButton, 
  ParticleButton,
  ShimmerText,
  DynamicText,
  TypeWriter,
  AttractButton,
  BeamsBackground
} from '@/components/ui';

export function ThemeTestPage() {
  return (
    <div className="min-h-screen space-y-12 p-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Shape Hero</h2>
        <ShapeHero className="h-64">
          <ShimmerText>Hero Content</ShimmerText>
        </ShapeHero>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Bento Grid</h2>
        <BentoGrid>
          {/* Test content */}
        </BentoGrid>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Buttons</h2>
        <div className="flex gap-4 flex-wrap">
          <GradientButton>Gradient Button</GradientButton>
          <ParticleButton>Particle Button</ParticleButton>
          <AttractButton>Attract Button</AttractButton>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Text Animations</h2>
        <div className="space-y-4">
          <ShimmerText>Shimmer Text</ShimmerText>
          <DynamicText texts={["Text 1", "Text 2", "Text 3"]} />
          <TypeWriter text="Type Writer Text" />
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Card Flip</h2>
        <CardFlip
          frontContent={<div>Front Content</div>}
          backContent={<div>Back Content</div>}
        />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-4">Beams Background</h2>
        <BeamsBackground className="h-64 relative">
          <div className="relative z-10">Content over beams</div>
        </BeamsBackground>
      </section>
    </div>
  );
}
```

### 3. Theme-Specific CSS Testing

Verify CSS custom properties work correctly:

```css
/* Test theme-specific styles */
.theme-test {
  /* Light theme variables */
  background: hsl(var(--background));
  color: hsl(var(--foreground));
  border: 1px solid hsl(var(--border));
  
  /* Dark theme should automatically switch */
}

/* Test component-specific theme overrides */
.kokonut-component {
  /* Verify these work in both themes */
  --primary: hsl(var(--primary));
  --primary-foreground: hsl(var(--primary-foreground));
}
```

---

## 🎨 Component Theme Coverage

| Component | Light Theme | Dark Theme | Notes |
|-----------|-------------|------------|-------|
| shape-hero | ✅ | ✅ | Test parallax effects in both themes |
| bento-grid | ✅ | ✅ | Verify grid layouts and spacing |
| card-flip | ✅ | ✅ | Test card animations and shadows |
| gradient-button | ✅ | ✅ | Verify gradient visibility |
| particle-button | ✅ | ✅ | Test particle effects visibility |
| shimmer-text | ✅ | ✅ | Verify shimmer effect contrast |
| dynamic-text | ✅ | ✅ | Test text transitions |
| type-writer | ✅ | ✅ | Verify cursor visibility |
| attract-button | ✅ | ✅ | Test magnetic effect |
| beams-background | ✅ | ✅ | Verify beam visibility and contrast |

---

## 🔍 Theme Testing Checklist

### Visual Testing
- [ ] All components render correctly in light theme
- [ ] All components render correctly in dark theme
- [ ] Theme switching is smooth without flicker
- [ ] Colors have sufficient contrast in both themes
- [ ] Shadows and effects work in both themes
- [ ] Gradients are visible in both themes

### Functional Testing
- [ ] Theme toggle works correctly
- [ ] System preference detection works
- [ ] Theme preference persists in localStorage
- [ ] All animations work in both themes
- [ ] Interactive elements maintain functionality

### Accessibility Testing
- [ ] WCAG AA contrast ratios met in both themes
- [ ] Focus indicators visible in both themes
- [ ] Screen reader compatibility maintained
- [ ] Keyboard navigation works in both themes

### Responsive Testing
- [ ] Mobile (320px+) works in both themes
- [ ] Tablet (768px+) works in both themes
- [ ] Desktop (1024px+) works in both themes
- [ ] Ultra-wide (1920px+) works in both themes

---

## 🐛 Common Theme Issues & Solutions

### Issue 1: Low Contrast in Dark Mode
```css
/* Solution: Adjust color variables */
:root {
  --foreground: 222.2 84% 4.9%;
  --background: 0 0% 100%;
}

.dark {
  --foreground: 210 40% 98%;
  --background: 222.2 84% 4.9%;
}
```

### Issue 2: Invisible Particles in Light Mode
```typescript
// Solution: Adjust particle colors based on theme
const particleColor = theme === 'dark' ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.3)';
```

### Issue 3: Gradient Not Visible
```css
/* Solution: Use theme-aware gradients */
.gradient-button {
  background: linear-gradient(
    to right,
    hsl(var(--primary)),
    hsl(var(--primary) / 0.8)
  );
}
```

---

## ✅ Verification

- [ ] Matches wireframes in both themes
- [ ] Uses design tokens consistently
- [ ] Responsive (320px-1920px) in both themes
- [ ] Theme switching works (light/dark)
- [ ] Accessible (WCAG AA) in both themes
- [ ] No console errors in either theme
- [ ] All Kokonut UI components work correctly
- [ ] Animations are smooth in both themes
- [ ] Theme preference persists

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI
