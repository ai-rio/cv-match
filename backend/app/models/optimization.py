"""
Pydantic models for resume optimization workflow.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OptimizationStatus(str, Enum):
    """Enumeration for optimization status values."""

    PENDING_PAYMENT = "pending_payment"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StartOptimizationRequest(BaseModel):
    """Request model for starting resume optimization."""

    resume_id: str = Field(..., description="ID of the resume to optimize")
    job_description: str = Field(..., description="Job description text")
    job_title: str | None = Field(None, description="Job title")
    company: str | None = Field(None, description="Company name")


class OptimizationResponse(BaseModel):
    """Response model for optimization results."""

    id: str = Field(..., description="Optimization ID")
    resume_id: str = Field(..., description="Associated resume ID")
    job_description_id: str = Field(..., description="Associated job description ID")
    match_score: int | None = Field(None, description="Match score (0-100)")
    improvements: list[str] = Field(
        default_factory=list, description="List of improvement suggestions"
    )
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords")
    status: OptimizationStatus = Field(..., description="Current optimization status")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    error_message: str | None = Field(None, description="Error message if failed")


class OptimizationDetailResponse(OptimizationResponse):
    """Detailed response model including full analysis."""

    resume_text: str | None = Field(None, description="Original resume text")
    job_description_text: str | None = Field(None, description="Job description text")
    strengths: list[str] = Field(default_factory=list, description="Resume strengths")
    embedding_similarity: float | None = Field(None, description="Embedding-based similarity score")
    improved_resume: str | None = Field(None, description="Improved resume text")
    changes_made: list[str] = Field(default_factory=list, description="List of changes made")
    expected_score: str | None = Field(None, description="Expected score after improvements")


class OptimizationListResponse(BaseModel):
    """Response model for listing optimizations."""

    optimizations: list[OptimizationResponse] = Field(..., description="List of optimizations")
    total: int = Field(..., description="Total number of optimizations")
    limit: int = Field(..., description="Number of optimizations returned")
    offset: int = Field(..., description="Number of optimizations skipped")


class JobDescriptionResponse(BaseModel):
    """Response model for job description."""

    id: str = Field(..., description="Job description ID")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Job description text")
    created_at: datetime = Field(..., description="Creation timestamp")
