# Backend Dependency Maintenance Guide

## Overview
This guide provides procedures for maintaining pinned dependencies in the CV-Matcher backend, ensuring security, compatibility, and reproducibility.

## Quick Reference Commands

### Security & Updates
```bash
# Check for outdated packages
uv pip list --outdated

# Check for security vulnerabilities
pip-audit

# Update a specific package
uv add package_name==new_version

# Update lockfile after changes
uv lock --upgrade

# Test installation (dry run)
uv sync --dry-run
```

### Development Environment
```bash
# Install pinned dependencies
uv sync

# Install with dev dependencies
uv sync --dev

# Check dependency tree
uv pip tree

# Verify installation
uv pip check
```

## Regular Maintenance Schedule

### Daily (Automated)
- [ ] **Security scans** via CI/CD pipeline
- [ ] **Dependency health checks** in automated tests
- [ ] **Monitor for critical advisories** from package maintainers

### Weekly
- [ ] **Review security advisories** for pinned packages
- [ ] **Check for high-priority updates**
- [ ] **Run full test suite** to ensure stability

### Monthly
- [ ] **Comprehensive security audit** of all dependencies
- [ ] **Review outdated packages** for non-critical updates
- [ ] **Update documentation** with any version changes
- [ ] **Performance review** of dependency ecosystem

### Quarterly
- [ ] **Major version review** and planning
- [ ] **Dependency ecosystem cleanup** (remove unused packages)
- [ ] **Security posture assessment**
- [ ] **Update strategy review** for upcoming quarter

## Update Procedures

### Security Updates (Critical)
**Timeline**: Immediate (within 24 hours of advisory)

1. **Assess Impact**
   ```bash
   # Check current installed version
   uv pip show package_name

   # Review advisory details
   # Check affected versions
   ```

2. **Test Update**
   ```bash
   # Create test branch
   git checkout -b security/patch-package-name

   # Update version in pyproject.toml
   # Update requirements.txt if needed

   # Test compatibility
   uv sync --dry-run
   uv sync
   pytest tests/
   ```

3. **Deploy Fix**
   ```bash
   # Update lockfile
   uv lock --upgrade

   # Commit changes
   git add .
   git commit -m "fix: security update for package_name to version"
   git push origin security/patch-package-name

   # Create PR and merge
   # Deploy to production
   ```

### Routine Updates (Non-Critical)
**Timeline**: Monthly maintenance window

1. **Research Updates**
   ```bash
   # Review changelogs for breaking changes
   # Check compatibility with other dependencies
   # Review performance improvements
   ```

2. **Test in Development**
   ```bash
   # Update versions in pyproject.toml
   # Update lockfile
   uv lock --upgrade

   # Full testing
   uv sync --dev
   pytest tests/
   # Manual testing of core functionality
   ```

3. **Staged Rollout**
   ```bash
   # Deploy to staging environment first
   # Run integration tests
   # Monitor for issues
   # Deploy to production
   ```

## Security Monitoring

### Automated Tools Setup

#### 1. GitHub Dependabot
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "monthly"
    open-pull-requests-limit: 5
    reviewers:
      - "carlos"
    assignees:
      - "carlos"
    commit-message:
      prefix: "deps"
    allow:
      - dependency-type: "direct"
      - dependency-type: "indirect"
```

#### 2. GitHub Security Advisories
- Enable security alerts for the repository
- Configure automatic security patch PRs
- Set up security advisory notifications

#### 3. CI/CD Security Checks
Add to workflow:
```yaml
- name: Run security audit
  run: |
    pip install pip-audit
    pip-audit

- name: Check for vulnerable dependencies
  run: |
    pip install safety
    safety check
```

### Manual Security Review

#### Weekly Security Checklist
- [ ] **Review security advisories** from PyPI
- [ ] **Check CVE database** for Python packages
- [ ] **Monitor package maintainer announcements**
- [ ] **Review GitHub security alerts**

#### Monthly Security Assessment
- [ ] **Full vulnerability scan** of all dependencies
- [ ] **Review dependency tree** for transitive vulnerabilities
- [ ] **Assess security impact** of outdated packages
- [ ] **Document security posture** and improvements needed

## Troubleshooting

### Common Issues

#### 1. Dependency Conflicts
**Problem**: `uv sync` fails with version conflicts
```bash
# Diagnose
uv pip tree
uv pip check

# Resolve
# Check which packages require conflicting versions
# Find compatible versions or update dependencies
# Use `uv add --resolution=lowest-direct` if needed
```

#### 2. Build Failures
**Problem**: Tests fail after dependency update
```bash
# Isolate the issue
git bisect start
git bisect bad HEAD
git bisect good <previous-working-commit>

# Test specific versions
uv add package_name==specific_version
pytest tests/
```

#### 3. Performance Regressions
**Problem**: Application slower after dependency update
```bash
# Profile dependencies
python -m cProfile -o profile.stats app/main.py
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

### Emergency Procedures

#### Critical Security Incident
1. **Immediate Assessment** (0-2 hours)
   - Identify vulnerable packages
   - Assess exploit potential
   - Determine impact scope

2. **Rapid Patch** (2-6 hours)
   - Update to secure version
   - Minimal testing (smoke tests only)
   - Emergency deployment

3. **Comprehensive Testing** (6-24 hours)
   - Full test suite execution
   - Integration testing
   - Performance validation

4. **Post-Incident Review** (within 1 week)
   - Root cause analysis
   - Process improvement
   - Documentation updates

## Documentation Standards

### Version Change Documentation
When updating dependencies, document:

```markdown
## Package Name Update - YYYY-MM-DD

### Changes
- **From**: version X.Y.Z
- **To**: version A.B.C
- **Type**: Security/Critical/Feature/Enhancement

### Reason
- Security vulnerability CVE-XXXX-XXXX
- Breaking changes requiring update
- New features required
- Performance improvements

### Impact
- **Breaking Changes**: Yes/No - Details
- **Performance**: Improved/No Change/Regressed
- **Compatibility**: Compatible with Python X.Y, Other Dependencies

### Testing
- [ ] Unit tests passed
- [ ] Integration tests passed
- [ ] Manual testing completed
- [ ] Performance benchmarks run

### Deployment
- **Staging**: YYYY-MM-DD HH:MM
- **Production**: YYYY-MM-DD HH:MM
- **Rollback Plan**: Revert to previous versions
```

### Security Incident Documentation
For security incidents, maintain:

```markdown
## Security Incident Report - YYYY-MM-DD

### Incident Summary
- **Package**: package_name
- **Vulnerability**: CVE-XXXX-XXXX
- **Severity**: Critical/High/Medium/Low
- **Affected Versions**: X.Y.Z - A.B.C

### Timeline
- **Discovery**: YYYY-MM-DD HH:MM
- **Assessment**: YYYY-MM-DD HH:MM
- **Patch Developed**: YYYY-MM-DD HH:MM
- **Deployment**: YYYY-MM-DD HH:MM
- **Resolution**: YYYY-MM-DD HH:MM

### Impact Assessment
- **Exploitable**: Yes/No
- **In Production**: Yes/No
- **Data Exposure**: None/Limited/Significant
- **Service Impact**: None/Degraded/Unavailable

### Resolution
- **Fix Applied**: Updated to version A.B.C
- **Testing Completed**: Yes/No
- **Monitoring**: Enhanced/Normal
- **Follow-up Required**: Yes/No
```

## Best Practices

### 1. Version Pinning Strategy
- **Pin exact versions** for production dependencies
- **Use compatible version ranges** only when necessary
- **Update pinned versions** regularly for security
- **Document reasons** for version choices

### 2. Security First
- **Prioritize security updates** over feature updates
- **Monitor advisories** for all dependencies
- **Test thoroughly** but act quickly for critical issues
- **Document security incidents** for future reference

### 3. Compatibility Management
- **Test in isolated environment** before deployment
- **Maintain compatibility** with existing codebase
- **Plan for breaking changes** in major version updates
- **Rollback plans** for all updates

### 4. Documentation & Communication
- **Document all changes** with clear reasoning
- **Communicate updates** to development team
- **Maintain change logs** for tracking purposes
- **Review procedures** regularly for improvements

## Tools & Resources

### Essential Tools
- **uv**: Fast Python package installer and resolver
- **pip-audit**: Check for known vulnerabilities
- **safety**: Security vulnerability scanner
- **pipdeptree**: Dependency tree visualization
- **pip-tools**: Dependency management and pinning

### Monitoring Resources
- **PyPI Security Advisories**: https://pypi.org/security/
- **CVE Database**: https://cve.mitre.org/
- **GitHub Security Advisories**: Repository security alerts
- **Snyk Vulnerability Database**: https://snyk.io/vuln/

### Community Resources
- **Python Packaging Authority**: https://www.pypa.io/
- **Python Security**: https://python-security.readthedocs.io/
- **OpenSSF Security Best Practices**: https://bestpractices.coreinfrastructure.org/

---

**Version**: 1.0
**Last Updated**: 2025-10-07
**Next Review**: 2025-11-07
**Maintainer**: Development Team