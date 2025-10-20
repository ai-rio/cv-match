# CV-Match Kilo Code Rules

This directory contains rules that guide AI code generation for the CV-Match project.

## 📂 File Structure

### Mode-Specific Rules
Mode-specific rules take precedence over general rules when the corresponding mode is active:

- `rules-backend-specialist/` - Backend Specialist mode rules
  - Backend architecture, security, performance, testing, and more
- `rules-frontend-specialist/` - Frontend Specialist mode rules
  - React/Next.js patterns, UI/UX, TypeScript, styling, and more
- `rules-docker/` - Docker mode rules
  - Dockerfile optimization, Docker Compose, container security, and more

### General Rules (Shared)
Rules are organized by topic and loaded alphabetically:

- `README.md` - This file

## 🎯 Purpose

These rules ensure:
- ✅ Type-safe TypeScript code
- ✅ Proper Next.js 15 patterns (App Router, Server Components)
- ✅ Consistent code style
- ✅ Security best practices
- ✅ Accessibility compliance
- ✅ Performance optimization

## 🚀 How It Works

Kilo Code reads these rules and applies them when generating code. The AI will:
- Follow TypeScript strict typing
- Use Server Components by default
- Implement proper error handling
- Apply security best practices
- Write accessible, semantic HTML
- Use project conventions

### Mode-Specific Rules
When a specific mode is active (e.g., Backend Specialist or Frontend Specialist), Kilo Code will:
1. Load the general rules from this directory
2. Load mode-specific rules from the corresponding mode directory
3. Apply mode-specific rules as overrides to general rules

**Available Modes:**
- **Backend Specialist**: For backend development, API design, database operations
- **Frontend Specialist**: For React/Next.js development, UI/UX, frontend architecture
- **Docker**: For containerization, Dockerfile optimization, and container orchestration

## 📝 Modifying Rules

### Mode-Specific Rules (Recommended)
For most development, use mode-specific rules:
1. Navigate to the appropriate mode directory:
   - `rules-backend-specialist/` for backend development
   - `rules-frontend-specialist/` for frontend development
   - `rules-docker/` for Docker and containerization tasks
2. Create or modify rule files in that directory
3. Mode-specific rules will override general rules when the mode is active

### General Rules (Shared)
To add or modify shared rules:
1. Create a new `.md` file with a numbered prefix (e.g., `01-shared-rule.md`)
2. Keep rules concise and example-driven
3. Use ✅ for good practices, ❌ for anti-patterns
4. Include code examples

## 🔍 Quick Reference

**Always:**
- Use TypeScript with explicit types
- Default to Server Components
- Validate input server-side
- Use `@/` for imports
- Handle errors properly

**Never:**
- Use `any` type
- Mutate state directly
- Skip accessibility
- Trust client input
- Commit console.logs

---

For full Next.js documentation: https://nextjs.org/docs