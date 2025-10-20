# Next.js App Router Rules

## Server vs Client Components
- DEFAULT to Server Components (no 'use client' directive)
- ONLY use 'use client' when you need:
  - useState, useEffect, or other React hooks
  - Event handlers (onClick, onChange, etc.)
  - Browser APIs (localStorage, window, etc.)
  - Third-party libraries that require client-side

## Server Components - DO
```typescript
// ✅ Fetch data directly in Server Components
export default async function Page() {
  const data = await fetchData(); // Direct async/await
  return <div>{data.title}</div>;
}
```

## Client Components - DO
```typescript
// ✅ Only when needed
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

## Page Props Pattern
```typescript
// ✅ ALWAYS await params and searchParams
interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function Page({ params, searchParams }: PageProps) {
  const { id } = await params;
  const { q } = await searchParams;
  // Use id and q...
}
```

## Layouts
- Root layout MUST include `<html>` and `<body>` tags
- Layouts receive a `children` prop
- Layouts are Server Components by default