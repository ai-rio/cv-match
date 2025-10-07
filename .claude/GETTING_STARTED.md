# Getting Started with Claude Code for CV-Match

Welcome! This guide helps you use Claude Code effectively for developing CV-Match.

## What is this `.claude/` directory?

This directory contains **custom instructions** that help Claude understand your project's:
- Architecture and tech stack
- Coding standards and patterns
- Business model and strategy
- Development workflow

Think of it as giving Claude a comprehensive onboarding document for your project.

## Quick Start

### 1. Basic Usage

When chatting with Claude, reference files with `@`:

```
@.claude/project-overview.md what database are we using?
```

### 2. Creating New Features

**Backend API Endpoint**:
```
@.claude/backend/fastapi-standards.md
@.claude/project-overview.md

Create a new API endpoint for analyzing job descriptions:
- POST /api/v1/jobs/analyze
- Extract requirements and keywords
- Return structured JSON
- Require authentication
```

**Frontend Component**:
```
@.claude/frontend/nextjs-standards.md
@.claude/business-context.md

Create a pricing card component showing our Flex & Flow plans with BRL pricing
```

### 3. Understanding Business Context

```
@.claude/business-context.md

Why do we have both credits and subscriptions?
```

### 4. Getting Workflow Help

```
@.claude/development-workflow.md

How do I create a new database migration?
```

## Available Files

### Core Context
- **[project-overview.md](.claude/project-overview.md)** - Complete project context, tech stack, standards
- **[business-context.md](.claude/business-context.md)** - Pricing model, market strategy, KPIs
- **[development-workflow.md](.claude/development-workflow.md)** - Daily workflow, commands, debugging

### Backend Standards
- **[backend/fastapi-standards.md](.claude/backend/fastapi-standards.md)** - API patterns, error handling, service layer

### Frontend Standards
- **[frontend/nextjs-standards.md](.claude/frontend/nextjs-standards.md)** - Component patterns, i18n, styling

## Common Scenarios

### Starting a New Feature

```
@.claude/project-overview.md
@.claude/backend/fastapi-standards.md
@.claude/frontend/nextjs-standards.md

I need to add a feature for users to save favorite job descriptions.
What's the full implementation plan following our standards?
```

### Debugging an Issue

```
@.claude/development-workflow.md

I'm getting a 403 error when uploading a resume.
The user has credits. Help me debug.
```

### Making Business Decisions

```
@.claude/business-context.md

Should we offer a discount for referrals?
How does it fit our monetization strategy?
```

### Code Review

```
@.claude/backend/fastapi-standards.md

Review this code and suggest improvements:
[paste code]
```

### Understanding Existing Code

```
@.claude/project-overview.md

Explain how the resume matching algorithm works
```

## Pro Tips

### 1. Reference Multiple Files for Complex Tasks

```
@.claude/project-overview.md
@.claude/business-context.md
@.claude/backend/fastapi-standards.md
@.claude/frontend/nextjs-standards.md

Implement a complete feature for annual subscription plans:
- Backend discount calculation
- Frontend pricing display
- Brazilian market considerations
- Payment processing
```

### 2. Ask for Architecture Advice

```
@.claude/project-overview.md

What's the best way to implement real-time notifications for when a resume analysis completes?
```

### 3. Get Pricing Strategy Help

```
@.claude/business-context.md

Analyze: Should we increase Flex 25 from R$ 59,90 to R$ 69,90?
```

### 4. Learn the Codebase

```
@.claude/project-overview.md

Give me a walkthrough of how a resume upload flows through the system,
from frontend to backend to database.
```

## Best Practices

### ✅ DO

- **Reference relevant context files** for your task
- **Be specific** about what you're building
- **Ask for explanations** of existing patterns
- **Request code that follows our standards**
- **Ask for PT-BR translations** when building UI

### ❌ DON'T

- Assume Claude knows your project without context
- Skip referencing standards files
- Forget to mention Brazilian market requirements
- Ask for generic code without project-specific patterns

## Examples from Real Development

### Example 1: New Payment Feature

**User Prompt**:
```
@.claude/business-context.md
@.claude/backend/fastapi-standards.md
@.claude/project-overview.md

Implement PIX payment support for the Brazilian market:
1. Add PIX as payment method in backend
2. Update Stripe configuration
3. Add PIX option to frontend payment flow
4. Include Portuguese translations
5. Follow our service layer pattern
```

**Claude will provide**:
- Backend service implementation
- API endpoint updates
- Frontend component changes
- Translation keys
- Testing approach
All following CV-Match standards!

### Example 2: Bug Fix

**User Prompt**:
```
@.claude/development-workflow.md
@.claude/backend/fastapi-standards.md

Users are getting 500 errors when uploading large PDF files (>5MB).
Debug and fix this issue following our error handling patterns.
```

**Claude will**:
- Check for file size validation
- Suggest proper error handling
- Recommend user-friendly error messages in PT-BR
- Follow FastAPI standards

### Example 3: Feature Planning

**User Prompt**:
```
@.claude/project-overview.md
@.claude/business-context.md

Plan the implementation for a team collaboration feature where:
- Multiple users share a Flow Business subscription
- Each team member has their own dashboard
- Credits are pooled
- Admin can manage team members

Consider our database schema, authentication, and subscription model.
```

**Claude will provide**:
- Database schema changes
- Authentication approach
- Backend API design
- Frontend components needed
- Migration strategy
- Pricing implications

## Keeping Rules Updated

As your project evolves, update these files:

- **Add new services**: Document in `project-overview.md`
- **Change pricing**: Update `business-context.md`
- **New workflow**: Add to `development-workflow.md`
- **New standards**: Add to relevant standards files

## Comparison with Cursor Rules

You may notice `.cursor/rules/` in the project. Key differences:

| Feature | Cursor Rules | Claude Rules |
|---------|-------------|--------------|
| **Format** | `.mdc` (Cursor-specific) | `.md` (standard markdown) |
| **Metadata** | YAML frontmatter with `globs:` | No metadata needed |
| **Auto-apply** | Based on file patterns | Manual with `@` |
| **Complexity** | More structured | Simpler |
| **Use Case** | Cursor IDE | Claude Code |

Both serve the same purpose: help AI understand your project. Keep them in sync when making major changes.

## Getting Help

### Claude Code Questions
- Read the [official Claude Code documentation](https://docs.claude.com/claude-code)
- Check the [development documentation](../docs/development/README.md)

### Project Questions
- Reference `@.claude/project-overview.md`
- Check `@.claude/development-workflow.md`
- Review relevant standard files

### Business Questions
- Reference `@.claude/business-context.md`
- Check [docs/development/business-model-analysis.md](../docs/development/business-model-analysis.md)

---

## Quick Reference Card

**Most Used Commands**:

```bash
# Reference full project context
@.claude/project-overview.md

# Get business strategy context
@.claude/business-context.md

# Check workflow/commands
@.claude/development-workflow.md

# Backend patterns
@.claude/backend/fastapi-standards.md

# Frontend patterns
@.claude/frontend/nextjs-standards.md
```

---

**Welcome to CV-Match development with Claude Code! 🚀**

Start building and let Claude help you maintain consistency with our standards and accelerate your development.
