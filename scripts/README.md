# Verification Scripts

This directory contains automation scripts for verifying the cv-match application.

## Available Scripts

### `verify-p0.sh`

**Purpose**: Automated verification of P0 (Frontend Migration) completion before moving to P1 (Payment Integration).

**What it checks**:

- ✅ Infrastructure health (Docker services, database connectivity)
- ✅ Backend services and imports
- ✅ Backend unit tests (65/65 tests)
- ✅ Security middleware tests
- ✅ Frontend build
- ✅ Internationalization setup (next-intl, locale files)
- ✅ Environment variables configuration
- ✅ Sentry integration (optional)
- ✅ Performance benchmarks

**Usage**:

```bash
# Make script executable (first time only)
chmod +x scripts/verify-p0.sh

# Run from project root
./scripts/verify-p0.sh

# Or run with bash
bash scripts/verify-p0.sh
```

**Output**:

- Colored output showing passed ✅, failed ❌, and warnings ⚠️
- Summary report with success rate
- Exit code 0 if all critical checks pass, 1 if any fail

**When to use**:

- After completing P0 (Frontend Migration) tasks
- Before starting P1 (Payment Integration)
- After making significant changes to verify nothing broke
- As part of CI/CD pipeline

**Manual verification**:
For detailed manual verification steps, see: `docs/development/P0-VERIFICATION-CHECKLIST.md`

---

## Prerequisites

Before running verification scripts:

1. **Docker services running**:

   ```bash
   docker compose up -d
   ```

2. **Dependencies installed**:

   ```bash
   # Backend
   cd backend && pip install -r requirements.txt && cd ..

   # Frontend
   cd frontend && bun install && cd ..
   ```

3. **Environment variables configured**:
   - Backend: `backend/.env`
   - Frontend: `frontend/.env.local`

---

## Troubleshooting

### Script fails with "command not found"

Make script executable:

```bash
chmod +x scripts/verify-p0.sh
```

### Docker services not running

Start services:

```bash
docker compose up -d
```

Check status:

```bash
docker compose ps
```

### Backend tests fail

Run tests manually to see detailed errors:

```bash
cd backend
docker compose exec backend python -m pytest tests/unit/ -vv --tb=long
```

### Frontend build fails

Check build logs:

```bash
cd frontend
bun run build
```

Common issues:

- Missing dependencies: Run `bun install`
- TypeScript errors: Check `bun run type-check`
- Missing environment variables: Check `.env.local`

---

## Adding New Verification Scripts

When creating new verification scripts:

1. **Naming convention**: `verify-[phase].sh` (e.g., `verify-p1.sh`, `verify-p2.sh`)
2. **Use colors**: Define color variables at the top
3. **Count checks**: Track passed/failed/warnings
4. **Exit codes**: 0 for success, 1 for failure
5. **Add documentation**: Update this README

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: P0 Verification

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  verify-p0:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up services
        run: |
          docker compose up -d
          sleep 10  # Wait for services to be ready

      - name: Run P0 verification
        run: |
          chmod +x scripts/verify-p0.sh
          ./scripts/verify-p0.sh

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: verification-results
          path: /tmp/pytest_output.log
```

---

## Related Documentation

- [P0 Verification Checklist](../docs/development/P0-VERIFICATION-CHECKLIST.md) - Detailed manual verification
- [ROADMAP](../docs/development/ROADMAP.md) - Full project roadmap
- [Backend Tests README](../backend/tests/README.md) - Backend testing guide
- [Development README](../docs/development/README.md) - Main development guide

---

**Last Updated**: 2025-10-09
**Maintained by**: Development Team
