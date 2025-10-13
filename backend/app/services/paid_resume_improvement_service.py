"""
Paid resume improvement service for cv-match.

Handles credit verification, AI optimization, and DOCX generation for paid SaaS functionality.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.database import SupabaseSession
from app.services.usage_limit_service import UsageLimitError, UsageLimitService

logger = logging.getLogger(__name__)


class CreditVerificationError(Exception):
    """Raised when credit verification fails."""

    pass


class PaidResumeImprovementService:
    """Service for handling paid resume improvements with mandatory credit verification."""

    def __init__(self, db: SupabaseSession):
        self.db = db
        self.usage_limit_service = UsageLimitService(db)

    async def improve_resume(
        self,
        resume_id: UUID,
        job_id: UUID,
        user_id: UUID,
        cost_credits: int = 1,
    ) -> dict[str, Any]:
        """
        Improve a resume after verifying and deducting credits.

        This method:
        1. Verifies user has sufficient credits
        2. Deducts credits atomically
        3. Retrieves resume and job data
        4. Optimizes resume using AI
        5. Returns optimization results

        Args:
            resume_id: Resume UUID
            job_id: Job UUID
            user_id: User ID for credit verification and tracking
            cost_credits: Number of credits this operation costs

        Returns:
            Dict containing optimization results

        Raises:
            CreditVerificationError: If credit verification fails
            ValueError: If resume or job is not found
            UsageLimitError: If credit deduction fails
        """
        try:
            logger.info(
                f"Starting paid resume improvement - Resume: {resume_id}, Job: {job_id}, "
                f"User: {user_id}, Cost: {cost_credits} credits"
            )

            # Step 1: Check and deduct credits
            limit_check = await self.usage_limit_service.check_and_track_usage(
                user_id=user_id, optimization_type="paid", cost_credits=cost_credits
            )

            if not limit_check.can_optimize:
                raise CreditVerificationError(limit_check.reason or "Insufficient credits")

            # Step 2: Retrieve resume and job data
            resume_data, job_data = await self._retrieve_resume_and_job_data(resume_id, job_id)

            # Step 3: Optimize resume using AI (placeholder for now)
            optimization_result = await self._optimize_resume_with_ai(
                resume_data["content"], job_data["content"], str(user_id)
            )

            # Step 4: Prepare response
            result = await self._prepare_response(
                resume_id=resume_id,
                job_id=job_id,
                user_id=user_id,
                optimization_result=optimization_result,
                cost_credits=cost_credits,
            )

            logger.info(
                f"Paid resume improvement completed successfully - Resume: {resume_id}, "
                f"User: {user_id}, Credits deducted: {cost_credits}"
            )

            return result

        except (CreditVerificationError, ValueError, UsageLimitError) as e:
            logger.error(f"Paid resume improvement failed: {str(e)}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error in paid resume improvement: {str(e)}")
            raise CreditVerificationError(f"Erro inesperado na otimização: {str(e)}") from e

    async def _retrieve_resume_and_job_data(
        self, resume_id: UUID, job_id: UUID
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Retrieve resume and job data from database.

        Args:
            resume_id: Resume UUID
            job_id: Job UUID

        Returns:
            Tuple of (resume_data, job_data) dictionaries

        Raises:
            ValueError: If resume or job is not found
        """
        try:
            # Get resume data
            resume_result = (
                self.db.client.table("resumes").select("*").eq("id", str(resume_id)).execute()
            )
            if not resume_result.data:
                raise ValueError(f"Resume not found: {resume_id}")

            resume = resume_result.data[0]

            # Get job data
            job_result = self.db.client.table("jobs").select("*").eq("id", str(job_id)).execute()
            if not job_result.data:
                raise ValueError(f"Job not found: {job_id}")

            job = job_result.data[0]

            resume_data = {
                "id": resume["id"],
                "filename": resume.get("filename", "resume.txt"),
                "content": resume["content"],
            }

            job_data = {
                "id": job["id"],
                "content": job["content"],
            }

            return resume_data, job_data

        except Exception as e:
            logger.error(f"Failed to retrieve resume and job data: {str(e)}")
            raise ValueError(f"Failed to retrieve data: {str(e)}") from e

    async def _optimize_resume_with_ai(
        self, resume_text: str, job_description: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Optimize resume using AI service (placeholder implementation).

        Args:
            resume_text: Original resume text
            job_description: Job description
            user_id: Optional user ID

        Returns:
            Optimization result dictionary
        """
        # Placeholder for AI optimization - to be implemented with actual AI service
        return {
            "optimized_text": f"Optimized resume for {job_description[:50]}...",
            "match_percentage": 85,
            "suggestions": [
                "Add quantifiable achievements",
                "Include relevant keywords",
                "Improve formatting",
            ],
            "keywords": ["python", "fastapi", "postgresql", "docker"],
        }

    async def _prepare_response(
        self,
        resume_id: UUID,
        job_id: UUID,
        user_id: UUID,
        optimization_result: dict[str, Any],
        cost_credits: int,
    ) -> dict[str, Any]:
        """
        Prepare optimization response.

        Args:
            resume_id: Resume UUID
            job_id: Job UUID
            user_id: User ID
            optimization_result: AI optimization result
            cost_credits: Credits deducted for this operation

        Returns:
            Response dictionary with optimization results
        """
        response = {
            "optimization_id": str(resume_id) + "_" + str(job_id),
            "resume_id": str(resume_id),
            "job_id": str(job_id),
            "user_id": str(user_id),
            "optimized_text": optimization_result["optimized_text"],
            "match_percentage": optimization_result["match_percentage"],
            "suggestions": optimization_result["suggestions"],
            "keywords": optimization_result["keywords"],
            "credits_used": cost_credits,
            "ai_metadata": {
                "model_used": "placeholder-ai-model",
                "processed_at": datetime.now(UTC).isoformat(),
            },
        }

        return response
