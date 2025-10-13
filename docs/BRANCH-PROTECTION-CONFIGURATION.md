# Branch Protection Configuration for CV-Match Brazilian SaaS

## Overview

This document outlines the comprehensive branch protection configuration implemented for the CV-Match project to ensure code quality, security, and compliance with Brazilian market requirements.

## 🎯 Objectives

1. **Code Quality**: Ensure all changes meet quality standards
2. **Security**: Prevent unauthorized changes to critical branches
3. **Compliance**: Maintain LGPD and Brazilian regulatory compliance
4. **Collaboration**: Enforce proper review processes
5. **Stability**: Protect production and integration branches

## 🔒 Protected Branches

### Main Branches

| Branch | Purpose | Protection Level | Brazilian Context |
|--------|---------|------------------|-------------------|
| `main` | Production code | 🔒 Maximum protection | Production Brazilian SaaS |
| `develop` | Integration branch | 🔒 High protection | Staging Brazilian features |

### Protection Rules Summary

```yaml
# Branch Protection Rules
main:
  required_reviews: 2
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  require_up_to_date: true
  require_linear_history: true
  restrict_pushes: true
  allowed_pushers: ["maintainers", "admins"]
  require_status_checks: all
  required_status_checks:
    - frontend-quality
    - backend-quality
    - security-scan
    - database-migration
    - brazilian-market-compliance

develop:
  required_reviews: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: false
  require_up_to_date: true
  require_linear_history: true
  restrict_pushes: true
  allowed_pushers: ["maintainers", "developers", "admins"]
  require_status_checks: core
  required_status_checks:
    - frontend-quality
    - backend-quality
    - security-scan
```

## 📋 Detailed Configuration

### Main Branch Protection

#### Basic Settings
- **Require pull request reviews before merging**: Enabled
- **Required approving reviews**: 2
- **Dismiss stale PR approvals when new commits are pushed**: Enabled
- **Require review from Code Owners**: Enabled
- **Require up-to-date branches before merging**: Enabled
- **Require linear history**: Enabled

#### Additional Restrictions
- **Limit who can push to matching branches**: Enabled
- **Allowed to push**: Maintainers and Admins only
- **Allow force pushes**: Disabled
- **Allow deletions**: Disabled

#### Required Status Checks
- **Require status checks to pass before merging**: Enabled
- **Required status checks**: All selected

#### Brazilian Market Specific Checks
```yaml
brazilian-market-compliance:
  - Portuguese localization verification
  - BRL payment integration tests
  - LGPD compliance validation
  - Brazilian regulatory requirements
  - Market-specific documentation updates
```

### Develop Branch Protection

#### Basic Settings
- **Require pull request reviews before merging**: Enabled
- **Required approving reviews**: 1
- **Dismiss stale PR approvals when new commits are pushed**: Enabled
- **Require up-to-date branches before merging**: Enabled
- **Require linear history**: Enabled
- **Require conversation resolution before merging**: Enabled

#### Additional Restrictions
- **Limit who can push to matching branches**: Enabled
- **Allowed to push**: Maintainers, Developers, and Admins
- **Allow force pushes**: Disabled
- **Allow deletions**: Disabled

#### Required Status Checks
- **Require status checks to pass before merging**: Enabled
- **Required status checks**: Core checks only

## 🔧 Status Checks Configuration

### Frontend Quality Checks
```yaml
frontend-quality:
  description: "Frontend code quality and build validation"
  context: "frontend-quality"

  checks:
    - type_check:
        command: "bun run type-check"
        description: "TypeScript type checking"

    - lint:
        command: "bun run lint"
        description: "ESLint code quality"

    - format_check:
        command: "bun run format:check"
        description: "Prettier formatting verification"

    - build:
        command: "bun run build"
        description: "Production build validation"
        environment_variables:
          - NEXT_PUBLIC_SUPABASE_URL
          - NEXT_PUBLIC_SUPABASE_ANON_KEY
          - NEXT_PUBLIC_API_URL

  brazilian_specific:
    - portuguese_translation_check:
        description: "Verify Portuguese translations are complete"

    - brl_currency_validation:
        description: "Validate BRL currency formatting"
```

### Backend Quality Checks
```yaml
backend-quality:
  description: "Backend code quality and API validation"
  context: "backend-quality"

  checks:
    - type_check:
        command: "uv run mypy ."
        description: "Python type checking"

    - lint:
        command: "uv run ruff check ."
        description: "Ruff code quality"

    - format_check:
        command: "uv run ruff format --check ."
        description: "Code formatting verification"

    - tests:
        command: "uv run pytest"
        description: "Test suite execution"
        coverage_threshold: 80

  brazilian_specific:
    - lgpd_compliance_check:
        description: "Verify LGPD compliance in data handling"

    - brazilian_validation_tests:
        description: "Test Brazilian-specific validations"
```

### Security Scan
```yaml
security-scan:
  description: "Security vulnerability scanning"
  context: "security-scan"

  checks:
    - dependency_audit:
        description: "Check for vulnerable dependencies"
        tools: ["trivy", "safety"]

    - secret_detection:
        description: "Scan for exposed secrets"
        tools: ["git-secrets", "trufflehog"]

    - code_security:
        description: "Static code security analysis"
        tools: ["bandit", "semgrep"]

  brazilian_specific:
    - lgpd_security_check:
        description: "Verify data protection for Brazilian users"

    - payment_security:
        description: "Validate BRL payment security measures"
```

### Database Migration Check
```yaml
database-migration:
  description: "Database migration validation"
  context: "database-migration"

  checks:
    - migration_syntax:
        description: "Validate SQL migration syntax"
        command: "psql --syntax-check"

    - migration_order:
        description: "Verify migration order and dependencies"

    - rollback_validation:
        description: "Ensure migrations can be rolled back"

  brazilian_specific:
    - brazilian_data_compliance:
        description: "Verify Brazilian data handling compliance"

    - lgpd_migration_check:
        description: "Check migrations for LGPD compliance"
```

### Brazilian Market Compliance
```yaml
brazilian-market-compliance:
  description: "Brazilian market specific validations"
  context: "brazilian-market-compliance"

  checks:
    - localization_completeness:
        description: "Verify Portuguese (pt-br) translations"
        required_files:
          - "frontend/messages/pt-br.json"
          - "docs/pt-br/"

    - payment_integration:
        description: "Validate BRL payment methods"
        required_methods:
          - "credit_card_brl"
          - "pix"
          - "boleto"

    - regulatory_compliance:
        description: "Check Brazilian regulatory requirements"
        requirements:
          - "LGPD consent mechanisms"
          - "Brazilian data storage"
          - "Local payment processing"

    - documentation_completeness:
        description: "Ensure Brazilian market documentation"
        required_docs:
          - "docs/brazilian-market/"
          - "docs/lgpd-compliance/"
          - "docs/brl-payments/"
```

## 👥 Team Access Configuration

### Permission Levels

| Role | Main Branch | Develop Branch | Description |
|------|-------------|----------------|-------------|
| **Admin** | ✅ Full Access | ✅ Full Access | Repository administrators |
| **Maintainer** | ✅ Merge + Push | ✅ Full Access | Senior developers, tech leads |
| **Developer** | ❌ No Direct Push | ✅ Push + PR | Regular developers |
| **Brazilian Team** | ❌ No Direct Push | ✅ Push + PR | Market specialists |
| **External Contributor** | ❌ No Access | ✅ PR Only | Community contributors |

### Code Ownership Configuration

```yaml
# .github/CODEOWNERS
# Global code owners
* @carlosnunes @cv-match/maintainers

# Frontend
frontend/ @cv-match/frontend-team
frontend/components/ @cv-match/ui-team
frontend/app/ @cv-match/frontend-team

# Backend
backend/ @cv-match/backend-team
backend/app/api/ @cv-match/api-team
backend/app/services/ @cv-match/backend-team

# Brazilian Market
docs/brazilian-market/ @cv-match/brazilian-team
frontend/messages/pt-br.json @cv-match/brazilian-team
backend/app/services/brazilian/ @cv-match/brazilian-team

# Database
supabase/migrations/ @cv-match/backend-team @cv-match/devops-team

# Security
backend/app/security/ @cv-match/security-team
docs/security/ @cv-match/security-team

# Documentation
docs/ @cv-match/docs-team
README.md @cv-match/maintainers
```

## 🚀 Automated Workflows

### Pull Request Automation

#### PR Validation Workflow
```yaml
name: PR Validation and Automation

on:
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]

jobs:
  validate-pr:
    runs-on: ubuntu-latest
    steps:
    - name: Validate PR structure
      uses: actions/github-script@v6
      with:
        script: |
          // Validate PR title follows conventional commits
          // Validate PR description completeness
          // Check for Brazilian market considerations
          // Verify required reviewers assigned

    - name: Add Brazilian market labels
      if: contains(github.event.pull_request.title, 'brazilian') || contains(github.event.pull_request.title, 'BRL')
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.addLabels({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            labels: ['brazilian-market', 'priority-high']
          })

    - name: Request required reviewers
      uses: actions/github-script@v6
      with:
        script: |
          // Automatically request reviews based on files changed
          // Brazilian market changes require Brazilian team review
          // Security changes require security team review
```

### Quality Gate Automation

#### Branch Protection Enforcement
```yaml
name: Branch Protection Enforcement

on:
  pull_request:
    branches: [main, develop]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
    - name: Check quality gates
      run: |
        # Ensure all quality checks pass
        # Verify Brazilian market compliance
        # Check documentation completeness
        # Validate security requirements

    - name: Block merge if requirements not met
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '❌ **Quality gates not met**. Please address all failing checks before merging.'
          })
```

## 🇧🇷 Brazilian Market Specific Protections

### LGPD Compliance Enforcement
```yaml
lgpd_protection:
  description: "LGPD compliance enforcement for Brazilian market"

  triggers:
    - files_changed:
        patterns:
          - "backend/app/models/user.py"
          - "backend/app/services/auth.py"
          - "supabase/migrations/*"

  checks:
    - data_consent_validation:
        description: "Verify LGPD consent mechanisms"
        required_fields:
          - "data_processing_consent"
          - "marketing_consent"
          - "analytics_consent"

    - brazilian_data_residency:
        description: "Ensure Brazilian user data is stored appropriately"
        validation_rules:
          - "Brazilian user data must be stored in compliant regions"
          - "Data export mechanisms must respect LGPD"

    - privacy_policy_sync:
        description: "Privacy policy must reflect Brazilian changes"
        required_files:
          - "docs/privacy-policy-pt-br.md"
          - "frontend/components/privacy/ConsentModal.tsx"
```

### BRL Payment Protection
```yaml
brl_payment_protection:
  description: "BRL payment method protection"

  triggers:
    - files_changed:
        patterns:
          - "backend/app/services/payment/*"
          - "frontend/components/payment/*"
          - "supabase/migrations/*payment*"

  checks:
    - payment_method_validation:
        description: "Validate BRL payment methods"
        required_methods:
          - "PIX"
          - "Boleto"
          - "Credit Card (BRL)"

    - tax_calculation_validation:
        description: "Verify Brazilian tax calculations"
        required_fields:
          - "IOF calculation"
          - "State tax handling"
          - "VAT considerations"

    - compliance_verification:
        description: "Check payment compliance"
        requirements:
          - "PCI DSS compliance"
          - "Brazilian Central Bank regulations"
          - "Anti-money laundering (AML) checks"
```

## 🔍 Monitoring and Enforcement

### Compliance Monitoring
```yaml
compliance_monitoring:
  description: "Continuous compliance monitoring"

  metrics:
    - branch_protection_compliance:
        description: "Percentage of merges following protection rules"
        threshold: 100%

    - brazilian_market_compliance:
        description: "Brazilian market requirement compliance"
        threshold: 95%

    - lgpd_compliance_score:
        description: "LGPD compliance score"
        threshold: 100%

  alerts:
    - protection_bypass:
        description: "Alert when branch protection is bypassed"
        recipients: ["maintainers", "security-team"]

    - compliance_violation:
        description: "Alert when Brazilian market compliance fails"
        recipients: ["brazilian-team", "maintainers"]
```

### Enforcement Actions
```yaml
enforcement_actions:
  automatic:
    - block_merge_on_failure:
        description: "Block PR merge if any required check fails"

    - auto_request_reviews:
        description: "Automatically request reviews based on changes"

    - add_compliance_labels:
        description: "Add labels for Brazilian market compliance"

  manual:
    - security_review_required:
        description: "Manual security review for sensitive changes"
        triggers: ["authentication", "payment", "database"]

    - brazilian_market_review:
        description: "Brazilian team review for market-specific changes"
        triggers: ["localization", "payment", "regulation"]
```

## 📋 Configuration Files

### GitHub Branch Protection API
```bash
# Set up main branch protection
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/cv-match/cv-match/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": [
        "frontend-quality",
        "backend-quality",
        "security-scan",
        "database-migration",
        "brazilian-market-compliance"
      ]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "required_approving_review_count": 2,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true
    },
    "restrictions": {
      "users": ["carlosnunes"],
      "teams": ["maintainers", "admins"]
    }
  }'
```

### GitHub Configuration as Code
```yaml
# .github/branch-protection.yml
protection_rules:
  main:
    required_reviews: 2
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
    require_up_to_date: true
    require_linear_history: true
    enforce_admins: true
    required_status_checks:
      strict: true
      contexts:
        - frontend-quality
        - backend-quality
        - security-scan
        - database-migration
        - brazilian-market-compliance
    restrictions:
      users: ["carlosnunes"]
      teams: ["maintainers", "admins"]

  develop:
    required_reviews: 1
    dismiss_stale_reviews: true
    require_up_to_date: true
    require_linear_history: true
    enforce_admins: false
    required_status_checks:
      strict: true
      contexts:
        - frontend-quality
        - backend-quality
        - security-scan
    restrictions:
      teams: ["maintainers", "developers", "admins"]
```

## 🔄 Maintenance and Updates

### Regular Review Schedule
- **Monthly**: Review and update protection rules
- **Quarterly**: Comprehensive compliance audit
- **Ad-hoc**: Update when new requirements emerge

### Update Process
1. **Assess Changes**: Evaluate new requirements
2. **Update Configuration**: Modify protection rules
3. **Test Changes**: Validate in develop branch
4. **Communicate**: Notify team of changes
5. **Deploy**: Apply to main branch
6. **Monitor**: Track effectiveness

### Rollback Procedures
```bash
# Emergency rollback of protection rules
curl -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/cv-match/cv-match/branches/main/protection

# Restore from backup configuration
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/cv-match/cv-match/branches/main/protection \
  -d @backup-protection-config.json
```

## 📊 Reporting and Analytics

### Compliance Dashboard
```yaml
compliance_dashboard:
  metrics:
    - protection_rule_compliance: 100%
    - merge_success_rate: 95%
    - pr_review_time: <24h
    - quality_check_pass_rate: 98%
    - brazilian_market_compliance: 100%

  alerts:
    - protection_bypass_attempt: Immediate
    - compliance_violation: Within 1 hour
    - quality_check_failure: Within 30 minutes
```

### Monthly Reports
- **Branch Protection Effectiveness**: Success rates, bypass attempts
- **Quality Metrics**: Test coverage, code quality trends
- **Brazilian Market Compliance**: Localization completeness, payment integration status
- **Security Posture**: Vulnerability scan results, compliance status
- **Team Performance**: Review times, PR throughput

## 🎯 Best Practices

### DO ✅
1. **Regular Reviews**: Monthly review of protection rules
2. **Brazilian Context**: Include market-specific requirements
3. **Compliance Focus**: LGPD and regulatory compliance
4. **Team Training**: Regular training on protection rules
5. **Monitoring**: Continuous monitoring and alerting
6. **Documentation**: Keep configuration documented
7. **Testing**: Test changes in develop branch first
8. **Communication**: Notify team of rule changes
9. **Backup**: Maintain backup configurations
10. **Audit Trail**: Log all protection rule changes

### DON'T ❌
1. **Bypass Protection**: Never disable protection without justification
2. **Ignore Brazilian Requirements**: Market-specific compliance is critical
3. **Skip Reviews**: All changes must be properly reviewed
4. **Forget Documentation**: Keep all rules documented
5. **Ignore Alerts**: Act on all compliance alerts promptly
6. **Rush Changes**: Test thoroughly before deployment
7. **Forget Rollback**: Always have rollback procedures
8. **Skip Training**: Ensure team understands rules
9. **Ignore Metrics**: Monitor effectiveness continuously
10. **Bypass Quality**: Never merge without quality checks

---

This branch protection configuration ensures the CV-Match Brazilian SaaS platform maintains high code quality, security standards, and regulatory compliance while enabling effective team collaboration and continuous delivery.