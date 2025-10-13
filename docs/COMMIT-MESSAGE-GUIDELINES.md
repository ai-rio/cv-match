# Commit Message Guidelines for CV-Match Brazilian SaaS

## Overview

This document provides comprehensive guidelines for writing consistent, informative commit messages in the CV-Match project. Following these guidelines ensures clear project history, automated changelog generation, and effective collaboration.

## 🎯 Objectives

1. **Clear History**: Commits should be self-explanatory
2. **Automation**: Enable automated changelog and versioning
3. **Collaboration**: Help team members understand changes
4. **Brazilian Context**: Include market-specific information
5. **Debugging**: Facilitate issue identification and resolution

## 📝 Conventional Commit Format

### Basic Structure

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Breaking Changes

```
<type>(<scope>)!: <description>

[optional body]

BREAKING CHANGE: <detailed description>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

## 🔤 Commit Types

| Type       | Purpose          | Impact             | Brazilian Context                             |
| ---------- | ---------------- | ------------------ | --------------------------------------------- |
| `feat`     | New feature      | Minor version bump | `feat(payment): add BRL support`              |
| `fix`      | Bug fix          | Patch version bump | `fix(currency): BRL conversion error`         |
| `docs`     | Documentation    | No version bump    | `docs(pt-br): update Portuguese guide`        |
| `style`    | Code formatting  | No version bump    | `style(frontend): format components`          |
| `refactor` | Code refactoring | No version bump    | `refactor(api): optimize Brazilian queries`   |
| `perf`     | Performance      | Patch version bump | `perf(database): optimize for large datasets` |
| `test`     | Tests            | No version bump    | `test(auth): add Brazilian user tests`        |
| `chore`    | Maintenance      | No version bump    | `chore(deps): update Brazilian packages`      |
| `build`    | Build system     | No version bump    | `build(docker): add Brazilian locale`         |
| `ci`       | CI/CD            | No version bump    | `ci(github): add Brazilian market checks`     |
| `revert`   | Revert changes   | Patch version bump | `revert: remove experimental BRL feature`     |

## 🎯 Scope Definitions

### Frontend Scopes

| Scope        | Description                    | Brazilian Examples                          |
| ------------ | ------------------------------ | ------------------------------------------- |
| `auth`       | Authentication & authorization | `feat(auth): add Brazilian OAuth providers` |
| `payment`    | Payment processing             | `feat(payment): integrate PIX for BRL`      |
| `ui`         | User interface components      | `fix(ui): Portuguese text overflow`         |
| `i18n`       | Internationalization           | `feat(i18n): add PT-BR translations`        |
| `dashboard`  | User dashboard                 | `feat(dashboard): add BRL balance display`  |
| `onboarding` | User onboarding flow           | `fix(onboarding): Brazilian CPF validation` |

### Backend Scopes

| Scope      | Description             | Brazilian Examples                                    |
| ---------- | ----------------------- | ----------------------------------------------------- |
| `api`      | API endpoints           | `feat(api): add Brazilian document validation`        |
| `database` | Database schema/queries | `refactor(database): optimize Brazilian user queries` |
| `llm`      | LLM integrations        | `feat(llm): add Portuguese resume analysis`           |
| `storage`  | File storage            | `fix(storage): handle Brazilian document formats`     |
| `auth`     | Authentication service  | `feat(auth): implement Brazilian ID verification`     |
| `payment`  | Payment backend         | `feat(payment): add BRL webhook handling`             |

### Infrastructure Scopes

| Scope        | Description              | Brazilian Examples                               |
| ------------ | ------------------------ | ------------------------------------------------ |
| `deploy`     | Deployment configuration | `fix(deploy): Brazilian region deployment`       |
| `security`   | Security configurations  | `feat(security): add LGPD compliance`            |
| `monitoring` | Monitoring & logging     | `feat(monitoring): add Brazilian market metrics` |
| `docker`     | Docker configuration     | `chore(docker): add Brazilian locale support`    |

## 📋 Description Guidelines

### Good Descriptions

- **Concise**: Use imperative mood ("add", "fix", "update")
- **Clear**: Explain what and why, not how
- **Specific**: Include relevant context
- **Brazilian Context**: Mention market-specific aspects when relevant

### Examples

```bash
# ✅ Good
feat(payment): integrate Stripe for BRL transactions
fix(auth): resolve Brazilian CPF validation error
docs(i18n): add Portuguese translation for payment flow
refactor(api): optimize Brazilian user data queries

# ❌ Bad
feat: added payment stuff
fix: auth is broken
docs: updated docs
refactor: made things faster
```

### Description Patterns

```bash
# Feature additions
feat(scope): add [feature] for [Brazilian market aspect]
feat(scope): implement [functionality] with [Brazilian requirement]

# Bug fixes
fix(scope): resolve [issue] affecting [Brazilian users]
fix(scope): handle [edge case] for [Brazilian data]

# Documentation
docs(scope): update [documentation] with [Brazilian information]
docs(i18n): add [Portuguese] translations for [feature]

# Performance
perf(scope): optimize [operation] for [Brazilian dataset size]
perf(scope): improve [functionality] response time
```

## 📄 Body Section Guidelines

### When to Include a Body

- **Complex changes**: Multiple files or components affected
- **Breaking changes**: Detailed explanation required
- **Brazilian market impact**: Specific market considerations
- **Migration needed**: Steps for users to follow
- **Performance impact**: Benchmarks or improvements

### Body Format

```
[type](scope): description

This commit implements [detailed explanation].

Key changes:
- [Change 1 with Brazilian context]
- [Change 2 with market impact]
- [Change 3 with technical details]

Brazilian market considerations:
- [Specific requirement addressed]
- [Compliance aspect handled]
- [User impact description]

Testing:
- [Test approach for Brazilian scenarios]
- [Validation steps performed]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Body Examples

```bash
feat(payment): integrate PIX instant payment for Brazilian users

This commit adds PIX (Brazilian instant payment system) integration to enable
real-time BRL transactions for CV-Match users.

Key changes:
- Added PIX payment method selection in checkout flow
- Implemented webhook handling for PIX confirmation
- Updated payment status tracking for instant settlements
- Added Portuguese error messages for PIX failures

Brazilian market considerations:
- PIX is the most popular instant payment method in Brazil
- 24/7 availability without banking hours restrictions
- Zero transaction fees for end users
- Immediate settlement for business accounts

Testing:
- Verified PIX QR code generation and display
- Tested webhook payload processing
- Validated error handling for failed transactions
- Confirmed Portuguese error message display

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

## 🔗 Footer Section Guidelines

### Breaking Changes

```
BREAKING CHANGE: [detailed description of breaking change]

This change affects [specific functionality]. Users need to:
1. [Action step 1]
2. [Action step 2]
3. [Action step 3]

Brazilian market impact:
- [Specific impact on Brazilian users]
- [Migration requirements]
```

### Issue References

```
Closes: #123
Fixes: #456
Related: #789

Brazilian market ticket: BRL-123
```

### Co-authored By

```
Co-authored-by: Brazilian Team Member <email@example.com>
```

## 🇧🇷 Brazilian Market Specific Guidelines

### Portuguese Terms

```bash
# Use Portuguese terms when appropriate
feat(i18n): add CPF/CNPJ validation for Brazilian users
feat(payment): implement Boleto payment method
docs(pt-br): create Brazilian user onboarding guide
fix(currency): handle Brazilian real (R$) formatting
```

### Compliance References

```bash
feat(security): implement LGPD data consent for Brazilian users
feat(privacy): add Brazilian data protection controls
fix(compliance): update privacy policy for Brazilian regulations
```

### Market Integration

```bash
feat(integration): connect to Brazilian credit bureau API
feat(localization): add Brazilian address validation
feat(market): implement Brazilian pricing tiers in BRL
```

### Cultural Considerations

```bash
feat(ui): add Brazilian holiday calendar to scheduling
fix(format): handle Brazilian date/time formats
feat(content): add Brazilian resume format templates
```

## 📏 Quality Checklist

### Before Committing

- [ ] **Type is correct**: Uses appropriate conventional type
- [ ] **Scope is specific**: Clearly indicates affected area
- [ ] **Description is clear**: Imperative mood, concise
- [ ] **Brazilian context**: Includes market-specific info when relevant
- [ ] **Body if needed**: Detailed explanation for complex changes
- [ ] **Breaking changes**: Clearly marked and explained
- [ ] **Grammar/spelling**: No typos or grammatical errors
- [ ] **Co-author tag**: Added when using Claude Code

### Common Mistakes to Avoid

```bash
# ❌ Common mistakes
feat: added stuff
fix: bug fix
docs: updated
feat: Fix bug (wrong type)
feat(payment): Add BRL (missing description)
feat(payment): add BRL support for payment (lowercase)

# ✅ Correct format
feat(payment): add BRL currency support
fix(auth): resolve Brazilian login timeout
docs(api): update Brazilian payment endpoints
feat(i18n): add Portuguese translations
```

## 🔧 Git Hooks Integration

### Commit Message Validation

```bash
# .husky/commit-msg
#!/bin/sh
# Validate commit message format

commit_msg=$(cat "$1")

# Check for conventional commit format
if ! echo "$commit_msg" | grep -E "^(feat|fix|docs|style|refactor|perf|test|chore|build|ci|revert)(\(.+\))?: .+"; then
  echo "❌ Invalid commit message format"
  echo "✅ Use: type(scope): description"
  echo "📖 See docs/COMMIT-MESSAGE-GUIDELINES.md"
  exit 1
fi

# Check for Brazilian market context when relevant
if echo "$commit_msg" | grep -E "(payment|currency|i18n|auth)" && ! echo "$commit_msg" | grep -E "(BRL|Brazilian|pt-br|CPF|CNPJ|PIX|Boleto)"; then
  echo "⚠️  Consider adding Brazilian market context to payment/i18n/auth commits"
fi

echo "✅ Commit message validation passed"
```

### Pre-commit Integration

```bash
# .husky/pre-commit
#!/bin/sh
# Check commit message quality

# Get current branch
branch=$(git branch --show-current)

# Check if this is a feature branch
if [[ "$branch" =~ ^feature/ ]]; then
  echo "🔍 Checking feature branch commit quality..."

  # Verify commit has proper scope
  latest_commit=$(git log -1 --format=%s)
  if ! echo "$latest_commit" | grep -q "^[a-z]+(\[[a-z]+\]\|([a-z]+)):"; then
    echo "⚠️  Consider adding scope to commit message for better tracking"
  fi
fi
```

## 📊 Commit Message Templates

### Feature Template

```bash
feat(<scope>): add <feature> for <Brazilian market aspect>

This commit implements <detailed description>.

Key changes:
- <Change 1 with Brazilian context>
- <Change 2 with market impact>
- <Change 3 with technical details>

Brazilian market considerations:
- <Specific requirement addressed>
- <User impact description>

Testing:
- <Test approach for Brazilian scenarios>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Bug Fix Template

```bash
fix(<scope>): resolve <issue> affecting <Brazilian users>

This commit fixes <detailed problem description>.

Root cause:
- <Technical explanation>
- <Brazilian market specific factor>

Solution:
- <Fix description>
- <Brazilian context consideration>

Verification:
- <Test steps performed>
- <Brazilian scenario validation>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Breaking Change Template

```bash
<type>(<scope>)!: <breaking change description>

BREAKING CHANGE: <detailed explanation>

This change breaks <specific functionality>.

Migration steps:
1. <Step 1>
2. <Step 2>
3. <Step 3>

Brazilian market impact:
- <Specific impact on Brazilian users>
- <Timeline for migration>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

## 📚 Examples by Category

### Authentication & Authorization

```bash
feat(auth): add Brazilian OAuth providers (Google, LinkedIn)
fix(auth): resolve CPF validation timeout for Brazilian users
feat(auth): implement two-factor authentication for Brazilian market
docs(auth): update Brazilian user onboarding documentation
```

### Payment Integration

```bash
feat(payment): integrate Stripe for BRL transactions
fix(payment): handle BRL currency conversion edge cases
feat(payment): add PIX instant payment method
feat(payment): implement Boleto payment processing
fix(payment): resolve Brazilian tax calculation errors
```

### Internationalization

```bash
feat(i18n): add Portuguese (pt-br) language support
fix(i18n): correct Portuguese translation for payment flow
feat(i18n): implement Brazilian date/time formatting
docs(i18n): create Brazilian localization guide
```

### Database & Storage

```bash
feat(database): add Brazilian user profile fields
refactor(database): optimize queries for Brazilian datasets
feat(storage): support Brazilian document formats (CPF, CNPJ)
fix(database): handle Brazilian address validation constraints
```

### API Development

```bash
feat(api): add Brazilian document validation endpoint
fix(api): resolve timeout for Brazilian credit bureau calls
feat(api): implement BRL currency conversion service
docs(api): update Brazilian market API documentation
```

### Performance & Optimization

```bash
perf(api): optimize Brazilian user data queries
perf(frontend): improve load time for Brazilian users
perf(database): add caching for Brazilian regulatory data
refactor(storage): compress Brazilian document uploads
```

### Security & Compliance

```bash
feat(security): implement LGPD data consent mechanisms
feat(security): add Brazilian IP whitelisting
fix(security): resolve LGPD compliance issue
feat(security): implement Brazilian data encryption standards
```

### Testing & Quality

```bash
test(auth): add Brazilian user authentication tests
test(payment): create BRL transaction test suite
test(i18n): verify Portuguese translation coverage
feat(testing): add Brazilian market test data fixtures
```

## 🛠 Tools and Integration

### VS Code Extension

```json
// .vscode/settings.json
{
  "conventionalCommits.autoCommit": false,
  "conventionalCommits.promptScopes": true,
  "conventionalCommits.promptBody": true,
  "conventionalCommits.customScopes": [
    "auth",
    "payment",
    "api",
    "frontend",
    "backend",
    "database",
    "i18n",
    "security",
    "brazilian-market"
  ]
}
```

### Git Aliases

```bash
# Add to .gitconfig
[alias]
  cm = "!git commit -m \"$(cat)\""
  feat = "!git commit -m \"feat: \""
  fix = "!git commit -m \"fix: \""
  docs = "!git commit -m \"docs: \""
  amend = "!git commit --amend --no-edit"
```

### Commitizen Integration

```json
// .commitlintrc.json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "chore",
        "build",
        "ci",
        "revert"
      ]
    ],
    "subject-case": [2, "never", ["start-case", "pascal-case", "upper-case"]],
    "body-leading-blank": [1, "always"],
    "footer-leading-blank": [1, "always"]
  }
}
```

## 📈 Continuous Improvement

### Metrics to Track

- **Commit Quality**: Percentage following guidelines
- **Brazilian Context**: Commits with market-specific info
- **Breakage Rate**: Breaking changes frequency
- **Message Length**: Average commit message length
- **Scope Usage**: Percentage with proper scope

### Review Process

1. **Automated Validation**: Git hooks check format
2. **Peer Review**: Team reviews commit messages
3. **Brazilian Review**: Market team validates context
4. **Quality Metrics**: Track compliance over time
5. **Guideline Updates**: Refine based on feedback

### Training and Resources

- **Onboarding**: Include commit guidelines in new hire training
- **Documentation**: Keep this guide updated with examples
- **Tools**: Provide IDE extensions and git aliases
- **Reviews**: Regular commit message quality reviews
- **Brazilian Context**: Market-specific training sessions

## 🎯 Best Practices Summary

### DO ✅

1. **Use conventional format**: `type(scope): description`
2. **Be specific**: Include relevant context and scope
3. **Think Brazilian**: Add market-specific information when relevant
4. **Use imperative mood**: "add", "fix", "update", not "added", "fixed"
5. **Explain breaking changes**: Clear migration path
6. **Reference issues**: Link to related tickets or PRs
7. **Keep it concise**: Subject line under 72 characters
8. **Add co-author tag**: When using Claude Code
9. **Use body for complexity**: Detailed explanations for complex changes
10. **Consider LGPD**: Include compliance information for data changes

### DON'T ❌

1. **Skip the type**: Always include conventional type
2. **Vague descriptions**: "fixed stuff", "added things"
3. **Mix types**: `feat: fix bug` (should be `fix:`)
4. **Forget Brazilian context**: When market-specific changes are made
5. **Ignore breaking changes**: Always mark and explain
6. **Use past tense**: "added feature" → "add feature"
7. **Include unnecessary details**: Keep subject line focused
8. **Forget scope**: When multiple areas are affected
9. **Ignore format**: Follow the conventional commit structure
10. **Skip documentation**: Document complex changes in body

---

Following these commit message guidelines ensures a clear, maintainable project history that supports automated tooling, effective collaboration, and proper Brazilian market context for the CV-Match SaaS platform.
