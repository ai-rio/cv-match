# 01 - CSS Variables & Theme Setup

**Agent**: `frontend-specialist`  
**Phase**: 1 (Foundation)  
**Execution**: Parallel with Prompt 02  
**Duration**: 2 hours  
**Dependencies**: None

---

## 🎯 Objective

Set up the complete CSS variable system with OKLCH colors and implement theme provider for light/dark mode switching.

---

## 📋 Tasks Overview

1. Update `globals.css` with design system CSS variables
2. Set up `next-themes` provider
3. Create theme toggle component
4. Test theme switching
5. Verify color system works

---

## 🔧 Implementation Steps

### Step 1: Update globals.css (30 min)

**Location**: `src/app/globals.css`

**Task**: Replace existing CSS variables with complete design system

```css
/* COPY THIS ENTIRE BLOCK - REPLACE EXISTING :root */

:root {
  /* Background & Foreground */
  --background: oklch(0.9824 0.0013 286.3757);
  --foreground: oklch(0.3211 0 0);
  
  /* Card */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.3211 0 0);
  
  /* Popover */
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.3211 0 0);
  
  /* Primary (Green - Growth & Success) */
  --primary: oklch(0.6487 0.1538 150.3071);
  --primary-foreground: oklch(1 0 0);
  
  /* Secondary (Purple - Innovation & AI) */
  --secondary: oklch(0.6746 0.1414 261.338);
  --secondary-foreground: oklch(1 0 0);
  
  /* Muted */
  --muted: oklch(0.8828 0.0285 98.1033);
  --muted-foreground: oklch(0.5382 0 0);
  
  /* Accent (Blue - Trust & Professionalism) */
  --accent: oklch(0.8269 0.108 211.9627);
  --accent-foreground: oklch(0.3211 0 0);
  
  /* Destructive (Red - Errors & Warnings) */
  --destructive: oklch(0.6368 0.2078 25.3313);
  --destructive-foreground: oklch(1 0 0);
  
  /* Border & Input */
  --border: oklch(0.8699 0 0);
  --input: oklch(0.8699 0 0);
  --ring: oklch(0.6487 0.1538 150.3071);
  
  /* Charts */
  --chart-1: oklch(0.6487 0.1538 150.3071);
  --chart-2: oklch(0.6746 0.1414 261.338);
  --chart-3: oklch(0.8269 0.108 211.9627);
  --chart-4: oklch(0.588 0.0993 245.7394);
  --chart-5: oklch(0.5905 0.1608 148.2409);
  
  /* Sidebar (if using) */
  --sidebar: oklch(0.9824 0.0013 286.3757);
  --sidebar-foreground: oklch(0.3211 0 0);
  --sidebar-primary: oklch(0.6487 0.1538 150.3071);
  --sidebar-primary-foreground: oklch(1 0 0);
  --sidebar-accent: oklch(0.8269 0.108 211.9627);
  --sidebar-accent-foreground: oklch(0.3211 0 0);
  --sidebar-border: oklch(0.8699 0 0);
  --sidebar-ring: oklch(0.6487 0.1538 150.3071);
  
  /* Typography */
  --font-sans: Plus Jakarta Sans, sans-serif;
  --font-serif: Source Serif 4, serif;
  --font-mono: JetBrains Mono, monospace;
  
  /* Radius */
  --radius: 0.5rem;
  
  /* Shadows */
  --shadow-2xs: 0 1px 3px 0px hsl(0 0% 0% / 0.05);
  --shadow-xs: 0 1px 3px 0px hsl(0 0% 0% / 0.05);
  --shadow-sm: 0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 1px 2px -1px hsl(0 0% 0% / 0.1);
  --shadow: 0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 1px 2px -1px hsl(0 0% 0% / 0.1);
  --shadow-md: 0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 2px 4px -1px hsl(0 0% 0% / 0.1);
  --shadow-lg: 0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 4px 6px -1px hsl(0 0% 0% / 0.1);
  --shadow-xl: 0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 8px 10px -1px hsl(0 0% 0% / 0.1);
  --shadow-2xl: 0 1px 3px 0px hsl(0 0% 0% / 0.25);
  
  /* Spacing */
  --spacing: 0.25rem;
}

/* DARK THEME */
.dark {
  /* Background & Foreground */
  --background: oklch(0.2303 0.0125 264.2926);
  --foreground: oklch(0.9219 0 0);
  
  /* Card */
  --card: oklch(0.321 0.0078 223.6661);
  --card-foreground: oklch(0.9219 0 0);
  
  /* Popover */
  --popover: oklch(0.321 0.0078 223.6661);
  --popover-foreground: oklch(0.9219 0 0);
  
  /* Primary (Green stays consistent) */
  --primary: oklch(0.6487 0.1538 150.3071);
  --primary-foreground: oklch(1 0 0);
  
  /* Secondary (Muted Purple) */
  --secondary: oklch(0.588 0.0993 245.7394);
  --secondary-foreground: oklch(0.9219 0 0);
  
  /* Muted */
  --muted: oklch(0.3867 0 0);
  --muted-foreground: oklch(0.7155 0 0);
  
  /* Accent (Vibrant Purple) */
  --accent: oklch(0.6746 0.1414 261.338);
  --accent-foreground: oklch(0.9219 0 0);
  
  /* Destructive (Red stays consistent) */
  --destructive: oklch(0.6368 0.2078 25.3313);
  --destructive-foreground: oklch(1 0 0);
  
  /* Border & Input */
  --border: oklch(0.3867 0 0);
  --input: oklch(0.3867 0 0);
  --ring: oklch(0.6487 0.1538 150.3071);
  
  /* Charts (consistent across themes) */
  --chart-1: oklch(0.6487 0.1538 150.3071);
  --chart-2: oklch(0.588 0.0993 245.7394);
  --chart-3: oklch(0.6746 0.1414 261.338);
  --chart-4: oklch(0.8269 0.108 211.9627);
  --chart-5: oklch(0.5905 0.1608 148.2409);
  
  /* Sidebar */
  --sidebar: oklch(0.2303 0.0125 264.2926);
  --sidebar-foreground: oklch(0.9219 0 0);
  --sidebar-primary: oklch(0.6487 0.1538 150.3071);
  --sidebar-primary-foreground: oklch(1 0 0);
  --sidebar-accent: oklch(0.6746 0.1414 261.338);
  --sidebar-accent-foreground: oklch(0.9219 0 0);
  --sidebar-border: oklch(0.3867 0 0);
  --sidebar-ring: oklch(0.6487 0.1538 150.3071);
}

/* Tailwind theme integration */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
  
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

/* Base styles */
* {
  border-color: var(--border);
}

body {
  background-color: var(--background);
  color: var(--foreground);
  font-family: var(--font-sans);
}
```

### Step 2: Install next-themes (10 min)

```bash
bun install next-themes
```

### Step 3: Update Root Layout (20 min)

**Location**: `src/app/layout.tsx`

```tsx
import { ThemeProvider } from 'next-themes'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-br" suppressHydrationWarning>
      <body className={`antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange={false}
          storageKey="cv-match-theme"
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**Key points:**
- `suppressHydrationWarning` prevents hydration mismatch
- `attribute="class"` uses class-based theming
- `enableSystem` detects OS theme preference
- `storageKey` persists user choice

### Step 4: Create Theme Toggle Component (40 min)

**Location**: `src/components/theme-toggle.tsx`

```tsx
'use client'

import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { theme, setTheme, systemTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <Button variant="ghost" size="icon" className="w-10 h-10">
        <Sun className="h-5 w-5" />
        <span className="sr-only">Toggle theme</span>
      </Button>
    )
  }

  const currentTheme = theme === 'system' ? systemTheme : theme
  const isDark = currentTheme === 'dark'

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="w-10 h-10 transition-colors hover:bg-accent"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {isDark ? (
        <Sun className="h-5 w-5 text-foreground" />
      ) : (
        <Moon className="h-5 w-5 text-foreground" />
      )}
      <span className="sr-only">
        {isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      </span>
    </Button>
  )
}
```

**Features:**
- Handles hydration properly
- Accessible (ARIA labels, keyboard)
- Smooth transitions
- System theme detection
- Icon changes based on theme

### Step 5: Add Toggle to Navigation (20 min)

**Location**: Update your navigation component (header/navbar)

```tsx
import { ThemeToggle } from '@/components/theme-toggle'

export function Navigation() {
  return (
    <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo, nav links, etc. */}
        
        <div className="flex items-center gap-4">
          {/* Other nav items */}
          <ThemeToggle />
        </div>
      </div>
    </nav>
  )
}
```

---

## ✅ Verification Checklist

Test each item before moving to next phase:

### Visual Tests
- [ ] Open app in browser
- [ ] Click theme toggle - page should switch immediately
- [ ] Background color changes (light: near-white, dark: dark blue-gray)
- [ ] Text color inverts appropriately
- [ ] Primary green color stays consistent in both themes
- [ ] Cards have proper background in both themes

### Technical Tests
- [ ] No console errors
- [ ] No hydration warnings
- [ ] Theme persists on page reload
- [ ] System theme detection works (test by changing OS theme)
- [ ] Smooth transitions between themes (no flicker)

### Color Verification
Use browser DevTools to verify CSS variables are applied:

**Light Theme** (check in DevTools):
```css
--background: oklch(0.9824 0.0013 286.3757)
--primary: oklch(0.6487 0.1538 150.3071)
```

**Dark Theme** (check in DevTools):
```css
--background: oklch(0.2303 0.0125 264.2926)
--primary: oklch(0.6487 0.1538 150.3071)  /* Same! */
```

### Accessibility Tests
- [ ] Keyboard navigation: Tab to theme toggle, Enter to activate
- [ ] Screen reader announces current theme
- [ ] Focus indicator visible on toggle button
- [ ] Color contrast meets WCAG AA (4.5:1 minimum)

---

## 🐛 Troubleshooting

### Issue: Hydration Mismatch Warning

**Symptoms**: Console warning about server/client mismatch

**Solution**:
```tsx
// In layout.tsx
<html lang="pt-br" suppressHydrationWarning>

// In ThemeToggle component
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return <LoadingSkeleton />
```

### Issue: Theme Flickers on Page Load

**Symptoms**: Brief flash of wrong theme

**Solution**:
1. Ensure `suppressHydrationWarning` on `<html>`
2. Use `disableTransitionOnChange={false}` in ThemeProvider
3. Add this script to `layout.tsx` before children:

```tsx
<script
  dangerouslySetInnerHTML={{
    __html: `
      try {
        const theme = localStorage.getItem('cv-match-theme') || 'light'
        document.documentElement.classList.add(theme)
      } catch {}
    `,
  }}
/>
```

### Issue: Colors Not Applying

**Symptoms**: Still seeing old colors

**Solution**:
1. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+F5)
2. Clear browser cache
3. Restart dev server
4. Check globals.css is imported in layout.tsx
5. Verify @theme inline is present

### Issue: Toggle Button Not Appearing

**Symptoms**: Theme toggle missing from UI

**Solution**:
1. Check Button component exists (from shadcn)
2. Verify lucide-react icons installed
3. Check import path is correct
4. Ensure navigation component renders

---

## 📊 Performance Considerations

### Theme Switching Performance
- Should be instant (<50ms)
- No layout shifts
- Smooth transitions

### CSS Variable Performance
- OKLCH is well-supported in modern browsers
- Fallbacks not needed for target browsers (2024+)
- CSS variables have minimal performance impact

### Bundle Size
- `next-themes`: ~2KB gzipped
- No additional libraries needed

---

## 🎨 Design System Compliance

### Color Usage
✅ **Correct**:
```tsx
<div className="bg-primary text-primary-foreground">CTA</div>
<Card className="bg-card text-card-foreground">Content</Card>
```

❌ **Incorrect**:
```tsx
<div className="bg-green-600">CTA</div>  {/* Don't use Tailwind colors directly */}
<Card className="bg-white">Content</Card>  {/* Use design tokens */}
```

### Theme-Aware Components
All components should automatically adapt to theme via CSS variables.

No need for conditional classes like:
```tsx
// ❌ Don't do this
<div className={theme === 'dark' ? 'bg-gray-900' : 'bg-white'}>

// ✅ Do this instead
<div className="bg-background">
```

---

## 📝 Documentation

### Add to Project README

```markdown
## Theme System

CV-Match uses a dual-theme system (light/dark) with OKLCH color space for perceptually uniform colors.

### Toggle Theme
Use the theme toggle in the navigation bar or let the system detect your OS preference.

### For Developers
Always use CSS variables from the design system:
- `bg-background` instead of `bg-white`
- `text-foreground` instead of `text-black`
- `bg-primary` for CTAs (green)
- See `/docs/design-system/README.md` for full color palette
```

---

## 🚀 Next Steps

After completing this prompt:

1. **Commit your changes**:
```bash
git add .
git commit -m "feat(design-system): Phase 1.1 - CSS variables and theme provider"
```

2. **Test thoroughly**: Click through entire app with both themes

3. **Proceed to Prompt 02**: Typography & Fonts (can run in parallel)

4. **Checkpoint**: Don't continue to Phase 2 until both 01 and 02 are complete

---

## 📚 Reference

- [Design System Colors](../../design-system/README.md#color-system)
- [OKLCH Color Picker](https://oklch.com)
- [next-themes Documentation](https://github.com/pacocoursey/next-themes)
- [Tailwind CSS Variables](https://tailwindcss.com/docs/customizing-colors#using-css-variables)

---

**Estimated Time**: 2 hours  
**Complexity**: Medium  
**Agent**: frontend-specialist  

**Status**: Ready for implementation ✅
