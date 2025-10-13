# Manual Quick Verification Commands

Run these commands to manually verify your P0 completion:

## 1. Infrastructure Check

```bash
# Check Docker services
docker compose ps

# Expected: All services "Up"
```

## 2. Backend Health

```bash
# Test backend health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy",...}
```

## 3. Backend Tests

```bash
# Run all backend unit tests
cd backend
docker compose exec backend python -m pytest tests/unit/ -v

# Expected: 65 tests passed
```

## 4. Backend Services Import

```bash
# Test all service imports
docker compose exec backend python -c "
from app.services.resume_service import ResumeService
from app.services.job_service import JobService
from app.services.score_improvement_service import ScoreImprovementService
from app.services.text_extraction import extract_text
from app.agent.manager import AgentManager
print('✅ All services imported successfully')
"
```

## 5. Database Connection

```bash
# Test Supabase connection
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()
print('✅ Database connected')
"
```

## 6. Frontend Build

```bash
cd frontend
bun run build

# Expected: Build completes successfully
```

## 7. i18n Check

```bash
# Count locale files
ls frontend/locales/pt-br/*.json | wc -l
# Expected: 10

ls frontend/locales/en/*.json | wc -l
# Expected: 10
```

## 8. Environment Variables

```bash
# Check backend env
grep "RESUME_MATCHER_LLM_PROVIDER" backend/.env
grep "SUPABASE_URL" backend/.env

# Check frontend env
grep "NEXT_PUBLIC_DEFAULT_LOCALE" frontend/.env.local
grep "NEXT_PUBLIC_API_URL" frontend/.env.local
```

## 9. Performance Test

```bash
# Test health endpoint response time
time curl http://localhost:8000/health

# Expected: < 1 second
```

## 10. Quick Summary

Run this one-liner to get a quick status:

```bash
echo "=== Quick P0 Status ===" && \
echo "Docker: $(docker compose ps | grep -c Up) services up" && \
echo "Backend: $(curl -s http://localhost:8000/health | grep -q healthy && echo 'OK' || echo 'FAIL')" && \
echo "PT-BR locales: $(ls frontend/locales/pt-br/*.json 2>/dev/null | wc -l) files" && \
echo "EN locales: $(ls frontend/locales/en/*.json 2>/dev/null | wc -l) files" && \
echo "======================="
```

---

## Expected Results Summary

If all checks pass, you should see:

- ✅ Docker services running
- ✅ Backend responding with healthy status
- ✅ 65 backend tests passing
- ✅ All services import successfully
- ✅ Database connected
- ✅ Frontend builds without errors
- ✅ 10 PT-BR locale files
- ✅ 10 EN locale files
- ✅ Environment variables configured

**If everything passes → You're ready for P1! 🚀**
