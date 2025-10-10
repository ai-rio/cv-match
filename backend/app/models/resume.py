"""
Pydantic models for resume upload and management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ResumeUploadRequest(BaseModel):
    """Request model for resume upload."""
    filename: str = Field(..., description="Original filename of the uploaded resume")
    file_content: bytes = Field(..., description="File content as bytes")


class ResumeUploadResponse(BaseModel):
    """Response model for resume upload."""
    id: str = Field(..., description="Resume ID")
    filename: str = Field(..., description="Original filename")
    extracted_text: Optional[str] = Field(None, description="Extracted text content from resume")
    content_type: str = Field(..., description="Content type of the extracted text")
    created_at: datetime = Field(..., description="Upload timestamp")


class ResumeResponse(BaseModel):
    """Response model for resume retrieval."""
    id: str = Field(..., description="Resume ID")
    filename: str = Field(..., description="Original filename")
    extracted_text: Optional[str] = Field(None, description="Extracted text content from resume")
    content_type: str = Field(..., description="Content type of the extracted text")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ResumeListResponse(BaseModel):
    """Response model for listing resumes."""
    resumes: list[ResumeResponse] = Field(..., description="List of resumes")
    total: int = Field(..., description="Total number of resumes")
    limit: int = Field(..., description="Number of resumes returned")
    offset: int = Field(..., description="Number of resumes skipped")