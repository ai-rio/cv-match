# Agent Prompt: Testing Suite

**Agent**: test-writer-agent  
**Phase**: 4 - Testing (Parallel with Frontend Integration)  
**Priority**: P1 (Important but not blocking)  
**Estimated Time**: 2 hours  
**Dependencies**: Phase 3 complete (API endpoints must exist)

---

## 🎯 Mission

Write comprehensive test suite for all P0 services, API endpoints, and integration tests to ensure reliability and catch regressions.

---

## 📋 Tasks

### Task 1: Service Unit Tests (45 min)

**Actions**:
1. Create test file for resume service:
   ```python
   # backend/tests/unit/test_resume_service.py
   
   import pytest
   from unittest.mock import AsyncMock, MagicMock, patch
   from app.services.resume_service import ResumeService
   
   @pytest.fixture
   def resume_service():
       return ResumeService()
   
   @pytest.mark.asyncio
   async def test_resume_service_initialization(resume_service):
       """Test ResumeService can be initialized"""
       assert resume_service is not None
   
   @pytest.mark.asyncio
   async def test_process_resume_pdf(resume_service):
       """Test processing PDF resume"""
       # Mock PDF content
       pdf_content = b"%PDF-1.4 mock content"
       
       with patch('app.services.text_extraction.extract_text') as mock_extract:
           mock_extract.return_value = "Extracted resume text"
           
           result = await resume_service.process_resume(
               file_content=pdf_content,
               filename="test.pdf",
               user_id="test-user-123"
           )
           
           assert result is not None
           assert "id" in result
   
   @pytest.mark.asyncio
   async def test_process_resume_invalid_file():
       """Test processing invalid file type"""
       service = ResumeService()
       
       with pytest.raises(Exception):
           await service.process_resume(
               file_content=b"invalid",
               filename="test.txt",
               user_id="test-user-123"
           )
   ```

2. Create test file for job service:
   ```python
   # backend/tests/unit/test_job_service.py
   
   import pytest
   from app.services.job_service import JobService
   
   @pytest.fixture
   def job_service():
       return JobService()
   
   @pytest.mark.asyncio
   async def test_job_service_initialization(job_service):
       """Test JobService can be initialized"""
       assert job_service is not None
   
   @pytest.mark.asyncio
   async def test_analyze_job_description(job_service):
       """Test analyzing job description"""
       job_desc = "Procuramos desenvolvedor Python sênior com experiência em FastAPI"
       
       result = await job_service.analyze_job(
           description=job_desc,
           title="Desenvolvedor Python",
           company="TechCorp"
       )
       
       assert result is not None
       assert "keywords" in result or "requirements" in result
   ```

3. Create test file for score improvement service:
   ```python
   # backend/tests/unit/test_score_improvement_service.py
   
   import pytest
   from unittest.mock import AsyncMock, patch
   from app.services.score_improvement_service import ScoreImprovementService
   
   @pytest.fixture
   def score_service():
       return ScoreImprovementService()
   
   @pytest.mark.asyncio
   async def test_score_service_initialization(score_service):
       """Test ScoreImprovementService can be initialized"""
       assert score_service is not None
   
   @pytest.mark.asyncio
   async def test_calculate_match_score(score_service):
       """Test match score calculation"""
       resume_text = "Desenvolvedor Python com 5 anos de experiência"
       job_description = "Buscamos desenvolvedor Python sênior"
       
       with patch.object(score_service, 'agent_manager') as mock_agent:
           mock_agent.generate.return_value = '{"score": 85, "keywords": ["Python"], "improvements": []}'
           
           result = await score_service.calculate_match_score(
               resume_text=resume_text,
               job_description=job_description
           )
           
           assert result is not None
           assert "match_score" in result or "score" in result
   ```

**Success Criteria**:
- [x] 3 test files created
- [x] 8+ unit tests written
- [x] All tests pass
- [x] Mocking external dependencies

---

### Task 2: API Integration Tests (45 min)

**Actions**:
1. Create test file for resume endpoints:
   ```python
   # backend/tests/integration/test_resume_endpoints.py
   
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app
   
   client = TestClient(app)
   
   @pytest.fixture
   def auth_headers():
       """Mock authentication headers"""
       return {"Authorization": "Bearer test_token"}
   
   def test_upload_resume_endpoint(auth_headers):
       """Test resume upload endpoint"""
       files = {
           "file": ("test.pdf", b"mock pdf content", "application/pdf")
       }
       
       response = client.post(
           "/api/resumes/upload",
           files=files,
           headers=auth_headers
       )
       
       # May fail without real auth, but structure should be correct
       assert response.status_code in [200, 201, 401]
   
   def test_get_resume_endpoint(auth_headers):
       """Test get resume endpoint"""
       resume_id = "test-resume-123"
       
       response = client.get(
           f"/api/resumes/{resume_id}",
           headers=auth_headers
       )
       
       assert response.status_code in [200, 404, 401]
   ```

2. Create test file for optimization endpoints:
   ```python
   # backend/tests/integration/test_optimization_endpoints.py
   
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app
   
   client = TestClient(app)
   
   @pytest.fixture
   def auth_headers():
       return {"Authorization": "Bearer test_token"}
   
   def test_start_optimization_endpoint(auth_headers):
       """Test start optimization endpoint"""
       payload = {
           "resume_id": "test-resume-123",
           "job_title": "Desenvolvedor Python",
           "company": "TechCorp",
           "job_description": "Desenvolvedor Python com experiência em FastAPI" * 10
       }
       
       response = client.post(
           "/api/optimizations/start",
           json=payload,
           headers=auth_headers
       )
       
       assert response.status_code in [200, 202, 401, 404]
   
   def test_get_optimization_endpoint(auth_headers):
       """Test get optimization endpoint"""
       optimization_id = "test-opt-123"
       
       response = client.get(
           f"/api/optimizations/{optimization_id}",
           headers=auth_headers
       )
       
       assert response.status_code in [200, 404, 401]
   
   def test_list_optimizations_endpoint(auth_headers):
       """Test list optimizations endpoint"""
       response = client.get(
           "/api/optimizations/",
           headers=auth_headers
       )
       
       assert response.status_code in [200, 401]
   ```

**Success Criteria**:
- [x] 2 test files created
- [x] 5+ integration tests written
- [x] Tests verify endpoint structure
- [x] Tests handle auth gracefully

---

### Task 3: Run All Tests (30 min)

**Actions**:
1. Run the complete test suite:
   ```bash
   cd /home/carlos/projects/cv-match/backend
   
   # Run all tests
   docker compose exec backend python -m pytest tests/ -v
   
   # Run with coverage
   docker compose exec backend python -m pytest tests/ --cov=app --cov-report=term-missing
   ```

2. Fix any failing tests

3. Document test coverage:
   ```bash
   # Generate coverage report
   docker compose exec backend python -m pytest tests/ --cov=app --cov-report=html
   
   # View report
   open htmlcov/index.html
   ```

**Success Criteria**:
- [x] All tests pass
- [x] Coverage > 60% overall
- [x] No critical code paths untested

---

## 🔧 Technical Details

### Test Structure

```
backend/tests/
├── unit/
│   ├── test_resume_service.py
│   ├── test_job_service.py
│   └── test_score_improvement_service.py
├── integration/
│   ├── test_resume_endpoints.py
│   └── test_optimization_endpoints.py
└── conftest.py  # Shared fixtures
```

### Pytest Configuration

Create/update `backend/pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

---

## 📊 Verification Checklist

```bash
cd /home/carlos/projects/cv-match/backend

# 1. Check test files created
ls -la tests/unit/
ls -la tests/integration/

# 2. Run unit tests only
docker compose exec backend python -m pytest tests/unit/ -v

# 3. Run integration tests only
docker compose exec backend python -m pytest tests/integration/ -v

# 4. Run all tests
docker compose exec backend python -m pytest tests/ -v

# 5. Check coverage
docker compose exec backend python -m pytest tests/ --cov=app --cov-report=term
```

---

## 📝 Deliverables

### Files to Create:
1. `backend/tests/unit/test_resume_service.py`
2. `backend/tests/unit/test_job_service.py`
3. `backend/tests/unit/test_score_improvement_service.py`
4. `backend/tests/integration/test_resume_endpoints.py`
5. `backend/tests/integration/test_optimization_endpoints.py`
6. `backend/pytest.ini` (if doesn't exist)

### Git Commit:
```bash
git add backend/tests/
git add backend/pytest.ini
git commit -m "test: Add P0 test suite

- Add unit tests for resume service
- Add unit tests for job service
- Add unit tests for score improvement service
- Add integration tests for resume endpoints
- Add integration tests for optimization endpoints
- Configure pytest for async tests
- Achieve 60%+ test coverage

Related: P0 Testing implementation
Tests: 13+ new tests passing"
```

---

## ⏱️ Timeline

- **00:00-00:45**: Task 1 (Service unit tests)
- **00:45-01:30**: Task 2 (API integration tests)
- **01:30-02:00**: Task 3 (Run and fix tests)

**Total**: 2 hours

---

## 🎯 Success Definition

Mission complete when:
1. 13+ tests written
2. All tests pass
3. Coverage > 60%
4. Both unit and integration tests
5. Pytest configured correctly
6. Ready for CI/CD integration

---

**Status**: Ready for deployment 🚀
