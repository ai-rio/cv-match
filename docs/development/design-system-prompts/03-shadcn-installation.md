# 03 - shadcn/ui Component Installation

**Agent**: `frontend-specialist`  
**Phase**: 2 (Components)  
**Duration**: 3 hours  
**Dependencies**: Phase 1 complete

---

## 🎯 Objective

Install and configure 15 essential shadcn/ui components with design system theming.

---

## 📋 Components to Install

1. **Form** - All form implementations
2. **Select** - Dropdowns
3. **Radio Group** - Payment selection
4. **Checkbox** - Feature lists
5. **Progress** - Credit usage bars
6. **Skeleton** - Loading states
7. **Toast** - Notifications
8. **Tooltip** - Help text
9. **Tabs** - Dashboard sections
10. **Separator** - Visual dividers
11. **Avatar** - User profile
12. **Dropdown Menu** - User menu
13. **Sheet** - Mobile navigation
14. **Table** - History lists
15. **Command** - Search palette

---

## 🔧 Steps

### 1. Initialize shadcn (15 min)
```bash
npx shadcn@latest init
```

Choose options:
- Style: Default
- Base color: Neutral
- CSS variables: Yes

### 2. Install Components (90 min)
```bash
# Install all at once
npx shadcn@latest add form select radio-group checkbox progress skeleton toast tooltip tabs separator avatar dropdown-menu sheet table command
```

### 3. Theme Components (45 min)
Update each component to use design system colors.

### 4. Create Component Playground (30 min)
Build `/components-test` page showing all components.

---

## ✅ Verification

- [ ] All 15 components installed
- [ ] Components use CSS variables
- [ ] Playground page works
- [ ] Theme applies to all components
- [ ] No console errors

---

**Reference**: [shadcn/ui](https://ui.shadcn.com)
