import logging
import uuid
from typing import Any

from app.services.supabase.database import SupabaseDatabaseService

# TODO: These will need to be created in a later phase
# from app.agent import AgentManager
# from app.prompt import prompt_factory
# from app.schemas.json import json_schema_factory
# from app.schemas.pydantic import StructuredJobModel

# TODO: Create JobNotFoundError when exceptions module is ready
# from .exceptions import JobNotFoundError

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self):
        # Use cv-match's Supabase pattern
        pass

        # TODO: Initialize these when AI Integration is complete
        # self.json_agent_manager = AgentManager()

    async def create_and_store_job(self, job_data: dict) -> list[str]:
        """
        Stores job data in the database and returns a list of job IDs.
        """
        resume_id = str(job_data.get("resume_id"))

        if not await self._is_resume_available(resume_id):
            raise AssertionError(f"resume corresponding to resume_id: {resume_id} not found")

        job_ids = []
        for job_description in job_data.get("job_descriptions", []):
            job_id = str(uuid.uuid4())

            job_data_entry = {
                "job_id": job_id,
                "resume_id": str(resume_id),
                "content": job_description,
                "content_type": "text/markdown",
            }

            # Insert job using cv-match's Supabase service
            service = SupabaseDatabaseService("jobs", dict)
            await service.create(job_data_entry)

            await self._extract_and_store_structured_job(
                job_id=job_id, job_description_text=job_description
            )
            logger.info(f"Job ID: {job_id}")
            job_ids.append(job_id)

        return job_ids

    async def _is_resume_available(self, resume_id: str) -> bool:
        """
        Checks if a resume exists in the database.
        """
        service = SupabaseDatabaseService("resumes", dict)
        resume = await service.get(resume_id)
        return resume is not None

    async def _extract_and_store_structured_job(self, job_id, job_description_text: str):
        """
        extract and store structured job data in the database
        """
        structured_job = await self._extract_structured_json(job_description_text)
        if not structured_job:
            logger.info("Structured job extraction failed.")
            return None

        processed_job_data = {
            "job_id": job_id,
            "job_title": structured_job.get("job_title"),
            "company_profile": structured_job.get("company_profile")
            if structured_job.get("company_profile")
            else None,
            "location": structured_job.get("location") if structured_job.get("location") else None,
            "date_posted": structured_job.get("date_posted"),
            "employment_type": structured_job.get("employment_type"),
            "job_summary": structured_job.get("job_summary"),
            "key_responsibilities": {
                "key_responsibilities": structured_job.get("key_responsibilities", [])
            }
            if structured_job.get("key_responsibilities")
            else None,
            "qualifications": structured_job.get("qualifications", [])
            if structured_job.get("qualifications")
            else None,
            "compensation_and_benfits": structured_job.get("compensation_and_benfits", [])
            if structured_job.get("compensation_and_benfits")
            else None,
            "application_info": structured_job.get("application_info", [])
            if structured_job.get("application_info")
            else None,
            "extracted_keywords": {
                "extracted_keywords": structured_job.get("extracted_keywords", [])
            }
            if structured_job.get("extracted_keywords")
            else None,
        }

        # Insert processed job using cv-match's Supabase service
        processed_service = SupabaseDatabaseService("processed_jobs", dict)
        await processed_service.create(processed_job_data)

        return job_id

    async def _extract_structured_json(self, job_description_text: str) -> dict[str, Any] | None:
        """
        Uses the AgentManager+JSONWrapper to ask the LLM to
        return the data in exact JSON schema we need.
        """
        # TODO: Implement when AI Integration is complete
        logger.info("Structured JSON extraction not yet implemented")
        return {
            "job_title": "Sample Job",
            "company_profile": "Sample Company",
            "location": "Remote",
            "date_posted": "2024-01-01",
            "employment_type": "Full-time",
            "job_summary": job_description_text[:200] + "...",
            "key_responsibilities": ["Responsibility 1", "Responsibility 2"],
            "qualifications": ["Qualification 1", "Qualification 2"],
            "compensation_and_benfits": ["Competitive salary", "Benefits"],
            "application_info": ["Apply via email"],
            "extracted_keywords": ["keyword1", "keyword2"],
        }

    async def get_job_with_processed_data(self, job_id: str) -> dict | None:
        """
        Fetches both job and processed job data from the database and combines them.

        Args:
            job_id: The ID of the job to retrieve

        Returns:
            Combined data from both job and processed_job models

        Raises:
            JobNotFoundError: If the job is not found
        """
        # Fetch job data using cv-match's Supabase service
        service = SupabaseDatabaseService("jobs", dict)
        job = await service.get(job_id)

        if not job:
            # TODO: Create and raise JobNotFoundError
            raise ValueError(f"Job with ID {job_id} not found")

        combined_data = {
            "job_id": job.get("job_id") or job_id,
            "raw_job": {
                "id": job.get("id"),
                "resume_id": job.get("resume_id"),
                "content": job.get("content"),
                "created_at": job.get("created_at"),
            },
            "processed_job": None,
        }

        # TODO: Fetch processed job data when database structure is ready
        # processed_service = SupabaseDatabaseService("processed_jobs", dict)
        # processed_job = await processed_service.get(job_id)

        return combined_data
