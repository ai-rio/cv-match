# 07 - Dashboard Implementation

**Agent**: `frontend-specialist`
**Phase**: 4
**Duration**: 4h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement stats and credit counter following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Implement components/pages
3. Apply theme styling
4. Test responsive behavior
5. Verify accessibility

---

## 📚 Reference

- [Design System](../../design-system/README.md)
- [Wireframes](../../design-system/wireframes.md)
- [Components](../../design-system/components.md)

---

## 🔍 Type Checking Integration

### Post-Implementation Type Check Instructions

After implementing the dashboard components and stats, perform comprehensive type checking to ensure type safety across all dashboard-related code.

### Phase-Specific Type Validation Commands

Execute the following commands in sequence to validate types:

```bash
# Run the project's type check script
bun run type-check

# Strict type checking for dashboard app routes
npx tsc --noEmit src/app/dashboard/**/*.tsx --strict

# Strict type checking for dashboard components
npx tsc --noEmit src/components/dashboard/**/*.tsx --strict

# Type validation for dashboard-specific types
npx tsc --noEmit src/types/dashboard.ts --strict
```

### Type Validation Checklist

- [ ] All dashboard app routes compile without type errors
- [ ] Dashboard components have proper prop types
- [ ] Dashboard type definitions are complete and accurate
- [ ] Stats and credit counter data flow is properly typed
- [ ] API responses match expected type interfaces
- [ ] State management hooks maintain type safety

### Type Error Resolution Guidance

If encountering type errors:

1. **Missing Type Definitions**: Add missing interfaces to `src/types/dashboard.ts`
2. **API Response Types**: Ensure API responses match the defined interfaces
3. **Component Props**: Verify all component props are properly typed
4. **State Management**: Check that useState and useReducer hooks have explicit types
5. **Data Flow**: Trace data from API through components to ensure type consistency

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] All type checks pass

---

**Status**: Template - Expand with full implementation steps
