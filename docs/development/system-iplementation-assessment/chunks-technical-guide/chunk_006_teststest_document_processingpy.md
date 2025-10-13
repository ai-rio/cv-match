---
chunk: 6
total_chunks: 7
title: tests/test_document_processing.py
context: tests/test_document_processing.py
estimated_tokens: 3969
source: technical-integration-guide.md
---

<!-- Context: backend/app/api/endpoints/resume_matching.py > File Structure Organization > Component Implementation Example -->

### Component Implementation Example

```typescript
// frontend/app/components/resume-matching/ResumeUpload.tsx

'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { uploadResume } from '@/app/api/resume-matching'
import { ProgressBar } from '@/app/components/ui/ProgressBar'
import { Alert, AlertDescription } from '@/app/components/ui/Alert'

interface ResumeUploadProps {
  onUploadSuccess: (resumeId: string) => void
  onError: (error: string) => void
}

export function ResumeUpload({ onUploadSuccess, onError }: ResumeUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      onError('Apenas arquivos PDF e DOCX são permitidos')
      return
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      onError('O arquivo deve ter menos de 10MB')
      return
    }

    setUploadedFile(file)
    await handleUpload(file)
  }, [onError])

  const handleUpload = async (file: File) => {
    setUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name.replace(/\.[^/.]+$/, ''))

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 200)

      const result = await uploadResume(formData)

      clearInterval(progressInterval)
      setUploadProgress(100)

      setTimeout(() => {
        onUploadSuccess(result.id)
        setUploading(false)
        setUploadProgress(0)
      }, 500)

    } catch (error) {
      setUploading(false)
      setUploadProgress(0)
      onError(error instanceof Error ? error.message : 'Falha no upload')
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    disabled: uploading
  })

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />

        {uploading ? (
          <div className="space-y-4">
            <div className="text-lg font-medium">Processando currículo...</div>
            <ProgressBar progress={uploadProgress} />
            <p className="text-sm text-gray-600">
              Isso pode levar alguns segundos. Estamos analisando seu currículo.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-lg font-medium">
              {isDragActive ? 'Solte o arquivo aqui' : 'Arraste seu currículo ou clique para selecionar'}
            </div>
            <p className="text-sm text-gray-600">
              PDF ou DOCX (máximo 10MB)
            </p>
            {uploadedFile && !uploading && (
              <Alert>
                <AlertDescription>
                  Arquivo selecionado: {uploadedFile.name}
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// API function
// frontend/app/api/resume-matching.ts

export async function uploadResume(formData: FormData) {
  try {
    const response = await fetch('/api/documents/upload/resume', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Falha no upload')
    }

    return await response.json()
  } catch (error) {
    throw error
  }
}
```

---


<!-- Context: backend/app/api/endpoints/resume_matching.py > Integration Patterns and Best Practices -->

## Integration Patterns and Best Practices


<!-- Context: backend/app/api/endpoints/resume_matching.py > Integration Patterns and Best Practices > 1. Error Handling Patterns -->

### 1. Error Handling Patterns

```python

<!-- Context: backend/app/core/exceptions.py -->

# backend/app/core/exceptions.py

from fastapi import HTTPException, status

class ResumeMatchingException(Exception):
    """Base exception for resume matching operations"""
    pass

class DocumentProcessingError(ResumeMatchingException):
    """Raised when document processing fails"""
    pass

class EmbeddingGenerationError(ResumeMatchingException):
    """Raised when embedding generation fails"""
    pass

class LLMServiceError(ResumeMatchingException):
    """Raised when LLM service operations fail"""
    pass

class VectorDatabaseError(ResumeMatchingException):
    """Raised when vector database operations fail"""
    pass


<!-- Context: Exception handler -->

# Exception handler

<!-- Context: backend/app/api/exception_handlers.py -->

# backend/app/api/exception_handlers.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.exceptions import ResumeMatchingException

async def resume_matching_exception_handler(request: Request, exc: ResumeMatchingException):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Resume matching operation failed",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


<!-- Context: Register exception handlers in main app -->

# Register exception handlers in main app

<!-- Context: backend/app/main.py -->

# backend/app/main.py

from fastapi import FastAPI
from app.core.exceptions import ResumeMatchingException
from app.api.exception_handlers import resume_matching_exception_handler

app = FastAPI()
app.add_exception_handler(ResumeMatchingException, resume_matching_exception_handler)
```


<!-- Context: backend/app/main.py > 2. Caching Strategies -->

### 2. Caching Strategies

```python

<!-- Context: backend/app/services/cache_service.py -->

# backend/app/services/cache_service.py

import redis
import json
import hashlib
from typing import Any, Optional
from app.core.config import settings

class CacheService:
    """Redis-based caching service"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass  # Cache failures should not break the application

    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            self.redis_client.delete(key)
        except Exception:
            pass

    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        key_data = ":".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"


<!-- Context: Usage in services -->

# Usage in services
class EmbeddingService:
    def __init__(self):
        self.cache_service = CacheService()

    async def generate_embedding(self, text: str) -> List[float]:
        # Check cache first
        cache_key = self.cache_service.generate_cache_key("embedding", text)
        cached_embedding = await self.cache_service.get(cache_key)

        if cached_embedding:
            return cached_embedding

        # Generate new embedding
        embedding = await self._generate_embedding_from_api(text)

        # Cache for 24 hours
        await self.cache_service.set(cache_key, embedding, ttl=86400)

        return embedding
```


<!-- Context: Usage in services > 3. Rate Limiting -->

### 3. Rate Limiting

```python

<!-- Context: backend/app/api/dependencies/rate_limiting.py -->

# backend/app/api/dependencies/rate_limiting.py

from fastapi import HTTPException, status, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis

limiter = Limiter(key_func=get_remote_address)

class RateLimiter:
    """Custom rate limiting for resume matching operations"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    async def check_rate_limit(self, user_id: str, operation: str, limit: int, window: int):
        """
        Check if user exceeds rate limit for specific operation

        Args:
            user_id: User identifier
            operation: Operation type (e.g., 'match_analysis', 'suggestions')
            limit: Number of allowed operations
            window: Time window in seconds
        """
        key = f"rate_limit:{user_id}:{operation}"
        current = self.redis_client.incr(key)

        if current == 1:
            self.redis_client.expire(key, window)

        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {operation}. Try again later."
            )


<!-- Context: Usage in endpoints -->

# Usage in endpoints
@router.post("/analyze")
@limiter.limit("10/minute")  # General rate limit
async def analyze_match(
    request: Request,
    match_request: MatchRequest,
    current_user: User = Depends(get_current_user)
):
    # Custom rate limit for premium users
    rate_limiter = RateLimiter()

    if current_user.subscription_tier == 'free':
        await rate_limiter.check_rate_limit(current_user.id, 'match_analysis', 5, 3600)  # 5 per hour
    else:
        await rate_limiter.check_rate_limit(current_user.id, 'match_analysis', 50, 3600)  # 50 per hour

    # ... rest of the function
```


<!-- Context: Usage in endpoints > 4. Background Job Processing -->

### 4. Background Job Processing

```python

<!-- Context: backend/app/services/background_jobs.py -->

# backend/app/services/background_jobs.py

from celery import Celery
from app.services.resume_matching.llm_service import LLMService
from app.core.config import settings

celery_app = Celery(
    "cv_match",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task(bind=True, max_retries=3)
def generate_suggestions_task(self, match_result_id: str, resume_text: str,
                            job_description_text: str, similarity_score: float):
    """Background task for generating improvement suggestions"""
    try:
        llm_service = LLMService()

        match_scores = {'overall': similarity_score}
        suggestions = await llm_service.generate_improvement_suggestions(
            resume_text, job_description_text, match_scores
        )

        # Store suggestions
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        for suggestion in suggestions:
            suggestion_data = {
                'match_result_id': match_result_id,
                'suggestion_type': suggestion.get('type', 'general'),
                'category': suggestion.get('category', 'medium_impact'),
                'title': suggestion.get('title', 'Improvement Suggestion'),
                'description': suggestion.get('text', ''),
                'priority': suggestion.get('priority', 3),
                'impact_score': suggestion.get('impact', 5.0),
                'effort_estimate': suggestion.get('effort', 'medium'),
                'ai_confidence': suggestion.get('confidence', 0.7)
            }

            await suggestion_service.create(suggestion_data)

    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---


<!-- Context: backend/app/services/background_jobs.py > Testing Strategies -->

## Testing Strategies


<!-- Context: backend/app/services/background_jobs.py > Testing Strategies > Unit Testing Examples -->

### Unit Testing Examples

```python

<!-- Context: tests/test_document_processing.py -->

# tests/test_document_processing.py

import pytest
from app.services.resume_matching.document_processing_service import DocumentProcessingService
from unittest.mock import Mock, patch
import io

class TestDocumentProcessingService:

    @pytest.fixture
    def service(self):
        return DocumentProcessingService()

    @pytest.fixture
    def sample_pdf_content(self):
        # Create a simple PDF for testing
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n..."

    @pytest.mark.asyncio
    async def test_process_pdf_document(self, service, sample_pdf_content):
        """Test PDF document processing"""

        # Mock file object
        mock_file = Mock()
        mock_file.filename = "test_resume.pdf"
        mock_file.read.return_value = sample_pdf_content

        # Mock PDF parsing
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\nExperience: 5 years"

            mock_reader = Mock()
            mock_reader.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader

            result = await service.process_document(mock_file, 'resume')

            assert result.text_content == "John Doe Software Engineer Experience: 5 years"
            assert result.quality_score > 0
            assert 'experience' in result.sections

    @pytest.mark.asyncio
    async def test_invalid_file_format(self, service):
        """Test handling of invalid file formats"""

        mock_file = Mock()
        mock_file.filename = "test.txt"

        with pytest.raises(ValueError, match="Unsupported file format"):
            await service.process_document(mock_file, 'resume')

    def test_clean_text(self, service):
        """Test text cleaning functionality"""

        dirty_text = "John   Doe\n\n\nSoftware    Engineer!!@@#"
        clean_text = service._clean_text(dirty_text)

        assert "  " not in clean_text  # No double spaces
        assert clean_text == "John Doe Software Engineer"

    def test_extract_contact_info(self, service):
        """Test contact information extraction"""

        text = """
        John Doe
        Email: john.doe@example.com
        Phone: (11) 98765-4321
        LinkedIn: linkedin.com/in/johndoe
        """

        contact_info = service._extract_contact_info(text)

        assert contact_info['email'] == 'john.doe@example.com'
        assert contact_info['phone'] == '(11) 98765-4321'
        assert contact_info['linkedin'] == 'linkedin.com/in/johndoe'
