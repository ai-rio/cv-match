"""
API endpoints for resume upload and management.
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.core.auth_dependencies import get_current_user
from app.models.resume import ResumeListResponse, ResumeResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService
from app.services.supabase.database import SupabaseDatabaseService
from app.utils.file_security import FileSecurityConfig, validate_file_security
from app.utils.validation import sanitize_filename, validate_string

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...), current_user: dict = Depends(get_current_user)
) -> ResumeUploadResponse:
    """
    Upload and process a resume file with comprehensive security validation.

    This endpoint accepts PDF and DOCX files, performs security validation,
    extracts text content, and stores the resume in the database associated
    with the current user.

    Security features:
    - File type and content validation
    - Malware scanning
    - Injection attack prevention
    - File size limits
    - Filename sanitization

    Args:
        file: Resume file (PDF or DOCX)
        current_user: Currently authenticated user

    Returns:
        ResumeUploadResponse with uploaded resume information

    Raises:
        HTTPException: If file upload or processing fails
    """
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)
        filename_validation = validate_string(safe_filename, input_type="general", max_length=255)

        if not filename_validation.is_valid:
            raise HTTPException(
                status_code=400, detail=f"Invalid filename: {'; '.join(filename_validation.errors)}"
            )

        # Read file content
        file_content = await file.read()

        # Comprehensive file security validation
        file_security_config = FileSecurityConfig(
            max_file_size=10 * 1024 * 1024,  # 10MB
            scan_for_malware=True,
            validate_content_signature=True,
            check_for_embedded_scripts=True,
        )

        security_result = validate_file_security(
            file_content=file_content,
            filename=filename_validation.sanitized_input,
            content_type=file.content_type,
            config=file_security_config,
        )

        if not security_result.is_safe:
            logger.error(
                f"File security validation failed for user {current_user['id']}: "
                f"filename={filename_validation.sanitized_input}, "
                f"errors={security_result.errors}, "
                f"blocked_patterns={security_result.blocked_patterns}"
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File security validation failed",
                    "details": security_result.errors,
                    "warnings": security_result.warnings,
                    "blocked_patterns": security_result.blocked_patterns,
                },
            )

        # Log successful security validation
        logger.info(
            f"File security validation passed for user {current_user['id']}: "
            f"filename={filename_validation.sanitized_input}, "
            f"size={len(file_content)}, "
            f"checksum={security_result.checksum}"
        )

        # Validate declared content type matches detected type
        if file.content_type != security_result.file_info.get("detected_content_type"):
            logger.warning(
                f"Content type mismatch for user {current_user['id']}: "
                f"declared={file.content_type}, "
                f"detected={security_result.file_info.get('detected_content_type')}"
            )

        # Reset file pointer for processing
        await file.seek(0)

        # Initialize resume service
        resume_service = ResumeService()

        # Process resume using existing service with user ownership
        resume_id = await resume_service.convert_and_store_resume(
            file_bytes=file_content,
            file_type=file.content_type,
            filename=filename_validation.sanitized_input,  # Use sanitized filename
            content_type="md",  # Store as markdown
            user_id=current_user["id"],  # CRITICAL: Associate with current user
        )

        # Get the stored resume data
        resume_data = await resume_service.get_resume_with_processed_data(resume_id)

        if not resume_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve stored resume data")

        # Extract relevant information
        raw_resume = resume_data.get("raw_resume", {})

        return ResumeUploadResponse(
            id=resume_id,
            filename=filename_validation.sanitized_input,
            extracted_text=raw_resume.get("content"),
            content_type=raw_resume.get("content_type", "text/markdown"),
            user_id=current_user["id"],  # Include user ownership in response
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

        # CRITICAL SECURITY: Verify user ownership
        resume_user_id = raw_resume.get("user_id")
        if not resume_user_id or resume_user_id != current_user["id"]:
            logger.warning(
                f"User {current_user['id']} attempted to access resume {resume_id} owned by {resume_user_id}"
            )
            raise HTTPException(status_code=403, detail="Access denied: Resume not found")

        return ResumeResponse(
            id=resume_id,
            filename=raw_resume.get("filename", "Unknown"),
            extracted_text=raw_resume.get("content"),
            content_type=raw_resume.get("content_type", "text/markdown"),
            user_id=current_user["id"],  # Include user ownership in response
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
        # Use Supabase database service to list resumes for current user only
        service = SupabaseDatabaseService("resumes", dict)

        # CRITICAL SECURITY: Filter by user_id to ensure users only see their own resumes
        # The RLS policies will enforce this at database level, but we also filter here
        filters = {"user_id": current_user["id"]}
        try:
            resumes_data = await service.list(limit=limit, offset=offset, filters=filters)
        except Exception:
            # Handle the case where model_class is dict (won't work with model_class(**item))
            # For now, use raw Supabase client
            query = service.supabase.table("resumes").select("*").eq("user_id", current_user["id"])
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            response = query.execute()
            resumes_data = response.data

        # Convert to response format
        resumes = []
        for resume_dict in resumes_data:
            # Double-check user ownership (defense in depth)
            if resume_dict.get("user_id") == current_user["id"]:
                resumes.append(
                    ResumeResponse(
                        id=resume_dict.get("resume_id", str(uuid.uuid4())),
                        filename=resume_dict.get("filename", "Unknown"),
                        extracted_text=resume_dict.get("content"),
                        content_type=resume_dict.get("content_type", "text/markdown"),
                        user_id=current_user["id"],  # Include user ownership in response
                        created_at=resume_dict.get("created_at", datetime.utcnow()),
                        updated_at=resume_dict.get("updated_at"),
                    )
                )
            else:
                # Log potential security issue if RLS policies are bypassed
                logger.error(
                    f"SECURITY VIOLATION: User {current_user['id']} received resume {resume_dict.get('resume_id')} owned by {resume_dict.get('user_id')}"
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

        # CRITICAL SECURITY: Verify user ownership before deletion
        raw_resume = resume_data.get("raw_resume", {})
        resume_user_id = raw_resume.get("user_id")
        if not resume_user_id or resume_user_id != current_user["id"]:
            logger.warning(
                f"User {current_user['id']} attempted to delete resume {resume_id} owned by {resume_user_id}"
            )
            raise HTTPException(status_code=403, detail="Access denied: Resume not found")

        # Delete resume using database service (by resume_id field)
        service = SupabaseDatabaseService("resumes", dict)
        try:
            # Delete by resume_id field, not id
            response = (
                service.supabase.table("resumes").delete().eq("resume_id", resume_id).execute()
            )
            if not response.data:
                raise HTTPException(status_code=404, detail="Resume not found")
        except Exception as e:
            logger.error(f"Failed to delete resume {resume_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}") from e

        logger.info(f"Resume {resume_id} deleted by user {current_user['id']}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}") from e
