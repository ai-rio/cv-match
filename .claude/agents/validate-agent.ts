#!/usr/bin/env bun

/**
 * Agent Validation Script
 *
 * Validates that agents follow Claude Agent SDK best practices
 *
 * Usage:
 *   bun run .claude/agents/validate-agent.ts frontend-specialist
 *   bun run .claude/agents/validate-agent.ts --all
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { join, basename } from 'path';

interface ValidationResult {
  agentName: string;
  isValid: boolean;
  errors: string[];
  warnings: string[];
  info: string[];
}

interface AgentDefinition {
  description: string;
  tools?: string[];
  prompt: string;
  model?: 'sonnet' | 'opus' | 'haiku' | 'inherit';
}

const VALID_TOOLS = [
  'TodoWrite',
  'Read',
  'Write',
  'Edit',
  'MultiEdit',
  'Bash',
  'BashOutput',
  'Grep',
  'Glob',
  'KillShell',
  'NotebookEdit',
  'WebFetch',
  'WebSearch',
  'Task',
  'ExitPlanMode',
  'ListMcpResources',
  'ReadMcpResource',
];

const VALID_MODELS = ['sonnet', 'opus', 'haiku', 'inherit'];

/**
 * Validate a TypeScript agent file
 */
function validateTypeScriptAgent(agentName: string): ValidationResult {
  const result: ValidationResult = {
    agentName,
    isValid: true,
    errors: [],
    warnings: [],
    info: [],
  };

  const agentPath = join(process.cwd(), '.claude', 'agents', `${agentName}.ts`);

  if (!existsSync(agentPath)) {
    result.errors.push(`TypeScript file not found: ${agentPath}`);
    result.isValid = false;
    return result;
  }

  const content = readFileSync(agentPath, 'utf-8');

  // Check for proper imports
  if (!content.includes("import type { AgentDefinition } from '@anthropic/claude-code-sdk'")) {
    result.errors.push('Missing AgentDefinition import from @anthropic/claude-code-sdk');
    result.isValid = false;
  }

  // Check for export
  if (!content.includes('export const') && !content.includes('export default')) {
    result.errors.push('Agent must be exported (export const or export default)');
    result.isValid = false;
  }

  // Try to dynamically import and validate the agent definition
  try {
    // Extract agent definition using regex (basic validation)
    const descMatch = content.match(/description:\s*['"`](.*?)['"`]/s);
    const toolsMatch = content.match(/tools:\s*\[(.*?)\]/s);
    const promptMatch = content.match(/prompt:\s*['"`](.*?)['"`]/s);
    const modelMatch = content.match(/model:\s*['"`](\w+)['"`]/);

    // Validate description
    if (descMatch && descMatch[1]) {
      const description = descMatch[1];

      if (description.length < 50) {
        result.warnings.push(
          'Description is quite short. Consider adding more detail about when to use this agent.'
        );
      }

      if (!description.includes('MUST BE USED') && !description.includes('Use PROACTIVELY')) {
        result.warnings.push(
          'Description should include "MUST BE USED" or "Use PROACTIVELY" to indicate when the agent should be invoked'
        );
      }

      result.info.push(`Description length: ${description.length} characters`);
    } else {
      result.errors.push('Missing or invalid description field');
      result.isValid = false;
    }

    // Validate tools
    if (toolsMatch && toolsMatch[1]) {
      const tools = toolsMatch[1]
        .split(',')
        .map(t => t.trim().replace(/['"`]/g, ''))
        .filter(t => t.length > 0);

      const invalidTools = tools.filter(tool => !VALID_TOOLS.includes(tool));
      if (invalidTools.length > 0) {
        result.errors.push(`Invalid tools: ${invalidTools.join(', ')}`);
        result.isValid = false;
      }

      if (!tools.includes('TodoWrite')) {
        result.warnings.push(
          'Agent does not include TodoWrite tool. Consider adding it for complex task tracking.'
        );
      }

      if (tools.includes('Write') && tools.includes('Edit')) {
        result.warnings.push(
          'Agent has both Write and Edit tools. Prefer Edit over Write for modifying existing files.'
        );
      }

      result.info.push(`Tools configured: ${tools.length} tool(s) - ${tools.join(', ')}`);
    } else {
      result.info.push('Tools: undefined (inherits all available tools)');
      result.warnings.push(
        'No tools restriction. Consider limiting tools for better security and clarity.'
      );
    }

    // Validate prompt
    if (promptMatch && promptMatch[1]) {
      const prompt = promptMatch[1];

      if (prompt.length < 200) {
        result.warnings.push(
          'Prompt is quite short. Consider adding more detailed instructions and context.'
        );
      }

      if (!prompt.includes('TodoWrite') && !prompt.includes('todo')) {
        result.warnings.push('Prompt should mention TodoWrite usage for complex tasks');
      }

      result.info.push(`Prompt length: ${prompt.length} characters`);
    } else {
      result.errors.push('Missing or invalid prompt field');
      result.isValid = false;
    }

    // Validate model
    if (modelMatch && modelMatch[1]) {
      const model = modelMatch[1];
      if (!VALID_MODELS.includes(model)) {
        result.errors.push(
          `Invalid model: ${model}. Must be one of: ${VALID_MODELS.join(', ')}`
        );
        result.isValid = false;
      }
      result.info.push(`Model: ${model}`);
    } else {
      result.info.push('Model: undefined (inherits main query model)');
    }

    // Check for JSDoc comments
    if (!content.includes('/**') || !content.includes('*/')) {
      result.warnings.push('Consider adding JSDoc comments for better IDE support');
    }

    // Check for @example in JSDoc
    if (!content.includes('@example')) {
      result.warnings.push('Consider adding @example in JSDoc to show usage');
    }
  } catch (error) {
    result.errors.push(`Failed to parse agent definition: ${error}`);
    result.isValid = false;
  }

  return result;
}

/**
 * Validate a Markdown agent file
 */
function validateMarkdownAgent(agentName: string): ValidationResult {
  const result: ValidationResult = {
    agentName,
    isValid: true,
    errors: [],
    warnings: [],
    info: [],
  };

  const agentPath = join(process.cwd(), '.claude', 'agents', `${agentName}.md`);

  if (!existsSync(agentPath)) {
    result.errors.push(`Markdown file not found: ${agentPath}`);
    result.isValid = false;
    return result;
  }

  const content = readFileSync(agentPath, 'utf-8');

  // Check for YAML frontmatter
  if (!content.startsWith('---')) {
    result.errors.push('Markdown file must start with YAML frontmatter (---)');
    result.isValid = false;
    return result;
  }

  const frontmatterMatch = content.match(/^---\n(.*?)\n---/s);
  if (!frontmatterMatch) {
    result.errors.push('Invalid YAML frontmatter format');
    result.isValid = false;
    return result;
  }

  const frontmatter = frontmatterMatch[1];
  const bodyContent = content.substring(frontmatterMatch[0].length);

  // Parse YAML frontmatter (basic parsing)
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const descMatch = frontmatter.match(/^description:\s*(.+)$/m);
  const modelMatch = frontmatter.match(/^model:\s*(.+)$/m);
  const toolsMatch = frontmatter.match(/^tools:\s*\n((?:\s*-\s*.+\n?)+)/m);

  // Validate name
  if (nameMatch && nameMatch[1]) {
    const name = nameMatch[1].trim();
    if (name !== agentName) {
      result.warnings.push(
        `Agent name in frontmatter (${name}) doesn't match filename (${agentName})`
      );
    }
  } else {
    result.errors.push('Missing name field in frontmatter');
    result.isValid = false;
  }

  // Validate description
  if (descMatch && descMatch[1]) {
    const description = descMatch[1].trim();

    if (description.length < 50) {
      result.warnings.push('Description is quite short');
    }

    if (!description.includes('MUST BE USED') && !description.includes('Use PROACTIVELY')) {
      result.warnings.push(
        'Description should include "MUST BE USED" or "Use PROACTIVELY" for clarity'
      );
    }

    result.info.push(`Description length: ${description.length} characters`);
  } else {
    result.errors.push('Missing description field in frontmatter');
    result.isValid = false;
  }

  // Validate model
  if (modelMatch && modelMatch[1]) {
    const model = modelMatch[1].trim();
    if (!VALID_MODELS.includes(model)) {
      result.errors.push(`Invalid model: ${model}. Must be one of: ${VALID_MODELS.join(', ')}`);
      result.isValid = false;
    }
    result.info.push(`Model: ${model}`);
  } else {
    result.info.push('Model: undefined (uses default)');
  }

  // Validate tools
  if (toolsMatch && toolsMatch[1]) {
    const tools = toolsMatch[1]
      .split('\n')
      .map(line => line.trim().replace(/^-\s*/, ''))
      .filter(tool => tool.length > 0);

    const invalidTools = tools.filter(tool => !VALID_TOOLS.includes(tool));
    if (invalidTools.length > 0) {
      result.errors.push(`Invalid tools: ${invalidTools.join(', ')}`);
      result.isValid = false;
    }

    if (!tools.includes('TodoWrite')) {
      result.warnings.push('Agent does not include TodoWrite tool');
    }

    result.info.push(`Tools configured: ${tools.length} tool(s) - ${tools.join(', ')}`);
  } else {
    result.info.push('Tools: undefined (inherits all tools)');
    result.warnings.push('No tools restriction');
  }

  // Validate body content
  if (bodyContent.length < 500) {
    result.warnings.push('Agent prompt is quite short. Consider adding more detail.');
  }

  if (!bodyContent.includes('TodoWrite') && !bodyContent.includes('todo')) {
    result.warnings.push('Agent prompt should mention TodoWrite usage');
  }

  // Check for TypeScript version reference
  if (
    existsSync(join(process.cwd(), '.claude', 'agents', `${agentName}.ts`)) &&
    !bodyContent.includes('programmatic')
  ) {
    result.warnings.push(
      'TypeScript version exists but not mentioned. Add a note about the programmatic version.'
    );
  }

  return result;
}

/**
 * Print validation results
 */
function printResults(results: ValidationResult[]): void {
  console.log('\n=== Agent Validation Results ===\n');

  let totalValid = 0;
  let totalErrors = 0;
  let totalWarnings = 0;

  for (const result of results) {
    console.log(`\n📋 ${result.agentName}`);
    console.log('─'.repeat(50));

    if (result.isValid) {
      console.log('✅ Status: VALID');
      totalValid++;
    } else {
      console.log('❌ Status: INVALID');
    }

    if (result.errors.length > 0) {
      console.log('\n❌ Errors:');
      result.errors.forEach(error => console.log(`   • ${error}`));
      totalErrors += result.errors.length;
    }

    if (result.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      result.warnings.forEach(warning => console.log(`   • ${warning}`));
      totalWarnings += result.warnings.length;
    }

    if (result.info.length > 0) {
      console.log('\nℹ️  Info:');
      result.info.forEach(info => console.log(`   • ${info}`));
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log(`\n📊 Summary:`);
  console.log(`   Valid agents: ${totalValid}/${results.length}`);
  console.log(`   Total errors: ${totalErrors}`);
  console.log(`   Total warnings: ${totalWarnings}`);

  if (results.every(r => r.isValid)) {
    console.log('\n✨ All agents are valid!\n');
  } else {
    console.log('\n⚠️  Some agents need attention.\n');
    process.exit(1);
  }
}

/**
 * Main execution
 */
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: bun run validate-agent.ts <agent-name> | --all');
    console.error('Example: bun run validate-agent.ts frontend-specialist');
    process.exit(1);
  }

  const results: ValidationResult[] = [];

  if (args[0] === '--all') {
    const agentsDir = join(process.cwd(), '.claude', 'agents');
    const files = readdirSync(agentsDir);

    const agentNames = new Set<string>();
    files.forEach(file => {
      if (file.endsWith('.ts') || file.endsWith('.md')) {
        const name = basename(file, file.endsWith('.ts') ? '.ts' : '.md');
        if (!name.startsWith('_') && !name.includes('validate')) {
          agentNames.add(name);
        }
      }
    });

    agentNames.forEach(name => {
      // Validate both TypeScript and Markdown versions if they exist
      const tsPath = join(agentsDir, `${name}.ts`);
      const mdPath = join(agentsDir, `${name}.md`);

      if (existsSync(tsPath)) {
        results.push(validateTypeScriptAgent(name));
      }

      if (existsSync(mdPath)) {
        results.push(validateMarkdownAgent(name));
      }
    });
  } else {
    const agentName = args[0];

    // Check both TypeScript and Markdown versions
    const tsPath = join(process.cwd(), '.claude', 'agents', `${agentName}.ts`);
    const mdPath = join(process.cwd(), '.claude', 'agents', `${agentName}.md`);

    if (existsSync(tsPath)) {
      results.push(validateTypeScriptAgent(agentName));
    }

    if (existsSync(mdPath)) {
      results.push(validateMarkdownAgent(agentName));
    }

    if (results.length === 0) {
      console.error(`❌ Agent not found: ${agentName}`);
      console.error(`   Looked for: ${tsPath} or ${mdPath}`);
      process.exit(1);
    }
  }

  printResults(results);
}

main();