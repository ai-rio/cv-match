"""
Base API response models for consistent API responses.
"""

from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseAPIResponse[T](BaseModel):
    """Base API response model for consistent responses."""

    status: str = Field(..., description="Response status: 'success' or 'error'")
    data: T | None = Field(None, description="Response data payload")
    error: dict[str, Any] | None = Field(None, description="Error details if status is 'error'")
    timestamp: str | None = Field(None, description="Response timestamp")


class APIError(BaseModel):
    """Standard API error model."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Any | None = Field(None, description="Additional error details")
    field: str | None = Field(None, description="Field name if this is a validation error")
    timestamp: str = Field(..., description="Error timestamp")


class ValidationError(APIError):
    """Validation error model."""

    field: str = Field(..., description="Field name that failed validation")
    validation_type: str = Field(..., description="Type of validation error")


# Common response types
class SuccessResponse(BaseAPIResponse[T]):
    """Success response wrapper."""

    status: str = Field(default="success", description="Always 'success'")


class ErrorResponse(BaseAPIResponse[None]):
    """Error response wrapper."""

    status: str = Field(default="error", description="Always 'error'")
    data: None = Field(default=None, description="Always None for error responses")


# Pagination types
class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int | None = Field(1, ge=1, description="Page number (1-based)")
    limit: int | None = Field(10, ge=1, le=100, description="Items per page")
    offset: int | None = Field(None, ge=0, description="Number of items to skip")
    page_size: int | None = Field(None, ge=1, le=100, description="Alias for limit")


class PaginatedResult[T](BaseModel):
    """Paginated result wrapper."""

    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


# Search and filter types
class SearchParams(PaginationParams):
    """Search parameters with pagination."""

    query: str | None = Field(None, description="Search query")
    sort_by: str | None = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")
    filters: dict[str, Any] = Field(default_factory=dict, description="Additional filters")


class FilterOption(BaseModel):
    """Filter option for dropdowns etc."""

    value: str = Field(..., description="Option value")
    label: str = Field(..., description="Option label")
    count: int | None = Field(None, description="Number of items with this option")
