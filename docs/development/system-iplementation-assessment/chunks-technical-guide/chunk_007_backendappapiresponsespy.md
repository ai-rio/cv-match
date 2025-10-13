---
chunk: 7
total_chunks: 7
title: backend/app/api/responses.py
context: backend/app/api/responses.py
estimated_tokens: 2440
source: technical-integration-guide.md
---

<!-- Context: tests/test_similarity_service.py -->

# tests/test_similarity_service.py

import pytest
from app.services.resume_matching.similarity_service import SimilarityService
from unittest.mock import AsyncMock

class TestSimilarityService:

    @pytest.fixture
    def service(self):
        return SimilarityService()

    @pytest.mark.asyncio
    async def test_calculate_document_similarity(self, service):
        """Test document similarity calculation"""

        # Mock embeddings
        resume_embeddings = {
            'full_text': [0.1, 0.2, 0.3],
            'section_skills': [0.4, 0.5, 0.6],
            'section_experience': [0.7, 0.8, 0.9]
        }

        job_embeddings = {
            'full_text': [0.1, 0.2, 0.4],
            'section_skills': [0.4, 0.5, 0.7],
            'section_experience': [0.7, 0.8, 0.8]
        }

        # Mock embedding service
        service.embedding_service = AsyncMock()
        service.embedding_service.calculate_similarity.return_value = 0.85

        result = await service.calculate_document_similarity(resume_embeddings, job_embeddings)

        assert result.overall_similarity > 0
        assert result.confidence_score > 0
        assert 'skills' in result.section_similarities
        assert 'experience' in result.section_similarities

<!-- Context: tests/test_api_endpoints.py -->

# tests/test_api_endpoints.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import Mock, patch

client = TestClient(app)

class TestResumeMatchingAPI:

    def test_upload_resume_success(self):
        """Test successful resume upload"""

        mock_file = b"PDF content"

        with patch('app.services.resume_matching.document_processing_service.DocumentProcessingService') as mock_service:
            mock_processor = Mock()
            mock_processor.process_document.return_value = Mock(
                text_content="Resume content",
                quality_score=85.0,
                sections={'experience': '5 years experience'},
                contact_info={'email': 'test@example.com'}
            )
            mock_service.return_value = mock_processor

            response = client.post(
                "/api/documents/upload/resume",
                files={"file": ("test.pdf", mock_file, "application/pdf")},
                data={"title": "Test Resume"}
            )

            assert response.status_code == 201
            data = response.json()
            assert data['quality_score'] == 85.0
            assert 'experience' in data['sections_found']

    def test_upload_resume_invalid_file(self):
        """Test upload with invalid file"""

        response = client.post(
            "/api/documents/upload/resume",
            files={"file": ("test.txt", b"content", "text/plain")}
        )

        assert response.status_code == 413  # Unsupported file type

````


<!-- Context: tests/test_api_endpoints.py > Integration Testing -->

### Integration Testing

```python

<!-- Context: tests/test_integration.py -->

# tests/test_integration.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.supabase.database import ResumeService, JobDescriptionService

client = TestClient(app)

class TestResumeMatchingIntegration:

    @pytest.mark.asyncio
    async def test_end_to_end_matching_flow(self):
        """Test complete resume matching flow"""

        # 1. Upload resume
        resume_response = client.post(
            "/api/documents/upload/resume",
            files={"file": ("resume.pdf", b"PDF resume content", "application/pdf")},
            data={"title": "Software Engineer Resume"}
        )

        assert resume_response.status_code == 201
        resume_id = resume_response.json()['id']

        # 2. Create job description
        job_response = client.post(
            "/api/documents/upload/job-description",
            data={
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "description": "We are looking for a senior software engineer with Python experience...",
                "requirements": "5+ years Python experience, React, AWS"
            }
        )

        assert job_response.status_code == 201
        job_id = job_response.json()['id']

        # 3. Analyze match
        match_response = client.post(
            "/api/matching/analyze",
            json={
                "resume_id": resume_id,
                "job_id": job_id,
                "include_suggestions": True
            }
        )

        assert match_response.status_code == 200
        match_data = match_response.json()

        assert 'overall_score' in match_data
        assert 'detailed_scores' in match_data
        assert 'analysis' in match_data
        assert match_data['overall_score'] >= 0
        assert match_data['overall_score'] <= 100

        # 4. Get suggestions (should be generated in background)
        suggestions_response = client.get(
            f"/api/matching/matches/{match_data['match_id']}/suggestions"
        )

        assert suggestions_response.status_code == 200
        suggestions = suggestions_response.json()
        assert isinstance(suggestions, list)

        # 5. Get match history
        history_response = client.get("/api/matching/matches")

        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) >= 1
        assert history[0]['id'] == match_data['match_id']
````

---

<!-- Context: tests/test_integration.py > Performance Optimization Guidelines -->

## Performance Optimization Guidelines

<!-- Context: tests/test_integration.py > Performance Optimization Guidelines > 1. Database Optimization -->

### 1. Database Optimization

```sql
-- Create materialized views for frequently accessed data
CREATE MATERIALIZED VIEW user_match_stats AS
SELECT
    user_id,
    COUNT(*) as total_matches,
    AVG(overall_score) as avg_score,
    MAX(overall_score) as best_score,
    MIN(created_at) as first_match,
    MAX(created_at) as last_match
FROM match_results
GROUP BY user_id;

-- Create indexes for common query patterns
CREATE INDEX idx_match_results_user_score ON match_results(user_id, overall_score DESC);
CREATE INDEX idx_ai_suggestions_match_priority ON ai_suggestions(match_result_id, priority);

-- Partition large tables by date
CREATE TABLE match_results_y2024m01 PARTITION OF match_results
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

<!-- Context: tests/test_integration.py > Performance Optimization Guidelines > 2. Caching Strategy -->

### 2. Caching Strategy

```python

<!-- Context: backend/app/services/cache_service.py (Enhanced) -->

# backend/app/services/cache_service.py (Enhanced)

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour

    async def get_user_resume_cache(self, user_id: str) -> dict:
        """Get cached resume data for user"""
        key = f"user_resumes:{user_id}"
        return await self.get(key)

    async def set_user_resume_cache(self, user_id: str, resumes: list, ttl: int = None):
        """Cache user's resumes"""
        key = f"user_resumes:{user_id}"
        await self.set(key, resumes, ttl or self.default_ttl)

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for user"""
        pattern = f"*:{user_id}*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
```

<!-- Context: backend/app/services/cache_service.py (Enhanced) > 3. API Response Optimization -->

### 3. API Response Optimization

```python

<!-- Context: backend/app/api/responses.py -->

# backend/app/api/responses.py

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.services.cache_service import CacheService

router = APIRouter()

@router.get("/matches", response_model=List[dict])
async def get_match_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's match history with caching"""

    cache_service = CacheService()

    # Check cache first
    cache_key = f"match_history:{current_user.id}:{limit}:{offset}"
    cached_result = await cache_service.get(cache_key)

    if cached_result:
        return JSONResponse(
            content=cached_result,
            headers={"X-Cache": "HIT"}
        )

    # Get from database
    match_service = MatchResultService()
    matches = await match_service.get_user_match_history(
        current_user.id, limit=limit, offset=offset
    )

    # Cache for 5 minutes
    await cache_service.set(cache_key, matches, ttl=300)

    return JSONResponse(
        content=matches,
        headers={"X-Cache": "MISS"}
    )
```

---

This technical integration guide provides comprehensive specifications for implementing Resume-Matcher features into the CV-Match platform. The guide covers all aspects from service architecture to testing strategies, ensuring a successful integration with minimal disruption to existing functionality.

**Key Implementation Points:**

- Follow the existing service layer patterns
- Implement comprehensive error handling
- Use caching strategies for performance optimization
- Maintain backward compatibility with existing features
- Implement proper rate limiting and usage tracking
- Create thorough test coverage for all new functionality

The integration builds upon CV-Match's strong foundation while adding sophisticated AI capabilities that will significantly enhance the platform's value proposition.
