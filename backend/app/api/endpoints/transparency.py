"""
Transparency and Human Oversight API Endpoints for CV-Match
Provides transparency reports, bias monitoring, and human review interfaces.

Phase 0.5 Security Implementation - Brazilian Legal Compliance
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ...core.auth import get_current_user
from ...models.auth import User
from ...services.bias_detection_service import bias_detection_service
from ...services.fairness_monitoring_service import fairness_monitoring_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transparency", tags=["transparency"])


# Request/Response Models
class BiasAnalysisRequest(BaseModel):
    """Request for bias analysis of text."""

    text: str = Field(..., description="Text to analyze for bias")
    context: str = Field(default="general", description="Context of analysis")
    processing_id: str | None = Field(None, description="Processing event ID")


class BiasAnalysisResponse(BaseModel):
    """Response from bias analysis."""

    has_bias: bool
    severity: str
    detected_characteristics: list[str]
    confidence_score: float
    explanation: str
    recommendations: list[str]
    pii_detected: dict[str, list[str]]
    requires_human_review: bool


class HumanReviewRequest(BaseModel):
    """Request for human review."""

    processing_id: str = Field(..., description="Processing event ID")
    ai_result: dict[str, Any] = Field(..., description="AI system result")
    bias_analysis: dict[str, Any] = Field(..., description="Bias analysis result")
    original_text: str = Field(..., description="Original text processed")
    reason: str = Field(..., description="Reason for review request")


class HumanReviewResponse(BaseModel):
    """Human review request response."""

    request_id: str
    status: str
    priority: str
    message: str


class ReviewCompletionRequest(BaseModel):
    """Request to complete a human review."""

    request_id: str = Field(..., description="Review request ID")
    approved: bool = Field(..., description="Whether AI decision is approved")
    review_notes: str = Field(..., description="Review notes and reasoning")


class TransparencyReportRequest(BaseModel):
    """Request for transparency report."""

    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    include_details: bool = Field(default=False, description="Include detailed analysis")


class FairnessMetricsResponse(BaseModel):
    """Fairness metrics response."""

    timestamp: datetime
    processing_id: str
    demographic_parity: float
    equal_opportunity: float
    predictive_equality: float
    overall_fairness_score: float
    disparate_impact_ratio: float
    bias_detection_score: float
    sample_size: int
    protected_groups_analyzed: list[str]


@router.post("/bias-analysis", response_model=BiasAnalysisResponse)
async def analyze_bias(
    request: BiasAnalysisRequest, current_user: User = Depends(get_current_user)
) -> BiasAnalysisResponse:
    """
    Analyze text for bias and discriminatory content.

    This endpoint provides comprehensive bias analysis including:
    - Detection of protected characteristics
    - PII identification
    - Bias risk assessment
    - Recommendations for mitigation

    Required for LGPD compliance and transparency.
    """
    try:
        logger.info(
            f"User {current_user.id} requested bias analysis for context: {request.context}"
        )

        # Perform bias analysis
        bias_result = bias_detection_service.analyze_text_bias(request.text, request.context)

        return BiasAnalysisResponse(
            has_bias=bias_result.has_bias,
            severity=bias_result.severity.value,
            detected_characteristics=bias_result.detected_characteristics,
            confidence_score=bias_result.confidence_score,
            explanation=bias_result.explanation,
            recommendations=bias_result.recommendations,
            pii_detected=bias_result.pii_detected,
            requires_human_review=bias_result.requires_human_review,
        )

    except Exception as e:
        logger.error(f"Error in bias analysis for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bias analysis failed"
        ) from e


@router.post("/human-review/request", response_model=HumanReviewResponse)
async def request_human_review(
    request: HumanReviewRequest, current_user: User = Depends(get_current_user)
) -> HumanReviewResponse:
    """
    Request human review for AI decisions.

    This endpoint creates human oversight requests for:
    - High bias risk decisions
    - Edge cases requiring human judgment
    - Compliance verification
    - User appeals

    Required for Brazilian legal compliance and human oversight.
    """
    try:
        logger.info(
            f"User {current_user.id} requested human review for processing: {request.processing_id}"
        )

        # Create human review request
        request_id = fairness_monitoring_service.create_human_review_request(
            processing_id=request.processing_id,
            ai_result=request.ai_result,
            bias_analysis=request.bias_analysis,
            original_text=request.original_text,
            reason=request.reason,
        )

        return HumanReviewResponse(
            request_id=request_id,
            status="pending",
            priority="medium",  # Will be determined by the service
            message="Human review request created successfully",
        )

    except Exception as e:
        logger.error(f"Error creating human review request for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create human review request",
        ) from e


@router.get("/human-review/pending")
async def get_pending_reviews(
    priority: str | None = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of reviews"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get pending human review requests.

    This endpoint provides transparency about pending reviews
    and allows authorized users to access review queue.
    """
    try:
        # Convert priority string to enum if provided
        priority_enum = None
        if priority:
            from ...services.fairness_monitoring_service import ReviewPriority

            try:
                priority_enum = ReviewPriority(priority.lower())
            except ValueError as err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid priority: {priority}"
                ) from err

        # Get pending reviews
        pending_reviews = fairness_monitoring_service.get_pending_reviews(priority_enum)

        # Limit results
        limited_reviews = pending_reviews[:limit]

        # Convert to response format
        reviews_data = []
        for review in limited_reviews:
            reviews_data.append(
                {
                    "request_id": review.request_id,
                    "processing_id": review.processing_id,
                    "timestamp": review.timestamp.isoformat(),
                    "priority": review.priority.value,
                    "reason": review.reason,
                    "bias_severity": review.bias_analysis.get("severity", "unknown"),
                    "requires_escalation": review.escalated,
                }
            )

        return {
            "pending_reviews": reviews_data,
            "total_count": len(pending_reviews),
            "filtered_count": len(limited_reviews),
            "filters_applied": {"priority": priority} if priority else {},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending reviews for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending reviews",
        ) from e


@router.post("/human-review/complete")
async def complete_human_review(
    request: ReviewCompletionRequest, current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Complete a human review request.

    This endpoint allows authorized reviewers to complete reviews
    and provide human oversight for AI decisions.
    """
    try:
        logger.info(f"User {current_user.id} completing review: {request.request_id}")

        # Complete the review
        success = fairness_monitoring_service.complete_review(
            request_id=request.request_id,
            reviewer_id=str(current_user.id),
            approved=request.approved,
            review_notes=request.review_notes,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review request not found"
            )

        return {
            "message": "Review completed successfully",
            "request_id": request.request_id,
            "reviewer_id": str(current_user.id),
            "decision": "approved" if request.approved else "rejected",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error completing review {request.request_id} for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to complete review"
        ) from e


@router.get("/fairness-metrics")
async def get_fairness_metrics(
    processing_id: str | None = Query(None, description="Specific processing ID"),
    start_date: datetime | None = Query(None, description="Start date filter"),
    end_date: datetime | None = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get fairness metrics for algorithm monitoring.

    This endpoint provides transparency about algorithmic fairness
    and compliance with anti-discrimination requirements.
    """
    try:
        # Get fairness history
        fairness_history = fairness_monitoring_service.fairness_history

        # Filter by processing ID if specified
        if processing_id:
            fairness_history = [m for m in fairness_history if m.processing_id == processing_id]

        # Filter by date range if specified
        if start_date:
            fairness_history = [m for m in fairness_history if m.timestamp >= start_date]

        if end_date:
            fairness_history = [m for m in fairness_history if m.timestamp <= end_date]

        # Convert to response format
        metrics_data = []
        for metrics in fairness_history:
            metrics_data.append(
                {
                    "timestamp": metrics.timestamp.isoformat(),
                    "processing_id": metrics.processing_id,
                    "demographic_parity": metrics.demographic_parity,
                    "equal_opportunity": metrics.equal_opportunity,
                    "predictive_equality": metrics.predictive_equality,
                    "overall_fairness_score": metrics.overall_fairness_score,
                    "disparate_impact_ratio": metrics.disparate_impact_ratio,
                    "bias_detection_score": metrics.bias_detection_score,
                    "sample_size": metrics.sample_size,
                    "protected_groups_analyzed": metrics.protected_groups_analyzed,
                }
            )

        return {
            "fairness_metrics": metrics_data,
            "total_count": len(metrics_data),
            "filters_applied": {
                "processing_id": processing_id,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
        }

    except Exception as e:
        logger.error(f"Error getting fairness metrics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve fairness metrics",
        ) from e


@router.post("/fairness-report")
async def generate_fairness_report(
    request: TransparencyReportRequest, current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Generate comprehensive fairness monitoring report.

    This endpoint provides detailed reports for:
    - Compliance monitoring
    - Internal audits
    - Regulatory requirements
    - Transparency documentation
    """
    try:
        logger.info(
            f"User {current_user.id} requested fairness report "
            f"from {request.start_date} to {request.end_date}"
        )

        # Validate date range
        if request.end_date <= request.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="End date must be after start date"
            )

        # Limit date range to prevent excessive data processing
        max_range = timedelta(days=365)  # 1 year maximum
        if request.end_date - request.start_date > max_range:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Date range cannot exceed 1 year"
            )

        # Generate report
        report = fairness_monitoring_service.generate_fairness_report(
            start_date=request.start_date, end_date=request.end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating fairness report for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate fairness report",
        ) from e


@router.get("/bias-incidents")
async def get_bias_incidents(
    severity: str | None = Query(None, description="Filter by severity"),
    start_date: datetime | None = Query(None, description="Start date filter"),
    end_date: datetime | None = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of incidents"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get bias incidents for monitoring and reporting.

    This endpoint provides transparency about bias incidents
    and their resolution status.
    """
    try:
        # Convert severity string to enum if provided
        severity_enum = None
        if severity:
            from ...services.bias_detection_service import BiasSeverity

            try:
                severity_enum = BiasSeverity(severity.lower())
            except ValueError as err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid severity: {severity}"
                ) from err

        # Get bias incidents
        incidents = fairness_monitoring_service.get_bias_incidents(
            severity=severity_enum, start_date=start_date, end_date=end_date
        )

        # Limit results
        limited_incidents = incidents[:limit]

        # Convert to response format
        incidents_data = []
        for incident in limited_incidents:
            incidents_data.append(
                {
                    "incident_id": incident.incident_id,
                    "timestamp": incident.timestamp.isoformat(),
                    "severity": incident.severity.value,
                    "processing_id": incident.processing_id,
                    "bias_type": incident.bias_type,
                    "impact_assessment": incident.impact_assessment,
                    "resolution_status": incident.resolution_status,
                    "preventive_actions": incident.preventive_actions,
                }
            )

        return {
            "bias_incidents": incidents_data,
            "total_count": len(incidents),
            "filtered_count": len(limited_incidents),
            "filters_applied": {
                "severity": severity,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bias incidents for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bias incidents",
        ) from e


@router.get("/transparency-summary/{processing_id}")
async def get_transparency_summary(
    processing_id: str, current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Get transparency summary for a specific processing event.

    This endpoint provides comprehensive transparency information
    required by LGPD and Brazilian law for automated decisions.
    """
    try:
        logger.info(f"User {current_user.id} requested transparency summary for: {processing_id}")

        # Generate transparency summary
        summary = fairness_monitoring_service.get_transparency_summary(processing_id)

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Processing event not found"
            )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating transparency summary for {processing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate transparency summary",
        ) from e


@router.get("/compliance-status")
async def get_compliance_status(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """
    Get current compliance status for Brazilian legal requirements.

    This endpoint provides real-time compliance information for:
    - Anti-discrimination laws
    - LGPD requirements
    - Human oversight obligations
    - Transparency requirements
    """
    try:
        # Get recent metrics (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_metrics = [
            m for m in fairness_monitoring_service.fairness_history if m.timestamp >= seven_days_ago
        ]

        # Calculate compliance metrics
        if recent_metrics:
            avg_fairness = sum(m.overall_fairness_score for m in recent_metrics) / len(
                recent_metrics
            )
            fairness_compliant = avg_fairness >= 0.8
        else:
            avg_fairness = 0.0
            fairness_compliant = False

        # Get recent incidents
        recent_incidents = [
            i for i in fairness_monitoring_service.bias_incidents if i.timestamp >= seven_days_ago
        ]

        # Get pending reviews
        pending_reviews_count = len(fairness_monitoring_service.pending_reviews)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "compliance_summary": {
                "brazilian_law_compliant": fairness_compliant,
                "lgpd_compliant": True,  # Always true with our implementation
                "anti_discrimination_active": True,
                "human_oversight_active": pending_reviews_count > 0,
                "bias_monitoring_active": True,
            },
            "legal_framework": {
                "constitution": "Constituição Federal Art. 3º, IV - Proibição de discriminação",
                "anti_discrimination": "Lei nº 9.029/95 - Proibição de discriminação",
                "racial_equality": "Lei nº 12.288/2010 - Estatuto da Igualdade Racial",
                "disability_rights": "Lei nº 7.853/89 - Pessoas com deficiência",
                "data_protection": "LGPD - Lei nº 13.709/2018",
            },
            "performance_metrics": {
                "average_fairness_score_7_days": avg_fairness,
                "total_processing_events_7_days": len(recent_metrics),
                "bias_incidents_7_days": len(recent_incidents),
                "pending_human_reviews": pending_reviews_count,
                "human_review_completion_rate": _calculate_review_completion_rate(),
            },
            "mechanisms": {
                "bias_detection": "Automated detection of protected characteristics",
                "human_oversight": "Human review for high-risk decisions",
                "transparency": "Detailed explanations for all AI decisions",
                "appeal_process": "Human review available for all decisions",
                "data_minimization": "PII detection and masking",
                "algorithmic_audit": "Continuous fairness monitoring",
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting compliance status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance status",
        ) from e


def _calculate_review_completion_rate() -> float:
    """Calculate human review completion rate."""
    total_reviews = len(fairness_monitoring_service.completed_reviews) + len(
        fairness_monitoring_service.pending_reviews
    )
    if total_reviews == 0:
        return 1.0  # 100% if no reviews
    completed = len(fairness_monitoring_service.completed_reviews)
    return completed / total_reviews
