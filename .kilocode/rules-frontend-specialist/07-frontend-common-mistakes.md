# Common Mistakes to Avoid

## TypeScript
❌ **NEVER DO:**
```typescript
function processData(data: any) { } // NO 'any'
const user: any = await getUser();   // NO 'any'
```

✅ **ALWAYS DO:**
```typescript
function processData(data: unknown) {
  if (isValidData(data)) {
    // Now TypeScript knows the type
  }
}
```

## React State
❌ **NEVER DO:**
```typescript
const [items, setItems] = useState([]);
items.push(newItem); // Mutating state directly
```

✅ **ALWAYS DO:**
```typescript
const [items, setItems] = useState<Item[]>([]);
setItems([...items, newItem]); // Immutable update
```

## Server/Client Components
❌ **NEVER DO:**
```typescript
'use client';

// Don't fetch data in client components with async/await
export default async function Page() {
  const data = await fetch('/api/data'); // WRONG
}
```

✅ **ALWAYS DO:**
```typescript
// Fetch in Server Component
export default async function Page() {
  const data = await fetch('/api/data'); // RIGHT
  return <ClientComponent data={data} />;
}
```

## Semantic HTML
❌ **NEVER DO:**
```typescript
<div onClick={handleClick}>Click me</div>
<img src="photo.jpg" />
```

✅ **ALWAYS DO:**
```typescript
<button onClick={handleClick}>Click me</button>
<img src="photo.jpg" alt="User profile" />
```

## Performance
❌ **NEVER DO:**
```typescript
// Don't create functions in render
<button onClick={() => handleClick(id)}>Click</button>

// Don't skip memoization for expensive calculations
const total = items.reduce((sum, item) => sum + item.price, 0);
```

✅ **ALWAYS DO:**
```typescript
// Use useCallback for event handlers
const handleItemClick = useCallback((id: string) => {
  handleClick(id);
}, [handleClick]);

<button onClick={() => handleItemClick(id)}>Click</button>

// Use useMemo for expensive calculations
const total = useMemo(
  () => items.reduce((sum, item) => sum + item.price, 0),
  [items]
);
```

## Console Logs
- Remove console.logs before committing
- Use proper logging library for production
- Never log sensitive information