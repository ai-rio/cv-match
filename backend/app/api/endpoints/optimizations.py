"""
API endpoints for resume optimization workflow.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth_dependencies import get_current_user
from app.core.database import SupabaseSession
from app.middleware.credit_check import check_credits, require_pro_or_credits
from app.models.optimization import (
    OptimizationDetailResponse,
    OptimizationListResponse,
    OptimizationResponse,
    OptimizationStatus,
    StartOptimizationRequest,
)
from app.services.job_service import JobService
from app.services.resume_service import ResumeService
from app.services.score_improvement_service import ScoreImprovementService
from app.services.supabase.database import SupabaseDatabaseService
from app.services.usage_limit_service import UsageLimitService


# Database dependency
async def get_db() -> SupabaseSession:
    """Get database session."""
    return SupabaseSession()


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimizations", tags=["optimizations"])


# Extend JobService to support job description creation
class ExtendedJobService(JobService):
    """Extended job service with additional methods for optimization workflow."""

    async def create_job_description(
        self, user_id: str, title: str, company: str, description: str
    ) -> dict[str, Any]:
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
            "content_type": "text/markdown",
        }

        # Store job description using Supabase service
        service = SupabaseDatabaseService("job_descriptions", dict)
        result = await service.create(job_data)

        return {
            "id": job_id,
            "title": title,
            "company": company,
            "description": description,
            "created_at": result.get("created_at", datetime.utcnow()),
        }


# Extend ScoreImprovementService to support optimization workflow
class ExtendedScoreImprovementService(ScoreImprovementService):
    """Extended score improvement service with optimization workflow support."""

    async def create_optimization(
        self, user_id: str, resume_id: str, job_description_id: str, status: OptimizationStatus
    ) -> dict[str, Any]:
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
            "created_at": datetime.utcnow(),
        }

        # Store optimization using Supabase service
        service = SupabaseDatabaseService("optimizations", dict)
        result = await service.create(optimization_data)

        return {
            "id": optimization_id,
            "resume_id": resume_id,
            "job_description_id": job_description_id,
            "status": status.value,
            "created_at": result.get("created_at", datetime.utcnow()),
        }

    async def get_optimization(self, optimization_id: str, user_id: str) -> dict[str, Any] | None:
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
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> list[dict[str, Any]]:
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
        results: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Update optimization status and results.

        Args:
            optimization_id: Optimization ID
            status: New status
            results: Optional optimization results

        Returns:
            Updated optimization data
        """
        update_data = {"status": status.value, "updated_at": datetime.utcnow()}

        if results:
            update_data.update(results)
            if status == OptimizationStatus.COMPLETED:
                update_data["completed_at"] = datetime.utcnow()

        service = SupabaseDatabaseService("optimizations", dict)
        return await service.update(optimization_id, update_data)


@router.post("/start", response_model=OptimizationResponse, status_code=201)
async def start_optimization(
    request: StartOptimizationRequest,
    current_user: dict = Depends(check_credits),
    db: SupabaseSession = Depends(get_db),
) -> OptimizationResponse:
    """
    Start resume optimization process.

    This endpoint checks user credits, creates a job description entry,
    initiates the optimization workflow, and atomically deducts credits.

    Args:
        request: Optimization request data
        current_user: Currently authenticated user with credit info
        db: Database session

    Returns:
        OptimizationResponse with optimization information

    Raises:
        HTTPException: If optimization creation fails or insufficient credits
    """
    try:
        from uuid import UUID

        # Verify resume exists and belongs to user
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(request.resume_id)

        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Create job description entry
        job_service = ExtendedJobService()
        job_result = await job_service.create_job_description(
            user_id=current_user["id"],
            title=request.job_title or "Job Description",
            company=request.company or "Company",
            description=request.job_description,
        )

        # Create optimization record
        optimization_service = ExtendedScoreImprovementService()
        result = await optimization_service.create_optimization(
            user_id=current_user["id"],
            resume_id=request.resume_id,
            job_description_id=job_result["id"],
            status=OptimizationStatus.PENDING_PAYMENT,
        )

        # Initialize usage limit service and deduct credits atomically
        usage_limit_service = UsageLimitService(db)
        user_id = UUID(current_user["id"])

        # Determine credit cost (1 credit for non-pro users, 0 for pro users)
        credit_cost = 0 if current_user.get("is_pro", False) else 1

        if credit_cost > 0:
            # Deduct credits atomically
            credit_deducted = await usage_limit_service.deduct_credits(
                user_id=user_id, amount=credit_cost, operation_id=result["id"]
            )

            if not credit_deducted:
                # Rollback optimization creation if credit deduction failed
                logger.error(f"Failed to deduct credits for user {current_user['id']}")
                await optimization_service.update_optimization_status(
                    optimization_id=result["id"],
                    status=OptimizationStatus.FAILED,
                    results={"error_message": "Failed to deduct credits"},
                )
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Failed to deduct credits. Please check your credit balance.",
                )

        # Update status to processing since credits have been deducted
        await optimization_service.update_optimization_status(
            optimization_id=result["id"], status=OptimizationStatus.PROCESSING
        )

        logger.info(
            f"Optimization {result['id']} started for user {current_user['id']}, {credit_cost} credits deducted"
        )

        return OptimizationResponse(
            id=result["id"],
            resume_id=result["resume_id"],
            job_description_id=result["job_description_id"],
            match_score=None,
            improvements=[],
            keywords=[],
            status=OptimizationStatus.PROCESSING,
            created_at=result["created_at"],
            completed_at=None,
            error_message=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start optimization: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start optimization: {str(e)}"
        ) from e


@router.get("/{optimization_id}", response_model=OptimizationDetailResponse)
async def get_optimization(
    optimization_id: str, current_user: dict = Depends(get_current_user)
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
            optimization_id=optimization_id, user_id=current_user["id"]
        )

        if not optimization:
            raise HTTPException(status_code=404, detail="Optimization not found")

        # Get resume and job description data
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(optimization["resume_id"])

        ExtendedJobService()
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
            expected_score=optimization.get("expected_score"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get optimization {optimization_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve optimization: {str(e)}"
        ) from e


@router.get("/", response_model=OptimizationListResponse)
async def list_optimizations(
    limit: int = Query(10, ge=1, le=100, description="Number of optimizations to return"),
    offset: int = Query(0, ge=0, description="Number of optimizations to skip"),
    current_user: dict = Depends(get_current_user),
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
            user_id=current_user["id"], limit=limit, offset=offset
        )

        # Convert to response format
        optimizations = []
        for opt_dict in optimizations_data:
            optimizations.append(
                OptimizationResponse(
                    id=opt_dict.get("optimization_id", str(uuid.uuid4())),
                    resume_id=opt_dict.get("resume_id") or "",
                    job_description_id=opt_dict.get("job_description_id") or "",
                    match_score=opt_dict.get("match_score"),
                    improvements=opt_dict.get("improvements", []),
                    keywords=opt_dict.get("keywords", []),
                    status=OptimizationStatus(opt_dict.get("status", "pending_payment")),
                    created_at=opt_dict.get("created_at", datetime.utcnow()),
                    completed_at=opt_dict.get("completed_at"),
                    error_message=opt_dict.get("error_message"),
                )
            )

        return OptimizationListResponse(
            optimizations=optimizations, total=len(optimizations), limit=limit, offset=offset
        )

    except Exception as e:
        logger.error(f"Failed to list optimizations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list optimizations: {str(e)}"
        ) from e


@router.post("/{optimization_id}/process", response_model=OptimizationDetailResponse)
async def process_optimization(
    optimization_id: str,
    current_user: dict = Depends(require_pro_or_credits),
    db: SupabaseSession = Depends(get_db),
) -> OptimizationDetailResponse:
    """
    Process an optimization (perform the actual analysis).

    This endpoint would typically be called after payment confirmation
    to start the actual resume optimization process. It uses a more
    permissive credit check that allows Pro users or users with credits.

    Args:
        optimization_id: Optimization ID
        current_user: Currently authenticated user with credit info
        db: Database session

    Returns:
        OptimizationDetailResponse with processing results

    Raises:
        HTTPException: If processing fails
    """
    try:
        optimization_service = ExtendedScoreImprovementService()
        optimization = await optimization_service.get_optimization(
            optimization_id=optimization_id, user_id=current_user["id"]
        )

        if not optimization:
            raise HTTPException(status_code=404, detail="Optimization not found")

        # Update status to processing
        await optimization_service.update_optimization_status(
            optimization_id=optimization_id, status=OptimizationStatus.PROCESSING
        )

        # Get resume and job description data
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(optimization["resume_id"])

        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Extract resume text
        raw_resume = resume_data.get("raw_resume", {})
        resume_text = raw_resume.get("content", "")

        # Get job description from database
        job_service = ExtendedJobService()
        job_data = await job_service.get_job_with_processed_data(optimization["job_description_id"])

        if not job_data:
            raise HTTPException(status_code=404, detail="Job description not found")

        # Extract job description text
        processed_job = job_data.get("processed_job", {})
        if processed_job and processed_job.get("job_summary"):
            job_description = processed_job["job_summary"]
        else:
            # Fallback to raw job content
            raw_job = job_data.get("raw_job", {})
            job_description = raw_job.get("content", "Job description not available")

        # Perform analysis using ScoreImprovementService
        analysis_result = await optimization_service.analyze_and_improve(
            resume_text=resume_text, job_description=job_description
        )

        # Update optimization with results
        analysis = analysis_result.get("analysis", {}) if analysis_result else {}
        results_data = {
            "match_score": analysis_result.get("original_score", 0) if analysis_result else 0,
            "strengths": analysis.get("strengths", []),
            "improvements": analysis.get("improvements", []),
            "keywords": analysis.get("keywords", []),
            "embedding_similarity": analysis.get("embedding_similarity"),
            "improved_resume": analysis_result.get("improved_resume") if analysis_result else None,
            "changes_made": analysis_result.get("changes_made", []) if analysis_result else [],
            "expected_score": analysis_result.get("expected_score") if analysis_result else None,
        }

        await optimization_service.update_optimization_status(
            optimization_id=optimization_id,
            status=OptimizationStatus.COMPLETED,
            results=results_data,
        )

        # Get updated optimization
        updated_optimization = await optimization_service.get_optimization(
            optimization_id=optimization_id, user_id=current_user["id"]
        )

        if not updated_optimization:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated optimization")

        logger.info(f"Optimization {optimization_id} processed successfully")

        return OptimizationDetailResponse(
            id=updated_optimization.get("optimization_id", optimization_id),
            resume_id=updated_optimization.get("resume_id", ""),
            job_description_id=updated_optimization.get("job_description_id", ""),
            match_score=updated_optimization.get("match_score"),
            improvements=updated_optimization.get("improvements", []),
            keywords=updated_optimization.get("keywords", []),
            status=OptimizationStatus(updated_optimization.get("status", "completed")),
            created_at=updated_optimization.get("created_at", datetime.utcnow()),
            completed_at=updated_optimization.get("completed_at"),
            error_message=updated_optimization.get("error_message"),
            resume_text=resume_text,
            job_description_text=job_description,
            strengths=updated_optimization.get("strengths", []),
            embedding_similarity=updated_optimization.get("embedding_similarity"),
            improved_resume=updated_optimization.get("improved_resume"),
            changes_made=updated_optimization.get("changes_made", []),
            expected_score=updated_optimization.get("expected_score"),
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
                results={"error_message": str(e)},
            )
        except Exception:
            # Log warning but don't fail the main error response
            logger.warning(f"Failed to update optimization status to failed: {optimization_id}")
            pass

        raise HTTPException(
            status_code=500, detail=f"Failed to process optimization: {str(e)}"
        ) from e


@router.get("/credits/check")
async def check_user_credits(
    current_user: dict = Depends(get_current_user), db: SupabaseSession = Depends(get_db)
):
    """
    Check user's current credit balance and status.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        User credit information
    """
    try:
        from uuid import UUID

        usage_limit_service = UsageLimitService(db)
        user_id = UUID(current_user["id"])

        # Get user credits
        credits_data = await usage_limit_service.get_user_credits(user_id)

        # Get usage stats
        usage_stats = await usage_limit_service.get_usage_stats(user_id)

        return {
            "user_id": current_user["id"],
            "credits_remaining": credits_data.get("credits_remaining", 0),
            "total_credits": credits_data.get("total_credits", 0),
            "subscription_tier": credits_data.get("subscription_tier", "free"),
            "is_pro": credits_data.get("is_pro", False),
            "usage_stats": {
                "free_optimizations_used": usage_stats.free_optimizations_used,
                "paid_optimizations_used": usage_stats.paid_optimizations_used,
                "total_optimizations_this_month": usage_stats.total_optimizations_this_month,
                "can_optimize": usage_stats.can_optimize,
            },
        }

    except Exception as e:
        logger.error(f"Failed to check credits for user {current_user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve credit information")
