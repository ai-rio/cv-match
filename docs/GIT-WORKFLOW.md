# Enterprise Git Workflow with Pre-commit Hooks

This document outlines the comprehensive Git workflow implemented for CV-Match to ensure code quality, security, and consistency across the enterprise.

## 🚀 Overview

Our Git workflow uses **Husky** for Git hooks management and **lint-staged** for efficient file processing. The system runs automated checks before commits and pushes to maintain high code quality standards.

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
   - TypeScript type checking
   - Production build validation

2. **🐍 Backend Tests**
   - pytest with coverage reporting
   - Python type checking
   - API endpoint validation

3. **🔐 Security Audit**
   - Frontend dependency vulnerability scanning
   - Warns about security issues

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

## 🛠 Available NPM Scripts

### Setup Commands:
```bash
npm run dev:setup          # Install all dependencies
npm run install:frontend   # Install frontend deps with bun
npm run install:backend    # Install backend deps with uv
npm run hooks:install      # Install Git hooks
```

### Quality Assurance:
```bash
npm run lint:all          # Lint frontend and backend
npm run format:all        # Format all code
npm run test:all          # Run all test suites
npm run type-check:all    # Type check frontend and backend
npm run quality:check     # Run complete quality check
```

### Build Commands:
```bash
npm run build:frontend    # Build frontend for production
```

## 🔄 Daily Workflow

### 1. Development Setup:
```bash
# Clone and setup
git clone <repository-url>
cd cv-match
npm run dev:setup
npm run hooks:install
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
npm run quality:check

# Push to remote (pre-push hooks will run full test suite)
git push origin feat/brazilian-payment-flow
```

## 🔍 Troubleshooting

### Hook Execution Issues:
```bash
# Reinstall hooks if they're not working
npm run hooks:uninstall
npm run hooks:install

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

## 🎯 Best Practices

1. **Write Descriptive Commits**: Use conventional commit format with clear scope
2. **Test Before Pushing**: Always run `npm run quality:check` locally
3. **Small Focused Commits**: Keep commits atomic and related
4. **Branch Naming**: Use `feat/`, `fix/`, `docs/` prefixes
5. **Brazilian Context**: Include BRL/PT-BR context when relevant

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