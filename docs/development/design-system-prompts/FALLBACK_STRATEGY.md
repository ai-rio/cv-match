# 🔧 FALLBACK STRATEGY - Custom Component Implementations

**Purpose:** Alternative implementations when external registries unavailable  
**Use When:** Aceternity UI or other registries not found  
**Status:** Production-ready custom components

---

## 📋 When to Use This Guide

Use this fallback strategy if:

```bash
# Registry verification fails:
$ bunx shadcn@latest registry list
# Aceternity UI not listed ❌

# OR component installation fails:
$ bunx shadcn@latest add @aceternity-ui/hero-parallax
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

Create these files to replace Aceternity UI components:

1. `hero-parallax.tsx` - Hero section with parallax
2. `bento-grid.tsx` - Feature grid layout
3. `3d-card.tsx` - Interactive 3D cards
4. `text-reveal.tsx` - Animated text
5. `moving-border.tsx` - Animated borders

### **Implementation Note:**

Each component uses:
- ✅ framer-motion for animations
- ✅ shadcn/ui components as foundation
- ✅ Tailwind CSS for styling
- ✅ TypeScript for type safety

---

## ✅ Success Criteria

Custom components are successful when:

- [ ] TypeScript compilation succeeds
- [ ] All components render without errors
- [ ] Animations are smooth (60fps)
- [ ] Responsive design works (mobile/tablet/desktop)
- [ ] Equivalent functionality to original plan

---

## 🎯 Next Steps

After implementing custom components:

1. Update implementation-log.md with fallback details
2. Continue with prompt 05 using custom components
3. Replace Aceternity references with custom imports
4. Proceed with remaining prompts

---

**Last Updated:** October 16, 2025  
**Status:** Production Ready
