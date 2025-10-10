"""
API endpoints for resume optimization workflow.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.optimization import (
    StartOptimizationRequest,
    OptimizationResponse,
    OptimizationDetailResponse,
    OptimizationListResponse,
    JobDescriptionResponse,
    OptimizationStatus
)
from app.services.score_improvement_service import ScoreImprovementService
from app.services.job_service import JobService
from app.services.resume_service import ResumeService
from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimizations", tags=["optimizations"])


# Extend JobService to support job description creation
class ExtendedJobService(JobService):
    """Extended job service with additional methods for optimization workflow."""

    async def create_job_description(
        self,
        user_id: str,
        title: str,
        company: str,
        description: str
    ) -> dict:
        """
        Create a job description entry for optimization.

        Args:
            user_id: User ID
            title: Job title
            company: Company name
            description: Job description text

        Returns:
            Created job description data
        """
        job_id = str(uuid.uuid4())

        job_data = {
            "job_id": job_id,
            "user_id": user_id,
            "title": title,
            "company": company,
            "description": description,
            "content_type": "text/markdown"
        }

        # Store job description using Supabase service
        service = SupabaseDatabaseService("job_descriptions", dict)
        result = await service.create(job_data)

        return {
            "id": job_id,
            "title": title,
            "company": company,
            "description": description,
            "created_at": result.get("created_at", datetime.utcnow())
        }


# Extend ScoreImprovementService to support optimization workflow
class ExtendedScoreImprovementService(ScoreImprovementService):
    """Extended score improvement service with optimization workflow support."""

    async def create_optimization(
        self,
        user_id: str,
        resume_id: str,
        job_description_id: str,
        status: OptimizationStatus
    ) -> dict:
        """
        Create an optimization record.

        Args:
            user_id: User ID
            resume_id: Resume ID
            job_description_id: Job description ID
            status: Initial optimization status

        Returns:
            Created optimization data
        """
        optimization_id = str(uuid.uuid4())

        optimization_data = {
            "optimization_id": optimization_id,
            "user_id": user_id,
            "resume_id": resume_id,
            "job_description_id": job_description_id,
            "status": status.value,
            "created_at": datetime.utcnow()
        }

        # Store optimization using Supabase service
        service = SupabaseDatabaseService("optimizations", dict)
        result = await service.create(optimization_data)

        return {
            "id": optimization_id,
            "resume_id": resume_id,
            "job_description_id": job_description_id,
            "status": status.value,
            "created_at": result.get("created_at", datetime.utcnow())
        }

    async def get_optimization(
        self,
        optimization_id: str,
        user_id: str
    ) -> Optional[dict]:
        """
        Get optimization by ID for a specific user.

        Args:
            optimization_id: Optimization ID
            user_id: User ID

        Returns:
            Optimization data or None if not found
        """
        service = SupabaseDatabaseService("optimizations", dict)
        optimization = await service.get(optimization_id)

        # Verify ownership
        if optimization and optimization.get("user_id") == user_id:
            return optimization

        return None

    async def list_optimizations(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        """
        List optimizations for a specific user.

        Args:
            user_id: User ID
            limit: Maximum number of optimizations to return
            offset: Number of optimizations to skip

        Returns:
            List of optimization data
        """
        service = SupabaseDatabaseService("optimizations", dict)
        # TODO: Add user_id filtering when RLS is properly configured
        optimizations = await service.list(limit=limit, offset=offset)

        # Filter by user_id (temporary solution until RLS is configured)
        return [opt for opt in optimizations if opt.get("user_id") == user_id]

    async def update_optimization_status(
        self,
        optimization_id: str,
        status: OptimizationStatus,
        results: Optional[dict] = None
    ) -> dict:
        """
        Update optimization status and results.

        Args:
            optimization_id: Optimization ID
            status: New status
            results: Optional optimization results

        Returns:
            Updated optimization data
        """
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow()
        }

        if results:
            update_data.update(results)
            if status == OptimizationStatus.COMPLETED:
                update_data["completed_at"] = datetime.utcnow()

        service = SupabaseDatabaseService("optimizations", dict)
        return await service.update(optimization_id, update_data)


@router.post("/start", response_model=OptimizationResponse, status_code=201)
async def start_optimization(
    request: StartOptimizationRequest,
    current_user: dict = Depends(get_current_user)
) -> OptimizationResponse:
    """
    Start resume optimization process.

    This endpoint creates a job description entry and initiates the
    optimization workflow for a resume.

    Args:
        request: Optimization request data
        current_user: Currently authenticated user

    Returns:
        OptimizationResponse with optimization information

    Raises:
        HTTPException: If optimization creation fails
    """
    try:
        # Verify resume exists and belongs to user
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(request.resume_id)

        if not resume_data:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        # Create job description entry
        job_service = ExtendedJobService()
        job_result = await job_service.create_job_description(
            user_id=current_user["id"],
            title=request.job_title or "Job Description",
            company=request.company or "Company",
            description=request.job_description
        )

        # Create optimization record
        optimization_service = ExtendedScoreImprovementService()
        result = await optimization_service.create_optimization(
            user_id=current_user["id"],
            resume_id=request.resume_id,
            job_description_id=job_result["id"],
            status=OptimizationStatus.PENDING_PAYMENT
        )

        logger.info(f"Optimization {result['id']} created for user {current_user['id']}")

        return OptimizationResponse(
            id=result["id"],
            resume_id=result["resume_id"],
            job_description_id=result["job_description_id"],
            status=OptimizationStatus(result["status"]),
            created_at=result["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start optimization: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start optimization: {str(e)}"
        ) from e


@router.get("/{optimization_id}", response_model=OptimizationDetailResponse)
async def get_optimization(
    optimization_id: str,
    current_user: dict = Depends(get_current_user)
) -> OptimizationDetailResponse:
    """
    Get optimization results by ID.

    Args:
        optimization_id: Optimization ID
        current_user: Currently authenticated user

    Returns:
        OptimizationDetailResponse with detailed optimization information

    Raises:
        HTTPException: If optimization not found or access denied
    """
    try:
        optimization_service = ExtendedScoreImprovementService()
        optimization = await optimization_service.get_optimization(
            optimization_id=optimization_id,
            user_id=current_user["id"]
        )

        if not optimization:
            raise HTTPException(
                status_code=404,
                detail="Optimization not found"
            )

        # Get resume and job description data
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(
            optimization["resume_id"]
        )

        job_service = ExtendedJobService()
        # Note: We need to implement get_job_description method
        job_data = {"description": "Job description not available"}

        # Extract relevant information
        raw_resume = resume_data.get("raw_resume", {}) if resume_data else {}

        return OptimizationDetailResponse(
            id=optimization["optimization_id"],
            resume_id=optimization["resume_id"],
            job_description_id=optimization["job_description_id"],
            match_score=optimization.get("match_score"),
            improvements=optimization.get("improvements", []),
            keywords=optimization.get("keywords", []),
            status=OptimizationStatus(optimization["status"]),
            created_at=optimization["created_at"],
            completed_at=optimization.get("completed_at"),
            error_message=optimization.get("error_message"),
            resume_text=raw_resume.get("content"),
            job_description_text=job_data.get("description"),
            strengths=optimization.get("strengths", []),
            embedding_similarity=optimization.get("embedding_similarity"),
            improved_resume=optimization.get("improved_resume"),
            changes_made=optimization.get("changes_made", []),
            expected_score=optimization.get("expected_score")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get optimization {optimization_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve optimization: {str(e)}"
        ) from e


@router.get("/", response_model=OptimizationListResponse)
async def list_optimizations(
    limit: int = Query(10, ge=1, le=100, description="Number of optimizations to return"),
    offset: int = Query(0, ge=0, description="Number of optimizations to skip"),
    current_user: dict = Depends(get_current_user)
) -> OptimizationListResponse:
    """
    List optimizations for the current user.

    Args:
        limit: Maximum number of optimizations to return
        offset: Number of optimizations to skip
        current_user: Currently authenticated user

    Returns:
        OptimizationListResponse with list of optimizations

    Raises:
        HTTPException: If listing fails
    """
    try:
        optimization_service = ExtendedScoreImprovementService()
        optimizations_data = await optimization_service.list_optimizations(
            user_id=current_user["id"],
            limit=limit,
            offset=offset
        )

        # Convert to response format
        optimizations = []
        for opt_dict in optimizations_data:
            optimizations.append(OptimizationResponse(
                id=opt_dict.get("optimization_id", str(uuid.uuid4())),
                resume_id=opt_dict.get("resume_id"),
                job_description_id=opt_dict.get("job_description_id"),
                match_score=opt_dict.get("match_score"),
                improvements=opt_dict.get("improvements", []),
                keywords=opt_dict.get("keywords", []),
                status=OptimizationStatus(opt_dict.get("status", "pending_payment")),
                created_at=opt_dict.get("created_at", datetime.utcnow()),
                completed_at=opt_dict.get("completed_at"),
                error_message=opt_dict.get("error_message")
            ))

        return OptimizationListResponse(
            optimizations=optimizations,
            total=len(optimizations),
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Failed to list optimizations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list optimizations: {str(e)}"
        ) from e


@router.post("/{optimization_id}/process", response_model=OptimizationDetailResponse)
async def process_optimization(
    optimization_id: str,
    current_user: dict = Depends(get_current_user)
) -> OptimizationDetailResponse:
    """
    Process an optimization (perform the actual analysis).

    This endpoint would typically be called after payment confirmation
    to start the actual resume optimization process.

    Args:
        optimization_id: Optimization ID
        current_user: Currently authenticated user

    Returns:
        OptimizationDetailResponse with processing results

    Raises:
        HTTPException: If processing fails
    """
    try:
        optimization_service = ExtendedScoreImprovementService()
        optimization = await optimization_service.get_optimization(
            optimization_id=optimization_id,
            user_id=current_user["id"]
        )

        if not optimization:
            raise HTTPException(
                status_code=404,
                detail="Optimization not found"
            )

        # Update status to processing
        await optimization_service.update_optimization_status(
            optimization_id=optimization_id,
            status=OptimizationStatus.PROCESSING
        )

        # Get resume and job description data
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(
            optimization["resume_id"]
        )

        if not resume_data:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        # Extract resume text
        raw_resume = resume_data.get("raw_resume", {})
        resume_text = raw_resume.get("content", "")

        # Get job description (simplified for now)
        job_description = "Sample job description"
        # TODO: Implement proper job description retrieval

        # Perform analysis using ScoreImprovementService
        analysis_result = await optimization_service.analyze_and_improve(
            resume_text=resume_text,
            job_description=job_description
        )

        # Update optimization with results
        results_data = {
            "match_score": analysis_result.get("original_score", 0),
            "strengths": analysis_result.get("analysis", {}).get("strengths", []),
            "improvements": analysis_result.get("analysis", {}).get("improvements", []),
            "keywords": analysis_result.get("analysis", {}).get("keywords", []),
            "embedding_similarity": analysis_result.get("analysis", {}).get("embedding_similarity"),
            "improved_resume": analysis_result.get("improved_resume"),
            "changes_made": analysis_result.get("changes_made", []),
            "expected_score": analysis_result.get("expected_score")
        }

        await optimization_service.update_optimization_status(
            optimization_id=optimization_id,
            status=OptimizationStatus.COMPLETED,
            results=results_data
        )

        # Get updated optimization
        updated_optimization = await optimization_service.get_optimization(
            optimization_id=optimization_id,
            user_id=current_user["id"]
        )

        logger.info(f"Optimization {optimization_id} processed successfully")

        return OptimizationDetailResponse(
            id=updated_optimization["optimization_id"],
            resume_id=updated_optimization["resume_id"],
            job_description_id=updated_optimization["job_description_id"],
            match_score=updated_optimization.get("match_score"),
            improvements=updated_optimization.get("improvements", []),
            keywords=updated_optimization.get("keywords", []),
            status=OptimizationStatus(updated_optimization["status"]),
            created_at=updated_optimization["created_at"],
            completed_at=updated_optimization.get("completed_at"),
            resume_text=resume_text,
            job_description_text=job_description,
            strengths=updated_optimization.get("strengths", []),
            embedding_similarity=updated_optimization.get("embedding_similarity"),
            improved_resume=updated_optimization.get("improved_resume"),
            changes_made=updated_optimization.get("changes_made", []),
            expected_score=updated_optimization.get("expected_score")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process optimization {optimization_id}: {str(e)}")

        # Update status to failed
        try:
            await optimization_service.update_optimization_status(
                optimization_id=optimization_id,
                status=OptimizationStatus.FAILED,
                results={"error_message": str(e)}
            )
        except:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process optimization: {str(e)}"
        ) from e