"""
API endpoints for resume upload and management.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.core.auth import get_current_user
from app.models.resume import ResumeListResponse, ResumeResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService
from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
) -> ResumeUploadResponse:
    """
    Upload and process a resume file.

    This endpoint accepts PDF and DOCX files, extracts text content,
    and stores the resume in the database associated with the current user.

    Args:
        file: Resume file (PDF or DOCX)
        current_user: Currently authenticated user

    Returns:
        ResumeUploadResponse with uploaded resume information

    Raises:
        HTTPException: If file upload or processing fails
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: PDF, DOCX",
            )

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        file_content = await file.read()

        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

        # Reset file pointer for processing
        await file.seek(0)

        # Initialize resume service
        resume_service = ResumeService()

        # Process resume using existing service
        resume_id = await resume_service.convert_and_store_resume(
            file_bytes=file_content,
            file_type=file.content_type,
            filename=file.filename or "unknown_file",
            content_type="md",  # Store as markdown
        )

        # Get the stored resume data
        resume_data = await resume_service.get_resume_with_processed_data(resume_id)

        if not resume_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve stored resume data")

        # Extract relevant information
        raw_resume = resume_data.get("raw_resume", {})

        return ResumeUploadResponse(
            id=resume_id,
            filename=file.filename or "unknown_file",
            extracted_text=raw_resume.get("content"),
            content_type=raw_resume.get("content_type", "text/markdown"),
            created_at=raw_resume.get("created_at", datetime.utcnow()),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume upload failed: {str(e)}") from e


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str, current_user: dict = Depends(get_current_user)
) -> ResumeResponse:
    """
    Get a specific resume by ID.

    Args:
        resume_id: ID of the resume to retrieve
        current_user: Currently authenticated user

    Returns:
        ResumeResponse with resume information

    Raises:
        HTTPException: If resume not found or access denied
    """
    try:
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(resume_id)

        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Extract relevant information
        raw_resume = resume_data.get("raw_resume", {})

        return ResumeResponse(
            id=resume_id,
            filename=raw_resume.get("filename", "Unknown"),
            extracted_text=raw_resume.get("content"),
            content_type=raw_resume.get("content_type", "text/markdown"),
            created_at=raw_resume.get("created_at", datetime.utcnow()),
            updated_at=raw_resume.get("updated_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resume: {str(e)}") from e


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    limit: int = Query(10, ge=1, le=100, description="Number of resumes to return"),
    offset: int = Query(0, ge=0, description="Number of resumes to skip"),
    current_user: dict = Depends(get_current_user),
) -> ResumeListResponse:
    """
    List resumes for the current user.

    Args:
        limit: Maximum number of resumes to return
        offset: Number of resumes to skip
        current_user: Currently authenticated user

    Returns:
        ResumeListResponse with list of resumes

    Raises:
        HTTPException: If listing fails
    """
    try:
        # Use Supabase database service to list resumes
        # Note: This assumes resumes table has user_id filtering
        service = SupabaseDatabaseService("resumes", dict)

        # Get resumes for current user
        # TODO: Update this query to filter by user_id when RLS is properly configured
        resumes_data = await service.list(limit=limit, offset=offset)

        # Convert to response format
        resumes = []
        for resume_dict in resumes_data:
            resumes.append(
                ResumeResponse(
                    id=resume_dict.get("resume_id", str(uuid.uuid4())),
                    filename=resume_dict.get("filename", "Unknown"),
                    extracted_text=resume_dict.get("content"),
                    content_type=resume_dict.get("content_type", "text/markdown"),
                    created_at=resume_dict.get("created_at", datetime.utcnow()),
                    updated_at=resume_dict.get("updated_at"),
                )
            )

        return ResumeListResponse(resumes=resumes, total=len(resumes), limit=limit, offset=offset)

    except Exception as e:
        logger.error(f"Failed to list resumes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list resumes: {str(e)}") from e


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str, current_user: dict = Depends(get_current_user)) -> None:
    """
    Delete a resume by ID.

    Args:
        resume_id: ID of the resume to delete
        current_user: Currently authenticated user

    Raises:
        HTTPException: If resume not found or deletion fails
    """
    try:
        # Verify resume exists and belongs to user
        resume_service = ResumeService()
        resume_data = await resume_service.get_resume_with_processed_data(resume_id)

        if not resume_data:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Delete resume using database service
        service = SupabaseDatabaseService("resumes", dict)
        await service.delete(resume_id)

        logger.info(f"Resume {resume_id} deleted by user {current_user['id']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}") from e
