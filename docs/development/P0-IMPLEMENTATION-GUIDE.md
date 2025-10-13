# P0 Core Services - Quick Implementation Guide

**Goal**: Complete P0 by copying Resume-Matcher services to cv-match
**Time**: 1-2 days
**Status**: Ready to start

---

## 📋 Overview

You have excellent infrastructure (Week 0-2 complete). Now you need to copy the actual resume processing services from Resume-Matcher to make the product work.

---

## 🎯 Step-by-Step Implementation

### Step 1: Backend Services (4-6 hours)

#### 1.1 Copy Resume Service

```bash
# Copy the service file
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/resume_service.py \
   /home/carlos/projects/cv-match/backend/app/services/

# Copy text extraction
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/text_extraction.py \
   /home/carlos/projects/cv-match/backend/app/services/

# Test the import
cd /home/carlos/projects/cv-match/backend
docker compose exec backend python -c "
from app.services.resume_service import ResumeService
print('✅ ResumeService imported')
"
```

**Checklist**:

- [ ] `resume_service.py` copied
- [ ] `text_extraction.py` copied
- [ ] Imports working
- [ ] No dependency errors

---

#### 1.2 Copy Job Service

```bash
# Copy the service file
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/job_service.py \
   /home/carlos/projects/cv-match/backend/app/services/

# Test the import
docker compose exec backend python -c "
from app.services.job_service import JobService
print('✅ JobService imported')
"
```

**Checklist**:

- [ ] `job_service.py` copied
- [ ] Imports working
- [ ] No dependency errors

---

#### 1.3 Copy Score Improvement Service

```bash
# Copy the service file
cp /home/carlos/projects/Resume-Matcher/apps/backend/app/services/score_improvement_service.py \
   /home/carlos/projects/cv-match/backend/app/services/

# Test the import
docker compose exec backend python -c "
from app.services.score_improvement_service import ScoreImprovementService
print('✅ ScoreImprovementService imported')
"
```

**Checklist**:

- [ ] `score_improvement_service.py` copied
- [ ] Imports working
- [ ] No dependency errors

---

#### 1.4 Copy Agent System

```bash
# Copy the entire agent directory
cp -r /home/carlos/projects/Resume-Matcher/apps/backend/app/agent \
      /home/carlos/projects/cv-match/backend/app/

# Test the import
docker compose exec backend python -c "
from app.agent.manager import AgentManager
manager = AgentManager()
print(f'✅ AgentManager initialized with {len(manager.providers)} providers')
"
```

**Checklist**:

- [ ] `app/agent/` directory copied
- [ ] AgentManager imports
- [ ] LLM providers configured
- [ ] Test completion works

---

### Step 2: Database Migrations (1-2 hours)

#### 2.1 Identify Needed Migrations

```bash
# List Resume-Matcher migrations
ls /home/carlos/projects/Resume-Matcher/apps/backend/supabase/migrations/

# Look for migrations that create:
# - resumes table
# - job_descriptions table
# - optimizations table
# - usage_tracking table (beyond payments)
```

#### 2.2 Copy Migrations

```bash
# Copy relevant migrations
cp /home/carlos/projects/Resume-Matcher/apps/backend/supabase/migrations/YYYYMMDDHHMMSS_create_resumes_table.sql \
   /home/carlos/projects/cv-match/supabase/migrations/

# Repeat for other tables
```

#### 2.3 Apply Migrations

```bash
cd /home/carlos/projects/cv-match

# Apply migrations
supabase db push

# Verify tables exist
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()

tables = ['resumes', 'job_descriptions', 'optimizations', 'usage_tracking']
for table in tables:
    try:
        result = client.table(table).select('count').execute()
        print(f'✅ Table {table} exists')
    except Exception as e:
        print(f'❌ Table {table} missing: {e}')
"
```

**Checklist**:

- [ ] Migrations identified
- [ ] Migrations copied
- [ ] Migrations applied
- [ ] All tables exist
- [ ] RLS policies active

---

### Step 3: API Endpoints (2-3 hours)

#### 3.1 Create Resume Upload Endpoint

**File**: `backend/app/api/endpoints/resumes.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.resume_service import ResumeService
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload and parse resume"""

    # Validate file type
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(400, "Invalid file type")

    # Validate file size (2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(400, "File too large")

    # Process resume
    resume_service = ResumeService()
    result = await resume_service.process_resume(
        file_content=contents,
        filename=file.filename,
        user_id=current_user.id
    )

    return {
        "resume_id": result["id"],
        "filename": file.filename,
        "status": "success"
    }
```

**Checklist**:

- [ ] Endpoint created
- [ ] File validation works
- [ ] Resume parsing works
- [ ] Database storage works

---

#### 3.2 Create Analysis Endpoint

**File**: `backend/app/api/endpoints/optimizations.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.job_service import JobService
from app.services.score_improvement_service import ScoreImprovementService
from app.core.auth import get_current_user

router = APIRouter()

class AnalysisRequest(BaseModel):
    resume_id: str
    job_description: str
    job_title: str
    company: str

@router.post("/start")
async def start_optimization(
    request: AnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Start resume optimization"""

    # Process job description
    job_service = JobService()
    job_analysis = await job_service.analyze_job(
        description=request.job_description,
        title=request.job_title,
        company=request.company
    )

    # Calculate match score
    score_service = ScoreImprovementService()
    optimization = await score_service.optimize(
        resume_id=request.resume_id,
        job_analysis=job_analysis,
        user_id=current_user.id
    )

    return {
        "optimization_id": optimization["id"],
        "status": "processing",
        "estimated_time": "2-3 minutes"
    }
```

**Checklist**:

- [ ] Endpoint created
- [ ] Job analysis works
- [ ] Match score calculated
- [ ] Results stored

---

#### 3.3 Create Results Endpoint

**File**: `backend/app/api/endpoints/optimizations.py` (add to existing)

```python
@router.get("/{optimization_id}")
async def get_optimization(
    optimization_id: str,
    current_user = Depends(get_current_user)
):
    """Get optimization results"""

    # Fetch from database
    from app.core.database import get_supabase_client
    client = get_supabase_client()

    result = client.table("optimizations")\
        .select("*")\
        .eq("id", optimization_id)\
        .eq("user_id", current_user.id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(404, "Optimization not found")

    return result.data
```

**Checklist**:

- [ ] Endpoint created
- [ ] Results retrieval works
- [ ] Authorization works

---

#### 3.4 Register Endpoints

**File**: `backend/app/api/router.py`

```python
from app.api.endpoints import resumes, optimizations

# Add to router
api_router.include_router(
    resumes.router,
    prefix="/resume",
    tags=["resumes"]
)

api_router.include_router(
    optimizations.router,
    prefix="/optimizations",
    tags=["optimizations"]
)
```

**Checklist**:

- [ ] Routes registered
- [ ] API docs show endpoints
- [ ] Endpoints accessible

---

### Step 4: Frontend Integration (2 hours)

#### 4.1 Update Optimize Page

**File**: `frontend/app/optimize/page.tsx`

Replace mock API calls with real ones:

```typescript
// Change this:
// const response = await fetch('/api/optimizations/start', {

// To this:
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/optimizations/start`,
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify({
      resume_id: resumeData.id,
      job_description: jobDescription.description,
      job_title: jobDescription.jobTitle,
      company: jobDescription.company,
    }),
  },
);
```

**Checklist**:

- [ ] Real API calls replace mocks
- [ ] Authentication headers added
- [ ] Error handling works
- [ ] Loading states work

---

### Step 5: End-to-End Testing (2-3 hours)

#### 5.1 Test Upload Flow

```bash
# Manual test
# 1. Open http://localhost:3001/pt-br/optimize
# 2. Upload a test resume PDF
# 3. Verify it processes
# 4. Check database for resume record
```

**Checklist**:

- [ ] Can upload PDF
- [ ] Can upload DOCX
- [ ] File validation works
- [ ] Resume appears in database

---

#### 5.2 Test Analysis Flow

```bash
# Manual test
# 1. Continue from uploaded resume
# 2. Enter job description
# 3. Submit for analysis
# 4. Verify processing starts
# 5. Check database for optimization record
```

**Checklist**:

- [ ] Job description validates
- [ ] Analysis starts
- [ ] Match score calculated
- [ ] Results stored

---

#### 5.3 Test Results Display

```bash
# Manual test
# 1. Wait for analysis complete
# 2. View results page
# 3. Verify match score shows
# 4. Verify improvements show
# 5. Test download (mock or real)
```

**Checklist**:

- [ ] Results display correctly
- [ ] Match score accurate
- [ ] Improvements listed
- [ ] Download works

---

#### 5.4 Test Portuguese (PT-BR)

```bash
# Manual test
# 1. Ensure locale is pt-br
# 2. Verify all labels in Portuguese
# 3. Test complete flow in PT-BR
```

**Checklist**:

- [ ] All UI in Portuguese
- [ ] Error messages in Portuguese
- [ ] No English leaking through

---

### Step 6: Write Tests (2-3 hours)

#### 6.1 Service Unit Tests

**File**: `backend/tests/unit/test_resume_service.py`

```python
import pytest
from app.services.resume_service import ResumeService

def test_resume_service_imports():
    """Test that ResumeService imports correctly"""
    service = ResumeService()
    assert service is not None

@pytest.mark.asyncio
async def test_process_resume():
    """Test resume processing"""
    service = ResumeService()
    # Add test implementation
    pass
```

**Checklist**:

- [ ] Resume service tests
- [ ] Job service tests
- [ ] Score service tests
- [ ] Agent tests

---

#### 6.2 API Integration Tests

**File**: `backend/tests/integration/test_optimization_flow.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_resume_endpoint():
    """Test resume upload"""
    with open("tests/fixtures/sample_resume.pdf", "rb") as f:
        response = client.post(
            "/api/resume/upload",
            files={"file": ("resume.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
```

**Checklist**:

- [ ] Upload endpoint test
- [ ] Analysis endpoint test
- [ ] Results endpoint test
- [ ] E2E flow test

---

## ✅ Completion Checklist

### Backend

- [ ] 4 services copied and working
- [ ] Agent system copied and working
- [ ] 4+ tables created via migrations
- [ ] 3 API endpoints created
- [ ] All imports resolve
- [ ] Basic tests written

### Frontend

- [ ] Mock API calls replaced with real calls
- [ ] Authentication headers added
- [ ] Error handling implemented
- [ ] Loading states work

### Testing

- [ ] Can upload resume
- [ ] Can analyze job description
- [ ] Match score calculates
- [ ] Results display correctly
- [ ] E2E flow works in PT-BR

### Documentation

- [ ] API endpoints documented
- [ ] Service interfaces documented
- [ ] Migration guide created
- [ ] ROADMAP updated

---

## 🚀 When Complete

After finishing all steps above:

1. **Run full test suite**:

```bash
cd backend
docker compose exec backend python -m pytest tests/ -v
# Expect: 70+ tests passing (59 existing + new ones)
```

2. **Test E2E manually**:

```bash
# Complete optimization flow from upload to results
```

3. **Update documentation**:

```bash
# Mark P0 as complete in ROADMAP.md
# Update P0-VERIFICATION-CHECKLIST.md
```

4. **Merge to main**:

```bash
git add .
git commit -m "feat: Complete P0 - Core services implemented and tested"
git push origin feature/p0-frontend-migration
# Create PR and merge
```

5. **Start P1**:

```bash
git checkout main
git pull
git checkout -b feature/p1-payment-integration
# Begin P1 work
```

---

## 🆘 Troubleshooting

### Import Errors

```bash
# Check Python path
docker compose exec backend python -c "import sys; print(sys.path)"

# Restart backend
docker compose restart backend
```

### Database Errors

```bash
# Check migrations
supabase db diff --schema public

# Reset database (if needed)
supabase db reset
```

### API Errors

```bash
# Check backend logs
docker compose logs backend --tail=100

# Test endpoint directly
curl http://localhost:8000/api/resume/upload -X POST
```

---

## 📊 Progress Tracking

Track your progress:

```
Backend Services:     [    ] 0/4
Agent System:         [    ] 0/1
Database Migrations:  [    ] 0/4
API Endpoints:        [    ] 0/3
Frontend Integration: [    ] 0/1
E2E Testing:          [    ] 0/1
Documentation:        [    ] 0/1

Overall: 0% Complete
```

Update as you go!

---

## 🎯 Success Criteria

P0 is complete when:

- ✅ All services copied and working
- ✅ All tables created
- ✅ All endpoints responding
- ✅ Can upload resume → analyze → view results
- ✅ Complete flow works in PT-BR
- ✅ Tests passing (70+)

**Then you're truly ready for P1!** 🚀

---

**Estimated Time**: 1-2 days
**Difficulty**: Medium (mostly copy-paste with some integration)
**Reward**: Working product! 🎉
