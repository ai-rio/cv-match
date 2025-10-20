# Data Fetching & Forms

## Server Actions
```typescript
// ✅ ALWAYS add 'use server' at top of Server Actions file
'use server';

import { revalidatePath } from 'next/cache';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  // 1. Validate input
  const result = schema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  });

  if (!result.success) {
    return { error: result.error.flatten().fieldErrors };
  }

  // 2. Database operation
  const user = await db.user.create({ data: result.data });

  // 3. Revalidate cache
  revalidatePath('/users');

  return { success: true, user };
}
```

## Form Validation
- ALWAYS validate on both client AND server
- Use Zod for schema validation
- Define schema once, reuse for client and server

```typescript
// lib/schemas/user.ts
import { z } from 'zod';

export const userSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
});

export type UserFormData = z.infer<typeof userSchema>;
```

## Data Fetching in Server Components
```typescript
// ✅ Direct async/await in Server Components
export default async function UsersPage() {
  const users = await db.user.findMany();
  return <UserList users={users} />;
}
```

## Client-Side Data Fetching (when needed)
- Use SWR or React Query for client-side fetching
- Include loading and error states
- Implement proper error boundaries