# Core Coding Standards

## TypeScript Requirements
- ALWAYS use TypeScript with strict mode enabled
- NEVER use `any` type - use `unknown` with type guards instead
- All functions MUST have explicit return types
- All function parameters MUST be typed

## Naming Conventions
- Components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`)
- Hooks: `use[Name].ts` (e.g., `useAuth.ts`)
- Constants: `UPPER_SNAKE_CASE`
- Boolean variables: prefix with `is`, `has`, `should`, `can`

## File Paths
- ALWAYS use relative paths from workspace root: `@/components/...` not `../../../components/...`
- Reference files as `@/lib/utils` not `C:/Projects/lib/utils`