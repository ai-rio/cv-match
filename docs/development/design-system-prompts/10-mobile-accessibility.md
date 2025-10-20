# 10 - Mobile & Accessibility

**Agent**: `frontend-specialist`
**Phase**: 5
**Duration**: 2h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement responsive + WCAG for all Kokonut UI components following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Test mobile responsiveness for all Kokonut UI components
3. Verify WCAG AA compliance for animated components
4. Test touch interactions for mobile devices
5. Verify accessibility with screen readers
6. Apply theme styling
7. Test responsive behavior
8. Verify accessibility

---

## 📚 Reference

- [Design System](../../design-system/README.md)
- [Wireframes](../../design-system/wireframes.md)
- [Components](../../design-system/components.md)
- [Kokonut UI Installation](04-kokonut-installation.md)
- [Kokonut UI Migration Guide](_design-reference/KOKONUT-UI-MIGRATION-GUIDE.md)

---

## 🛠️ Testing Steps

### 1. Mobile Responsive Testing

Test all Kokonut UI components across mobile breakpoints:

```typescript
// frontend/components/test/mobile-test-page.tsx
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

export function MobileTestPage() {
  return (
    <div className="min-h-screen space-y-12 p-4 md:p-8">
      {/* Test each component at different breakpoints */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Mobile Component Tests</h2>
        
        {/* Hero Section - Mobile */}
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold mb-2">Shape Hero (Mobile)</h3>
          <ShapeHero className="h-48 md:h-64">
            <ShimmerText className="text-lg md:text-2xl">Mobile Hero</ShimmerText>
          </ShapeHero>
        </div>

        {/* Buttons - Touch Targets */}
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold mb-2">Touch Targets (Min 44x44px)</h3>
          <div className="flex flex-wrap gap-2">
            <GradientButton size="lg" className="min-h-[44px] min-w-[44px]">
              Mobile Button
            </GradientButton>
            <ParticleButton size="lg" className="min-h-[44px] min-w-[44px]">
              Touch Me
            </ParticleButton>
            <AttractButton size="lg" className="min-h-[44px] min-w-[44px]">
              Attract
            </AttractButton>
          </div>
        </div>

        {/* Bento Grid - Responsive */}
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold mb-2">Bento Grid (Responsive)</h3>
          <BentoGrid className="grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Test content */}
          </BentoGrid>
        </div>

        {/* Card Flip - Touch Interaction */}
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold mb-2">Card Flip (Touch)</h3>
          <CardFlip
            frontContent={<div className="p-4 text-center">Tap to Flip</div>}
            backContent={<div className="p-4 text-center">Back Content</div>}
            className="h-32"
          />
        </div>

        {/* Text Animations - Readability */
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold mb-2">Text Animations (Readability)</h3>
          <div className="space-y-2">
            <ShimmerText className="text-base md:text-lg">Readable Shimmer</ShimmerText>
            <DynamicText 
              texts={["Mobile", "Tablet", "Desktop"]} 
              className="text-base md:text-lg"
            />
            <TypeWriter text="Mobile typewriter" className="text-base md:text-lg" />
          </div>
        </div>
      </section>
    </div>
  );
}
```

### 2. Accessibility Testing

Test WCAG compliance for animated components:

```typescript
// frontend/components/test/a11y-test-page.tsx
import { useReducedMotion } from 'framer-motion';
import { 
  ShapeHero, 
  CardFlip, 
  GradientButton,
  ShimmerText
} from '@/components/ui';

export function A11yTestPage() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="min-h-screen space-y-12 p-8">
      <section>
        <h2 className="text-2xl font-bold mb-4">Accessibility Tests</h2>
        
        {/* Respect prefers-reduced-motion */}
        <div className="space-y-4">
          <h3 className="font-semibold">Reduced Motion Support</h3>
          <p className="text-sm text-muted-foreground">
            Current setting: {shouldReduceMotion ? 'Reduced' : 'Normal'}
          </p>
          
          <ShapeHero 
            className="h-64"
            disableAnimations={shouldReduceMotion}
          >
            <ShimmerText 
              disableAnimation={shouldReduceMotion}
              className="text-2xl"
            >
              Accessible Animation
            </ShimmerText>
          </ShapeHero>
        </div>

        {/* Keyboard Navigation */}
        <div className="space-y-4 mt-8">
          <h3 className="font-semibold">Keyboard Navigation</h3>
          <div className="space-x-4">
            <GradientButton>
              Tab to me (Enter to activate)
            </GradientButton>
            <CardFlip
              frontContent={
                <div className="p-4">
                  <h4>Card with Keyboard Support</h4>
                  <p>Press Space or Enter to flip</p>
                </div>
              }
              backContent={
                <div className="p-4">
                  <h4>Back Side</h4>
                  <p>Press Space or Enter to flip back</p>
                </div>
              }
              tabIndex={0}
              role="button"
              aria-label="Flip card"
            />
          </div>
        </div>

        {/* Screen Reader Support */}
        <div className="space-y-4 mt-8">
          <h3 className="font-semibold">Screen Reader Support</h3>
          <div className="space-y-2">
            <div 
              role="status" 
              aria-live="polite"
              className="p-4 border rounded"
            >
              <ShimmerText className="text-lg">
                Important announcement for screen readers
              </ShimmerText>
            </div>
            
            <button
              aria-describedby="button-help"
              className="px-4 py-2 bg-primary text-primary-foreground rounded"
            >
              Accessible Button
            </button>
            <p id="button-help" className="text-sm text-muted-foreground">
              This button has proper ARIA description
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
```

### 3. Touch Interaction Testing

```typescript
// frontend/components/test/touch-test-page.tsx
export function TouchTestPage() {
  return (
    <div className="min-h-screen p-4 space-y-8">
      <h2 className="text-2xl font-bold">Touch Interaction Tests</h2>
      
      {/* Touch Target Sizes */}
      <section>
        <h3 className="font-semibold mb-4">Touch Target Sizes (WCAG 44x44px minimum)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary rounded-lg mx-auto mb-2"></div>
            <span className="text-xs">48x48px ✅</span>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 bg-primary rounded-lg mx-auto mb-2"></div>
            <span className="text-xs">40x40px ❌</span>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary rounded-lg mx-auto mb-2"></div>
            <span className="text-xs">64x64px ✅</span>
          </div>
          <div className="text-center">
            <div className="w-14 h-14 bg-primary rounded-lg mx-auto mb-2"></div>
            <span className="text-xs">56x56px ✅</span>
          </div>
        </div>
      </section>

      {/* Gesture Support */}
      <section>
        <h3 className="font-semibold mb-4">Gesture Support</h3>
        <CardFlip
          frontContent={
            <div className="p-8 text-center">
              <h4>Swipe or Tap to Flip</h4>
              <p className="text-sm text-muted-foreground">
                Supports both touch gestures
              </p>
            </div>
          }
          backContent={
            <div className="p-8 text-center">
              <h4>Back Side</h4>
              <p className="text-sm text-muted-foreground">
                Swipe or tap again
              </p>
            </div>
          }
          className="h-48"
          enableSwipe={true}
        />
      </section>
    </div>
  );
}
```

---

## 🎨 Component Mobile & A11y Coverage

| Component | Mobile Responsive | Touch Targets | WCAG AA | Reduced Motion | Screen Reader |
|-----------|------------------|---------------|---------|----------------|---------------|
| shape-hero | ✅ | ✅ | ✅ | ✅ | ✅ |
| bento-grid | ✅ | ✅ | ✅ | ✅ | ✅ |
| card-flip | ✅ | ✅ | ✅ | ✅ | ✅ |
| gradient-button | ✅ | ✅ | ✅ | ✅ | ✅ |
| particle-button | ✅ | ✅ | ✅ | ✅ | ✅ |
| shimmer-text | ✅ | ✅ | ✅ | ✅ | ✅ |
| dynamic-text | ✅ | ✅ | ✅ | ✅ | ✅ |
| type-writer | ✅ | ✅ | ✅ | ✅ | ✅ |
| attract-button | ✅ | ✅ | ✅ | ✅ | ✅ |
| beams-background | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔍 Mobile & Accessibility Testing Checklist

### Mobile Responsiveness
- [ ] All components work at 320px width
- [ ] Touch targets minimum 44x44px
- [ ] Text readable without zooming (16px minimum)
- [ ] No horizontal scrolling
- [ ] Adequate spacing between touch targets
- [ ] Animations don't cause layout shifts

### WCAG AA Compliance
- [ ] Color contrast ratios met (4.5:1 normal text, 3:1 large text)
- [ ] Focus indicators visible
- [ ] Keyboard navigation works for all interactive elements
- [ ] ARIA labels and descriptions provided
- [ ] Semantic HTML used correctly
- [ ] Form inputs properly labeled

### Motion & Animation
- [ ] Respects prefers-reduced-motion
- [ ] No flashing content (3 flashes per second limit)
- [ ] Animations can be paused/disabled
- [ ] Moving content has controls
- [ ] Auto-updating content can be paused

### Screen Reader Support
- [ ] All images have alt text
- [ ] Dynamic content announced (aria-live regions)
- [ ] Component state changes announced
- [ ] Logical reading order maintained
- [ ] Skip navigation provided

---

## 🐛 Common Mobile & A11y Issues & Solutions

### Issue 1: Touch Targets Too Small
```css
/* Solution: Ensure minimum touch target size */
.kokonut-button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}
```

### Issue 2: Animations Not Respecting Reduced Motion
```typescript
// Solution: Check for reduced motion preference
const shouldReduceMotion = useReducedMotion();

<ShimmerText disableAnimation={shouldReduceMotion}>
  Content
</ShimmerText>
```

### Issue 3: Poor Color Contrast
```css
/* Solution: Use theme-aware colors with proper contrast */
.text-primary {
  color: hsl(var(--foreground)); /* Ensures proper contrast */
}
```

### Issue 4: Keyboard Navigation Issues
```typescript
// Solution: Add proper keyboard support
<CardFlip
  tabIndex={0}
  role="button"
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleFlip();
    }
  }}
>
```

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] All Kokonut UI components mobile-friendly
- [ ] Touch targets meet minimum size requirements
- [ ] Keyboard navigation works
- [ ] Screen reader compatibility verified
- [ ] Reduced motion preferences respected

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI
