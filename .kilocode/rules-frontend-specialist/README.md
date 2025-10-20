# Frontend Specialist Mode Rules

This directory contains specialized rules for the Frontend Specialist mode in Kilo Code. These rules override the general rules when working in frontend-specific contexts.

## Purpose

The Frontend Specialist mode provides enhanced guidance for:
- React and Next.js best practices
- TypeScript implementation for frontend
- UI/UX design patterns
- Responsive design and accessibility
- State management strategies
- Frontend performance optimization
- Modern CSS and styling approaches

## When to Use

Activate this mode when:
- Building React components and pages
- Implementing Next.js App Router patterns
- Designing responsive layouts
- Working with state management (React hooks, context, etc.)
- Optimizing frontend performance
- Implementing accessibility features
- Creating reusable UI components

## Rule Files

- `01-frontend-core-standards.md` - TypeScript, naming conventions, file paths
- `02-frontend-nextjs-patterns.md` - Next.js App Router, Server/Client components
- `03-frontend-react-patterns.md` - React hooks, component structure
- `04-frontend-styling-ui.md` - Tailwind CSS, responsive design, accessibility
- `05-frontend-data-forms.md` - Server Actions, form validation, data fetching
- `06-frontend-security-errors.md` - Error handling, input validation, security
- `07-frontend-common-mistakes.md` - Anti-patterns and what to avoid
- `08-frontend-next-intl-i18n.md` - Internationalization rules

## Mode-Specific Overrides

These rules take precedence over the general rules in the parent directory when the Frontend Specialist mode is active.

## How to Activate

To activate the Frontend Specialist mode in Kilo Code, use the mode selector or specify the mode when starting a new task. The mode will automatically load these specialized rules and apply them in addition to the general rules.

## Key Principles

The Frontend Specialist mode emphasizes:
- **Type Safety**: Strict TypeScript usage with proper typing
- **Performance**: Optimized rendering and loading strategies
- **Accessibility**: WCAG compliance and inclusive design
- **User Experience**: Intuitive interfaces and smooth interactions
- **Modern Patterns**: Current best practices in React/Next.js development
- **Responsive Design**: Mobile-first approach with progressive enhancement

## Integration with Design System

These rules work in conjunction with the project's design system:
- Use shadcn/ui components as base
- Follow established color schemes and typography
- Implement consistent spacing and layout patterns
- Maintain design system consistency across features