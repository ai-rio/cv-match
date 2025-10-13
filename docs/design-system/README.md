# 🎨 CV-Match Design System

**Version:** 1.0
**Last Updated:** October 12, 2025
**Status:** Active

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Spacing & Layout](#spacing--layout)
6. [Shadows & Elevation](#shadows--elevation)
7. [Theme Support](#theme-support)
8. [Usage Examples](#usage-examples)

---

## 🎯 Overview

CV-Match's design system is built on modern web standards using:

- **OKLCH Color Space** - Perceptually uniform, accessible colors
- **CSS Variables** - Dynamic theming with light/dark modes
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality component primitives
- **Aceternity UI** - Premium animated components

### Design Goals

✅ **Professional & Trustworthy** - AI-powered career tool
✅ **Modern & Fresh** - Appeal to tech-savvy Brazilian professionals
✅ **Accessible** - WCAG 2.1 AA compliant
✅ **Responsive** - Mobile-first approach
✅ **Performant** - Fast, smooth interactions

---

## 💡 Design Principles

### 1. **Clarity Over Cleverness**

- Clear CTAs (e.g., "Começar Grátis • 3 Créditos")
- Transparent pricing and features
- No hidden costs or surprises

### 2. **Trust Through Design**

- Professional color palette
- Consistent spacing and alignment
- High-quality typography
- Security badges and social proof

### 3. **Delight in Details**

- Smooth animations (Aceternity)
- Microinteractions on hover/click
- Loading states that inform
- Celebrate user wins

### 4. **Inclusive by Default**

- Light and dark modes
- Accessible color contrast (4.5:1 minimum)
- Keyboard navigation support
- Screen reader friendly

### 5. **Brazilian Market Focus**

- Portuguese-first copy
- Local payment methods (PIX)
- LGPD compliance messaging
- Cultural relevance

---

## 🎨 Color System

### Color Philosophy

Our colors are chosen to convey:

- **Green (Primary)** - Growth, success, money (Brazilian context)
- **Purple (Secondary)** - Innovation, AI, premium
- **Blue (Accent)** - Trust, professionalism, stability

### Light Theme Colors

```css
/* Base Colors */
--background: oklch(0.9824 0.0013 286.3757); /* Off-white, warm */
--foreground: oklch(0.3211 0 0); /* Near-black text */

/* Interactive Colors */
--primary: oklch(0.6487 0.1538 150.3071); /* Green - CTAs, success */
--primary-foreground: oklch(1 0 0); /* White text on green */

--secondary: oklch(0.6746 0.1414 261.338); /* Purple - secondary actions */
--secondary-foreground: oklch(1 0 0); /* White text on purple */

--accent: oklch(0.8269 0.108 211.9627); /* Blue - highlights */
--accent-foreground: oklch(0.3211 0 0); /* Dark text on blue */

/* Semantic Colors */
--destructive: oklch(0.6368 0.2078 25.3313); /* Red - errors, warnings */
--destructive-foreground: oklch(1 0 0); /* White text on red */

--muted: oklch(0.8828 0.0285 98.1033); /* Subtle backgrounds */
--muted-foreground: oklch(0.5382 0 0); /* Muted text */

/* UI Elements */
--card: oklch(1 0 0); /* Pure white cards */
--card-foreground: oklch(0.3211 0 0); /* Dark text on cards */

--border: oklch(0.8699 0 0); /* Light borders */
--input: oklch(0.8699 0 0); /* Input borders */
--ring: oklch(0.6487 0.1538 150.3071); /* Focus ring (green) */
```

### Dark Theme Colors

```css
/* Base Colors */
--background: oklch(0.2303 0.0125 264.2926); /* Dark blue-gray */
--foreground: oklch(0.9219 0 0); /* Off-white text */

/* Interactive Colors */
--primary: oklch(0.6487 0.1538 150.3071); /* Green (same as light) */
--primary-foreground: oklch(1 0 0); /* White text */

--secondary: oklch(0.588 0.0993 245.7394); /* Muted purple */
--secondary-foreground: oklch(0.9219 0 0); /* Light text */

--accent: oklch(0.6746 0.1414 261.338); /* Vibrant purple */
--accent-foreground: oklch(0.9219 0 0); /* Light text */

/* Semantic Colors */
--destructive: oklch(0.6368 0.2078 25.3313); /* Red (same as light) */
--destructive-foreground: oklch(1 0 0); /* White text */

--muted: oklch(0.3867 0 0); /* Dark gray backgrounds */
--muted-foreground: oklch(0.7155 0 0); /* Light gray text */

/* UI Elements */
--card: oklch(0.321 0.0078 223.6661); /* Dark card background */
--card-foreground: oklch(0.9219 0 0); /* Light text on cards */

--border: oklch(0.3867 0 0); /* Dark borders */
--input: oklch(0.3867 0 0); /* Dark input borders */
--ring: oklch(0.6487 0.1538 150.3071); /* Focus ring (green) */
```

### Chart Colors (Data Visualization)

Both themes use the same chart colors for consistency:

```css
--chart-1: oklch(0.6487 0.1538 150.3071); /* Green */
--chart-2: oklch(0.6746 0.1414 261.338); /* Purple */
--chart-3: oklch(0.8269 0.108 211.9627); /* Blue */
--chart-4: oklch(0.588 0.0993 245.7394); /* Muted purple */
--chart-5: oklch(0.5905 0.1608 148.2409); /* Teal */
```

### Color Usage Guidelines

| Color                  | Use For                                  | Don't Use For             |
| ---------------------- | ---------------------------------------- | ------------------------- |
| **Primary (Green)**    | Main CTAs, success states, paid features | Errors, warnings          |
| **Secondary (Purple)** | Secondary actions, premium features      | Primary CTAs              |
| **Accent (Blue)**      | Links, info badges, highlights           | Primary CTAs              |
| **Destructive (Red)**  | Errors, delete actions, warnings         | Success, positive actions |
| **Muted**              | Disabled states, subtle backgrounds      | Important content         |

### Accessibility Requirements

All color combinations meet **WCAG 2.1 AA** standards:

- Normal text: 4.5:1 contrast minimum
- Large text (18px+): 3:1 contrast minimum
- Interactive elements: Clear focus indicators

**Test your colors:**

```bash
# Use WebAIM Contrast Checker
https://webaim.org/resources/contrastchecker/
```

---

## 📝 Typography

### Font Families

```css
--font-sans: Plus Jakarta Sans, sans-serif; /* Body, UI */
--font-serif: Source Serif 4, serif; /* Headers, emphasis */
--font-mono: JetBrains Mono, monospace; /* Code, data */
```

### Font Loading

Fonts are loaded via Google Fonts (or self-hosted for better performance):

```tsx
import {
  Plus_Jakarta_Sans,
  Source_Serif_4,
  JetBrains_Mono,
} from "next/font/google";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-serif",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});
```

### Type Scale

| Size     | Usage           | Tailwind Class | CSS             |
| -------- | --------------- | -------------- | --------------- |
| **4xl**  | Hero headlines  | `text-4xl`     | 2.25rem / 36px  |
| **3xl**  | Page titles     | `text-3xl`     | 1.875rem / 30px |
| **2xl**  | Section headers | `text-2xl`     | 1.5rem / 24px   |
| **xl**   | Card titles     | `text-xl`      | 1.25rem / 20px  |
| **lg**   | Subheadings     | `text-lg`      | 1.125rem / 18px |
| **base** | Body text       | `text-base`    | 1rem / 16px     |
| **sm**   | Small text      | `text-sm`      | 0.875rem / 14px |
| **xs**   | Captions        | `text-xs`      | 0.75rem / 12px  |

### Font Weights

| Weight  | Name     | Usage               | Tailwind Class  |
| ------- | -------- | ------------------- | --------------- |
| **700** | Bold     | Headlines, emphasis | `font-bold`     |
| **600** | Semibold | Subheads, buttons   | `font-semibold` |
| **500** | Medium   | Labels, strong body | `font-medium`   |
| **400** | Regular  | Body text           | `font-normal`   |

### Typography Examples

```tsx
{
  /* Hero Headline */
}
<h1 className="font-serif text-4xl md:text-5xl font-bold">
  Otimize seu Currículo com IA
</h1>;

{
  /* Section Header */
}
<h2 className="font-sans text-2xl font-semibold">Como Funciona</h2>;

{
  /* Body Text */
}
<p className="font-sans text-base font-normal text-foreground">
  Nossa IA analisa seu currículo e otimiza para passar pelos sistemas ATS das
  empresas.
</p>;

{
  /* Small Print */
}
<p className="font-sans text-xs text-muted-foreground">
  *Créditos não expiram
</p>;

{
  /* Code/Data */
}
<code className="font-mono text-sm bg-muted px-2 py-1 rounded">
  85% match score
</code>;
```

### Line Height

- **Headlines:** `leading-tight` (1.25)
- **Body:** `leading-normal` (1.5)
- **Captions:** `leading-relaxed` (1.625)

### Letter Spacing

```css
--tracking-normal: 0em; /* Default */
```

Headlines can use tighter tracking:

```tsx
<h1 className="tracking-tight">Headline</h1>
```

---

## 📐 Spacing & Layout

### Spacing Scale

Based on `--spacing: 0.25rem` (4px base unit):

| Tailwind | Value   | Pixels | Usage             |
| -------- | ------- | ------ | ----------------- |
| `p-0`    | 0       | 0px    | No padding        |
| `p-1`    | 0.25rem | 4px    | Tight spacing     |
| `p-2`    | 0.5rem  | 8px    | Icon padding      |
| `p-3`    | 0.75rem | 12px   | Button padding    |
| `p-4`    | 1rem    | 16px   | Card padding      |
| `p-6`    | 1.5rem  | 24px   | Section padding   |
| `p-8`    | 2rem    | 32px   | Component spacing |
| `p-12`   | 3rem    | 48px   | Section gaps      |
| `p-16`   | 4rem    | 64px   | Hero spacing      |
| `p-24`   | 6rem    | 96px   | Large gaps        |

### Container Widths

```tsx
{
  /* Default Container */
}
<div className="container mx-auto px-4 sm:px-6 lg:px-8">
  {/* Max width: 1280px */}
</div>;

{
  /* Narrow Container (forms, text) */
}
<div className="max-w-2xl mx-auto px-4">{/* Max width: 672px */}</div>;

{
  /* Wide Container (dashboard) */
}
<div className="max-w-7xl mx-auto px-4">{/* Max width: 1280px */}</div>;
```

### Grid System

```tsx
{
  /* Two Column */
}
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
</div>;

{
  /* Three Column */
}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>;

{
  /* Pricing Grid */
}
<div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
  {pricingTiers.map((tier) => (
    <PricingCard {...tier} />
  ))}
</div>;
```

### Breakpoints

| Breakpoint | Min Width | Usage            |
| ---------- | --------- | ---------------- |
| `sm`       | 640px     | Mobile landscape |
| `md`       | 768px     | Tablet           |
| `lg`       | 1024px    | Desktop          |
| `xl`       | 1280px    | Large desktop    |
| `2xl`      | 1536px    | Extra large      |

---

## 🌑 Shadows & Elevation

### Shadow Scale

```css
--shadow-2xs: 0 1px 3px 0px hsl(0 0% 0% / 0.05);
--shadow-xs: 0 1px 3px 0px hsl(0 0% 0% / 0.05);
--shadow-sm:
  0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 1px 2px -1px hsl(0 0% 0% / 0.1);
--shadow: 0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 1px 2px -1px hsl(0 0% 0% / 0.1);
--shadow-md:
  0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 2px 4px -1px hsl(0 0% 0% / 0.1);
--shadow-lg:
  0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 4px 6px -1px hsl(0 0% 0% / 0.1);
--shadow-xl:
  0 1px 3px 0px hsl(0 0% 0% / 0.1), 0 8px 10px -1px hsl(0 0% 0% / 0.1);
--shadow-2xl: 0 1px 3px 0px hsl(0 0% 0% / 0.25);
```

### Usage Guidelines

| Shadow      | Usage                  | Tailwind Class |
| ----------- | ---------------------- | -------------- |
| **2xs/xs**  | Subtle borders, inputs | `shadow-xs`    |
| **sm**      | Buttons, small cards   | `shadow-sm`    |
| **default** | Cards, dropdowns       | `shadow`       |
| **md**      | Raised cards           | `shadow-md`    |
| **lg**      | Modals, popovers       | `shadow-lg`    |
| **xl**      | Sticky headers         | `shadow-xl`    |
| **2xl**     | Overlays, dialogs      | `shadow-2xl`   |

### Examples

```tsx
{
  /* Card */
}
<Card className="shadow-md hover:shadow-lg transition-shadow">
  {/* ... */}
</Card>;

{
  /* Button */
}
<Button className="shadow-sm hover:shadow-md">Click me</Button>;

{
  /* Modal */
}
<Dialog>
  <DialogContent className="shadow-2xl">{/* ... */}</DialogContent>
</Dialog>;
```

---

## 🌓 Theme Support

### Light/Dark Mode Toggle

```tsx
"use client";

import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="p-2 rounded-md border border-border hover:bg-accent"
    >
      {theme === "dark" ? (
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </button>
  );
}
```

### Theme Provider Setup

```tsx
// app/layout.tsx
import { ThemeProvider } from "next-themes";

export default function RootLayout({ children }) {
  return (
    <html lang="pt-br" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### System Preference Detection

```tsx
// Automatically follows user's system preference
<ThemeProvider
  attribute="class"
  defaultTheme="system"  // 👈 Follows OS setting
  enableSystem
>
```

### Per-Component Theme Overrides

```tsx
{
  /* Force light theme for specific section */
}
<div className="light">
  <Card>Always light theme</Card>
</div>;

{
  /* Force dark theme */
}
<div className="dark">
  <Card>Always dark theme</Card>
</div>;
```

### Theme-Specific Styling

```tsx
{
  /* Background changes based on theme */
}
<div className="bg-background text-foreground">Content</div>;

{
  /* Conditional classes */
}
<div className="bg-white dark:bg-gray-900">Content</div>;

{
  /* Custom colors per theme */
}
<div className="bg-blue-100 dark:bg-blue-900">Content</div>;
```

### Testing Themes

```tsx
// Force themes in Storybook or tests
<div className="light">
  <YourComponent />
</div>

<div className="dark">
  <YourComponent />
</div>
```

---

## 🎯 Usage Examples

### Button Variants

```tsx
import { Button } from "@/components/ui/button";

{
  /* Primary CTA */
}
<Button className="bg-primary text-primary-foreground hover:bg-primary/90">
  Começar Grátis
</Button>;

{
  /* Secondary */
}
<Button variant="outline">Ver Planos</Button>;

{
  /* Destructive */
}
<Button variant="destructive">Excluir Conta</Button>;

{
  /* Ghost */
}
<Button variant="ghost">Cancelar</Button>;
```

### Card Layouts

```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

<Card className="hover:shadow-lg transition-shadow">
  <CardHeader>
    <CardTitle className="text-xl font-semibold">Plano Pro</CardTitle>
    <CardDescription>O mais escolhido por profissionais</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="text-3xl font-bold text-primary mb-4">R$ 29,90</div>
    <ul className="space-y-2">
      <li>✓ 50 otimizações por mês</li>
      <li>✓ IA avançada</li>
      <li>✓ Suporte prioritário</li>
    </ul>
  </CardContent>
</Card>;
```

### Form Inputs

```tsx
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    placeholder="seu@email.com"
    className="w-full"
  />
</div>;
```

### Alert Messages

```tsx
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle, AlertCircle } from "lucide-react";

{
  /* Success */
}
<Alert className="bg-primary/10 border-primary">
  <CheckCircle className="h-4 w-4 text-primary" />
  <AlertDescription>Currículo otimizado com sucesso!</AlertDescription>
</Alert>;

{
  /* Error */
}
<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertDescription>
    Erro ao processar arquivo. Tente novamente.
  </AlertDescription>
</Alert>;
```

### Badge Components

```tsx
import { Badge } from '@/components/ui/badge'

<Badge variant="default">Mais Popular</Badge>
<Badge variant="secondary">Novo</Badge>
<Badge variant="outline">Grátis</Badge>
<Badge variant="destructive">Esgotado</Badge>
```

---

## 📚 Additional Resources

### Design Tools

- **Figma:** [CV-Match Design File](#) (TBD)
- **Color Tool:** [OKLCH Color Picker](https://oklch.com)
- **Contrast Checker:** [WebAIM](https://webaim.org/resources/contrastchecker/)

### Component Libraries

- **shadcn/ui:** [Documentation](https://ui.shadcn.com)
- **Aceternity UI:** [Components](https://ui.aceternity.com)
- **Tailwind CSS:** [Documentation](https://tailwindcss.com)

### Fonts

- **Plus Jakarta Sans:** [Google Fonts](https://fonts.google.com/specimen/Plus+Jakarta+Sans)
- **Source Serif 4:** [Google Fonts](https://fonts.google.com/specimen/Source+Serif+4)
- **JetBrains Mono:** [Google Fonts](https://fonts.google.com/specimen/JetBrains+Mono)

---

## 🔄 Version History

| Version | Date       | Changes                             |
| ------- | ---------- | ----------------------------------- |
| 1.0     | 2025-10-12 | Initial design system documentation |

---

## 📞 Questions or Feedback?

Contact the design team or open an issue in the repository.

**Maintained by:** CV-Match Design Team
**Last Review:** October 12, 2025
