# Claude Code Rules for CV-Match

This directory contains Claude Code-specific instructions that provide context-aware guidance for developing CV-Match. These rules help maintain consistency, follow best practices, and accelerate development with Claude as your AI coding assistant.

## Rule Structure

### Core Rules
- **`project-overview.md`**: Overall project standards and architecture principles
- **`development-workflow.md`**: Development workflow, commands, and troubleshooting
- **`business-context.md`**: Business model, pricing strategy, and market focus

### Backend Rules (`backend/`)
- **`fastapi-standards.md`**: FastAPI endpoint patterns and best practices
- **`supabase-integration.md`**: Supabase service usage and patterns
- **`llm-integration.md`**: LLM and embedding service integration

### Frontend Rules (`frontend/`)
- **`nextjs-standards.md`**: Next.js component patterns and standards
- **`supabase-auth.md`**: Frontend authentication patterns
- **`api-integration.md`**: API client and service integration

### Database Rules
- **`database-migrations.md`**: Migration patterns and SQL best practices

### Templates (`templates/`)
- **`api-endpoint-template.md`**: Complete FastAPI endpoint template
- **`react-component-template.md`**: Complete React component template
- **`service-class-template.md`**: Service class pattern template

## How to Use with Claude Code

### Reference in Prompts
When working with Claude, you can reference specific rules:

```
@.claude/backend/fastapi-standards.md help me create a new API endpoint
```

```
@.claude/templates/react-component-template.md create a new dashboard component
```

### Context Awareness
Claude will use these files as context when you're working in relevant areas:
- Editing Python files in `backend/` → Backend rules apply
- Editing React components → Frontend rules apply
- Working with migrations → Database rules apply

### Custom Instructions
All markdown files in `.claude/` directory are treated as custom instructions that Claude can reference to understand your project's specific patterns and requirements.

## Key Differences from Cursor Rules

1. **File Format**: Claude uses `.md` (markdown) instead of `.mdc` (markdown cursor)
2. **No YAML Frontmatter**: Claude doesn't use `globs:` or `alwaysApply:` metadata
3. **Simpler Structure**: Just plain markdown files that Claude can read as context
4. **Explicit References**: Use `@.claude/filename.md` to explicitly include context

## Benefits

1. **Consistency**: Ensures all code follows established patterns
2. **Speed**: Templates and patterns accelerate development
3. **Quality**: Built-in best practices and error handling
4. **Context**: Claude understands your project structure and standards
5. **Learning**: New developers can quickly understand project patterns
6. **Business Alignment**: Claude understands your monetization strategy and market focus

## Getting Started with Claude

1. **Reference project overview**: `@.claude/project-overview.md` for general context
2. **Use templates**: `@.claude/templates/` when creating new components
3. **Follow standards**: `@.claude/backend/` or `@.claude/frontend/` for specific patterns
4. **Understand business**: `@.claude/business-context.md` for strategic decisions

## Customization

Feel free to modify these rules to match your evolving needs:
- Add new rules for additional services or patterns
- Modify existing rules to match your coding style
- Create project-specific templates for common use cases
- Update business context as your strategy evolves

## Examples

### Creating a New API Endpoint
```
@.claude/templates/api-endpoint-template.md
@.claude/backend/fastapi-standards.md

Create a new API endpoint for resume analysis with proper authentication and error handling
```

### Building a New Component
```
@.claude/templates/react-component-template.md
@.claude/frontend/nextjs-standards.md

Build a pricing card component for the Flex & Flow hybrid model
```

### Making Strategic Decisions
```
@.claude/business-context.md

Should we offer a discount for annual subscriptions? What's our pricing strategy?
```

---

**Note**: This is adapted from the Cursor rules in `.cursor/rules/` but optimized for Claude Code's simpler, markdown-based approach. Keep both in sync when making architectural changes.
