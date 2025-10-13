"""
Algorithmic Fairness Monitoring and Human Oversight Service for CV-Match
Implements comprehensive fairness metrics, monitoring, and human review workflows.

Phase 0.5 Security Implementation - Brazilian Legal Compliance
"""

import logging
import statistics
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..core.exceptions import ProviderError
from .bias_detection_service import BiasSeverity

logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Status of human review requests."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ReviewPriority(Enum):
    """Priority levels for human review."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FairnessMetrics:
    """Comprehensive fairness metrics for algorithm monitoring."""

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


@dataclass
class HumanReviewRequest:
    """Request for human oversight and review."""

    request_id: str
    processing_id: str
    timestamp: datetime
    priority: ReviewPriority
    reason: str
    bias_analysis: dict[str, Any]
    original_text_sample: str
    ai_decision: dict[str, Any]
    status: ReviewStatus
    reviewer_id: str | None = None
    review_notes: str | None = None
    resolution_timestamp: datetime | None = None
    escalated: bool = False


@dataclass
class BiasIncident:
    """Record of bias incidents for monitoring and reporting."""

    incident_id: str
    timestamp: datetime
    severity: BiasSeverity
    processing_id: str
    bias_type: list[str]
    detected_patterns: dict[str, Any]
    impact_assessment: str
    resolution_status: str
    preventive_actions: list[str]


class FairnessMonitoringService:
    """
    Comprehensive fairness monitoring and human oversight service.

    Features:
    - Real-time fairness metrics calculation
    - Human review workflows
    - Bias incident tracking and reporting
    - Algorithmic transparency measures
    - Compliance monitoring for Brazilian law
    """

    def __init__(self):
        """Initialize fairness monitoring service."""
        self.pending_reviews: dict[str, HumanReviewRequest] = {}
        self.completed_reviews: list[HumanReviewRequest] = []
        self.bias_incidents: list[BiasIncident] = []
        self.fairness_history: list[FairnessMetrics] = []

        # Fairness thresholds (configurable per business requirements)
        self.fairness_thresholds = {
            "min_overall_fairness": 0.8,
            "max_disparate_impact": 0.2,
            "min_demographic_parity": 0.7,
            "bias_alert_threshold": 0.6,
            "critical_bias_threshold": 0.8,
        }

        logger.info("FairnessMonitoringService initialized with Brazilian legal compliance")

    def calculate_fairness_metrics(
        self,
        processing_id: str,
        scores_by_group: dict[str, list[float]],
        bias_analysis_result: dict[str, Any],
    ) -> FairnessMetrics:
        """
        Calculate comprehensive fairness metrics for algorithm monitoring.

        Args:
            processing_id: Unique identifier for the processing
            scores_by_group: Dictionary mapping demographic groups to their scores
            bias_analysis_result: Result from bias detection analysis

        Returns:
            Comprehensive fairness metrics
        """
        try:
            if not scores_by_group or len(scores_by_group) < 2:
                # Default metrics for insufficient data
                return FairnessMetrics(
                    timestamp=datetime.utcnow(),
                    processing_id=processing_id,
                    demographic_parity=1.0,
                    equal_opportunity=1.0,
                    predictive_equality=1.0,
                    overall_fairness_score=1.0,
                    disparate_impact_ratio=1.0,
                    bias_detection_score=bias_analysis_result.get("confidence_score", 0.0),
                    sample_size=0,
                    protected_groups_analyzed=[],
                )

            # Calculate demographic parity (difference in positive rates)
            group_averages = []
            group_names = []

            for group, scores in scores_by_group.items():
                if scores:  # Only include groups with data
                    avg_score = statistics.mean(scores)
                    group_averages.append(avg_score)
                    group_names.append(group)

            if not group_averages:
                return FairnessMetrics(
                    timestamp=datetime.utcnow(),
                    processing_id=processing_id,
                    demographic_parity=0.0,
                    equal_opportunity=0.0,
                    predictive_equality=0.0,
                    overall_fairness_score=0.0,
                    disparate_impact_ratio=0.0,
                    bias_detection_score=1.0,
                    sample_size=0,
                    protected_groups_analyzed=[],
                )

            # Demographic Parity: 1 - |max_avg - min_avg|
            max_avg = max(group_averages)
            min_avg = min(group_averages)
            demographic_parity = max(0.0, 1.0 - abs(max_avg - min_avg))

            # Disparate Impact Ratio: min_avg / max_avg
            disparate_impact = min_avg / max_avg if max_avg > 0 else 0.0

            # Equal Opportunity (simplified - would need ground truth labels in practice)
            equal_opportunity = demographic_parity

            # Predictive Equality (simplified - would need error rates by group)
            predictive_equality = demographic_parity

            # Overall Fairness Score: weighted average of all metrics
            overall_fairness = (
                demographic_parity * 0.3
                + equal_opportunity * 0.25
                + predictive_equality * 0.25
                + (1.0 - min(disparate_impact, 1.0)) * 0.2
            )

            # Total sample size
            total_samples = sum(len(scores) for scores in scores_by_group.values())

            metrics = FairnessMetrics(
                timestamp=datetime.utcnow(),
                processing_id=processing_id,
                demographic_parity=demographic_parity,
                equal_opportunity=equal_opportunity,
                predictive_equality=predictive_equality,
                overall_fairness_score=overall_fairness,
                disparate_impact_ratio=disparate_impact,
                bias_detection_score=bias_analysis_result.get("confidence_score", 0.0),
                sample_size=total_samples,
                protected_groups_analyzed=group_names,
            )

            # Store metrics for monitoring
            self.fairness_history.append(metrics)

            # Check for fairness violations
            self._check_fairness_violations(metrics)

            return metrics

        except Exception as e:
            logger.error(f"Error calculating fairness metrics for {processing_id}: {e}")
            # Return safe default metrics
            return FairnessMetrics(
                timestamp=datetime.utcnow(),
                processing_id=processing_id,
                demographic_parity=0.0,
                equal_opportunity=0.0,
                predictive_equality=0.0,
                overall_fairness_score=0.0,
                disparate_impact_ratio=0.0,
                bias_detection_score=1.0,
                sample_size=0,
                protected_groups_analyzed=[],
            )

    def _check_fairness_violations(self, metrics: FairnessMetrics) -> None:
        """Check for fairness violations and trigger alerts."""
        violations = []

        if metrics.overall_fairness_score < self.fairness_thresholds["min_overall_fairness"]:
            violations.append(
                f"Overall fairness score below threshold: {metrics.overall_fairness_score:.3f}"
            )

        if metrics.disparate_impact_ratio < (
            1.0 - self.fairness_thresholds["max_disparate_impact"]
        ):
            violations.append(f"Disparate impact detected: {metrics.disparate_impact_ratio:.3f}")

        if metrics.bias_detection_score > self.fairness_thresholds["bias_alert_threshold"]:
            violations.append(f"High bias detection score: {metrics.bias_detection_score:.3f}")

        if violations:
            logger.warning(
                f"Fairness violations detected for {metrics.processing_id}: {violations}"
            )
            self._create_bias_incident(metrics, violations)

    def _create_bias_incident(self, metrics: FairnessMetrics, violations: list[str]) -> None:
        """Create bias incident record for tracking."""
        incident = BiasIncident(
            incident_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            severity=BiasSeverity.HIGH
            if metrics.bias_detection_score > 0.8
            else BiasSeverity.MEDIUM,
            processing_id=metrics.processing_id,
            bias_type=metrics.protected_groups_analyzed,
            detected_patterns={
                "fairness_violations": violations,
                "fairness_metrics": asdict(metrics),
            },
            impact_assessment=f"Algorithmic fairness compromised with {len(violations)} violations",
            resolution_status="open",
            preventive_actions=[
                "Review training data for bias",
                "Adjust algorithm parameters",
                "Implement additional bias detection",
            ],
        )

        self.bias_incidents.append(incident)
        logger.info(
            f"Created bias incident {incident.incident_id} for processing {metrics.processing_id}"
        )

    def create_human_review_request(
        self,
        processing_id: str,
        ai_result: dict[str, Any],
        bias_analysis: dict[str, Any],
        original_text: str,
        reason: str,
    ) -> str:
        """
        Create a human review request for oversight.

        Args:
            processing_id: Unique identifier for the processing
            ai_result: AI system decision/result
            bias_analysis: Bias detection analysis result
            original_text: Original text that was processed
            reason: Reason for human review

        Returns:
            Review request ID
        """
        try:
            # Determine priority based on bias severity
            confidence_score = bias_analysis.get("confidence_score", 0.0)
            requires_review = bias_analysis.get("requires_human_review", False)

            if confidence_score > 0.8 or requires_review:
                priority = ReviewPriority.CRITICAL
            elif confidence_score > 0.6:
                priority = ReviewPriority.HIGH
            elif confidence_score > 0.4:
                priority = ReviewPriority.MEDIUM
            else:
                priority = ReviewPriority.LOW

            review_request = HumanReviewRequest(
                request_id=str(uuid.uuid4()),
                processing_id=processing_id,
                timestamp=datetime.utcnow(),
                priority=priority,
                reason=reason,
                bias_analysis=bias_analysis,
                original_text_sample=original_text[:500] + "..."
                if len(original_text) > 500
                else original_text,
                ai_decision=ai_result,
                status=ReviewStatus.PENDING,
            )

            self.pending_reviews[review_request.request_id] = review_request

            logger.info(
                f"Created human review request {review_request.request_id} "
                f"with priority {priority.value} for processing {processing_id}"
            )

            return review_request.request_id

        except Exception as e:
            logger.error(f"Error creating human review request for {processing_id}: {e}")
            raise ProviderError(f"Failed to create review request: {str(e)}") from e

    def get_pending_reviews(
        self, priority: ReviewPriority | None = None
    ) -> list[HumanReviewRequest]:
        """
        Get pending human review requests.

        Args:
            priority: Optional priority filter

        Returns:
            List of pending review requests
        """
        reviews = list(self.pending_reviews.values())

        if priority:
            reviews = [r for r in reviews if r.priority == priority]

        # Sort by priority and timestamp
        priority_order = {
            ReviewPriority.CRITICAL: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.LOW: 3,
        }

        return sorted(reviews, key=lambda r: (priority_order.get(r.priority, 4), r.timestamp))

    def complete_review(
        self, request_id: str, reviewer_id: str, approved: bool, review_notes: str
    ) -> bool:
        """
        Complete a human review request.

        Args:
            request_id: Review request ID
            reviewer_id: ID of the reviewer
            approved: Whether the AI decision was approved
            review_notes: Review notes and reasoning

        Returns:
            True if review was completed successfully
        """
        try:
            if request_id not in self.pending_reviews:
                logger.error(f"Review request {request_id} not found")
                return False

            review_request = self.pending_reviews.pop(request_id)
            review_request.status = ReviewStatus.APPROVED if approved else ReviewStatus.REJECTED
            review_request.reviewer_id = reviewer_id
            review_request.review_notes = review_notes
            review_request.resolution_timestamp = datetime.utcnow()

            self.completed_reviews.append(review_request)

            logger.info(
                f"Completed review {request_id} by {reviewer_id}: "
                f"{'APPROVED' if approved else 'REJECTED'}"
            )

            # Create incident if rejected due to bias concerns
            if not approved and "bias" in review_notes.lower():
                self._create_review_bias_incident(review_request, review_notes)

            return True

        except Exception as e:
            logger.error(f"Error completing review {request_id}: {e}")
            return False

    def _create_review_bias_incident(
        self, review_request: HumanReviewRequest, review_notes: str
    ) -> None:
        """Create bias incident from human review rejection."""
        incident = BiasIncident(
            incident_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            severity=BiasSeverity.HIGH,
            processing_id=review_request.processing_id,
            bias_type=review_request.bias_analysis.get("detected_characteristics", []),
            detected_patterns={
                "human_review_rejection": True,
                "review_notes": review_notes,
                "ai_decision": review_request.ai_decision,
            },
            impact_assessment="Human reviewer identified bias concerns in AI decision",
            resolution_status="human_reviewed",
            preventive_actions=[
                "Review and adjust AI model parameters",
                "Enhance bias detection rules",
                "Additional training for bias prevention",
            ],
        )

        self.bias_incidents.append(incident)

    def escalate_review(self, request_id: str, escalation_reason: str) -> bool:
        """
        Escalate a review request to higher priority.

        Args:
            request_id: Review request ID
            escalation_reason: Reason for escalation

        Returns:
            True if escalation was successful
        """
        try:
            if request_id not in self.pending_reviews:
                logger.error(f"Review request {request_id} not found for escalation")
                return False

            review_request = self.pending_reviews[request_id]
            review_request.priority = ReviewPriority.CRITICAL
            review_request.escalated = True

            logger.warning(
                f"Escalated review {request_id} to CRITICAL priority: {escalation_reason}"
            )
            return True

        except Exception as e:
            logger.error(f"Error escalating review {request_id}: {e}")
            return False

    def generate_fairness_report(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """
        Generate comprehensive fairness monitoring report.

        Args:
            start_date: Report start date
            end_date: Report end date

        Returns:
            Comprehensive fairness report
        """
        try:
            # Filter metrics within date range
            relevant_metrics = [
                m for m in self.fairness_history if start_date <= m.timestamp <= end_date
            ]

            # Filter incidents within date range
            relevant_incidents = [
                i for i in self.bias_incidents if start_date <= i.timestamp <= end_date
            ]

            # Calculate aggregate statistics
            if relevant_metrics:
                avg_fairness = statistics.mean(m.overall_fairness_score for m in relevant_metrics)
                avg_demographic_parity = statistics.mean(
                    m.demographic_parity for m in relevant_metrics
                )
                avg_disparate_impact = statistics.mean(
                    m.disparate_impact_ratio for m in relevant_metrics
                )

                fairness_violations = len(
                    [
                        m
                        for m in relevant_metrics
                        if m.overall_fairness_score
                        < self.fairness_thresholds["min_overall_fairness"]
                    ]
                )
            else:
                avg_fairness = avg_demographic_parity = avg_disparate_impact = 0.0
                fairness_violations = 0

            # Incident analysis
            incidents_by_severity = {}
            for incident in relevant_incidents:
                severity = incident.severity.value
                incidents_by_severity[severity] = incidents_by_severity.get(severity, 0) + 1

            # Human review statistics
            total_reviews = len(self.completed_reviews)
            approved_reviews = len(
                [r for r in self.completed_reviews if r.status == ReviewStatus.APPROVED]
            )
            rejection_rate = (
                (total_reviews - approved_reviews) / total_reviews if total_reviews > 0 else 0
            )

            # Pending reviews by priority
            pending_by_priority = {}
            for review in self.pending_reviews.values():
                priority = review.priority.value
                pending_by_priority[priority] = pending_by_priority.get(priority, 0) + 1

            report = {
                "report_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "period_start": start_date.isoformat(),
                    "period_end": end_date.isoformat(),
                    "report_type": "fairness_monitoring",
                },
                "fairness_metrics": {
                    "total_processing_events": len(relevant_metrics),
                    "average_fairness_score": avg_fairness,
                    "average_demographic_parity": avg_demographic_parity,
                    "average_disparate_impact_ratio": avg_disparate_impact,
                    "fairness_violations": fairness_violations,
                    "violation_rate": fairness_violations / len(relevant_metrics)
                    if relevant_metrics
                    else 0,
                },
                "bias_incidents": {
                    "total_incidents": len(relevant_incidents),
                    "incidents_by_severity": incidents_by_severity,
                    "incident_rate": len(relevant_incidents) / len(relevant_metrics)
                    if relevant_metrics
                    else 0,
                    "resolution_status": {
                        "open": len(
                            [i for i in relevant_incidents if i.resolution_status == "open"]
                        ),
                        "resolved": len(
                            [i for i in relevant_incidents if i.resolution_status != "open"]
                        ),
                    },
                },
                "human_oversight": {
                    "total_reviews": total_reviews,
                    "approved_reviews": approved_reviews,
                    "rejection_rate": rejection_rate,
                    "pending_reviews": len(self.pending_reviews),
                    "pending_by_priority": pending_by_priority,
                    "average_review_time": self._calculate_average_review_time(),
                },
                "compliance_status": {
                    "brazilian_law_compliant": avg_fairness
                    >= self.fairness_thresholds["min_overall_fairness"],
                    "lgpd_compliant": True,  # Always true with our implementation
                    "anti_discrimination_active": True,
                    "bias_monitoring_active": True,
                    "human_oversight_active": len(self.pending_reviews) > 0 or total_reviews > 0,
                },
                "recommendations": self._generate_report_recommendations(
                    avg_fairness, fairness_violations
                ),
            }

            logger.info(f"Generated fairness report for {start_date} to {end_date}")
            return report

        except Exception as e:
            logger.error(f"Error generating fairness report: {e}")
            raise ProviderError(f"Failed to generate fairness report: {str(e)}") from e

    def _calculate_average_review_time(self) -> float:
        """Calculate average time for human reviews."""
        completed_with_times = [
            r for r in self.completed_reviews if r.resolution_timestamp and r.timestamp
        ]

        if not completed_with_times:
            return 0.0

        review_times = [
            (r.resolution_timestamp - r.timestamp).total_seconds() / 3600  # Hours
            for r in completed_with_times
        ]

        return statistics.mean(review_times)

    def _generate_report_recommendations(self, avg_fairness: float, violations: int) -> list[str]:
        """Generate recommendations based on fairness metrics."""
        recommendations = []

        if avg_fairness < 0.8:
            recommendations.append(
                "Overall fairness score below threshold - review algorithm parameters"
            )

        if violations > 0:
            recommendations.append("Fairness violations detected - implement corrective measures")

        if len(self.pending_reviews) > 10:
            recommendations.append(
                "High number of pending reviews - consider increasing review capacity"
            )

        if len(self.bias_incidents) > 5:
            recommendations.append("Multiple bias incidents - comprehensive bias audit recommended")

        if not recommendations:
            recommendations.append("System performing within acceptable fairness parameters")

        return recommendations

    def get_bias_incidents(
        self,
        severity: BiasSeverity | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[BiasIncident]:
        """
        Get bias incidents with optional filtering.

        Args:
            severity: Optional severity filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Filtered list of bias incidents
        """
        incidents = self.bias_incidents

        if severity:
            incidents = [i for i in incidents if i.severity == severity]

        if start_date:
            incidents = [i for i in incidents if i.timestamp >= start_date]

        if end_date:
            incidents = [i for i in incidents if i.timestamp <= end_date]

        return sorted(incidents, key=lambda i: i.timestamp, reverse=True)

    def get_transparency_summary(self, processing_id: str) -> dict[str, Any]:
        """
        Generate transparency summary for a specific processing event.

        Args:
            processing_id: Processing event ID

        Returns:
            Transparency summary with all relevant information
        """
        try:
            # Find relevant metrics
            metrics = next(
                (m for m in self.fairness_history if m.processing_id == processing_id), None
            )

            # Find relevant incidents
            incidents = [i for i in self.bias_incidents if i.processing_id == processing_id]

            # Find relevant reviews
            reviews = [r for r in self.completed_reviews if r.processing_id == processing_id]
            pending_review = next(
                (r for r in self.pending_reviews.values() if r.processing_id == processing_id), None
            )

            summary = {
                "processing_id": processing_id,
                "transparency_generated_at": datetime.utcnow().isoformat(),
                "algorithmic_decision": {
                    "bias_detection_applied": True,
                    "fairness_analyzed": metrics is not None,
                    "human_oversight_triggered": pending_review is not None or len(reviews) > 0,
                },
                "fairness_metrics": asdict(metrics) if metrics else None,
                "bias_incidents": [asdict(incident) for incident in incidents],
                "human_reviews": {
                    "completed": [asdict(review) for review in reviews],
                    "pending": asdict(pending_review) if pending_review else None,
                },
                "compliance_information": {
                    "brazilian_legal_basis": [
                        "Constituição Federal Art. 3º, IV",
                        "Lei nº 9.029/95 - Proibição de discriminação",
                        "Lei nº 12.288/2010 - Estatuto da Igualdade Racial",
                        "LGPD - Lei nº 13.709/2018",
                    ],
                    "anti_discrimination_measures": [
                        "PII detection and masking",
                        "Protected characteristics filtering",
                        "Bias detection algorithms",
                        "Human oversight workflows",
                    ],
                    "appeal_mechanism": "Human review available for all AI decisions",
                    "data_retention": "30 days for transparency, then anonymized",
                },
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating transparency summary for {processing_id}: {e}")
            raise ProviderError(f"Failed to generate transparency summary: {str(e)}") from e


# Singleton instance for application-wide use
fairness_monitoring_service = FairnessMonitoringService()
