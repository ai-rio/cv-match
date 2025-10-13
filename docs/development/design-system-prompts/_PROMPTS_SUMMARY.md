# 📋 Design System Prompts - Quick Reference

**Total**: 10 prompts | 28h dev time | 21h wall time
**Status**: Ready for deployment ✅

---

## 📦 All Prompts

### Phase 1: Foundation (2h wall - PARALLEL)

- `01-css-theme-setup.md` - CSS variables + theme toggle (2h)
- `02-typography-fonts.md` - 3 font families + type scale (2h)

### Phase 2: Components (6h - SEQUENTIAL)

- `03-shadcn-installation.md` - 15 shadcn components (3h)
- `04-aceternity-installation.md` - 8 Aceternity components (3h)

### Phase 3: Landing (3h wall - PARALLEL)

- `05-landing-hero.md` - Hero + parallax (3h)
- `06-landing-features.md` - Features + bento grid (3h)

### Phase 4: App UI (8h - SEQUENTIAL)

- `07-dashboard-implementation.md` - Dashboard + stats (4h)
- `08-optimize-flow-ui.md` - Optimize flow + results (4h)

### Phase 5: Polish (2h wall - PARALLEL)

- `09-theme-testing.md` - Theme coverage (2h)
- `10-mobile-accessibility.md` - Responsive + WCAG (2h)

---

## 🎯 Quick Start

```bash
# 1. Setup
git checkout -b feature/design-system-implementation

# 2. Phase 1 (parallel - 2 terminals)
# Terminal 1: Run prompt 01
# Terminal 2: Run prompt 02

# 3. Continue sequentially through phases
# Test after each phase, commit when complete
```

---

## ✅ Done When

- [ ] Theme toggle works (light/dark)
- [ ] All fonts load (3 families)
- [ ] All components installed (23 total)
- [ ] Landing page matches design
- [ ] Dashboard styled
- [ ] Mobile responsive (320px+)
- [ ] WCAG AA compliant
- [ ] Lighthouse 90+

---

**Agent**: `frontend-specialist` for all prompts
**Dependencies**: [Design System Docs](../../design-system/)
