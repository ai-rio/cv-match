# Styling & UI Guidelines

## Tailwind CSS
- Use `cn()` utility from `@/lib/utils` for conditional classes
- Mobile-first approach: base styles are mobile, use `md:`, `lg:` for larger screens
- Use Tailwind utility classes, avoid custom CSS when possible

```typescript
import { cn } from '@/lib/utils';

<div className={cn(
  'flex items-center gap-2', // Base classes
  'md:gap-4',                // Tablet+
  isActive && 'bg-blue-500', // Conditional
  className                  // Allow override
)} />
```

## Responsive Design Pattern
```typescript
<div className="
  flex flex-col        // Mobile: stack vertically
  md:flex-row          // Tablet+: horizontal
  gap-4 md:gap-6       // Progressive spacing
  p-4 md:p-6 lg:p-8    // Responsive padding
">
  <aside className="w-full md:w-64">Sidebar</aside>
  <main className="flex-1">Content</main>
</div>
```

## shadcn/ui Components
- Import from `@/components/ui/[component-name]`
- DO NOT modify shadcn component files directly
- Create wrapper components if customization needed
- Use the `cn()` utility for className overrides

## Accessibility
- ALWAYS include `alt` text for images
- Use semantic HTML: `<button>` not `<div onClick>`
- Include ARIA labels when needed
- Ensure keyboard navigation works