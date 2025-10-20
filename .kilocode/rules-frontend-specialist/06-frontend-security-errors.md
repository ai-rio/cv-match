# Error Handling & Security

## Error Handling
- ALWAYS handle errors in async operations
- Use try-catch blocks in Server Actions
- Provide user-friendly error messages
- Log errors for debugging

```typescript
// ✅ Proper error handling
try {
  const result = await dangerousOperation();
  return { success: true, data: result };
} catch (error) {
  console.error('Operation failed:', error);
  return { 
    success: false, 
    error: 'Something went wrong. Please try again.' 
  };
}
```

## Error Boundaries
```typescript
// ✅ Wrap components that might error
<ErrorBoundary fallback={<ErrorMessage />}>
  <SuspiciousComponent />
</ErrorBoundary>
```

## Input Validation
- NEVER trust client input
- ALWAYS validate on server side
- Use Zod schemas for validation
- Sanitize user input

```typescript
// ✅ Server-side validation is REQUIRED
'use server';

export async function updateProfile(formData: FormData) {
  // Validate EVERY input
  const result = schema.safeParse(formData);
  if (!result.success) {
    return { error: 'Invalid data' };
  }
  // Now safe to use result.data
}
```

## Environment Variables
- Store secrets in `.env.local` (NEVER commit this file)
- Prefix public vars with `NEXT_PUBLIC_`
- Validate env vars with Zod

```typescript
// lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  API_KEY: z.string(),
});

export const env = envSchema.parse(process.env);
```

## Security Checklist
- [ ] All user input is validated server-side
- [ ] Sensitive data is not exposed to client
- [ ] Environment variables are properly configured
- [ ] Authentication is required for protected routes
- [ ] CSRF protection is enabled