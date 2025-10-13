# Agent Prompt: Backend Services Migration

**Agent**: backend-specialist
**Phase**: 1 - Backend Services
**Priority**: P0
**Estimated Time**: 3 hours
**Dependencies**: None (can start immediately)

---

## 🎯 Mission

Copy and adapt 4 core service files from Resume-Matcher to cv-match, ensuring they integrate with the existing cv-match infrastructure while maintaining all functionality.

---

## 📋 Tasks

### Task 1: Copy resume_service.py (45 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/resume_service.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/resume_service.py`

**Actions**:

1. Copy the file to target location
2. Update imports to match cv-match structure:
   - Change `from app.` to match cv-match import paths
   - Verify all dependencies exist in cv-match
   - Add missing imports if needed
3. Adapt database calls to use cv-match's Supabase client pattern:
   - Replace any direct DB calls with `get_supabase_client()`
   - Ensure async/await patterns are consistent
4. Test the service can be imported:
   ```bash
   cd /home/carlos/projects/cv-match/backend
   docker compose exec backend python -c "from app.services.resume_service import ResumeService; print('✅ Imported')"
   ```

**Success Criteria**:

- [x] File copied to correct location
- [x] All imports resolve
- [x] No syntax errors
- [x] Can instantiate ResumeService class
- [x] Database client works

---

### Task 2: Copy job_service.py (45 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/job_service.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/job_service.py`

**Actions**:

1. Copy the file to target location
2. Update imports to match cv-match structure
3. Adapt any Resume-Matcher-specific patterns to cv-match
4. Ensure async patterns are consistent
5. Test import:
   ```bash
   docker compose exec backend python -c "from app.services.job_service import JobService; print('✅ Imported')"
   ```

**Success Criteria**:

- [x] File copied
- [x] Imports work
- [x] JobService instantiable
- [x] Methods callable

---

### Task 3: Copy text_extraction.py (30 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/app/services/text_extraction.py`
**Target**: `/home/carlos/projects/cv-match/backend/app/services/text_extraction.py`

**Actions**:

1. Copy the file
2. Update imports
3. Ensure PDF/DOCX parsing libraries are in cv-match's dependencies
4. Test extraction:
   ```bash
   docker compose exec backend python -c "from app.services.text_extraction import extract_text; print('✅ Imported')"
   ```

**Success Criteria**:

- [x] File copied
- [x] Dependencies available
- [x] Can import extract_text function
- [x] Function signature matches usage patterns

---

### Task 4: Verify All Services Together (30 min)

**Actions**:

1. Create a verification script that imports all services:

   ```python
   # File: backend/verify_services.py
   from app.services.resume_service import ResumeService
   from app.services.job_service import JobService
   from app.services.text_extraction import extract_text

   print("✅ All services imported successfully")

   # Test instantiation
   resume_svc = ResumeService()
   job_svc = JobService()
   print("✅ All services instantiable")
   ```

2. Run verification:

   ```bash
   docker compose exec backend python verify_services.py
   ```

3. Document any issues found and resolve them

**Success Criteria**:

- [x] All 3 services import without errors
- [x] All services can be instantiated
- [x] No missing dependencies
- [x] Ready for next phase

---

## 🔧 Technical Details

### Import Pattern Translation

**Resume-Matcher Pattern**:

```python
from app.services.database import get_db_client
from app.models.resume import Resume Model
```

**cv-match Pattern**:

```python
from app.core.database import get_supabase_client
from app.models.resume import ResumeModel  # If exists, or create
```

### Database Client Pattern

**Resume-Matcher**:

```python
db = get_db_client()
result = db.table('resumes').select('*').execute()
```

**cv-match (keep same)**:

```python
from app.core.database import get_supabase_client
client = get_supabase_client()
result = client.table('resumes').select('*').execute()
```

### Async Patterns

Ensure all service methods that do I/O are async:

```python
async def process_resume(self, file_content: bytes) -> dict:
    # Extract text
    text = await extract_text(file_content)
    # Store in DB
    result = await self._store_resume(text)
    return result
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Missing Dependencies

**Symptom**: `ModuleNotFoundError`
**Solution**: Check `requirements.txt`, add missing packages, run `uv sync`

### Issue 2: Import Path Errors

**Symptom**: `ImportError: cannot import name...`
**Solution**: Check directory structure, update imports to match cv-match paths

### Issue 3: Database Client Mismatch

**Symptom**: `AttributeError` on database operations
**Solution**: Verify Supabase client methods, adapt if Resume-Matcher uses different patterns

### Issue 4: Async/Await Issues

**Symptom**: `RuntimeWarning: coroutine was never awaited`
**Solution**: Add `await` to all async calls, ensure functions are marked `async def`

---

## 📊 Verification Checklist

Run these commands to verify each service:

```bash
# Navigate to backend
cd /home/carlos/projects/cv-match/backend

# Test resume_service
docker compose exec backend python -c "
from app.services.resume_service import ResumeService
svc = ResumeService()
print('✅ ResumeService working')
"

# Test job_service
docker compose exec backend python -c "
from app.services.job_service import JobService
svc = JobService()
print('✅ JobService working')
"

# Test text_extraction
docker compose exec backend python -c "
from app.services.text_extraction import extract_text
print('✅ text_extraction working')
"

# Test all together
docker compose exec backend python -c "
from app.services.resume_service import ResumeService
from app.services.job_service import JobService
from app.services.text_extraction import extract_text
print('✅ All services operational!')
"
```

---

## 📝 Deliverables

### Files to Create:

1. `/home/carlos/projects/cv-match/backend/app/services/resume_service.py`
2. `/home/carlos/projects/cv-match/backend/app/services/job_service.py`
3. `/home/carlos/projects/cv-match/backend/app/services/text_extraction.py`
4. `/home/carlos/projects/cv-match/backend/verify_services.py` (verification script)

### Documentation to Update:

- Add comments explaining any significant adaptations
- Note any Resume-Matcher patterns that were changed
- Document dependencies added

### Git Commit:

```bash
git add backend/app/services/resume_service.py
git add backend/app/services/job_service.py
git add backend/app/services/text_extraction.py
git commit -m "feat(backend): Copy core services from Resume-Matcher

- Add resume_service.py for resume processing
- Add job_service.py for job description analysis
- Add text_extraction.py for PDF/DOCX parsing
- Adapt imports to cv-match structure
- All services verified and working

Related: P0 Core Services implementation"
```

---

## ⏱️ Timeline

- **00:00-00:45**: Task 1 (resume_service.py)
- **00:45-01:30**: Task 2 (job_service.py)
- **01:30-02:00**: Task 3 (text_extraction.py)
- **02:00-02:30**: Task 4 (Verification)
- **02:30-03:00**: Buffer for issues/testing

**Total**: 3 hours

---

## 🎯 Success Definition

Mission complete when:

1. All 3 service files exist in cv-match
2. All imports resolve correctly
3. All services can be instantiated
4. Verification script passes
5. No errors in Docker logs
6. Ready for AI Integration Specialist to add score_improvement_service

---

## 🔄 Handoff to Next Agent

After completion, provide to AI Integration Specialist:

- Confirmation all 3 services are working
- Any patterns they should follow
- List of available services they can depend on

**Status**: Ready for deployment 🚀
