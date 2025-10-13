# Branch Cleanup Strategy for CV-Match

## Overview

This document outlines the systematic approach for branch cleanup and maintenance in the CV-Match project. Proper branch management ensures a clean repository, reduces confusion, and improves development velocity.

## 🎯 Objectives

1. **Maintain Clean Repository**: Remove obsolete branches to reduce clutter
2. **Prevent Merge Conflicts**: Regular cleanup reduces divergence risks
3. **Improve Performance**: Fewer branches improve Git operations
4. **Ensure Compliance**: Follow Git Flow best practices
5. **Brazilian Market Focus**: Maintain organized workflow for SaaS delivery

## 📅 Cleanup Schedule

### Daily Cleanup

- **Review merged PRs**: Check for branches ready for deletion
- **Remove stale feature branches**: Delete branches inactive > 7 days
- **Update protected branches**: Ensure main/develop are up to date

### Weekly Cleanup

- **Comprehensive branch review**: Analyze all active branches
- **Release branch maintenance**: Clean up completed releases
- **Hotfix branch review**: Remove resolved hotfix branches
- **Documentation update**: Update branch documentation

### Monthly Cleanup

- **Deep repository analysis**: Review long-term branch patterns
- **Archive strategy**: Move significant branches to archive if needed
- **Workflow optimization**: Refine cleanup processes
- **Team coordination**: Ensure alignment on cleanup policies

## 🔍 Branch Classification

### Active Branches

- **Main branches**: `main`, `develop` (never delete)
- **Current features**: Features under active development
- **Recent releases**: Release branches in preparation
- **Active hotfixes**: Emergency fixes in progress

### Stale Branches

- **Merged features**: Features successfully merged (delete after 7 days)
- **Abandoned features**: Features with no activity > 14 days
- **Completed releases**: Released versions (delete after tag creation)
- **Resolved hotfixes**: Hotfixes merged to main (delete after 7 days)

### Archive Candidates

- **Historical features**: Significant features worth preserving
- **Experimental branches**: Research/prototype work
- **Major refactoring**: Large-scale changes with future reference value

## 🛠 Cleanup Commands

### Identify Merged Branches

```bash
# List merged branches (excluding main and develop)
git branch --merged --no-contains main --no-contains develop

# List merged branches older than 7 days
git branch --merged --no-contains main --no-contains develop --sort=-committerdate |
  awk 'NR>1 {print $1}' |
  while read branch; do
    commit_date=$(git log -1 --format=%ct "$branch")
    age=$(( ($(date +%s) - commit_date) / 86400 ))
    if [ $age -gt 7 ]; then
      echo "$branch ($age days old)"
    fi
  done
```

### Identify Stale Branches

```bash
# List branches with no activity in last 14 days
git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads/ |
  awk '$2 < "'$(date -d '14 days ago' '+%Y-%m-%d')'" {print $1}' |
  grep -v -E '^(main|develop|release/|hotfix/)'
```

### Safe Branch Deletion

```bash
# Delete merged local branch
git branch -d branch-name

# Force delete unmerged branch (careful!)
git branch -D branch-name

# Delete remote branch
git push origin --delete branch-name

# Batch delete merged branches
git branch --merged --no-contains main --no-contains develop |
  grep -v -E '^(main|develop)$' |
  xargs git branch -d
```

### Cleanup Script

```bash
#!/bin/bash
# branch-cleanup.sh - Automated branch cleanup

set -e

BRANCHES_TO_CLEAN=(
  "merged-features-older-than-7-days"
  "stale-features-older-than-14-days"
  "completed-releases"
  "resolved-hotfixes"
)

echo "🧹 Starting branch cleanup for CV-Match..."

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Cleanup merged features
echo "📦 Cleaning up merged features..."
merged_features=$(git branch --merged --no-contains main --no-contains develop | grep '^feature/')
if [ ! -z "$merged_features" ]; then
  echo "$merged_features" | xargs git branch -d
  echo "$merged_features" | xargs -I {} git push origin --delete {}
fi

# Cleanup stale features
echo "🕐 Cleaning up stale features..."
stale_features=$(git for-each-ref --format='%(refname:short)' refs/heads/ |
  grep '^feature/' |
  while read branch; do
    last_activity=$(git log -1 --format=%ct "$branch")
    age=$(( ($(date +%s) - last_activity) / 86400 ))
    if [ $age -gt 14 ]; then
      echo "$branch"
    fi
  done)

if [ ! -z "$stale_features" ]; then
  echo "Found stale features: $stale_features"
  echo "⚠️  Please review these branches before deletion"
fi

# Cleanup completed releases
echo "🚀 Cleaning up completed releases..."
current_tag=$(git describe --tags --abbrev=0)
completed_releases=$(git branch | grep '^release/' | grep -v "$current_tag")
if [ ! -z "$completed_releases" ]; then
  echo "$completed_releases" | xargs git branch -d
  echo "$completed_releases" | xargs -I {} git push origin --delete {}
fi

# Cleanup resolved hotfixes
echo "🔧 Cleaning up resolved hotfixes..."
merged_hotfixes=$(git branch --merged main | grep '^hotfix/')
if [ ! -z "$merged_hotfixes" ]; then
  echo "$merged_hotfixes" | xargs git branch -d
  echo "$merged_hotfixes" | xargs -I {} git push origin --delete {}
fi

echo "✅ Branch cleanup completed!"
```

## 📋 Branch Deletion Checklist

### Before Deleting Any Branch

- [ ] **Verify Merge Status**: Confirm branch is merged to appropriate target
- [ ] **Check Active PRs**: Ensure no open PRs depend on this branch
- [ ] **Review Dependencies**: Check if other branches depend on this branch
- [ ] **Backup if Needed**: Consider archiving important work
- [ ] **Team Communication**: Notify team before deletion
- [ ] **Documentation**: Update any related documentation

### Feature Branch Deletion

- [ ] Merged to develop branch
- [ ] No open PRs
- [ ] Code reviewed and approved
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Brazilian market considerations addressed

### Release Branch Deletion

- [ ] Tag created for release version
- [ ] Merged to main branch
- [ ] Merged back to develop branch
- [ ] Release notes published
- [ ] Deployment verified
- [ ] Documentation updated

### Hotfix Branch Deletion

- [ ] Merged to main branch
- [ ] Tag created for hotfix version
- [ ] Merged back to develop branch
- [ ] Hotfix deployed to production
- [ ] Incident documented
- [ ] Post-mortem completed

## 🔄 Automated Cleanup Workflow

### GitHub Actions Integration

```yaml
# .github/workflows/branch-cleanup.yml
name: Branch Cleanup

on:
  schedule:
    - cron: "0 2 * * 1" # Every Monday at 2 AM UTC
  workflow_dispatch:

jobs:
  cleanup-branches:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Cleanup merged branches
        run: |
          # Add cleanup script here
          ./scripts/branch-cleanup.sh

      - name: Report cleanup results
        uses: actions/github-script@v6
        with:
          script: |
            // Create issue with cleanup report
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Weekly Branch Cleanup Report',
              body: 'Automated branch cleanup completed successfully.',
              labels: ['maintenance', 'branch-cleanup']
            })
```

### Pre-commit Hook for Branch Name Validation

```bash
# .husky/pre-commit
#!/bin/sh
# Validate branch name format

branch_name=$(git branch --show-current)

# Check if branch name follows Git Flow conventions
if [[ ! "$branch_name" =~ ^(main|develop|feature/|release/|hotfix/) ]]; then
  echo "❌ Invalid branch name: $branch_name"
  echo "✅ Use Git Flow naming: feature/, release/, hotfix/"
  exit 1
fi

echo "✅ Branch name validation passed: $branch_name"
```

## 📊 Branch Analytics

### Monitoring Metrics

```bash
# Branch activity report
echo "📊 Branch Activity Report"
echo "========================"

# Total branches
total_branches=$(git branch | wc -l)
echo "Total branches: $total_branches"

# Active features
active_features=$(git branch | grep '^feature/' | wc -l)
echo "Active features: $active_features"

# Merged branches
merged_count=$(git branch --merged | wc -l)
echo "Merged branches: $merged_count"

# Stale branches
stale_count=$(git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads/ |
  awk '$2 < "'$(date -d '14 days ago' '+%Y-%m-%d')'" {print $1}' | wc -l)
echo "Stale branches: $stale_count"

# Brazilian market specific branches
br_branches=$(git branch | grep -i -E '(brazil|brazilian|pt-br|brl)' | wc -l)
echo "Brazilian market branches: $br_branches"
```

### Health Score Calculation

```bash
# Repository health score
total_score=100
feature_weight=10
release_weight=5
hotfix_weight=15
stale_penalty=20
merged_bonus=5

# Calculate penalties and bonuses
if [ $active_features -gt 10 ]; then
  total_score=$((total_score - feature_weight))
fi

if [ $stale_count -gt 5 ]; then
  total_score=$((total_score - stale_penalty))
fi

if [ $merged_count -gt 10 ]; then
  total_score=$((total_score + merged_bonus))
fi

echo "🎯 Repository Health Score: $total_score/100"
```

## 🚨 Emergency Procedures

### Accidental Branch Deletion Recovery

```bash
# Find deleted commit
git reflog --no-merges | grep "branch-name"

# Recover branch
git checkout -b recovered-branch <commit-hash>
```

### Mass Deletion Recovery

```bash
# List all recently deleted branches
git log --walk-reflogs --oneline | grep "branch:" | head -20

# Recover specific branch
git branch branch-name <commit-hash>
```

### Backup Before Cleanup

```bash
# Create backup of all branches
git branch -a > backup-branches-$(date +%Y%m%d).txt

# Archive important branches
git tag archive/feature-branch-name feature/feature-name
git push origin --tags
```

## 🇧🇷 Brazilian Market Considerations

### Special Branch Types

- **Localization branches**: `feature/i18n-pt-br-updates`
- **Payment branches**: `feature/brl-payment-integration`
- **Compliance branches**: `feature/lgpd-compliance`
- **Market branches**: `feature/brazilian-market-launch`

### Extended Retention

- **Market launch branches**: Keep for 30 days post-launch
- **Compliance branches**: Archive for legal reference
- **Payment integration**: Extended retention for audit purposes

### Cleanup Exceptions

```bash
# Never delete these Brazilian market branches
protected_patterns=(
  "feature/brazilian-market"
  "feature/pt-br"
  "feature/brl"
  "feature/lgpd"
  "release/brazil"
)

for pattern in "${protected_patterns[@]}"; do
  if [[ "$branch_name" =~ $pattern ]]; then
    echo "🇧🇷 Protected Brazilian market branch: $branch_name"
    continue
  fi
done
```

## 📚 Documentation Requirements

### Before Branch Deletion

1. **Update Documentation**: Ensure all changes are documented
2. **Wiki Updates**: Update project wiki pages
3. **API Documentation**: Update API docs for backend changes
4. **User Documentation**: Update user-facing docs

### After Branch Deletion

1. **Cleanup References**: Remove branch references from docs
2. **Update Roadmap**: Reflect completed features
3. **Archive Notes**: Store important learnings
4. **Team Notification**: Inform team of cleanup

## 🎯 Best Practices

### DO ✅

1. **Regular Cleanup**: Schedule consistent cleanup operations
2. **Team Communication**: Notify before deletion
3. **Backup Strategy**: Maintain backups of important work
4. **Documentation**: Keep comprehensive records
5. **Automation**: Use scripts and workflows
6. **Monitoring**: Track repository health metrics
7. **Brazilian Context**: Consider market-specific needs
8. **Safety First**: Verify before deletion
9. **Gradual Process**: Start with safe deletions
10. **Review Process**: Team review for important branches

### DON'T ❌

1. **Force Delete**: Avoid force deletion without verification
2. **Skip Communication**: Don't delete without team notice
3. **Ignore Dependencies**: Check for dependent branches
4. **Bulk Operations**: Avoid mass deletions without review
5. **Forget Backup**: Don't delete without backup option
6. **Ignore Stale Branches**: Address long-standing stale branches
7. **Skip Documentation**: Maintain proper records
8. **Rush Process**: Take time for proper review
9. **Ignore Patterns**: Learn from branch lifecycle patterns
10. **Forget Brazilian Market**: Consider market-specific implications

## 🔧 Tools and Integration

### Git Aliases for Cleanup

```bash
# Add to .gitconfig
[alias]
  cleanup-merged = "!git branch --merged --no-contains main --no-contains develop | grep -v -E '^(main|develop)$' | xargs git branch -d"
  cleanup-stale = "!git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads/ | awk '$2 < \"'$(date -d '14 days ago' '+%Y-%m-%d')'\" {print $1}' | grep -v -E '^(main|develop|release/|hotfix/)'"
  branch-report = "!echo 'Branch Report:' && git branch && echo 'Merged:' && git branch --merged && echo 'Stale:' && git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads/ | awk '$2 < \"'$(date -d '14 days ago' '+%Y-%m-%d')'\" {print $1}'"
```

### Integration with Project Management

- **Jira Integration**: Link branches to tickets
- **GitHub Projects**: Track branch lifecycle
- **Slack Notifications**: Automated cleanup notifications
- **Dashboard Integration**: Repository health metrics

## 📞 Support and Escalation

### When to Seek Help

1. **Uncertain Deletion**: Unsure about branch deletion
2. **Dependencies Found**: Complex branch dependencies
3. **Brazilian Market**: Market-specific branch concerns
4. **Recovery Needed**: Accidental deletion occurred
5. **Process Issues**: Cleanup workflow problems

### Escalation Path

1. **Team Lead**: First point of contact
2. **DevOps Engineer**: Technical assistance
3. **Product Manager**: Feature branch decisions
4. **Brazilian Market Team**: Market-specific concerns
5. **Repository Admin**: Final escalation point

## 📈 Continuous Improvement

### Metrics to Track

- **Branch Lifecycle**: Average branch age
- **Cleanup Efficiency**: Time from merge to deletion
- **Repository Growth**: Branch count trends
- **Team Velocity**: Impact on development speed
- **Brazilian Market**: Market-specific branch metrics

### Process Optimization

1. **Regular Reviews**: Monthly process assessment
2. **Tool Improvements**: Enhance automation tools
3. **Team Feedback**: Collect and implement suggestions
4. **Market Adaptation**: Adjust for Brazilian market needs
5. **Performance Monitoring**: Track cleanup efficiency

---

This branch cleanup strategy ensures a healthy, maintainable repository while supporting the specific needs of the CV-Match Brazilian SaaS platform. Regular cleanup and proper branch management contribute to improved development velocity and reduced technical debt.
