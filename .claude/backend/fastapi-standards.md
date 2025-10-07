# FastAPI Backend Development Standards

## API Endpoint Structure

Follow this pattern for all API endpoints:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import User
from app.models.resume import ResumeRequest, ResumeResponse
from app.services.supabase.auth import get_current_user
from app.services.resume.resume_service import ResumeService

router = APIRouter(prefix="/api/v1", tags=["resumes"])

@router.post("/resumes/analyze", response_model=ResumeResponse)
async def analyze_resume(
    request: ResumeRequest,
    current_user: User = Depends(get_current_user)
) -> ResumeResponse:
    """
    Analyze a resume and provide improvement suggestions.

    Args:
        request: Resume analysis request with file data
        current_user: Authenticated user from JWT token

    Returns:
        ResumeResponse with analysis results and suggestions

    Raises:
        HTTPException: If analysis fails or user lacks credits
    """
    try:
        # Initialize service
        service = ResumeService()

        # Business logic
        result = await service.analyze(
            user_id=current_user.id,
            resume_data=request.resume_text,
            job_description=request.job_description
        )

        return ResumeResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log error
        print(f"Resume analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze resume. Please try again."
        )
```

## Service Layer Pattern

All external service interactions must go through service classes:

### Database Operations
```python
from app.services.supabase.database import SupabaseDatabaseService

db = SupabaseDatabaseService()

# Create record
result = await db.create("resumes", {
    "user_id": user_id,
    "content": resume_text,
    "status": "processing"
})

# Read record
resume = await db.get_by_id("resumes", resume_id)

# Update record
await db.update("resumes", resume_id, {
    "status": "completed",
    "score": 85.5
})

# Query with filters
resumes = await db.query(
    "resumes",
    filters={"user_id": user_id},
    order_by="created_at",
    limit=10
)
```

### LLM Operations
```python
from app.agent.agent_manager import AgentManager

agent = AgentManager()

# Generate text
response = await agent.generate(
    prompt="Analyze this resume...",
    system_prompt="You are a professional resume expert.",
    model="anthropic/claude-3.5-sonnet",
    temperature=0.7
)

# Stream response
async for chunk in agent.generate_stream(
    prompt=prompt,
    model="anthropic/claude-3.5-sonnet"
):
    yield chunk
```

### Payment Operations
```python
from app.services.stripe.stripe_service import StripeService

stripe = StripeService()

# Create checkout session
session = await stripe.create_checkout_session(
    user_id=user_id,
    user_email=user.email,
    amount=5990,  # R$ 59,90 in centavos
    currency="brl",
    success_url="https://cvmatch.com/payment/success",
    cancel_url="https://cvmatch.com/payment/cancel"
)

# Verify payment
payment = await stripe.verify_payment(session_id)
```

## Error Handling

Always use proper HTTP status codes and descriptive error messages:

```python
from fastapi import HTTPException, status

# Bad Request (400)
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid resume format. Please upload PDF or DOCX."
)

# Unauthorized (401)
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired authentication token."
)

# Forbidden (403)
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient credits. Please purchase more credits."
)

# Not Found (404)
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Resume with ID {resume_id} not found."
)

# Conflict (409)
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Resume with this name already exists."
)

# Too Many Requests (429)
raise HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Rate limit exceeded. Please try again in 60 seconds."
)

# Internal Server Error (500)
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="An unexpected error occurred. Please try again later."
)
```

## Authentication

All protected endpoints must use the authentication dependency:

```python
from app.services.supabase.auth import get_current_user
from app.models.auth import User

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Protected endpoint requiring authentication."""
    return {"message": f"Hello {current_user.email}"}

# Optional authentication (for features available to both logged in and anonymous)
from typing import Optional

@router.get("/public-with-auth")
async def public_endpoint(
    current_user: Optional[User] = Depends(get_current_user)
):
    """Endpoint available to both authenticated and anonymous users."""
    if current_user:
        return {"message": f"Welcome back, {current_user.email}"}
    return {"message": "Welcome, guest"}
```

## Configuration

Use the centralized config system:

```python
from app.core.config import settings

# Access environment variables through settings
supabase_url = settings.SUPABASE_URL
openai_key = settings.OPENAI_API_KEY
stripe_secret = settings.STRIPE_SECRET_KEY

# Use configuration for service initialization
if settings.ENVIRONMENT == "production":
    # Production behavior
    pass
else:
    # Development behavior
    pass
```

## Async/Await

Always use async/await for I/O operations:

```python
# Database operations
result = await database_service.create(data)

# External API calls
response = await llm_service.generate(prompt)

# File operations
async with aiofiles.open(file_path, 'w') as f:
    await f.write(content)

# Multiple concurrent operations
import asyncio

results = await asyncio.gather(
    db.get_user(user_id),
    db.get_resumes(user_id),
    stripe.get_subscription(user_id)
)
user, resumes, subscription = results
```

## Pydantic Models

Define request/response models using Pydantic:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ResumeRequest(BaseModel):
    """Request model for resume analysis."""
    resume_text: str = Field(..., min_length=100, max_length=50000)
    job_description: str = Field(..., min_length=50, max_length=10000)
    language: str = Field(default="pt-br", regex="^(pt-br|en)$")

    @validator('resume_text')
    def validate_resume_text(cls, v):
        if not v.strip():
            raise ValueError("Resume text cannot be empty")
        return v.strip()

class ImprovementSuggestion(BaseModel):
    """Model for a single improvement suggestion."""
    category: str  # e.g., "skills", "experience", "formatting"
    suggestion: str
    priority: str = Field(..., regex="^(high|medium|low)$")

class ResumeResponse(BaseModel):
    """Response model for resume analysis."""
    resume_id: str
    score: float = Field(..., ge=0, le=100)
    match_percentage: float = Field(..., ge=0, le=100)
    suggestions: List[ImprovementSuggestion]
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "resume_id": "123e4567-e89b-12d3-a456-426614174000",
                "score": 85.5,
                "match_percentage": 78.3,
                "suggestions": [
                    {
                        "category": "skills",
                        "suggestion": "Add Python programming to your skills",
                        "priority": "high"
                    }
                ],
                "created_at": "2025-10-07T12:00:00Z"
            }
        }
```

## Dependency Injection

Use FastAPI dependencies for reusable logic:

```python
from fastapi import Depends, HTTPException

# Dependency for credit validation
async def verify_credits(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify user has sufficient credits."""
    from app.services.usage.usage_service import UsageService

    usage_service = UsageService()
    has_credits = await usage_service.check_credits(current_user.id, required=1)

    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient credits. Please purchase more."
        )

    return current_user

# Use in endpoint
@router.post("/analyze")
async def analyze(
    request: ResumeRequest,
    user: User = Depends(verify_credits)
):
    # User is guaranteed to have credits
    pass
```

## Response Models and Status Codes

Use appropriate response models and status codes:

```python
from fastapi import status
from fastapi.responses import JSONResponse

# 200 OK - Success
@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str):
    return resume

# 201 Created - Resource created
@router.post("/resumes", status_code=status.HTTP_201_CREATED)
async def create_resume(request: ResumeRequest):
    result = await service.create(request)
    return result

# 204 No Content - Success with no body
@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str):
    await service.delete(resume_id)
    return None

# Custom response
@router.post("/payment/webhook")
async def stripe_webhook(request: Request):
    # Process webhook
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"received": True}
    )
```

## Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Info
logger.info(f"Resume analysis started for user {user_id}")

# Warning
logger.warning(f"User {user_id} has low credits: {credits_remaining}")

# Error with exception
try:
    result = await service.process()
except Exception as e:
    logger.error(f"Processing failed: {str(e)}", exc_info=True)
    raise
```

## Testing

Write tests for all endpoints:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_resume_success():
    """Test successful resume analysis."""
    response = client.post(
        "/api/v1/resumes/analyze",
        json={
            "resume_text": "John Doe, Software Engineer...",
            "job_description": "Looking for Python developer..."
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert "score" in response.json()
    assert response.json()["score"] >= 0

def test_analyze_resume_no_auth():
    """Test resume analysis without authentication."""
    response = client.post(
        "/api/v1/resumes/analyze",
        json={"resume_text": "...", "job_description": "..."}
    )

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_service_layer():
    """Test service layer directly."""
    from app.services.resume.resume_service import ResumeService

    service = ResumeService()
    result = await service.analyze(
        user_id="test_user",
        resume_data="test resume",
        job_description="test job"
    )

    assert result is not None
    assert "score" in result
```

---

**Key Principles**:
1. Always use type hints
2. Follow the service layer pattern
3. Use proper HTTP status codes
4. Include comprehensive error handling
5. Use async/await for I/O operations
6. Validate all inputs with Pydantic
7. Test all endpoints
8. Log important operations
