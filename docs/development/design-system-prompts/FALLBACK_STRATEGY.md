# 🔧 FALLBACK STRATEGY - Custom Component Implementations

**Purpose:** Alternative implementations when external registries unavailable  
**Use When:** Kokonut UI or other registries not found  
**Status:** Production-ready custom components

---

## 📋 When to Use This Guide

Use this fallback strategy if:

```bash
# Registry verification fails:
$ bunx shadcn@latest registry list
# Kokonut UI not listed ❌

# OR component installation fails:
$ bunx shadcn@latest add @kokonutui/shape-hero
# Error: Registry not found ❌
```

**Action:** Follow custom implementations below instead of prompt 04.

---

## 📦 Dependencies Installation

First, install required packages:

```bash
# Navigate to frontend
cd frontend

# Install animation dependencies
bun add framer-motion clsx tailwind-merge

# Verify installation
bun run type-check
```

---

## 🎨 Custom Component Templates

### **Location:** `frontend/components/custom/`

Create these files to replace Kokonut UI components:

1. `shape-hero.tsx` - Hero section with parallax effects
2. `bento-grid.tsx` - Feature grid layout
3. `card-flip.tsx` - Interactive 3D cards
4. `shimmer-text.tsx` - Animated text reveal
5. `gradient-button.tsx` - Animated gradient buttons
6. `particle-button.tsx` - Buttons with particle effects
7. `dynamic-text.tsx` - Dynamic text animations
8. `type-writer.tsx` - Typewriter effect
9. `attract-button.tsx` - Magnetic button effect
10. `beams-background.tsx` - Animated background beams

### **Implementation Note:**

Each component uses:
- ✅ framer-motion for animations
- ✅ shadcn/ui components as foundation
- ✅ Tailwind CSS for styling
- ✅ TypeScript for type safety

---

## 🗂️ Component Mapping Reference

| Kokonut UI Component | Custom Implementation | Purpose |
|----------------------|----------------------|---------|
| shape-hero | shape-hero.tsx | Landing hero section |
| bento-grid | bento-grid.tsx | Feature grid layout |
| card-flip | card-flip.tsx | Interactive cards |
| gradient-button | gradient-button.tsx | Animated buttons |
| particle-button | particle-button.tsx | Buttons with particles |
| shimmer-text | shimmer-text.tsx | Text reveal animation |
| dynamic-text | dynamic-text.tsx | Dynamic text effects |
| type-writer | type-writer.tsx | Typewriter effect |
| attract-button | attract-button.tsx | Magnetic button effect |
| beams-background | beams-background.tsx | Background animation |

---

## ✅ Success Criteria

Custom components are successful when:

- [ ] TypeScript compilation succeeds
- [ ] All components render without errors
- [ ] Animations are smooth (60fps)
- [ ] Responsive design works (mobile/tablet/desktop)
- [ ] Equivalent functionality to original plan
- [ ] Components follow design system tokens
- [ ] Accessibility standards met (WCAG AA)

---

## 🎯 Next Steps

After implementing custom components:

1. Update implementation-log.md with fallback details
2. Continue with prompt 05 using custom components
3. Replace Kokonut UI references with custom imports
4. Proceed with remaining prompts
5. Test all animations and interactions

---

## 🔧 Custom Component Templates

### Basic Component Structure

```typescript
// Example: shape-hero.tsx
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { forwardRef } from 'react';

interface ShapeHeroProps {
  className?: string;
  children: React.ReactNode;
}

const ShapeHero = forwardRef<HTMLDivElement, ShapeHeroProps>(
  ({ className, children }, ref) => {
    return (
      <motion.div
        ref={ref}
        className={cn('relative overflow-hidden', className)}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        {children}
      </motion.div>
    );
  }
);

ShapeHero.displayName = 'ShapeHero';

export { ShapeHero };
```

---

**Last Updated:** October 20, 2025  
**Status:** Production Ready  
**Updated:** Migrated from Aceternity UI to Kokonut UI
