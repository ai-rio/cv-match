# 08 - Optimize Flow UI

**Agent**: `frontend-specialist`
**Phase**: 4
**Duration**: 4h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement upload, form, results following design system specs.

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

After implementing the optimize flow UI components, perform comprehensive type checking to ensure type safety across the upload, form, and results components.

### Phase-Specific Type Validation Commands

Execute the following commands in sequence to validate types:

```bash
# Run the project's type check script
bun run type-check

# Strict type checking for optimize app routes
npx tsc --noEmit src/app/optimize/**/*.tsx --strict

# Strict type checking for file upload components
npx tsc --noEmit src/components/file-upload/**/*.tsx --strict

# Type validation for flow-specific types
npx tsc --noEmit src/types/flow.ts --strict
```

### Type Validation Checklist

- [ ] All optimize app routes compile without type errors
- [ ] File upload components have proper prop types
- [ ] Form validation maintains type safety
- [ ] Results display components are properly typed
- [ ] Flow state management is type-safe
- [ ] File handling operations have correct types

### Type Error Resolution Guidance

If encountering type errors:

1. **File Upload Types**: Ensure file objects and event handlers are properly typed
2. **Form Validation**: Verify form data structures match validation schemas
3. **Results Types**: Check that API response types match results component expectations
4. **Flow State**: Ensure state transitions between upload, form, and results are typed
5. **File Processing**: Verify file processing functions have proper input/output types

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
