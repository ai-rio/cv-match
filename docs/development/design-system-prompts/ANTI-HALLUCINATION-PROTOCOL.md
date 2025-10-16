# 🚨 ANTI-HALLUCINATION PROTOCOL

**Purpose:** Prevent AI agents from hallucinating during design system implementation  
**Status:** CRITICAL - READ BEFORE EXECUTING ANY PROMPTS  
**Version:** 1.0  
**Last Updated:** October 16, 2025

---

## ⚠️ CRITICAL INFORMATION FOR AI AGENTS

### **REALITY CHECK:**

Before executing prompts 03-04 (Aceternity UI installation), you MUST understand:

| Registry | Status | Action |
|----------|--------|--------|
| shadcn/ui (@shadcn) | ✅ **REAL** | Use directly as documented |
| Aceternity UI | ❌ **UNVERIFIED** | Verify first, fallback to custom |
| @kibo-ui | ❌ **HYPOTHETICAL** | Use custom implementations |
| @ai-sdk | ❌ **HYPOTHETICAL** | Use standard libraries |

### **MANDATORY VERIFICATION BEFORE PROMPT 04:**

```bash
# Before executing 04-aceternity-installation.md, run:
bunx shadcn@latest registry list

# Expected outcomes:
# ✅ If Aceternity appears → Follow prompt as-is
# ❌ If Aceternity NOT listed → Use FALLBACK_STRATEGY.md
```

---

## 🛡️ Protection Mechanisms

### **1. Pre-Flight Checklist (Before Each Prompt)**

```markdown
□ Read the prompt objective
□ Identify external dependencies (registries, packages)
□ Verify dependencies actually exist
□ If unavailable → Use fallback strategy
□ Document what works vs. what was planned
```

### **2. Verification Commands**

```bash
# Verify shadcn component availability
bunx shadcn@latest search [component-name]

# Verify npm package existence
npm view [package-name]

# Verify registry availability
bunx shadcn@latest registry list
```

### **3. Fallback Decision Tree**

```
Component needed?
├─→ Check if in shadcn/ui → Use it ✅
├─→ NOT in shadcn/ui → Check npm registry
│   ├─→ Package exists → Install from npm ✅
│   └─→ Package doesn't exist → Build custom ⚠️
└─→ Unknown → STOP and verify first 🚨
```

---

## 📋 Enhanced Prompt Execution Protocol

### **Standard Execution (Prompts 01-03, 05-10):**

```markdown
1. Read prompt objective
2. Execute tasks as documented
3. Run verification checklist
4. Commit and proceed
```

### **Enhanced Execution (Prompt 04 - Aceternity):**

```markdown
1. Read prompt objective
2. ⚠️ STOP - Run verification first:
   bunx shadcn@latest registry list
3. If Aceternity found:
   → Execute prompt as documented
4. If Aceternity NOT found:
   → Read FALLBACK_STRATEGY.md
   → Execute custom implementation plan
5. Document actual vs. planned approach
6. Run verification checklist
7. Commit and proceed
```

---

## 🔧 Integration with Existing Prompts

### **Updated Execution Flow:**

```
START
  ↓
Read: ANTI-HALLUCINATION-PROTOCOL.md ← NEW STEP
  ↓
PHASE 1: Foundation (4h - PARALLEL)
  ├─→ 01-css-theme-setup.md ✅
  └─→ 02-typography-fonts.md ✅
  ↓
PHASE 2: Component Library (6h - SEQUENTIAL)
  ├─→ 03-shadcn-installation.md ✅
  └─→ 04-aceternity-installation.md ⚠️ VERIFY FIRST
      └─→ If fail → FALLBACK_STRATEGY.md
  ↓
PHASE 3-5: Continue as documented
  ↓
DONE ✅
```

---

## 📊 Hallucination Risk by Prompt

| Prompt | Risk | Mitigation |
|--------|------|------------|
| 01-css-theme-setup | ✅ LOW | Standard CSS variables |
| 02-typography-fonts | ✅ LOW | Google Fonts (verified) |
| 03-shadcn-installation | ✅ LOW | Official registry |
| 04-aceternity-installation | 🚨 **HIGH** | **Verify first, use fallback** |
| 05-landing-hero | ⚠️ MEDIUM | Depends on 04 success |
| 06-landing-features | ⚠️ MEDIUM | Depends on 04 success |
| 07-dashboard-implementation | ✅ LOW | Uses shadcn only |
| 08-optimize-flow-ui | ✅ LOW | Uses shadcn only |
| 09-theme-testing | ✅ LOW | Standard testing |
| 10-mobile-accessibility | ✅ LOW | Standard testing |

---

## 🎯 Action Items for Implementation

### **Immediate Actions:**

1. ✅ Read this protocol
2. ⚠️ Before running prompt 04:
   ```bash
   bunx shadcn@latest registry list
   ```
3. ⚠️ If Aceternity not found → Read FALLBACK_STRATEGY.md
4. ✅ Continue with remaining prompts

### **Documentation Actions:**

After each prompt, update implementation log:

```markdown
# implementation-log.md

## Prompt 03: shadcn Installation
- Status: ✅ Success
- Components installed: [list]
- Issues: None

## Prompt 04: Aceternity Installation
- Status: ⚠️ Registry not found
- Fallback used: Custom implementations with framer-motion
- Components built: hero-parallax, bento-grid, 3d-card
- Issues: Original registry unavailable, custom solution working
```

---

## 🔍 Red Flags to Watch For

### **Signs of Hallucination:**

- ❌ AI claims to have installed from @aceternity-ui without verification
- ❌ AI references non-existent component APIs
- ❌ AI assumes registry exists without checking
- ❌ Import statements for unavailable packages
- ❌ No fallback strategy when installation fails

### **Correct Behavior:**

- ✅ AI verifies registry/package availability FIRST
- ✅ AI documents when fallback strategy used
- ✅ AI provides working alternative implementations
- ✅ AI runs type-check after each installation
- ✅ AI reports actual vs. planned approach

---

## 📝 Updated SUCCESS CRITERIA

Original prompts remain valid, but add:

### **For Prompt 04 (Aceternity):**

```markdown
Success Criteria:
□ Registry verification completed
□ IF registry found:
  □ Components installed from registry
  □ All imports resolve correctly
□ IF registry NOT found:
  □ Fallback strategy documented
  □ Custom components implemented
  □ Equivalent functionality achieved
□ TypeScript compilation succeeds
□ Visual appearance matches design system
□ No hallucinated component references
```

---

## 🚀 Quick Reference

### **Before Starting Implementation:**

```bash
# 1. Read anti-hallucination protocol
cat docs/development/design-system-prompts/ANTI-HALLUCINATION-PROTOCOL.md

# 2. Verify shadcn/ui works
bunx shadcn@latest search

# 3. Verify Aceternity availability
bunx shadcn@latest registry list

# 4. If Aceternity unavailable, read fallback
cat docs/development/design-system-prompts/FALLBACK_STRATEGY.md

# 5. Start with prompt 01
cat docs/development/design-system-prompts/01-css-theme-setup.md
```

### **During Implementation:**

- ✅ Run type-check after each prompt
- ✅ Verify imports work before proceeding
- ✅ Document actual vs. planned approach
- ⚠️ Stop if registry/package not found
- ⚠️ Use fallback strategy when needed

---

## 🎯 Key Principles

1. **VERIFY FIRST** - Never assume components exist
2. **FALLBACK READY** - Have alternative plan
3. **DOCUMENT REALITY** - Track what works vs. plan
4. **TEST FREQUENTLY** - Type-check after each step
5. **NO ASSUMPTIONS** - Check availability explicitly

---

## 📞 Support

If you encounter hallucinations or unclear instructions:

1. STOP current task
2. Read FALLBACK_STRATEGY.md
3. Verify component/registry availability
4. Document the issue
5. Use alternative approach
6. Continue with next prompt

---

**Remember:** The goal is working functionality, not perfect adherence to hypothetical registries.

---

**Last Updated:** October 16, 2025  
**Maintained by:** CV-Match Design System Team  
**Status:** Active Protection
