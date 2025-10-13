# Claude Agent SDK Usage Guide

This guide explains how to use Resume-Matcher's agents with the Claude Agent SDK in both programmatic (TypeScript) and filesystem-based (markdown) modes.

## Overview

Resume-Matcher provides specialized agents for different development tasks. Each agent is available in two formats:

1. **Programmatic (TypeScript)** - `.ts` files for SDK integration
2. **Filesystem-based (Markdown)** - `.md` files for CLI usage

The programmatic versions take precedence when both exist, allowing for flexible integration with TypeScript applications.

## Available Agents

| Agent | TypeScript | Markdown | Purpose |
|-------|-----------|----------|---------|
| `frontend-specialist` | ✅ | ✅ | Next.js, React, TypeScript, Tailwind CSS |
| `backend-specialist` | ⏳ | ✅ | FastAPI, Python, Repository Pattern |
| `database-specialist` | ⏳ | ✅ | Supabase, PostgreSQL, RLS policies |
| `ai-integration-specialist` | ⏳ | ✅ | OpenRouter API, prompt engineering |
| `payment-specialist` | ⏳ | ✅ | Stripe integration, webhooks |
| `test-writer-agent` | ⏳ | ✅ | Jest, React Testing Library, Pytest |
| `code-reviewer-agent` | ⏳ | ✅ | Code review, security, LGPD |
| `orchestrator-agent` | ⏳ | ✅ | Multi-agent coordination |

> **Legend**: ✅ Available | ⏳ Coming soon

## Programmatic Usage (TypeScript SDK)

### Basic Example

```typescript
import { query } from '@anthropic/claude-code-sdk';
import { frontendSpecialist } from './.claude/agents/frontend-specialist';

const result = query({
  prompt: "Create a résumé upload component with drag-and-drop",
  options: {
    agents: {
      'frontend-specialist': frontendSpecialist
    }
  }
});

for await (const message of result) {
  if (message.type === 'assistant') {
    console.log(message.message);
  } else if (message.type === 'result') {
    console.log('Task completed:', message.result);
  }
}
```

### Advanced Example with Multiple Agents

```typescript
import { query } from '@anthropic/claude-code-sdk';
import { frontendSpecialist } from './.claude/agents/frontend-specialist';
import { backendSpecialist } from './.claude/agents/backend-specialist';
import { testWriter } from './.claude/agents/test-writer-agent';

async function buildFeature() {
  const result = query({
    prompt: "Build a complete résumé optimization feature with frontend, backend, and tests",
    options: {
      agents: {
        'frontend-specialist': frontendSpecialist,
        'backend-specialist': backendSpecialist,
        'test-writer': testWriter
      },
      // Allow specific tools
      allowedTools: ['Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob', 'TodoWrite'],
      // Set working directory
      cwd: process.cwd(),
      // Use Sonnet model
      model: 'claude-sonnet-4',
      // Automatic permission mode for CI
      permissionMode: 'bypassPermissions'
    }
  });

  for await (const message of result) {
    if (message.type === 'assistant') {
      console.log('Agent:', message.message);
    } else if (message.type === 'result') {
      console.log('Final result:', message.result);
      console.log('Cost:', message.total_cost_usd);
      console.log('Duration:', message.duration_ms, 'ms');
    }
  }
}

buildFeature();
```

### Custom Agent Configuration

You can dynamically configure agents based on your needs:

```typescript
import { query, type AgentDefinition } from '@anthropic/claude-code-sdk';

// Create a custom variant of the frontend specialist
const strictFrontendSpecialist: AgentDefinition = {
  description: 'MUST BE USED for frontend tasks requiring strict accessibility compliance',
  prompt: `You are a frontend specialist with extra focus on WCAG 2.1 AAA (not just AA).

  All the standard frontend-specialist rules apply, plus:
  - Use AAA contrast ratios (7:1 for text, 4.5:1 for UI)
  - Provide skip links for all navigation
  - Ensure all interactive elements are keyboard accessible
  - Test with multiple screen readers (NVDA, JAWS, VoiceOver)
  - Add comprehensive ARIA live regions
  `,
  tools: ['Read', 'Write', 'Edit', 'Grep', 'Glob', 'TodoWrite'],
  model: 'opus' // Use Opus for complex accessibility logic
};

const result = query({
  prompt: "Build an accessible payment form",
  options: {
    agents: {
      'frontend-specialist': strictFrontendSpecialist
    }
  }
});
```

### Integration with CI/CD

```typescript
// scripts/run-agent-task.ts
import { query } from '@anthropic/claude-code-sdk';
import { codeReviewer } from './.claude/agents/code-reviewer-agent';

async function reviewPullRequest(prNumber: number) {
  console.log(`Reviewing PR #${prNumber}...`);

  const result = query({
    prompt: `Review the changes in pull request #${prNumber} for security, code quality, and LGPD compliance`,
    options: {
      agents: {
        'code-reviewer': codeReviewer
      },
      // CI mode: bypass permissions, load only project settings
      permissionMode: 'bypassPermissions',
      settingSources: ['project'],
      // Limit to read-only tools for safety
      allowedTools: ['Read', 'Grep', 'Glob', 'Bash'],
      // Use environment variable for API key
      env: {
        ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY
      }
    }
  });

  let reviewComments = '';
  for await (const message of result) {
    if (message.type === 'result') {
      reviewComments = message.result;
    }
  }

  return reviewComments;
}

// Usage in GitHub Actions
const prNumber = parseInt(process.env.GITHUB_PR_NUMBER || '0');
reviewPullRequest(prNumber).then(comments => {
  console.log('Review completed:', comments);
});
```

## Filesystem-based Usage (CLI)

### Basic CLI Usage

When using the Claude Code CLI, agents are automatically detected from `.claude/agents/` directory:

```bash
# The CLI automatically finds and loads frontend-specialist.md
claude "Create a résumé upload component"

# Explicitly request a specific agent
claude "Use frontend-specialist to create a payment form"
```

### Agent Selection Triggers

Agents are automatically invoked based on their `description` field. For example:

- **frontend-specialist** - Triggered by: "Create a component", "Style the page", "Add accessibility"
- **backend-specialist** - Triggered by: "Create an API endpoint", "Add database logic"
- **test-writer** - Triggered by: "Write tests", "Add test coverage"

### Manual Agent Invocation

```bash
# Explicitly use a specific agent
claude "Use frontend-specialist: Build the résumé upload UI"

# Use multiple agents in sequence
claude "Use frontend-specialist to build the UI, then backend-specialist to create the API"
```

## Agent Configuration Reference

### AgentDefinition Structure

```typescript
interface AgentDefinition {
  // Natural language description of when to use this agent
  // Should clearly indicate with "MUST BE USED" or "Use PROACTIVELY"
  description: string;

  // Optional: Array of allowed tool names
  // If omitted, agent inherits all available tools
  tools?: string[];

  // The agent's system prompt defining role and behavior
  prompt: string;

  // Optional: Model override for this agent
  // Options: 'sonnet' | 'opus' | 'haiku' | 'inherit'
  // If omitted, uses the main query model
  model?: 'sonnet' | 'opus' | 'haiku' | 'inherit';
}
```

### Available Tools

Common tools used by Resume-Matcher agents:

- `Read` - Read files from the filesystem
- `Write` - Write new files (use sparingly)
- `Edit` - Edit existing files (preferred over Write)
- `MultiEdit` - Make multiple edits to one file
- `Bash` - Execute bash commands
- `Grep` - Search file contents with regex
- `Glob` - Find files by pattern
- `TodoWrite` - Manage task lists (mandatory for complex tasks)
- `Task` - Delegate to subagents

### Tool Restrictions for Safety

**Read-only agents** (analysis, review):
```typescript
tools: ['Read', 'Grep', 'Glob']
```

**Code modification agents**:
```typescript
tools: ['Read', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'TodoWrite']
```

**Test execution agents**:
```typescript
tools: ['Bash', 'Read', 'Grep', 'TodoWrite']
```

**Full-stack development agents**:
```typescript
tools: ['Read', 'Write', 'Edit', 'MultiEdit', 'Bash', 'Grep', 'Glob', 'TodoWrite']
```

## Best Practices

### 1. Use Descriptive Agent Names

```typescript
// ✅ Good - Clear, descriptive name
'frontend-specialist': frontendSpecialist

// ❌ Bad - Generic name
'agent1': someAgent
```

### 2. Write Clear Descriptions

```typescript
// ✅ Good - Explicit triggers
description: 'MUST BE USED for ALL frontend development tasks with Next.js 15+. Use PROACTIVELY when user requests involve UI components.'

// ❌ Bad - Vague description
description: 'Frontend developer'
```

### 3. Restrict Tools Appropriately

```typescript
// ✅ Good - Limited tools for review agent
{
  description: 'Code review specialist',
  tools: ['Read', 'Grep', 'Glob'], // Read-only
  // ...
}

// ❌ Bad - Unnecessary permissions
{
  description: 'Code review specialist',
  tools: undefined, // Inherits ALL tools including Write, Bash
  // ...
}
```

### 4. Use TodoWrite for Complex Tasks

All agents should use TodoWrite for tasks with 3+ steps:

```typescript
// Agent prompt should include:
`
**MANDATORY TODO USAGE**: Use TodoWrite tool for any task requiring 3+ steps.
Follow exact patterns: pending → in_progress → completed.
Only ONE task in_progress at a time.
`
```

### 5. Choose the Right Model

- **Haiku** (`haiku`) - Simple, repetitive tasks (fast, cheap)
- **Sonnet** (`sonnet`) - Balanced tasks (default, recommended)
- **Opus** (`opus`) - Complex logic, architecture decisions (slow, expensive)
- **Inherit** (`inherit`) - Use the main query model

```typescript
// ✅ Good - Use Opus for complex architectural decisions
{
  description: 'System architecture specialist',
  model: 'opus',
  // ...
}

// ✅ Good - Use Haiku for simple formatting tasks
{
  description: 'Code formatter',
  model: 'haiku',
  // ...
}
```

## Troubleshooting

### Agent Not Being Invoked

**Problem**: Agent exists but Claude doesn't use it

**Solutions**:
1. Check the `description` field - make it more explicit with "MUST BE USED"
2. Explicitly request the agent: "Use frontend-specialist to..."
3. Verify the agent is properly exported (TypeScript) or has valid YAML frontmatter (Markdown)

### TypeScript Import Errors

**Problem**: `Cannot find module './.claude/agents/frontend-specialist'`

**Solutions**:
```typescript
// Option 1: Add .ts extension
import { frontendSpecialist } from './.claude/agents/frontend-specialist.ts';

// Option 2: Update tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true
  }
}
```

### Agent Has Too Many Permissions

**Problem**: Agent can modify files when it should only read

**Solution**: Explicitly set the `tools` array:
```typescript
{
  description: 'Analysis agent',
  tools: ['Read', 'Grep', 'Glob'], // Only read tools
  // ...
}
```

### Multiple Agents Conflict

**Problem**: Multiple agents try to handle the same task

**Solution**: Make descriptions more specific:
```typescript
// ✅ Good - Non-overlapping responsibilities
{
  'frontend-specialist': {
    description: 'MUST BE USED for UI components, styling, and client-side logic'
  },
  'backend-specialist': {
    description: 'MUST BE USED for API endpoints, business logic, and database access'
  }
}
```

## Migration Guide

### Converting Markdown Agents to TypeScript

To convert an existing `.md` agent to programmatic `.ts`:

1. **Extract YAML frontmatter**:
```yaml
---
name: my-agent
description: Agent description here
model: sonnet
tools: Read, Write, Grep
---
```

2. **Create TypeScript file**:
```typescript
import type { AgentDefinition } from '@anthropic/claude-code-sdk';

export const myAgent: AgentDefinition = {
  description: 'Agent description here',
  tools: ['Read', 'Write', 'Grep'],
  model: 'sonnet',
  prompt: `
  [Copy the markdown content after frontmatter]
  `
};

export default myAgent;
```

3. **Keep the markdown file** for CLI compatibility, but add a note:
```markdown
---
name: my-agent
description: Agent description here
model: sonnet
tools:
  - Read
  - Write
  - Grep
---

> **Note**: A programmatic TypeScript version is available at `my-agent.ts`
```

## Examples Repository

For more examples, see:
- `/home/carlos/projects/Resume-Matcher/.claude/agents/frontend-specialist.ts` - Complete TypeScript agent
- `/home/carlos/projects/Resume-Matcher/.claude/agents/frontend-specialist.md` - Markdown equivalent
- `/home/carlos/projects/Resume-Matcher/docs/claucde/` - SDK documentation

## Further Reading

- [Claude Agent SDK - TypeScript Reference](../docs/claucde/type-script-agent-sdk.md)
- [Claude Agent SDK - Subagents Guide](../docs/claucde/sub-agents-sdk.md)
- [Resume-Matcher Agent System](./README.md)

---

**Need help?** Check the [Claude Agent SDK documentation](https://docs.anthropic.com/en/api/agent-sdk/typescript) or open an issue in the Resume-Matcher repository.
