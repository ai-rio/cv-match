# Git Flow Workflow Guide for CV-Match Brazilian SaaS

## Overview

This document outlines the comprehensive Git Flow workflow implemented for CV-Match, specifically tailored for the Brazilian SaaS market. The workflow combines **Git Flow** principles with modern CI/CD automation to ensure systematic development, proper versioning, and seamless collaboration.

## 🚀 Architecture

Our Git Flow workflow uses:

- **Git Flow** branching strategy for systematic development
- **GitHub Actions** for automated quality checks and CI/CD
- **Husky** for local pre-commit hooks
- **Semantic Release** for automated versioning
- **Brazilian Market** specific validations and considerations

## 📁 Workflow Structure

```
.husky/
├── pre-commit    # Runs before each commit
├── pre-push      # Runs before each push
├── commit-msg    # Validates commit messages
└── post-commit   # Runs after successful commits

.lintstagedrc.js    # Configuration for staged file processing
commitlint.config.js # Commit message validation rules
package.json         # Global scripts and dependencies
```

## 🔧 Pre-commit Hooks

### What runs automatically:

1. **🔍 Lint-staged Processing**
   - TypeScript/JavaScript: ESLint + Prettier
   - CSS/SCSS: Stylelint + Prettier
   - JSON/MD/YAML: Prettier formatting
   - Python files: ruff formatting + linting
   - SQL migrations: Basic validation

2. **🐍 Python Type Checking**
   - Runs mypy on staged Python files
   - Ensures type hints are correct

3. **🗄️ Database Migration Validation**
   - Validates SQL migration files
   - Ensures proper SQL syntax

4. **🔒 Security Scanning**
   - Detects potential secrets in staged files
   - Blocks commits with exposed credentials

5. **📏 File Size Checks**
   - Prevents commits with files >5MB
   - Encourages Git LFS usage

6. **📦 Dependency Validation**
   - Checks if frontend/backend dependencies are installed

## 🧪 Pre-push Hooks

### Comprehensive testing before pushing:

1. **⚛️ Frontend Tests**
   - Jest test suite with coverage
   - TypeScript type checking with error classification
   - Production build validation
   - Type safety score calculation

2. **🐍 Backend Tests**
   - pytest with coverage reporting
   - Python type checking with error classification
   - API endpoint validation
   - Type safety metrics tracking

3. **🔐 Security Audit**
   - Frontend dependency vulnerability scanning
   - Warns about security issues

4. **🔍 Type Quality Gates**
   - Critical error validation (blocks push)
   - High priority error thresholds
   - Type safety score requirements
   - Brazilian market type validation

## 📝 Commit Message Standards

We use **conventional commits** with Brazilian market context:

### Format:

```
type(scope): description

[optional body]

[optional footer]
```

### Available Types:

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/modifications
- `chore`: Maintenance tasks
- `build`: Build system changes
- `ci`: CI configuration changes
- `revert`: Revert previous commit
- `bump`: Version updates
- `lint`: Linting fixes
- `security`: Security fixes
- `deps`: Dependency updates
- `i18n`: Internationalization changes
- `wip`: Work in progress

### Examples:

```bash
feat(auth): add Brazilian Portuguese translations
fix(payment): handle BRL currency conversion errors
docs(readme): update Brazilian market setup instructions
test(api): add resume processing unit tests
refactor(database): optimize query performance for large datasets
```

## 🎯 Brazilian Market Specifics

### Commit Context:

- Use BRL- prefix for Brazilian market tickets
- Reference PT-BR translations in i18n commits
- Document currency handling for Brazilian real

### Examples:

```bash
feat(i18n): add PT-BR translations for payment flow
fix(currency): handle BRL decimal formatting correctly
docs(BRL-123): update Brazilian payment methods documentation
```

## 🛠 Available bun Scripts

### Setup Commands:

```bash
bun run dev:setup          # Install all dependencies
bun run install:frontend   # Install frontend deps with bun
bun run install:backend    # Install backend deps with uv
bun run hooks:install      # Install Git hooks
```

### Quality Assurance:

```bash
bun run lint:all          # Lint frontend and backend
bun run format:all        # Format all code
bun run test:all          # Run all test suites
bun run type-check:all    # Type check frontend and backend
bun run type-analysis     # Analyze type errors without fixing
bun run type-fix:all      # Apply automated type fixes (all priorities)
bun run type-fix:critical # Fix critical type errors manually
bun run type-fix:high     # Apply high priority automated fixes
bun run type-fix:medium   # Apply medium priority automated fixes
bun run type-fix:low      # Apply low priority automated fixes
bun run type-fix:dry-run  # Preview fixes without applying
bun run type-safety:report# Generate comprehensive type safety report
bun run quality:check     # Run complete quality check
```

### Build Commands:

```bash
bun run build:frontend    # Build frontend for production
```

## 🔄 Daily Workflow

### 1. Development Setup:

```bash
# Clone and setup
git clone <repository-url>
cd cv-match
bun run dev:setup
bun run hooks:install
```

### 2. Feature Development:

```bash
# Create feature branch
git checkout -b feat/brazilian-payment-flow

# Make changes...
git add .
git commit -m "feat(payment): implement Brazilian PIX payment method"

# The pre-commit hooks will automatically:
# - Lint and format your code
# - Run type checking
# - Scan for security issues
# - Validate file sizes
```

### 3. Quality Assurance:

```bash
# Run comprehensive checks before pushing
bun run quality:check

# Push to remote (pre-push hooks will run full test suite)
git push origin feat/brazilian-payment-flow
```

## 🔍 Troubleshooting

### Hook Execution Issues:

```bash
# Reinstall hooks if they're not working
bun run hooks:uninstall
bun run hooks:install

# Check hook permissions
ls -la .husky/
chmod +x .husky/*
```

### Bypassing Hooks (Emergency Only):

```bash
# WARNING: Use only in emergency situations
git commit -m "emergency fix" --no-verify
git push --no-verify
```

### Lint-staged Issues:

```bash
# Debug lint-staged configuration
bunx  lint-staged --verbose

# Check configuration
cat .lintstagedrc.js
```

## 📊 Metrics and Monitoring

The workflow automatically tracks:

- Commit frequency and author statistics
- File change patterns
- Test coverage trends
- Security scan results
- Build success rates

## 🔍 Automated Type Checking System

Our comprehensive type checking system is integrated throughout the CI/CD pipeline:

### Type Error Classification

- **🔴 Critical**: Build-blocking errors (TS2307, TS2304, undefined names)
- **🟡 High**: Affects multiple files (TS2339, TS2345, type incompatibilities)
- **🟢 Medium**: Local to component/function (TS18047, TS2322)
- **⚪ Low**: Cosmetic/warnings (TS7006, TS6133, unused variables)

### Quality Gates

- Critical errors: 0 allowed (blocks merge)
- High priority: Maximum 10 allowed
- Medium priority: Maximum 25 allowed
- Low priority: Maximum 50 allowed
- Type safety score: Minimum 80% for production

### Automated Workflows

1. **Type Error Analysis**: Runs on every PR and push
2. **Progressive Fixing**: Automated fixes for non-critical errors
3. **Brazilian Market Validation**: PT-BR and BRL type checking
4. **PR Metrics**: Type safety scores in PR descriptions

### Manual Bulk Fixes

```bash
# Analyze current state
bun run type-analysis

# Apply automated fixes by priority
bun run type-fix:critical  # Manual intervention required
bun run type-fix:high      # Automated fixes applied
bun run type-fix:medium    # Automated fixes applied
bun run type-fix:low       # Automated fixes applied

# Preview changes before applying
bun run type-fix:dry-run

# Generate comprehensive report
bun run type-safety:report
```

### Integration with Git Flow

- **Feature branches**: Type checking runs on every push
- **Release branches**: Strict type gates (90%+ safety score required)
- **Hotfix branches**: Critical errors only (rapid fixes prioritized)
- **Main branch**: Full type validation with automated fixes

---

## 🎯 Best Practices

1. **Write Descriptive Commits**: Use conventional commit format with clear scope
2. **Test Before Pushing**: Always run `bun run quality:check` locally
3. **Monitor Type Safety**: Keep type safety score above 80%
4. **Fix Progressively**: Address critical errors first, then automate remaining fixes
5. **Small Focused Commits**: Keep commits atomic and related
6. **Branch Naming**: Use `feat/`, `fix/`, `docs/` prefixes
7. **Brazilian Context**: Include BRL/PT-BR context when relevant
8. **Type Safety First**: Run `bun run type-analysis` before major changes

## 🔐 Security Considerations

- Never commit API keys, passwords, or secrets
- Use environment variables for sensitive data
- Security scanning runs automatically on each commit
- Regular dependency audits recommended

## 📚 Additional Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Husky Documentation](https://typicode.github.io/husky/)
- [lint-staged Documentation](https://github.com/lint-staged/lint-staged)
- [Commitlint Documentation](https://commitlint.js.org/)

---

## 🎉 Summary

This enterprise Git workflow ensures:
✅ High code quality through automated linting and formatting
✅ Type safety with TypeScript and Python type checking
✅ Security through secret scanning and vulnerability detection
✅ Test coverage validation before deployment
✅ Consistent commit messages with Brazilian market context
✅ Performance monitoring and metrics tracking

The workflow is designed to be **fast**, **reliable**, and **tailored** for the Brazilian SaaS market requirements of CV-Match.
