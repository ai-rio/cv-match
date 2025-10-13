# 02 - Typography & Font Configuration

**Agent**: `frontend-specialist`
**Phase**: 1 (Foundation)
**Execution**: Parallel with Prompt 01
**Duration**: 2 hours
**Dependencies**: None

---

## 🎯 Objective

Implement the complete typography system with three font families (Plus Jakarta Sans, Source Serif 4, JetBrains Mono) and establish the type scale across the application.

---

## 📋 Tasks Overview

1. Configure Google Fonts in Next.js
2. Update Tailwind config with font families
3. Apply typography scale
4. Create typography utility classes
5. Test font loading and performance

---

## 🔧 Implementation Steps

### Step 1: Install & Configure Fonts in Layout (40 min)

**Location**: `src/app/layout.tsx`

```tsx
import {
  Plus_Jakarta_Sans,
  Source_Serif_4,
  JetBrains_Mono,
} from "next/font/google";

// Configure Plus Jakarta Sans (Body & UI)
const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600", "700"],
  display: "swap",
  preload: true,
});

// Configure Source Serif 4 (Headers & Emphasis)
const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-serif",
  weight: ["400", "600", "700"],
  display: "swap",
  preload: true,
});

// Configure JetBrains Mono (Code & Data)
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500", "600"],
  display: "swap",
  preload: false, // Less critical, load later
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="pt-br"
      suppressHydrationWarning
      className={`${jakarta.variable} ${sourceSerif.variable} ${jetbrainsMono.variable}`}
    >
      <body className={`${jakarta.className} antialiased`}>
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
  );
}
```

**Key Configuration Details**:

- `display: 'swap'` - Show fallback font while loading (better UX)
- `preload: true` - Prioritize critical fonts
- `variable` - Creates CSS variable for Tailwind
- `antialiased` - Smooth font rendering

### Step 2: Update Tailwind Config (20 min)

**Location**: `tailwind.config.ts`

Add font family configuration:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "Menlo", "monospace"],
      },
      fontSize: {
        // Type Scale
        xs: ["0.75rem", { lineHeight: "1rem" }], // 12px
        sm: ["0.875rem", { lineHeight: "1.25rem" }], // 14px
        base: ["1rem", { lineHeight: "1.5rem" }], // 16px
        lg: ["1.125rem", { lineHeight: "1.75rem" }], // 18px
        xl: ["1.25rem", { lineHeight: "1.75rem" }], // 20px
        "2xl": ["1.5rem", { lineHeight: "2rem" }], // 24px
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }], // 30px
        "4xl": ["2.25rem", { lineHeight: "2.5rem" }], // 36px
        "5xl": ["3rem", { lineHeight: "1" }], // 48px
        "6xl": ["3.75rem", { lineHeight: "1" }], // 60px
      },
      fontWeight: {
        normal: "400",
        medium: "500",
        semibold: "600",
        bold: "700",
      },
      letterSpacing: {
        tighter: "-0.02em",
        tight: "-0.01em",
        normal: "0em",
        wide: "0.01em",
        wider: "0.02em",
      },
    },
  },
  plugins: [],
};

export default config;
```

### Step 3: Create Typography Component Library (30 min)

**Location**: `src/components/ui/typography.tsx`

Create reusable typography components:

```tsx
import { cn } from "@/lib/utils";

interface TypographyProps {
  children: React.ReactNode;
  className?: string;
}

// H1 - Hero Headlines
export function H1({ children, className }: TypographyProps) {
  return (
    <h1
      className={cn(
        "font-serif text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight",
        "text-foreground",
        className,
      )}
    >
      {children}
    </h1>
  );
}

// H2 - Section Headers
export function H2({ children, className }: TypographyProps) {
  return (
    <h2
      className={cn(
        "font-sans text-2xl md:text-3xl font-semibold tracking-tight",
        "text-foreground",
        className,
      )}
    >
      {children}
    </h2>
  );
}

// H3 - Subsection Headers
export function H3({ children, className }: TypographyProps) {
  return (
    <h3
      className={cn(
        "font-sans text-xl md:text-2xl font-semibold",
        "text-foreground",
        className,
      )}
    >
      {children}
    </h3>
  );
}

// H4 - Card Titles
export function H4({ children, className }: TypographyProps) {
  return (
    <h4
      className={cn(
        "font-sans text-lg md:text-xl font-semibold",
        "text-foreground",
        className,
      )}
    >
      {children}
    </h4>
  );
}

// Body - Paragraph Text
export function P({ children, className }: TypographyProps) {
  return (
    <p
      className={cn(
        "font-sans text-base leading-normal",
        "text-foreground",
        className,
      )}
    >
      {children}
    </p>
  );
}

// Lead - Intro/Lead Paragraph
export function Lead({ children, className }: TypographyProps) {
  return (
    <p
      className={cn(
        "font-sans text-lg md:text-xl leading-relaxed",
        "text-muted-foreground",
        className,
      )}
    >
      {children}
    </p>
  );
}

// Small - Fine Print
export function Small({ children, className }: TypographyProps) {
  return (
    <small
      className={cn(
        "font-sans text-sm leading-none",
        "text-muted-foreground",
        className,
      )}
    >
      {children}
    </small>
  );
}

// Muted - Secondary Text
export function Muted({ children, className }: TypographyProps) {
  return (
    <p className={cn("font-sans text-sm", "text-muted-foreground", className)}>
      {children}
    </p>
  );
}

// Code - Inline Code
export function Code({ children, className }: TypographyProps) {
  return (
    <code
      className={cn(
        "font-mono text-sm",
        "relative rounded bg-muted px-[0.3rem] py-[0.2rem]",
        "text-foreground",
        className,
      )}
    >
      {children}
    </code>
  );
}

// Blockquote
export function Blockquote({ children, className }: TypographyProps) {
  return (
    <blockquote
      className={cn(
        "font-serif text-lg italic",
        "border-l-4 border-primary pl-6",
        "text-muted-foreground",
        className,
      )}
    >
      {children}
    </blockquote>
  );
}
```

### Step 4: Create Typography Demo Page (20 min)

**Location**: `src/app/typography/page.tsx`

Create a test page to verify all typography:

```tsx
import {
  H1,
  H2,
  H3,
  H4,
  P,
  Lead,
  Small,
  Muted,
  Code,
  Blockquote,
} from "@/components/ui/typography";

export default function TypographyPage() {
  return (
    <div className="container max-w-4xl py-12 space-y-12">
      {/* Hero */}
      <section className="space-y-4">
        <H1>Typography System</H1>
        <Lead>
          Testing the complete typography scale with Plus Jakarta Sans, Source
          Serif 4, and JetBrains Mono.
        </Lead>
      </section>

      {/* Headings */}
      <section className="space-y-4">
        <H2>Heading Hierarchy</H2>
        <div className="space-y-3">
          <H1>H1 - Hero Headlines (Serif)</H1>
          <H2>H2 - Section Headers (Sans)</H2>
          <H3>H3 - Subsection Headers (Sans)</H3>
          <H4>H4 - Card Titles (Sans)</H4>
        </div>
      </section>

      {/* Body Text */}
      <section className="space-y-4">
        <H2>Body Text</H2>
        <P>
          This is regular paragraph text using Plus Jakarta Sans. It should be
          highly readable at 16px (1rem) with a line height of 1.5. The font is
          optimized for body copy and UI elements.
        </P>
        <Lead>
          This is lead text - slightly larger and used for introductions or
          emphasis. Great for setting context before diving into details.
        </Lead>
        <Muted>
          This is muted text - used for secondary information that's less
          important but still relevant.
        </Muted>
        <Small>
          This is small text - perfect for fine print, captions, or
          supplementary information.
        </Small>
      </section>

      {/* Code */}
      <section className="space-y-4">
        <H2>Code & Data</H2>
        <P>
          Inline code looks like this: <Code>const theme = 'dark'</Code> using
          JetBrains Mono.
        </P>
        <div className="bg-muted p-4 rounded-lg">
          <code className="font-mono text-sm block">
            {`function OptimizeResume() {
  const [score, setScore] = useState(0)
  return <MatchGauge score={score} />
}`}
          </code>
        </div>
      </section>

      {/* Quote */}
      <section className="space-y-4">
        <H2>Quotes</H2>
        <Blockquote>
          "Depois de otimizar, consegui 3 entrevistas em uma semana!" — Maria
          S., Desenvolvedora Senior
        </Blockquote>
      </section>

      {/* Font Samples */}
      <section className="space-y-4">
        <H2>Font Families</H2>
        <div className="space-y-3">
          <div>
            <Small>Plus Jakarta Sans (Sans-Serif)</Small>
            <p className="font-sans text-2xl">
              The quick brown fox jumps over the lazy dog
            </p>
          </div>
          <div>
            <Small>Source Serif 4 (Serif)</Small>
            <p className="font-serif text-2xl">
              The quick brown fox jumps over the lazy dog
            </p>
          </div>
          <div>
            <Small>JetBrains Mono (Monospace)</Small>
            <p className="font-mono text-2xl">
              The quick brown fox jumps over the lazy dog
            </p>
          </div>
        </div>
      </section>

      {/* Weights */}
      <section className="space-y-4">
        <H2>Font Weights</H2>
        <div className="space-y-2">
          <p className="font-sans text-lg font-normal">Normal (400)</p>
          <p className="font-sans text-lg font-medium">Medium (500)</p>
          <p className="font-sans text-lg font-semibold">Semibold (600)</p>
          <p className="font-sans text-lg font-bold">Bold (700)</p>
        </div>
      </section>
    </div>
  );
}
```

### Step 5: Update Global Styles (10 min)

**Location**: `src/app/globals.css`

Add base typography styles:

```css
/* Add after your CSS variables */

/* Base Typography */
body {
  @apply font-sans antialiased;
  font-feature-settings:
    "rlig" 1,
    "calt" 1;
}

/* Headings */
h1,
h2,
h3,
h4,
h5,
h6 {
  @apply font-semibold tracking-tight;
}

/* Links */
a {
  @apply text-primary underline-offset-4 hover:underline;
}

/* Strong */
strong {
  @apply font-semibold;
}

/* Code */
code {
  @apply font-mono text-sm;
}

/* Smooth font rendering */
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## ✅ Verification Checklist

### Visual Tests

- [ ] Navigate to `/typography` page
- [ ] All three font families load correctly
- [ ] Headings use Source Serif 4 (check in DevTools)
- [ ] Body text uses Plus Jakarta Sans
- [ ] Code uses JetBrains Mono
- [ ] Font weights display correctly (400, 500, 600, 700)
- [ ] Line heights look comfortable
- [ ] Text is crisp and readable

### Technical Tests

- [ ] No FOUT (Flash of Unstyled Text)
- [ ] No FOIT (Flash of Invisible Text)
- [ ] Fonts load with `display: swap`
- [ ] CSS variables (`--font-sans`, etc.) applied correctly
- [ ] Tailwind classes work (`font-sans`, `font-serif`, `font-mono`)
- [ ] No console errors
- [ ] Network tab shows fonts loading

### Performance Tests

- [ ] Lighthouse Performance score 90+
- [ ] Check font file sizes (should be <100KB each)
- [ ] Fonts preload correctly
- [ ] No layout shift (CLS score good)

### Responsive Tests

- [ ] Test on mobile (320px) - text readable at base size
- [ ] Test on tablet (768px) - scale transitions work
- [ ] Test on desktop (1920px) - max sizes appropriate

---

## 🐛 Troubleshooting

### Issue: Fonts Not Loading

**Symptoms**: Fallback fonts showing instead of Google Fonts

**Solution**:

1. Check import statement syntax
2. Verify `className` applied to `<html>` and `<body>`
3. Check network tab for font requests
4. Restart dev server
5. Clear browser cache

```tsx
// ✅ Correct
<html className={`${jakarta.variable} ${sourceSerif.variable} ${jetbrainsMono.variable}`}>
  <body className={jakarta.className}>

// ❌ Incorrect
<html>
  <body className={jakarta.variable}>  {/* Wrong! */}
```

### Issue: FOUT (Flash of Unstyled Text)

**Symptoms**: Text appears in fallback font briefly before switching

**Solution**:

1. Ensure `display: 'swap'` in font config
2. Add `preload: true` for critical fonts
3. Use font-display CSS:

```css
@font-face {
  font-family: "Plus Jakarta Sans";
  font-display: swap;
}
```

### Issue: Font Not Showing in DevTools

**Symptoms**: Computed font family shows fallback

**Solution**:

1. Check if CSS variable is defined
2. Verify Tailwind config has fontFamily extension
3. Inspect element - should see CSS variable in styles
4. Check if `variable` prop matches Tailwind config

### Issue: Wrong Font on Headings

**Symptoms**: H1 showing sans instead of serif

**Solution**:

```tsx
// ✅ Use typography components
<H1>Headline</H1>

// ✅ Or apply class directly
<h1 className="font-serif">Headline</h1>

// ❌ Don't do this
<h1>Headline</h1>  {/* Will use default/body font */}
```

---

## 📊 Performance Optimization

### Font Loading Strategy

**Critical fonts** (preload):

- Plus Jakarta Sans (400, 600) - Body text
- Source Serif 4 (700) - Headlines

**Non-critical fonts** (defer):

- JetBrains Mono - Code blocks
- Extra weights - Loaded on demand

### Font Subsetting

Google Fonts automatically subsets to Latin characters. For Brazilian Portuguese, we're good with `latin` subset.

### File Size Monitoring

Check font sizes in Network tab:

- Sans: ~30-50KB per weight
- Serif: ~40-60KB per weight
- Mono: ~30-40KB per weight

**Total**: <300KB for all fonts (acceptable)

---

## 🎨 Typography Usage Guidelines

### When to Use Each Font

**Plus Jakarta Sans (Sans-Serif)**:

- ✅ Body text, paragraphs
- ✅ UI elements (buttons, forms)
- ✅ Navigation
- ✅ Small text, captions
- ✅ Data labels

**Source Serif 4 (Serif)**:

- ✅ Hero headlines (H1)
- ✅ Marketing copy
- ✅ Emphasis, quotes
- ✅ Emotional/storytelling content
- ❌ Don't use for long body text
- ❌ Don't use in forms/UI

**JetBrains Mono (Monospace)**:

- ✅ Code snippets
- ✅ Technical data
- ✅ Match scores (85%)
- ✅ Credit counts
- ❌ Don't use for regular text
- ❌ Don't use for headings

### Size Recommendations

| Element    | Desktop           | Mobile            | Font          |
| ---------- | ----------------- | ----------------- | ------------- |
| Hero H1    | 4xl-6xl (36-60px) | 3xl-4xl (30-36px) | Serif Bold    |
| Section H2 | 2xl-3xl (24-30px) | xl-2xl (20-24px)  | Sans Semibold |
| Card H3    | xl-2xl (20-24px)  | lg-xl (18-20px)   | Sans Semibold |
| Body       | base (16px)       | base (16px)       | Sans Normal   |
| Small      | sm (14px)         | xs-sm (12-14px)   | Sans Normal   |

---

## 📝 Examples

### Hero Section

```tsx
<section className="text-center space-y-6">
  <H1>Otimize seu Currículo com IA</H1>
  <Lead>3 otimizações grátis • Sem cartão de crédito</Lead>
  <Button size="lg" className="text-lg font-semibold">
    Começar Grátis
  </Button>
</section>
```

### Feature Card

```tsx
<Card>
  <CardHeader>
    <H4>IA Avançada</H4>
  </CardHeader>
  <CardContent>
    <P>Algoritmos que analisam e melhoram seu currículo automaticamente.</P>
  </CardContent>
</Card>
```

### Stats Display

```tsx
<div className="text-center">
  <div className="font-mono text-4xl font-bold text-primary">85%</div>
  <Muted>Score de Compatibilidade</Muted>
</div>
```

---

## 🚀 Next Steps

After completing this prompt:

1. **Commit your changes**:

```bash
git add .
git commit -m "feat(design-system): Phase 1.2 - Typography system with 3 fonts"
```

2. **Test typography page**: Visit `/typography` and verify all styles

3. **Wait for Prompt 01**: Both Phase 1 prompts must complete before Phase 2

4. **Checkpoint Meeting**: Review typography with design team

---

## 📚 Reference

- [Design System Typography](../../design-system/README.md#typography)
- [Google Fonts](https://fonts.google.com)
- [Next.js Font Optimization](https://nextjs.org/docs/app/building-your-application/optimizing/fonts)
- [Web Typography Best Practices](https://fonts.google.com/knowledge)

---

**Estimated Time**: 2 hours
**Complexity**: Medium
**Agent**: frontend-specialist

**Status**: Ready for implementation ✅
