# 04 - Kokonut UI Installation

**Agent**: `frontend-specialist`
**Phase**: 2
**Duration**: 3h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement animated components following design system specs using Kokonut UI.

---

## 📋 Key Tasks

1. Review design system docs
2. Install Kokonut UI components
3. Implement components/pages
4. Apply theme styling
5. Test responsive behavior
6. Verify accessibility

---

## 📚 Reference

- [Design System](../../design-system/README.md)
- [Wireframes](../../design-system/wireframes.md)
- [Components](../../design-system/components.md)
- [Kokonut UI Migration Guide](_design-reference/KOKONUT-UI-MIGRATION-GUIDE.md)

---

## 🔧 Installation Commands

```bash
# Navigate to frontend
cd frontend

# Install Kokonut UI packages
bun add @kokonutui/react

# Install required dependencies
bun add framer-motion clsx tailwind-merge

# Verify installation
bun run type-check
```

---

## 📦 Component Installation

Install the specific Kokonut UI components needed for the project:

```bash
# Install core components
bunx shadcn@latest add @kokonutui/shape-hero
bunx shadcn@latest add @kokonutui/bento-grid
bunx shadcn@latest add @kokonutui/card-flip
bunx shadcn@latest add @kokonutui/gradient-button
bunx shadcn@latest add @kokonutui/particle-button
bunx shadcn@latest add @kokonutui/shimmer-text
bunx shadcn@latest add @kokonutui/dynamic-text
bunx shadcn@latest add @kokonutui/type-writer
bunx shadcn@latest add @kokonutui/attract-button
bunx shadcn@latest add @kokonutui/beams-background

# Verify registry
bunx shadcn@latest registry list
# Should show @kokonutui entries ✅
```

---

## 🔍 Type Checking Integration

### Post-Implementation Type Check Instructions

After implementing Kokonut UI components, perform thorough type checking to ensure type safety across all animated components and their dependencies.

### Phase-Specific Type Validation Commands

Execute the following commands in sequence to validate types:

```bash
# Run the project's type check script
bun run type-check

# Strict type checking for Kokonut UI components
npx tsc --noEmit src/components/kokonutui/**/*.tsx --strict

# Type validation for framer-motion dependencies
npx tsc --noEmit --skipLibCheck node_modules/framer-motion/dist/**/*.d.ts

# Bundle analysis to check for type-related issues
bunx bundle-analyzer frontend/.next/static/chunks/**/*.js
```

### Type Validation Checklist

- [ ] All Kokonut UI components compile without type errors
- [ ] Framer-motion animation props are properly typed
- [ ] Component variants maintain type safety
- [ ] Animation hooks have correct return types
- [ ] No type conflicts with existing shadcn components
- [ ] Bundle analysis shows no type-related issues

### Type Error Resolution Guidance

If encountering type errors:

1. **Animation Variant Types**: Ensure variant objects match Framer Motion's `Variants` type
2. **Motion Component Props**: Check that all motion props conform to `MotionProps` interface
3. **Custom Hook Types**: Verify custom animation hooks return proper typed values
4. **Dependency Conflicts**: Resolve type conflicts between Kokonut UI and shadcn components
5. **Bundle Issues**: Address any type-related warnings in bundle analysis

---

## 🗂️ Component Mapping Reference

| Aceternity UI | Kokonut UI | Usage |
|---------------|------------|-------|
| Hero-Parallax | shape-hero | Landing hero section |
| Bento Grid | bento-grid | Feature grid layout |
| 3D-Card-Hover | card-flip | Interactive cards |
| Moving Border | gradient-button, particle-button | Animated buttons |
| Text Reveal | shimmer-text, dynamic-text, type-writer | Text animations |
| Sparkles | particle-button, attract-button, beams-background | Visual effects |

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] All type checks pass
- [ ] Kokonut UI components installed correctly
- [ ] Component registry shows @kokonutui entries

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI