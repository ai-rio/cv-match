---
chunk: 5
total_chunks: 7
title: Frontend Component Structure
context: backend/app/api/endpoints/resume_matching.py > File Structure Organization > Frontend Component Structure
estimated_tokens: 3018
source: technical-integration-guide.md
---

<!-- Context: backend/app/api/endpoints/documents.py > 2. Resume Matching Endpoints -->

#### 2. Resume Matching Endpoints

```python

<!-- Context: backend/app/api/endpoints/resume_matching.py -->

# backend/app/api/endpoints/resume_matching.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from app.services.resume_matching.similarity_service import SimilarityService
from app.services.resume_matching.llm_service import LLMService
from app.services.supabase.database import ResumeService, JobDescriptionService, MatchResultService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/matching", tags=["resume-matching"])

class MatchRequest(BaseModel):
    resume_id: str
    job_id: str
    include_suggestions: bool = True

class MatchResponse(BaseModel):
    match_id: str
    overall_score: float
    confidence_score: float
    detailed_scores: dict
    analysis: dict
    suggestions: List[dict] = []

@router.post("/analyze", response_model=MatchResponse)
async def analyze_match(
    request: MatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze match between resume and job description

    Args:
        request: Match request with resume and job IDs
        background_tasks: FastAPI background tasks
        current_user: Authenticated user

    Returns:
        Detailed match analysis results
    """
    try:
        # Validate ownership
        resume_service = ResumeService()
        job_service = JobDescriptionService()

        resume = await resume_service.get_by_id(request.resume_id)
        job = await job_service.get_by_id(request.job_id)

        if not resume or resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or access denied"
            )

        if not job or job.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found or access denied"
            )

        # Check if match already exists
        match_service = MatchResultService()
        existing_matches = await match_service.get_by_user(
            current_user.id,
            filters={'resume_id': request.resume_id, 'job_id': request.job_id}
        )

        if existing_matches:
            existing_match = existing_matches[0]
            return MatchResponse(
                match_id=existing_match.id,
                overall_score=existing_match.overall_score,
                confidence_score=existing_match.confidence_score,
                detailed_scores={
                    'skills': existing_match.skills_score,
                    'experience': existing_match.experience_score,
                    'education': existing_match.education_score,
                    'keywords': existing_match.keyword_score
                },
                analysis=existing_match.match_analysis
            )

        # Get embeddings
        from app.services.resume_matching.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()

        resume_embeddings = await embedding_service.get_document_embeddings(request.resume_id)
        job_embeddings = await embedding_service.get_document_embeddings(request.job_id)

        if not resume_embeddings or not job_embeddings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Embeddings not found for documents"
            )

        # Calculate similarity
        similarity_service = SimilarityService()
        similarity_result = await similarity_service.calculate_document_similarity(
            resume_embeddings, job_embeddings
        )

        # Perform LLM analysis
        llm_service = LLMService()
        llm_analysis = await llm_service.analyze_resume_job_match(
            resume.content_text,
            job.description
        )

        # Create match result
        match_data = {
            'user_id': current_user.id,
            'resume_id': request.resume_id,
            'job_id': request.job_id,
            'overall_score': similarity_result.overall_similarity * 100,
            'confidence_score': similarity_result.confidence_score * 100,
            'skills_score': similarity_result.section_similarities.get('skills', 0) * 100,
            'experience_score': similarity_result.section_similarities.get('experience', 0) * 100,
            'education_score': similarity_result.section_similarities.get('education', 0) * 100,
            'keyword_score': similarity_result.keyword_similarity * 100,
            'section_scores': {k: v * 100 for k, v in similarity_result.section_similarities.items()},
            'match_analysis': llm_analysis.dict(),
            'skill_gaps': llm_analysis.skills_match.get('gaps', []),
            'strengths': llm_analysis.skills_match.get('strengths', [])
        }

        match_result = await match_service.create(match_data)

        # Generate suggestions in background
        if request.include_suggestions:
            background_tasks.add_task(
                generate_improvement_suggestions,
                match_result.id,
                resume.content_text,
                job.description,
                similarity_result.overall_similarity
            )

        return MatchResponse(
            match_id=match_result.id,
            overall_score=match_result.overall_score,
            confidence_score=match_result.confidence_score,
            detailed_scores={
                'skills': match_result.skills_score,
                'experience': match_result.experience_score,
                'education': match_result.education_score,
                'keywords': match_result.keyword_score
            },
            analysis=match_result.match_analysis
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match analysis failed: {str(e)}"
        )

async def generate_improvement_suggestions(
    match_result_id: str,
    resume_text: str,
    job_description_text: str,
    similarity_score: float
):
    """Generate improvement suggestions in background"""
    try:
        llm_service = LLMService()

        # Generate suggestions
        match_scores = {'overall': similarity_score}
        suggestions = await llm_service.generate_improvement_suggestions(
            resume_text, job_description_text, match_scores
        )

        # Store suggestions in database
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

    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to generate suggestions: {str(e)}")

@router.get("/matches", response_model=List[dict])
async def get_match_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's match history"""
    try:
        match_service = MatchResultService()
        matches = await match_service.get_user_match_history(
            current_user.id, limit=limit, offset=offset
        )
        return matches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve match history: {str(e)}"
        )

@router.get("/matches/{match_id}/suggestions", response_model=List[dict])
async def get_match_suggestions(
    match_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get suggestions for a specific match"""
    try:
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        suggestions = await suggestion_service.get_by_user(
            current_user.id,
            filters={'match_result_id': match_id}
        )

        # Sort by priority
        suggestions.sort(key=lambda x: x.get('priority', 5))

        return suggestions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve suggestions: {str(e)}"
        )

@router.put("/suggestions/{suggestion_id}/status")
async def update_suggestion_status(
    suggestion_id: str,
    status: str,  # 'implemented', 'rejected'
    current_user: User = Depends(get_current_user)
):
    """Update suggestion implementation status"""
    try:
        from app.services.supabase.database import SupabaseDatabaseService
        suggestion_service = SupabaseDatabaseService("ai_suggestions", dict)

        # Validate ownership
        suggestions = await suggestion_service.get_by_user(
            current_user.id,
            filters={'id': suggestion_id}
        )

        if not suggestions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or access denied"
            )

        # Update status
        update_data = {
            'status': status,
            'implemented_at': datetime.utcnow().isoformat() if status == 'implemented' else None
        }

        updated_suggestion = await suggestion_service.update(suggestion_id, update_data)

        return {"status": "updated", "suggestion": updated_suggestion}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update suggestion status: {str(e)}"
        )
```

---


<!-- Context: backend/app/api/endpoints/resume_matching.py > File Structure Organization -->

## File Structure Organization


<!-- Context: backend/app/api/endpoints/resume_matching.py > File Structure Organization > Frontend Component Structure -->

### Frontend Component Structure

```typescript
// frontend/app/components/resume-matching/
├── ResumeUpload.tsx              // Enhanced file upload component
├── JobDescriptionInput.tsx       // Job description form
├── MatchResults.tsx             // Results display and visualization
├── SuggestionsPanel.tsx         // AI improvement suggestions
├── ScoreVisualization.tsx       // Score charts and graphs
├── DocumentPreview.tsx          // Document preview component
├── MatchingHistory.tsx          // User's match history
├── FeedbackForm.tsx             // User feedback collection
└── index.ts                     // Component exports

// frontend/app/hooks/
├── useResumeMatching.ts         // Main matching logic hook
├── useDocumentUpload.ts         // File upload handling
├── useSuggestions.ts            // Suggestions management
└── useMatchingHistory.ts        // History management

// frontend/app/types/
├── resume.ts                    // Resume-related types
├── job-description.ts           // Job description types
├── match-result.ts              // Match result types
└── suggestion.ts                // Suggestion types
```
