# React Component Patterns

## Component Props
```typescript
// ✅ ALWAYS define props interfaces
interface ButtonProps extends React.ComponentPropsWithoutRef<'button'> {
  variant?: 'primary' | 'secondary';
  isLoading?: boolean;
}

export function Button({ variant = 'primary', children, ...props }: ButtonProps) {
  return <button {...props}>{children}</button>;
}
```

## Hooks Best Practices
- Include ALL dependencies in useEffect dependency arrays
- Use `useCallback` for functions passed as props to prevent re-renders
- Use `useMemo` for expensive calculations only

```typescript
// ✅ Proper dependency array
useEffect(() => {
  if (!userId) return;
  fetchUserData(userId);
}, [userId]); // Include userId

// ❌ Missing dependencies
useEffect(() => {
  fetchUserData(userId);
}, []); // WRONG - userId should be included
```

## Component Structure
1. Props interface
2. Component function
3. Hooks (useState, useEffect, etc.)
4. Event handlers
5. Early returns (loading, error states)
6. Main render

```typescript
export function UserProfile({ userId }: { userId: string }) {
  // 1. Hooks
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 2. Effects
  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setIsLoading(false));
  }, [userId]);

  // 3. Early returns
  if (isLoading) return <Skeleton />;
  if (!user) return <NotFound />;

  // 4. Main render
  return <div>{user.name}</div>;
}
```