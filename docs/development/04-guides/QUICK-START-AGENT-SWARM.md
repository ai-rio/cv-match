# 🚀 P0 Agent Swarm - Quick Start Card

**Copy this to your desktop for quick reference!**

---

## ⚡ TL;DR

Run 4 specialized AI agents to complete P0 in **8.5 hours** instead of 16 hours.

**Time Savings**: 47% ⚡
**Approach**: Parallel + Sequential execution
**Quality**: Expert-level in each domain

---

## 📍 Where Everything Is

```
docs/development/p0-prompts/
├── README.md                           ← START HERE
├── 01-backend-services-migration.md    ← Phase 1a
├── 02-ai-integration-specialist.md     ← Phase 1b (parallel)
├── 03-database-migrations.md           ← Phase 2
└── 04-api-endpoints.md                 ← Phase 3
```

---

## 🎯 Execution Order

### Phase 1: Backend Services (1.5h) - PARALLEL ⚡

**Run both simultaneously**:

```bash
# Terminal 1 - Backend Specialist
cd /home/carlos/projects/cv-match
# Open: docs/development/p0-prompts/01-backend-services-migration.md
# Copy entire prompt to Claude with backend-specialist agent

# Terminal 2 - AI Integration Specialist
cd /home/carlos/projects/cv-match
# Open: docs/development/p0-prompts/02-ai-integration-specialist.md
# Copy entire prompt to Claude with ai-integration-specialist agent
```

**Verify Phase 1**:

```bash
docker compose exec backend python -c "
from app.services.resume_service import ResumeService
from app.services.job_service import JobService
from app.services.score_improvement_service import ScoreImprovementService
from app.agent.manager import AgentManager
print('✅ Phase 1 Complete!')
"
```

---

### Phase 2: Database (2h) - SEQUENTIAL

**Run after Phase 1 completes**:

```bash
cd /home/carlos/projects/cv-match
# Open: docs/development/p0-prompts/03-database-migrations.md
# Copy entire prompt to Claude with database-architect agent
```

**Verify Phase 2**:

```bash
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()
for table in ['resumes', 'job_descriptions', 'optimizations', 'usage_tracking']:
    client.table(table).select('count').execute()
    print(f'✅ {table}')
print('✅ Phase 2 Complete!')
"
```

---

### Phase 3: API Endpoints (3h) - SEQUENTIAL

**Run after Phase 2 completes**:

```bash
cd /home/carlos/projects/cv-match
# Open: docs/development/p0-prompts/04-api-endpoints.md
# Copy entire prompt to Claude with backend-specialist agent
```

**Verify Phase 3**:

```bash
curl http://localhost:8000/docs | grep "resumes"
curl http://localhost:8000/docs | grep "optimizations"
echo "✅ Phase 3 Complete!"
```

---

## ✅ Quick Verification

After all phases:

```bash
cd /home/carlos/projects/cv-match

# Run verification script
./scripts/verify-p0.sh

# Or manual check
docker compose exec backend python -c "
# Services
from app.services.resume_service import ResumeService
from app.services.score_improvement_service import ScoreImprovementService
from app.agent.manager import AgentManager

# Database
from app.core.database import get_supabase_client
client = get_supabase_client()
client.table('resumes').select('count').execute()

# API
from app.api.router import api_router

print('✅ ALL SYSTEMS GO!')
"
```

---

## 🎯 Success Checklist

- [ ] Phase 1a: backend-specialist complete (3 services)
- [ ] Phase 1b: ai-integration-specialist complete (agent + score service)
- [ ] Phase 2: database-architect complete (4 tables)
- [ ] Phase 3: backend-specialist complete (5 endpoints)
- [ ] All verifications pass
- [ ] E2E test works
- [ ] Ready to merge!

---

## 🚨 If Something Fails

1. Check the prompt's troubleshooting section
2. Run the verification commands
3. Review Docker logs: `docker compose logs backend --tail=100`
4. Fix issues manually if needed
5. Re-run that specific agent only
6. DON'T proceed to next phase until current phase passes

---

## 💾 Git Commits

After **EACH** phase:

```bash
git add .
git commit -m "Phase X complete: [description]"
```

---

## 📊 Timeline

| Phase                | Time | Total |
| -------------------- | ---- | ----- |
| Phase 1 (parallel)   | 1.5h | 1.5h  |
| Phase 2 (sequential) | 2h   | 3.5h  |
| Phase 3 (sequential) | 3h   | 6.5h  |
| Verification         | 0.5h | 7h    |
| Buffer               | 1.5h | 8.5h  |

**Total**: 8.5 hours 🎉

---

## 🏆 When Complete

1. ✅ All services copied and working
2. ✅ Database tables created
3. ✅ API endpoints functional
4. ✅ E2E workflow tested
5. ✅ P0 COMPLETE!

Then:

```bash
git add .
git commit -m "feat: Complete P0 using agent swarm deployment"
git push origin feature/p0-frontend-migration
# Merge to main
# Start P1!
```

---

## 📞 Quick Links

- **Full Guide**: `docs/development/p0-prompts/README.md`
- **Strategy**: `docs/development/p0-agent-swarm-strategy.md`
- **Executive Summary**: `docs/development/AGENT-SWARM-EXECUTIVE-SUMMARY.md`

---

## 🎉 Result

**Before**: 16 hours manual work
**After**: 8.5 hours with agent swarm
**Savings**: 47% ⚡

**You're ready to deploy the swarm!** 🚀

---

**Print this card and keep it handy while executing!** 📋
