---
name: base-agent-template
description: Base template with mandatory todo enforcement for all Resume-Matcher agents
model: sonnet
tools: TodoWrite, Read, Write, Bash, Grep, Glob
---

# Base Agent Template with Todo Enforcement

**MANDATORY TODO REQUIREMENTS**: All agents MUST follow these todo patterns without exception.

## Todo Usage Rules (CRITICAL)

### When to Create Todos

- **Complex tasks** requiring 3+ distinct operations
- **Multi-step workflows** (upload → optimize → payment → download)
- **User-provided task lists** (comma-separated, numbered items)
- **Non-trivial operations** that benefit from progress tracking
- **Explicit requests** when users ask for todo organization
- **Multi-language tasks** (TypeScript + Python coordination)

### Todo Lifecycle Management

1. **Create todos immediately** when starting complex tasks
2. **Mark exactly ONE task as in_progress** when beginning work
3. **Complete tasks immediately** when finished (no batching)
4. **Use proper formats**: Both `content` and `activeForm` fields required
5. **Remove completed lists** when all tasks are done

### Required Todo Patterns

```typescript
// MANDATORY: Use this exact pattern
TodoWrite({
  todos: [
    {
      content: 'Implement résumé upload component', // Imperative form
      status: 'in_progress',
      activeForm: 'Implementing résumé upload component', // Present continuous
    },
    {
      content: 'Set up database schema for optimizations', // Imperative form
      status: 'pending',
      activeForm: 'Setting up database schema', // Present continuous
    },
  ],
});
```

### Quality Gates

- ✅ Exactly ONE task `in_progress` at any time
- ✅ Immediate completion marking when task finishes
- ✅ Both `content` and `activeForm` fields present
- ✅ Proper state transitions: pending → in_progress → completed
- ✅ Clear, actionable task descriptions

## Implementation Enforcement

### Agent Prompt Addition

Every agent MUST include this in their system context:

```
MANDATORY TODO USAGE: Use TodoWrite tool for any task requiring 3+ steps or having complexity.
Follow exact patterns: pending → in_progress → completed. Only ONE task in_progress at a time.
Complete tasks immediately when finished. Use both content/activeForm fields correctly.
```

### Tool Requirements

All agents MUST have:

- `TodoWrite` in tools list
- `TodoWrite` in allowedTools for automatic usage

### Validation Hooks

Agents should include reminders:

```
hooks:
  agentSpawn: "echo 'Todo tracking enabled - use TodoWrite for multi-step tasks'"
  userPromptSubmit: "echo 'Remember: Use TodoWrite for complex tasks (3+ steps)'"
```

## Detection Triggers

Agents MUST create todos when detecting:

- Multiple tasks in user request
- Keywords: "implement", "build", "create", "setup", "configure"
- Complex workflows: frontend + backend + database + testing
- Multi-system integrations (Supabase + Stripe + OpenRouter)
- Resume-Matcher specific patterns: upload → optimize → payment → download
- LGPD compliance implementation
- Brazilian localization tasks

## Resume-Matcher Specific Patterns

### Common Task Patterns

```typescript
// Pattern 1: Full Feature Implementation
TodoWrite({
  todos: [
    { content: 'Design frontend component (TypeScript)', status: 'in_progress', activeForm: 'Designing frontend component' },
    { content: 'Implement backend endpoint (Python)', status: 'pending', activeForm: 'Implementing backend endpoint' },
    { content: 'Create database schema (Supabase)', status: 'pending', activeForm: 'Creating database schema' },
    { content: 'Add integration tests (Jest + Pytest)', status: 'pending', activeForm: 'Adding integration tests' },
    { content: 'Update documentation', status: 'pending', activeForm: 'Updating documentation' },
  ],
});

// Pattern 2: Resume Optimization Flow
TodoWrite({
  todos: [
    { content: 'Implement résumé upload validation', status: 'in_progress', activeForm: 'Implementing upload validation' },
    { content: 'Integrate OpenRouter API for AI optimization', status: 'pending', activeForm: 'Integrating OpenRouter API' },
    { content: 'Add Stripe payment verification', status: 'pending', activeForm: 'Adding payment verification' },
    { content: 'Generate DOCX output file', status: 'pending', activeForm: 'Generating DOCX output' },
  ],
});

// Pattern 3: Testing & Quality Assurance
TodoWrite({
  todos: [
    { content: 'Write frontend unit tests (Jest)', status: 'in_progress', activeForm: 'Writing frontend tests' },
    { content: 'Write backend unit tests (Pytest)', status: 'pending', activeForm: 'Writing backend tests' },
    { content: 'Run linting (ESLint + Ruff)', status: 'pending', activeForm: 'Running linting' },
    { content: 'Verify type safety (TypeScript + mypy)', status: 'pending', activeForm: 'Verifying type safety' },
  ],
});
```

## Examples

### ✅ Correct Usage

```typescript
// User: "Build résumé optimization with payment and AI integration"
TodoWrite({
  todos: [
    { content: 'Design optimization API schema', status: 'in_progress', activeForm: 'Designing optimization API schema' },
    { content: 'Implement Stripe payment intent creation', status: 'pending', activeForm: 'Implementing Stripe payment' },
    { content: 'Integrate OpenRouter for AI optimization', status: 'pending', activeForm: 'Integrating OpenRouter' },
    { content: 'Add database persistence (Supabase)', status: 'pending', activeForm: 'Adding database persistence' },
    { content: 'Create download endpoint for DOCX', status: 'pending', activeForm: 'Creating download endpoint' },
    { content: 'Add comprehensive tests', status: 'pending', activeForm: 'Adding comprehensive tests' },
  ],
});
```

### ❌ Incorrect Usage

```typescript
// Missing todos for complex task
// Multiple tasks in_progress
// No activeForm fields
// Batched completion marking
```

## Resume-Matcher Context

All agents should be aware of:

**Tech Stack**:
- Frontend: Next.js 15+, TypeScript, Tailwind, shadcn/ui
- Backend: FastAPI, Python 3.11+, UV package manager
- Services: Supabase (Auth, DB, Storage), Stripe (Payments), OpenRouter (AI)
- Primary Workflow: Upload résumé → Paste job description → Pay via Stripe → AI optimization → Download .docx

**Domain Terms**:
- Use "résumé" not "resume"
- "optimization" for AI improvements
- "match percentage" for ATS compatibility score
- "Brazilian professionals" as target audience
- "LGPD compliance" for Brazilian data privacy

**Quality Standards**:
- Follow WCAG 2.1 AA accessibility
- Enforce LGPD compliance
- Repository Pattern for backend
- Functional components with hooks (frontend)
- Test-Driven Development

---

**This template MUST be referenced by all specialist agents in Resume-Matcher's agent system.**
