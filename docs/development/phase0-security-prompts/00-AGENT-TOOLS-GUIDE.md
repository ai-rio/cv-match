# 🛠️ Phase 0 Security Implementation - Agent Tools Guide

**Purpose**: Security testing tools, database migration tools, and verification requirements for all agents
**Scope**: Comprehensive tooling setup for Phase 0 security implementation
**Priority**: CRITICAL - All agents must complete setup before starting work

> 🚨 **MANDATORY SETUP**: All agents must complete the tool setup in this guide before starting any Phase 0 security work. Failure to use proper tools will result in incomplete security fixes and rejected PRs.

---

## 📋 Table of Contents

1. [Required Tools for All Agents](#required-tools-for-all-agents)
2. [Security Testing Tools](#security-testing-tools)
3. [Database Security Tools](#database-security-tools)
4. [Code Analysis Tools](#code-analysis-tools)
5. [LGPD Compliance Tools](#lgpd-compliance-tools)
6. [Documentation Tools](#documentation-tools)
7. [Environment Setup](#environment-setup)
8. [Tool Configuration](#tool-configuration)
9. [Verification Procedures](#verification-procedures)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Required Tools for All Agents

### Core Development Tools

```bash
# Essential tools - install if not present
which git  # Version control
which node  # Node.js runtime
which python3  # Python runtime
which docker  # Container platform
which make  # Build automation
```

### Security-Specific Tools

```bash
# Install security testing tools
pip install bandit  # Python security linter
pip install safety  # Dependency vulnerability scanner
bun install -g audit-ci  # Node.js security auditor
bun install -g retire  # Dependency scanner
```

### CV-Match Project Tools

```bash
# Verify project-specific tools are available
make help  # Check Makefile commands
which supabase  # Supabase CLI
which psql  # PostgreSQL client
which uv  # Python package manager
which bun  # Frontend package manager
```

---

## 🔒 Security Testing Tools

### 1. Static Application Security Testing (SAST)

#### Backend Security Scanner
```bash
# Python security scanning
pip install bandit[toml]

# Usage:
bandit -r backend/app/ -f json -o security-report.json
bandit -r backend/app/ -f txt -o security-report.txt

# Integration with pre-commit
bandit -r backend/app/ --severity-level high
```

#### Frontend Security Scanner
```bash
# Node.js security scanning
bun install -g audit-ci

# Usage:
cd frontend
audit-ci --moderate

# Dependency vulnerability scan
bun audit --audit-level high
```

### 2. Dynamic Application Security Testing (DAST)

#### API Security Testing
```bash
# Install OWASP ZAP or use cloud service
# Basic API testing with curl:
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "wrong"}' \
  -w "%{http_code}\n"

# Test authentication bypass attempts
curl -X GET http://localhost:8000/api/resumes/ \
  -H "Authorization: Bearer invalid_token" \
  -w "%{http_code}\n"
```

#### Web Application Security Testing
```bash
# Use OWASP ZAP Baseline Scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:3000 \
  -J zap-report.json

# Alternative: Use Burp Suite Community Edition
```

### 3. Infrastructure Security Testing

#### Container Security
```bash
# Docker security scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image cv-match:latest

# Kubernetes security (if using)
kubectl auth can-i --list --as=system:serviceaccount:default:default
```

#### Database Security Testing
```bash
# PostgreSQL security check
psql $DATABASE_URL -c "\l+"  # List databases
psql $DATABASE_URL -c "\du"  # List users
psql $DATABASE_URL -c "SELECT table_name, row_security FROM pg_tables WHERE schemaname = 'public';"
```

---

## 🗄️ Database Security Tools

### 1. Supabase/PostgreSQL Tools

#### Database Migration Tools
```bash
# Supabase CLI setup
supabase login
supabase link --project-ref your-project-ref
supabase db push  # Apply migrations
supabase db diff  # Compare schema
supabase db reset  # Reset database (development only)
```

#### Database Security Analysis
```bash
# Check RLS policies
psql $DATABASE_URL -c "
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename LIKE '%resume%';
"

# Verify foreign key constraints
psql $DATABASE_URL -c "
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
"
```

### 2. Database Schema Validation

#### Schema Security Check
```bash
# Create security check script
cat > db_security_check.sql << 'EOF'
-- Check for tables without RLS
SELECT table_name
FROM pg_tables
WHERE schemaname = 'public'
  AND rowsecurity = false
  AND table_name NOT LIKE 'migration%';

-- Check for columns without constraints
SELECT table_name, column_name, is_nullable, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND is_nullable = 'YES'
  AND column_name LIKE '%user_id';

-- Check for missing indexes on foreign keys
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
LEFT JOIN pg_index ON tc.constraint_name = pg_index.indexrelid::text
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND pg_index.indexrelid IS NULL;
EOF

# Run security check
psql $DATABASE_URL -f db_security_check.sql
```

### 3. Data Migration Security

#### Secure Migration Practices
```bash
# Create backup before migration
supabase db dump --data-only -f backup_$(date +%Y%m%d_%H%M%S).sql

# Test migration on staging first
# Use transactional migrations
BEGIN;
-- Migration SQL here
-- Verify results
ROLLBACK;  -- or COMMIT if successful

# Verify data integrity after migration
psql $DATABASE_URL -c "
SELECT COUNT(*) FROM resumes WHERE user_id IS NULL;
SELECT COUNT(*) FROM user_profiles WHERE user_id IS NULL;
"
```

---

## 🔍 Code Analysis Tools

### 1. Security Code Review

#### Backend Code Analysis
```bash
# Python security analysis with bandit
bandit -r backend/app/ \
  -f json \
  -o bandit-report.json \
  --severity-level high

# Custom security rules for CV-Match
bandit -r backend/app/ \
  --severity-level medium \
  --confidence-level high \
  -B backend/security_issues/

# Check for hardcoded secrets
grep -r -i "password\|secret\|key\|token" backend/app/ \
  --include="*.py" \
  --exclude-dir=__pycache__ | grep -v "getenv\|environ"
```

#### Frontend Code Analysis
```bash
# JavaScript/TypeScript security analysis
bun install -g eslint-plugin-security

# Create .eslintrc.js for security rules
cat > .eslintrc.js << 'EOF'
module.exports = {
  extends: [
    'plugin:security/recommended'
  ],
  rules: {
    'security/detect-eval-with-expression': 'error',
    'security/detect-non-literal-regexp': 'error',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'error',
    'security/detect-disable-mustache-escape': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-non-literal-fs-filename': 'error',
    'security/detect-non-literal-require': 'error',
    'security/detect-object-injection': 'error',
    'security/detect-possible-timing-attacks': 'error',
    'security/detect-pseudoRandomBytes': 'error'
  }
};
EOF

# Run security linting
cd frontend
npx eslint . --ext .ts,.tsx --format json -o eslint-security-report.json
```

### 2. Dependency Security Scanning

#### Python Dependencies
```bash
# Safety scanner for Python vulnerabilities
pip install safety
safety check --json --output safety-report.json

# Check for known vulnerable packages
pip-audit --format json --output pip-audit-report.json

# Update dependencies securely
pip install --upgrade pip setuptools wheel
pip-review --local --interactive
```

#### Node.js Dependencies
```bash
# Audit Node.js dependencies
cd frontend
bun audit --json --audit-level high > npm-audit-report.json

# Check for outdated packages
bun outdated --json > npm-outdated-report.json

# Update dependencies securely
bun update
bun audit fix
```

### 3. Code Quality Analysis

#### Backend Code Quality
```bash
# Python code quality
pip install flake8 pydocstyle black isort

# Run quality checks
flake8 backend/app/ --format=json --output=flake8-report.json
pydocstyle backend/app/ --json > pydocstyle-report.json
black --check --diff backend/app/ > black-report.txt
isort --check-only --diff backend/app/ > isort-report.txt
```

#### Frontend Code Quality
```bash
# TypeScript/JavaScript code quality
cd frontend

# Prettier formatting check
npx prettier --check . --json > prettier-report.json

# TypeScript compilation check
npx tsc --noEmit --pretty false > typescript-report.txt
```

---

## 🛡️ LGPD Compliance Tools

### 1. PII Detection and Analysis

#### PII Detection Script
```bash
# Create PII detection tool
cat > pii_detector.py << 'EOF'
import re
import json
from typing import List, Dict, Any

PIIPATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
    'phone': r'\b(?:\+55\s?)?(?:\(?[1-9]{2}\)?\s?)?(?:[2-9]\d{4}-?\d{4})\b',
    'rg': r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[A-Z0-9]\b',
    'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
}

def detect_pii(text: str) -> Dict[str, List[str]]:
    """Detect PII patterns in text."""
    findings = {}
    for pii_type, pattern in PIIPATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            findings[pii_type] = matches
    return findings

def scan_file_for_pii(file_path: str) -> Dict[str, Any]:
    """Scan a file for PII."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            'file': file_path,
            'pii_found': detect_pii(content),
            'size': len(content)
        }
    except Exception as e:
        return {'file': file_path, 'error': str(e)}

if __name__ == '__main__':
    import sys
    result = scan_file_for_pii(sys.argv[1])
    print(json.dumps(result, indent=2))
EOF

# Install required Python packages
pip install python-dotenv

# Usage examples
python pii_detector.py backend/app/models/user.py
python pii_detector.py frontend/components/ResumeUpload.tsx
```

#### Data Masking Tool
```bash
# Create data masking utility
cat > data_masker.py << 'EOF'
import re
import hashlib
from typing import Dict, Any

def mask_email(email: str) -> str:
    """Mask email address."""
    if '@' not in email:
        return email
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"

def mask_cpf(cpf: str) -> str:
    """Mask CPF number."""
    # Remove non-digits
    cpf_digits = re.sub(r'\D', '', cpf)
    if len(cpf_digits) != 11:
        return cpf
    return f"***{cpf_digits[-3]}-{cpf_digits[-2:]}"

def mask_phone(phone: str) -> str:
    """Mask phone number."""
    # Remove non-digits
    phone_digits = re.sub(r'\D', '', phone)
    if len(phone_digits) < 4:
        return phone
    return f"**{phone_digits[-4:]}"

def mask_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask PII in data dictionary."""
    masked = data.copy()

    # Common PII field names
    pii_fields = {
        'email': mask_email,
        'cpf': mask_cpf,
        'telefone': mask_phone,
        'phone': mask_phone,
        'celular': mask_phone,
        'mobile': mask_phone,
    }

    for field, masker in pii_fields.items():
        if field in masked and masked[field]:
            masked[field] = masker(str(masked[field]))

    return masked

if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        masked = mask_data(data)
        print(json.dumps(masked, indent=2))
EOF
```

### 2. Consent Management Tools

#### Consent Tracking Script
```bash
# Create consent management utility
cat > consent_manager.py << 'EOF'
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json

class ConsentManager:
    def __init__(self):
        self.consents = {}

    def record_consent(self, user_id: str, consent_type: str,
                      granted: bool, purpose: str,
                      legal_basis: str = "explicit") -> Dict:
        """Record user consent."""
        consent_record = {
            "user_id": user_id,
            "consent_type": consent_type,
            "granted": granted,
            "purpose": purpose,
            "legal_basis": legal_basis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": None,  # Should be captured from request
            "user_agent": None,  # Should be captured from request
        }

        if user_id not in self.consents:
            self.consents[user_id] = []

        self.consents[user_id].append(consent_record)
        return consent_record

    def check_consent(self, user_id: str, consent_type: str) -> Optional[Dict]:
        """Check if user has given valid consent."""
        if user_id not in self.consents:
            return None

        user_consents = self.consents[user_id]
        relevant_consents = [
            c for c in user_consents
            if c["consent_type"] == consent_type and c["granted"]
        ]

        if not relevant_consents:
            return None

        # Return most recent consent
        return max(relevant_consents, key=lambda x: x["timestamp"])

    def revoke_consent(self, user_id: str, consent_type: str) -> Dict:
        """Revoke user consent."""
        return self.record_consent(
            user_id=user_id,
            consent_type=consent_type,
            granted=False,
            purpose="User revocation",
            legal_basis="explicit"
        )

    def export_consents(self, user_id: str) -> List[Dict]:
        """Export all user consents (data portability)."""
        return self.consents.get(user_id, [])

    def delete_consents(self, user_id: str) -> bool:
        """Delete all user consents (right to be forgotten)."""
        if user_id in self.consents:
            del self.consents[user_id]
            return True
        return False

# LGPD required consent types
LGPD_CONSENT_TYPES = [
    "data_processing",
    "email_marketing",
    "analytics",
    "cookies",
    "third_party_sharing",
    "ai_processing"
]

if __name__ == '__main__':
    # Example usage
    manager = ConsentManager()

    # Record consent
    consent = manager.record_consent(
        user_id="user123",
        consent_type="data_processing",
        granted=True,
        purpose="Resume processing and matching",
        legal_basis="explicit"
    )
    print(json.dumps(consent, indent=2))
EOF
```

### 3. Data Retention Management

#### Retention Policy Tool
```bash
# Create data retention management tool
cat > retention_manager.py << 'EOF'
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import json

class RetentionManager:
    def __init__(self):
        self.retention_policies = {
            "user_profile": timedelta(days=365 * 7),  # 7 years
            "resume": timedelta(days=365 * 2),        # 2 years
            "application": timedelta(days=365),       # 1 year
            "analytics": timedelta(days=395),         # 13 months
            "consent_records": timedelta(days=365 * 10),  # 10 years
            "audit_logs": timedelta(days=365 * 6),     # 6 years
        }

    def check_retention(self, data_type: str, created_date: str) -> bool:
        """Check if data should be retained based on retention policy."""
        if data_type not in self.retention_policies:
            return True  # Keep if no policy defined

        created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        retention_period = self.retention_policies[data_type]
        expiry_date = created + retention_period

        return datetime.now(timezone.utc) < expiry_date

    def get_retention_schedule(self) -> Dict[str, Dict]:
        """Get data retention schedule for all data types."""
        schedule = {}
        now = datetime.now(timezone.utc)

        for data_type, period in self.retention_policies.items():
            schedule[data_type] = {
                "retention_period_days": period.days,
                "retention_period_years": period.days / 365,
                "policy_description": f"Keep for {period.days} days"
            }

        return schedule

    def identify_expired_data(self, data_items: List[Dict]) -> List[Dict]:
        """Identify data items that have exceeded retention period."""
        expired = []

        for item in data_items:
            data_type = item.get("type")
            created_date = item.get("created_date")

            if not data_type or not created_date:
                continue

            if not self.check_retention(data_type, created_date):
                expired.append(item)

        return expired

# Usage example
if __name__ == '__main__':
    manager = RetentionManager()

    # Get retention schedule
    schedule = manager.get_retention_schedule()
    print(json.dumps(schedule, indent=2))
EOF
```

---

## 📚 Documentation Tools

### 1. Security Documentation Generator

#### Security Documentation Script
```bash
# Create security documentation generator
cat > security_docs_generator.py << 'EOF'
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class SecurityDocumentationGenerator:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.security_measures = []

    def add_security_measure(self, measure: Dict[str, Any]):
        """Add a security measure to the documentation."""
        measure["documented_at"] = datetime.now().isoformat()
        self.security_measures.append(measure)

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        return {
            "project_path": self.project_path,
            "generated_at": datetime.now().isoformat(),
            "security_measures": self.security_measures,
            "summary": {
                "total_measures": len(self.security_measures),
                "categories": list(set(m["category"] for m in self.security_measures)),
                "status": "implemented"
            }
        }

    def export_markdown(self, report: Dict[str, Any]) -> str:
        """Export security report as Markdown."""
        md = f"""# Security Implementation Report

**Generated**: {report['generated_at']}
**Project**: {report['project_path']}
**Total Security Measures**: {report['summary']['total_measures']}

## Summary

- **Categories**: {', '.join(report['summary']['categories'])}
- **Status**: {report['summary']['status']}

## Security Measures Implemented

"""

        for measure in report['security_measures']:
            md += f"""### {measure['title']}

**Category**: {measure['category']}
**Implemented**: {measure.get('implemented', 'Unknown')}
**Tested**: {measure.get('tested', 'Unknown')}

{measure.get('description', 'No description')}

"""

            if 'verification_steps' in measure:
                md += "**Verification Steps**:\n"
                for step in measure['verification_steps']:
                    md += f"- [ ] {step}\n"
                md += "\n"

        return md

# Example usage
if __name__ == '__main__':
    generator = SecurityDocumentationGenerator("/home/carlos/projects/cv-match")

    # Add security measures
    generator.add_security_measure({
        "title": "User Authorization Implementation",
        "category": "Authentication",
        "description": "Implemented user authorization to ensure users can only access their own data",
        "implemented": True,
        "tested": True,
        "verification_steps": [
            "Test cross-user data access (should fail)",
            "Verify RLS policies are active",
            "Check user ownership of resources"
        ]
    })

    report = generator.generate_security_report()
    markdown = generator.export_markdown(report)

    with open("security_report.md", "w") as f:
        f.write(markdown)

    print("Security documentation generated: security_report.md")
EOF
```

### 2. API Documentation Security

#### OpenAPI Security Documentation
```bash
# Create security-focused OpenAPI documentation generator
cat > generate_security_docs.py << 'EOF'
import json
from typing import Dict, Any

def add_security_schemes(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Add security schemes to OpenAPI specification."""
    if "components" not in openapi_spec:
        openapi_spec["components"] = {}

    openapi_spec["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    return openapi_spec

def add_security_requirements(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Add security requirements to all endpoints."""
    security_requirements = [{"bearerAuth": []}]

    if "paths" in openapi_spec:
        for path in openapi_spec["paths"]:
            for method in openapi_spec["paths"][path]:
                if method.upper() != "GET" or "secure" in path.lower():
                    openapi_spec["paths"][path][method]["security"] = security_requirements

    return openapi_spec

def add_security_responses(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Add security response definitions."""
    if "components" not in openapi_spec:
        openapi_spec["components"] = {}

    openapi_spec["components"]["responses"] = {
        "Unauthorized": {
            "description": "Unauthorized access",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"},
                            "error_code": {"type": "string"}
                        }
                    }
                }
            }
        },
        "Forbidden": {
            "description": "Access forbidden",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"},
                            "error_code": {"type": "string"}
                        }
                    }
                }
            }
        },
        "TooManyRequests": {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"},
                            "retry_after": {"type": "integer"}
                        }
                    }
                }
            }
        }
    }

    return openapi_spec

if __name__ == '__main__':
    # Example usage
    with open("openapi.json", "r") as f:
        spec = json.load(f)

    spec = add_security_schemes(spec)
    spec = add_security_requirements(spec)
    spec = add_security_responses(spec)

    with open("openapi_security.json", "w") as f:
        json.dump(spec, f, indent=2)

    print("Security-enhanced OpenAPI specification generated: openapi_security.json")
EOF
```

---

## 🌍 Environment Setup

### 1. Development Environment Security

#### Secure Environment Configuration
```bash
# Create secure environment setup script
cat > setup_secure_env.sh << 'EOF'
#!/bin/bash

# Secure environment setup for Phase 0 security implementation

echo "🔒 Setting up secure development environment..."

# Check required tools
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is required but not installed"
        exit 1
    else
        echo "✅ $1 found"
    fi
}

# Check required tools
check_tool git
check_tool docker
check_tool python3
check_tool node
check_tool psql
check_tool make

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install bandit safety flake8 black isort pydocstyle
cd ..

# Setup Node.js environment
echo "📦 Setting up Node.js environment..."
cd frontend
bun install
bun install --save-dev eslint eslint-plugin-security audit-ci
cd ..

# Setup security scanning tools
echo "🔍 Installing security tools..."
pip install safety
bun install -g audit-ci retire

# Setup pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
pip install pre-commit
pre-commit install

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOL'
repos:
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ['-c', 'backend/.bandit']
        files: ^backend/

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        files: ^backend/
        args: [--config=backend/.flake8]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.23.0
    hooks:
      - id: eslint
        files: ^frontend/
        types: [file]
        types_or: [javascript, jsx, ts, tsx]
        additional_dependencies:
          - eslint@8.23.0
          - eslint-plugin-security@1.5.0

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.3.0
    hooks:
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace
EOL

echo "✅ Secure development environment setup complete!"
echo "📖 Next: Run security tools before committing changes"
EOF

chmod +x setup_secure_env.sh
./setup_secure_env.sh
```

### 2. Database Security Setup

#### Secure Database Configuration
```bash
# Create secure database setup script
cat > setup_secure_db.sh << 'EOF'
#!/bin/bash

# Secure database setup for Phase 0

echo "🗄️ Setting up secure database..."

# Check Supabase CLI
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI is required"
    echo "Install with: bun install -g supabase"
    exit 1
fi

# Start local Supabase
echo "🚀 Starting local Supabase..."
supabase start

# Setup RLS on all tables
echo "🔒 Setting up Row Level Security..."
supabase db push --db-url 'postgresql://postgres:postgres@localhost:54322/postgres'

# Create security monitoring
cat > monitor_db_security.sql << 'EOL'
-- Monitor failed login attempts
CREATE OR REPLACE VIEW security_failed_logins AS
SELECT
    username,
    timestamp,
    error_message,
    ip_address
FROM auth.audit_logs
WHERE event = 'login_failed'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Monitor data access patterns
CREATE OR REPLACE VIEW security_data_access AS
SELECT
    user_id,
    table_name,
    operation,
    COUNT(*) as access_count,
    MAX(timestamp) as last_access
FROM auth.audit_logs
WHERE event IN ('row_read', 'row_inserted', 'row_updated', 'row_deleted')
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY user_id, table_name, operation
ORDER BY access_count DESC;

-- Monitor PII access
CREATE OR REPLACE VIEW security_pii_access AS
SELECT
    user_id,
    table_name,
    operation,
    timestamp
FROM auth.audit_logs
WHERE event IN ('row_read', 'row_updated')
  AND table_name IN ('user_profiles', 'resumes', 'contact_info')
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
EOL

# Apply monitoring
supabase db push --file monitor_db_security.sql

echo "✅ Secure database setup complete!"
echo "📊 Monitoring views created for security analysis"
EOF

chmod +x setup_secure_db.sh
```

---

## ⚙️ Tool Configuration

### 1. Security Testing Configuration

#### Bandit Configuration (Python)
```bash
# Create .bandit configuration file
cat > backend/.bandit << 'EOF'
[bandit]
exclude_dirs = tests,venv,__pycache__
tests = B101, B102, B103, B104, B105, B106, B107, B108, B110, B112, B201, B301, B302, B303, B304, B305, B306, B307, B308, B309, B310, B311, B312, B313, B314, B315, B316, B317, B318, B319, B320, B321, B322, B323, B324, B325, B401, B402, B403, B404, B405, B406, B407, B408, B409, B410, B411, B412, B413, B501, B502, B503, B504, B505, B506, B507, B601, B602, B603, B604, B605, B606, B607, B608, B609, B610, B611

[bandit.assert_used]
skips = ['*_test.py', '*/test_*.py']
EOF
```

#### ESLint Security Configuration (TypeScript)
```bash
# Create security-focused ESLint configuration
cat > frontend/.eslintrc.security.js << 'EOF'
module.exports = {
  extends: [
    'plugin:security/recommended',
    '@typescript-eslint/recommended'
  ],
  plugins: ['security', '@typescript-eslint'],
  rules: {
    // Security rules
    'security/detect-eval-with-expression': 'error',
    'security/detect-non-literal-regexp': 'error',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'error',
    'security/detect-disable-mustache-escape': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-non-literal-fs-filename': 'error',
    'security/detect-non-literal-require': 'error',
    'security/detect-object-injection': 'error',
    'security/detect-possible-timing-attacks': 'error',
    'security/detect-pseudoRandomBytes': 'error',

    // TypeScript rules
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn'
  },
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    project: './tsconfig.json'
  }
};
EOF
```

### 2. CI/CD Security Configuration

#### GitHub Actions Security Workflow
```bash
# Create security testing workflow
mkdir -p .github/workflows
cat > .github/workflows/security.yml << 'EOF'
name: Security Tests

on:
  push:
    branches: [ main, feature/* ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install Python dependencies
      run: |
        cd backend
        pip install bandit safety flake8
        pip install -r requirements.txt

    - name: Install Node.js dependencies
      run: |
        cd frontend
        bun ci

    - name: Run Bandit security scan
      run: |
        cd backend
        bandit -r . -f json -o bandit-report.json
        bandit -r . --severity-level high

    - name: Run Safety dependency check
      run: |
        cd backend
        safety check --json --output safety-report.json

    - name: Run bun audit
      run: |
        cd frontend
        bun audit --audit-level high

    - name: Run ESLint security check
      run: |
        cd frontend
        npx eslint . --ext .ts,.tsx --config .eslintrc.security.js

    - name: Upload security reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          backend/bandit-report.json
          backend/safety-report.json
          frontend/npm-audit-report.json
EOF
```

---

## ✅ Verification Procedures

### 1. Pre-Implementation Verification

#### Tool Setup Verification
```bash
# Create tool verification script
cat > verify_tools.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying security tools setup..."

# Check required tools
tools=("git" "python3" "node" "npm" "docker" "psql" "supabase" "bandit" "safety" "eslint")

for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "✅ $tool found"
    else
        echo "❌ $tool missing - please install"
        exit 1
    fi
done

# Test security tools
echo "🧪 Testing security tools..."

# Test bandit
cd backend
if bandit --version &> /dev/null; then
    echo "✅ Bandit working"
else
    echo "❌ Bandit not working"
    exit 1
fi

# Test safety
if safety check &> /dev/null; then
    echo "✅ Safety working"
else
    echo "❌ Safety not working"
    exit 1
fi

# Test eslint
cd ../frontend
if npx eslint --version &> /dev/null; then
    echo "✅ ESLint working"
else
    echo "❌ ESLint not working"
    exit 1
fi

# Test Supabase
if supabase --help &> /dev/null; then
    echo "✅ Supabase CLI working"
else
    echo "❌ Supabase CLI not working"
    exit 1
fi

cd ..

echo "✅ All security tools verified and working!"
EOF

chmod +x verify_tools.sh
./verify_tools.sh
```

### 2. Implementation Verification

#### Security Implementation Checklist
```bash
# Create security implementation verification script
cat > verify_security_implementation.sh << 'EOF'
#!/bin/bash

echo "🔒 Verifying security implementation..."

# Run comprehensive security checks
echo "📊 Running security analysis..."

# Backend security checks
cd backend
echo "🐍 Backend security analysis..."

echo "  - Running Bandit security scan..."
bandit -r app/ --severity-level high --format json -o ../security-reports/bandit-report.json
if [ $? -eq 0 ]; then
    echo "  ✅ Bandit scan passed"
else
    echo "  ❌ Bandit scan found issues"
fi

echo "  - Running Safety dependency check..."
safety check --json --output ../security-reports/safety-report.json
if [ $? -eq 0 ]; then
    echo "  ✅ Safety check passed"
else
    echo "  ❌ Safety check found issues"
fi

echo "  - Running code quality checks..."
flake8 app/ --output-file=../security-reports/flake8-report.txt
if [ $? -eq 0 ]; then
    echo "  ✅ Code quality check passed"
else
    echo "  ❌ Code quality issues found"
fi

cd ..

# Frontend security checks
cd frontend
echo "📦 Frontend security analysis..."

echo "  - Running bun audit..."
bun audit --audit-level high --json > ../security-reports/npm-audit-report.json
if [ $? -eq 0 ]; then
    echo "  ✅ bun audit passed"
else
    echo "  ❌ bun audit found vulnerabilities"
fi

echo "  - Running ESLint security check..."
npx eslint . --ext .ts,.tsx --config .eslintrc.security.js --format json -o ../security-reports/eslint-report.json
if [ $? -eq 0 ]; then
    echo "  ✅ ESLint security check passed"
else
    echo "  ❌ ESLint security issues found"
fi

cd ..

# Database security checks
echo "🗄️ Database security analysis..."

echo "  - Checking RLS policies..."
supabase db shell --command "SELECT schemaname, tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';" > security-reports/rls-status.txt

echo "  - Checking foreign key constraints..."
supabase db shell --command "SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY';" > security-reports/foreign-keys.txt

echo "✅ Security verification complete!"
echo "📁 Reports saved to security-reports/"
EOF

chmod +x verify_security_implementation.sh
mkdir -p security-reports
./verify_security_implementation.sh
```

---

## 🚨 Troubleshooting

### Common Tool Issues

#### Bandit Issues
```bash
# Problem: Bandit not finding files
# Solution: Check file paths and configuration
bandit -r backend/app/ -c backend/.bandit

# Problem: False positives
# Solution: Create skip list or disable specific tests
bandit -r backend/app/ --skip B101,B601
```

#### ESLint Security Issues
```bash
# Problem: Security plugin not found
# Solution: Install plugin locally
cd frontend
bun install eslint-plugin-security --save-dev

# Problem: TypeScript errors
# Solution: Update parser configuration
npx eslint . --parser-options '{"project": "./tsconfig.json"}'
```

#### Database Issues
```bash
# Problem: Supabase connection issues
# Solution: Check local Supabase status
supabase status
supabase stop && supabase start

# Problem: RLS policies not working
# Solution: Check RLS is enabled and policies exist
supabase db shell --command "ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;"
```

### Performance Issues

#### Slow Security Scans
```bash
# Optimize bandit scan
bandit -r backend/app/ --jobs 4  # Use multiple cores

# Optimize ESLint
npx eslint . --quiet --max-warnings 0

# Cache results
bandit -r backend/app/ --baseline baseline.json
```

---

## 📚 Additional Resources

### Security Tool Documentation
- [Bandit Python Security Scanner](https://bandit.readthedocs.io/)
- [Safety Dependency Scanner](https://pyup.io/safety/)
- [ESLint Security Plugin](https://github.com/nodesecurity/eslint-plugin-security)
- [OWASP ZAP Security Scanner](https://www.zaproxy.org/)
- [Supabase Security](https://supabase.com/docs/guides/security)

### LGPD Compliance Resources
- [LGPD Official Text (Portuguese)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [LGPD Compliance Guide](https://www.auth0.com/blog/lgpd-compliance-guide/)
- [Data Protection Best Practices](https://gdpr.eu/data-protection-best-practices/)

### Security Testing Resources
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Security Testing Handbook](https://github.com/OWASP/Security-Testing-Handbook)
- [API Security Testing](https://owasp.org/www-project-api-security/)

---

**Document Version**: 1.0
**Last Updated**: October 13, 2025
**Next Review**: After Phase 0 completion
**Maintainers**: CV-Match Security Team

---

**🚨 CRITICAL**: All agents must complete tool setup and verification before starting Phase 0 security implementation.