# CV-Match Phase 0.8 Design System

## Overview

The CV-Match Phase 0.8 Design System is a comprehensive, Brazilian market-optimized design system built with accessibility, performance, and user experience at its core. It provides a complete set of design tokens, components, and utilities for building consistent, accessible, and beautiful web applications.

## Key Features

- 🎨 **OKLCH Color System**: Modern color space with WCAG 2.1 AA compliance
- 🇧🇷 **Brazilian Market Optimization**: Optimized for Brazilian users and Portuguese content
- ♿ **WCAG 2.1 AA Accessibility**: Full accessibility compliance with testing utilities
- 🌙 **Dark/Light Theme Support**: Seamless theme switching with system preference sync
- 📱 **Mobile-First Design**: Brazilian mobile market optimized responsive design
- 🎯 **TypeScript Safety**: Full TypeScript support with strict type checking
- ⚡ **Performance Optimized**: Lightweight and performant components

## Installation

The design system is integrated into the CV-Match frontend. All components and utilities are available for immediate use.

```bash
# Design system files are located in:
frontend/lib/design-system/
frontend/components/ui/
frontend/contexts/
frontend/lib/accessibility/
```

## Quick Start

### 1. Theme Provider

Wrap your application with the ThemeProvider:

```tsx
'use client';

import { ThemeProvider } from '@/contexts/theme-context';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider defaultTheme="system" enableSystem attribute="class">
      {children}
    </ThemeProvider>
  );
}
```

### 2. Using Components

```tsx
import { Button, Card, Alert, Typography } from '@/components/ui';
import { useTheme } from '@/contexts/theme-context';

export function ExampleComponent() {
  const { theme, toggleTheme } = useTheme();

  return (
    <Card variant="elevated" className="p-6">
      <Typography variant="h2" className="mb-4">
        CV-Match Design System
      </Typography>

      <Typography variant="body-md" className="mb-6">
        Brazilian market optimized design system with full accessibility support.
      </Typography>

      <Button variant="primary" onClick={toggleTheme}>
        Toggle Theme ({theme.mode})
      </Button>

      <Alert variant="success" className="mt-4">
        <AlertTitle>Success!</AlertTitle>
        <AlertDescription>The design system is working perfectly.</AlertDescription>
      </Alert>
    </Card>
  );
}
```

## Color System

### OKLCH Colors

The design system uses OKLCH color space for better perceptual uniformity and wider gamut:

```tsx
import { colors, getColor } from '@/lib/design-system/colors';

// Get a color with automatic theme support
const primaryColor = getColor('primary-500');
const successColor = getColor('success-500');

// Brazilian market specific colors
const brazilianGreen = colors.brazilian.green;
```

### Semantic Colors

Use semantic color tokens for consistent theming:

```css
/* CSS Variables (automatically applied by ThemeProvider */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --success: 142.1 76.2% 36.3%;
  --success-foreground: 355.7 100% 97.3%;
  /* ... more colors */
}
```

## Typography

### Typography Scale

```tsx
import { Typography, Heading, Text } from '@/components/ui/typography';

// Display typography
<Typography variant="display">Hero Title</Typography>

// Semantic headings
<Heading level={1}>Page Title</Heading>
<Heading level={2}>Section Title</Heading>

// Body text
<Text size="lg">Large body text</Text>
<Text size="md">Normal body text</Text>
<Text size="sm">Small body text</Text>

// Special variants
<Typography variant="lead">Lead paragraph</Typography>
<Typography variant="muted">Muted text</Typography>
<Typography variant="gradient">Gradient text</Typography>
```

### Brazilian Portuguese Support

The typography system is optimized for Brazilian Portuguese:

```tsx
import { BrazilianTypography } from '@/components/ui/typography';

<BrazilianTypography.CPF>123.456.789-00</BrazilianTypography.CPF>
<BrazilianTypography.CNPJ>12.345.678/0001-00</BrazilianTypography.CNPJ>
<BrazilianTypography.Currency>1.234,56</BrazilianTypography.Currency>
```

## Components

### Button

```tsx
import { Button, ButtonGroup } from '@/components/ui/button';

// Variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="success">Success</Button>
<Button variant="warning">Warning</Button>
<Button variant="destructive">Destructive</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
<Button size="xl">Extra Large</Button>

// States
<Button loading>Loading</Button>
<Button icon={<Icon />}>With Icon</Button>
<Button success>Success State</Button>

// Button Group
<ButtonGroup>
  <Button variant="outline">Left</Button>
  <Button variant="outline">Middle</Button>
  <Button variant="outline">Right</Button>
</ButtonGroup>
```

### Card

```tsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';

// Basic card
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

// Variants
<Card variant="elevated">Elevated Card</Card>
<Card variant="outlined">Outlined Card</Card>
<Card variant="interactive">Interactive Card</Card>
<Card variant="success">Success Card</Card>

// With media
<CardMedia aspectRatio="landscape" src="/image.jpg" alt="Description" />

// Skeleton loading
<CardSkeleton lines={3} showMedia showAvatar />
```

### Input

```tsx
import { Input, InputGroup, FormField } from '@/components/ui/input';

// Basic input
<Input placeholder="Enter text" />

// Variants
<Input variant="outlined" placeholder="Outlined" />
<Input variant="filled" placeholder="Filled" />
<Input variant="search" placeholder="Search..." />

// States
<Input error placeholder="Error state" />
<Input success placeholder="Success state" />
<Input loading placeholder="Loading..." />

// With icons
<Input
  leftIcon={<Search />}
  rightIcon={<Eye />}
  placeholder="With icons"
/>

// Password input
<Input
  type="password"
  showPasswordToggle
  placeholder="Password"
/>

// Form field
<FormField
  name="email"
  label="Email Address"
  description="We'll never share your email"
  error="Invalid email address"
  required
>
  <Input type="email" placeholder="you@example.com" />
</FormField>
```

### Alert

```tsx
import { Alert, AlertTitle, AlertDescription, AlertList } from '@/components/ui/alert';

// Basic alert
<Alert variant="success">
  <AlertTitle>Success</AlertTitle>
  <AlertDescription>Operation completed successfully</AlertDescription>
</Alert>

// Variants
<Alert variant="destructive">Error message</Alert>
<Alert variant="warning">Warning message</Alert>
<Alert variant="info">Info message</Alert>

// Dismissible
<Alert dismissible onDismiss={() => console.log('dismissed')}>
  Dismissible alert
</Alert>

// Auto-dismiss
<Alert autoDismiss autoDismissDelay={3000}>
  Auto-dismissing alert
</Alert>

// Alert list
<AlertList
  alerts={[
    { id: '1', variant: 'success', title: 'Success', description: 'Item saved' },
    { id: '2', variant: 'warning', title: 'Warning', description: 'Check inputs' },
  ]}
  onDismiss={(id) => console.log('Dismissed', id)}
/>
```

## Theme System

### Using Theme

```tsx
import { useTheme, useThemeColors, useIsDarkTheme } from '@/contexts/theme-context';

function ThemeControls() {
  const { theme, setTheme, toggleTheme } = useTheme();
  const colors = useThemeColors();
  const isDark = useIsDarkTheme();

  return (
    <div>
      <p>Current theme: {theme.mode}</p>
      <p>Resolved theme: {isDark ? 'dark' : 'light'}</p>
      <Button onClick={() => setTheme('light')}>Light</Button>
      <Button onClick={() => setTheme('dark')}>Dark</Button>
      <Button onClick={() => setTheme('system')}>System</Button>
      <Button onClick={toggleTheme}>Toggle</Button>
    </div>
  );
}
```

### CSS Variables

The theme system uses CSS custom properties for dynamic theming:

```css
/* Light theme */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  /* ... */
}

/* Dark theme */
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  /* ... */
}
```

## Accessibility

### WCAG 2.1 AA Compliance

The design system includes comprehensive accessibility utilities:

```tsx
import {
  runAccessibilityAudit,
  checkContrastCompliance,
  announceToScreenReader,
  BrazilianAccessibility,
} from '@/lib/accessibility/wcag-utils';

// Run accessibility audit
const audit = runAccessibilityAudit();
console.log('Accessibility score:', audit.overallScore);
console.log('Recommendations:', audit.recommendations);

// Check color contrast
const contrast = checkContrastCompliance('#ffffff', '#000000');
console.log('Contrast ratio:', contrast.ratio);
console.log('Passes AA:', contrast.passesAA);

// Screen reader announcements
announceToScreenReader('Form submitted successfully', 'polite');

// Brazilian accessibility helpers
const formattedDate = BrazilianAccessibility.formatDateForScreenReader(new Date());
const formattedCurrency = BrazilianAccessibility.formatCurrencyForScreenReader(1234.56);
```

### Focus Management

```tsx
import { getFocusableElements, createFocusTrap } from '@/lib/accessibility/wcag-utils';

// Get focusable elements in a container
const focusable = getFocusableElements(containerRef.current);

// Create focus trap for modals
const cleanup = createFocusTrap(modalRef.current);

// Cleanup when modal closes
useEffect(() => {
  return cleanup;
}, []);
```

## Brazilian Market Features

### Portuguese Language Support

```tsx
// Language attribute is automatically set
<html lang="pt-BR" dir="ltr">

// Brazilian date formatting
const date = new Date();
// "13 de outubro de 2025"

// Brazilian currency formatting
const price = 1234.56;
// "R$ 1.234,56"

// Brazilian document formatting
const cpf = "12345678900";
// "123.456.789-00"
```

### Mobile Optimization

```tsx
// Touch targets meet WCAG minimums (44x44px)
<Button className="touch-target">Accessible Button</Button>

// Brazilian mobile-first responsive design
<div className="w-full sm:w-auto">
  <Button size="lg">Mobile Optimized</Button>
</div>
```

## Customization

### Extending Colors

```tsx
// Add custom colors to the theme
const customColors = {
  brand: {
    50: '#f0f9ff',
    500: '#0ea5e9',
    900: '#0c4a6e',
  },
};
```

### Custom Components

```tsx
// Create components using design system utilities
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const customVariants = cva('base-styles', {
  variants: {
    variant: {
      primary: 'bg-primary text-primary-foreground',
      secondary: 'bg-secondary text-secondary-foreground',
    },
  },
});
```

## Best Practices

### 1. Theme Usage

- Always use semantic color tokens (`primary`, `success`, etc.)
- Let the ThemeProvider handle theme switching
- Test both light and dark themes

### 2. Accessibility

- Ensure minimum touch targets (44x44px)
- Provide alt text for images
- Use semantic HTML elements
- Test keyboard navigation
- Check color contrast ratios

### 3. Brazilian Market

- Use Portuguese for all user-facing text
- Format dates, times, and numbers for Brazilian locale
- Consider Brazilian mobile usage patterns
- Test on common Brazilian devices

### 4. Performance

- Use the design system components (they're optimized)
- Avoid inline styles
- Use CSS variables for dynamic values
- Minimize custom CSS

## Migration Guide

### From Existing Components

1. Replace colors with semantic tokens:

   ```css
   /* Before */
   .button {
     background-color: #0ea5e9;
   }

   /* After */
   .button {
     background-color: hsl(var(--primary));
   }
   ```

2. Update components to use design system:

   ```tsx
   // Before
   <button className="bg-blue-500 text-white px-4 py-2">
     Click me
   </button>

   // After
   <Button variant="primary">Click me</Button>
   ```

3. Add theme provider to app root:
   ```tsx
   <ThemeProvider>
     <App />
   </ThemeProvider>
   ```

## Troubleshooting

### Common Issues

1. **Theme not applying**: Ensure ThemeProvider wraps your app
2. **Color contrast warnings**: Use semantic color tokens
3. **Touch target warnings**: Ensure minimum 44x44px touch targets
4. **TypeScript errors**: Use proper component props

### Getting Help

- Check the component examples in this guide
- Review the accessibility audit results
- Test with Brazilian users for cultural feedback
- Use the browser developer tools for debugging

## Contributing

When contributing to the design system:

1. Follow the Brazilian market optimization guidelines
2. Ensure WCAG 2.1 AA compliance
3. Test both light and dark themes
4. Add TypeScript types for new features
5. Update documentation

---

The CV-Match Phase 0.8 Design System is designed to make building beautiful, accessible, and Brazilian market-optimized web applications effortless. Happy coding!
