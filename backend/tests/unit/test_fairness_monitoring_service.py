"""
Comprehensive Unit Tests for Fairness Monitoring Service
Phase 0.5 Security Implementation - Brazilian Legal Compliance
"""

import pytest
from datetime import datetime, timedelta
from app.services.fairness_monitoring_service import (
    FairnessMonitoringService,
    ReviewStatus,
    ReviewPriority,
    FairnessMetrics,
    HumanReviewRequest,
    BiasIncident
)


class TestFairnessMonitoringService:
    """Test suite for FairnessMonitoringService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fairness_service = FairnessMonitoringService()

    def test_initialization(self):
        """Test service initialization."""
        assert self.fairness_service is not None
        assert hasattr(self.fairness_service, 'pending_reviews')
        assert hasattr(self.fairness_service, 'completed_reviews')
        assert hasattr(self.fairness_service, 'bias_incidents')
        assert hasattr(self.fairness_service, 'fairness_history')
        assert hasattr(self.fairness_service, 'fairness_thresholds')

    def test_fairness_thresholds_initialization(self):
        """Test fairness thresholds initialization."""
        thresholds = self.fairness_service.fairness_thresholds

        assert "min_overall_fairness" in thresholds
        assert "max_disparate_impact" in thresholds
        assert "min_demographic_parity" in thresholds
        assert "bias_alert_threshold" in thresholds
        assert "critical_bias_threshold" in thresholds

        assert thresholds["min_overall_fairness"] == 0.8
        assert thresholds["max_disparate_impact"] == 0.2

    def test_calculate_fairness_metrics_perfect(self):
        """Test fairness metrics calculation with perfect fairness."""
        scores_by_group = {
            "group_a": [0.8, 0.8, 0.8],
            "group_b": [0.8, 0.8, 0.8],
            "group_c": [0.8, 0.8, 0.8]
        }
        bias_analysis = {"confidence_score": 0.1}

        metrics = self.fairness_service.calculate_fairness_metrics(
            "test_proc_1", scores_by_group, bias_analysis
        )

        assert isinstance(metrics, FairnessMetrics)
        assert metrics.processing_id == "test_proc_1"
        assert metrics.demographic_parity == 1.0
        assert metrics.equal_opportunity == 1.0
        assert metrics.predictive_equality == 1.0
        assert metrics.overall_fairness_score == 1.0
        assert metrics.disparate_impact_ratio == 1.0
        assert metrics.sample_size == 9
        assert len(metrics.protected_groups_analyzed) == 3
        assert metrics.bias_detection_score == 0.1

    def test_calculate_fairness_metrics_with_disparity(self):
        """Test fairness metrics calculation with disparity."""
        scores_by_group = {
            "group_a": [0.9, 0.8, 0.85],  # avg = 0.85
            "group_b": [0.6, 0.7, 0.65]   # avg = 0.65
        }
        bias_analysis = {"confidence_score": 0.3}

        metrics = self.fairness_service.calculate_fairness_metrics(
            "test_proc_2", scores_by_group, bias_analysis
        )

        assert isinstance(metrics, FairnessMetrics)
        assert metrics.demographic_parity == 0.8  # 1.0 - (0.85 - 0.65)
        assert metrics.disparate_impact_ratio == 0.65 / 0.85
        assert metrics.overall_fairness_score < 1.0
        assert metrics.sample_size == 6

    def test_calculate_fairness_metrics_insufficient_data(self):
        """Test fairness metrics with insufficient data."""
        scores_by_group = {}  # Empty
        bias_analysis = {"confidence_score": 0.1}

        metrics = self.fairness_service.calculate_fairness_metrics(
            "test_proc_3", scores_by_group, bias_analysis
        )

        assert isinstance(metrics, FairnessMetrics)
        assert metrics.demographic_parity == 1.0  # Default value
        assert metrics.overall_fairness_score == 1.0  # Default value
        assert metrics.sample_size == 0
        assert len(metrics.protected_groups_analyzed) == 0

    def test_calculate_fairness_metrics_single_group(self):
        """Test fairness metrics with single group."""
        scores_by_group = {
            "group_a": [0.8, 0.7, 0.9]
        }
        bias_analysis = {"confidence_score": 0.1}

        metrics = self.fairness_service.calculate_fairness_metrics(
            "test_proc_4", scores_by_group, bias_analysis
        )

        assert isinstance(metrics, FairnessMetrics)
        assert metrics.sample_size == 3
        assert len(metrics.protected_groups_analyzed) == 1

    def test_create_human_review_request_low_priority(self):
        """Test human review request creation with low priority."""
        ai_result = {"score": 85, "analysis": "Good match"}
        bias_analysis = {"confidence_score": 0.3, "requires_human_review": False}
        original_text = "Resume text"
        reason = "Low bias risk"

        request_id = self.fairness_service.create_human_review_request(
            "proc_123", ai_result, bias_analysis, original_text, reason
        )

        assert request_id is not None
        assert request_id in self.fairness_service.pending_reviews

        review = self.fairness_service.pending_reviews[request_id]
        assert review.processing_id == "proc_123"
        assert review.priority == ReviewPriority.LOW
        assert review.status == ReviewStatus.PENDING
        assert review.reason == reason

    def test_create_human_review_request_high_priority(self):
        """Test human review request creation with high priority."""
        ai_result = {"score": 45, "analysis": "Poor match"}
        bias_analysis = {"confidence_score": 0.7, "requires_human_review": True}
        original_text = "Resume with bias indicators"
        reason = "High bias risk detected"

        request_id = self.fairness_service.create_human_review_request(
            "proc_456", ai_result, bias_analysis, original_text, reason
        )

        review = self.fairness_service.pending_reviews[request_id]
        assert review.priority == ReviewPriority.HIGH
        assert review.status == ReviewStatus.PENDING

    def test_create_human_review_request_critical_priority(self):
        """Test human review request creation with critical priority."""
        ai_result = {"score": 20, "analysis": "Very poor match"}
        bias_analysis = {"confidence_score": 0.9, "requires_human_review": True}
        original_text = "Resume with critical bias indicators"
        reason = "Critical bias risk - multiple protected characteristics"

        request_id = self.fairness_service.create_human_review_request(
            "proc_789", ai_result, bias_analysis, original_text, reason
        )

        review = self.fairness_service.pending_reviews[request_id]
        assert review.priority == ReviewPriority.CRITICAL
        assert review.status == ReviewStatus.PENDING

    def test_get_pending_reviews_all(self):
        """Test getting all pending reviews."""
        # Create some review requests
        for i in range(3):
            self.fairness_service.create_human_review_request(
                f"proc_{i}",
                {"score": 50},
                {"confidence_score": 0.5},
                "text",
                f"reason_{i}"
            )

        pending = self.fairness_service.get_pending_reviews()
        assert len(pending) == 3

    def test_get_pending_reviews_filtered_by_priority(self):
        """Test getting pending reviews filtered by priority."""
        # Create reviews with different priorities
        self.fairness_service.create_human_review_request(
            "proc_low",
            {"score": 80},
            {"confidence_score": 0.2},
            "text",
            "low priority"
        )
        self.fairness_service.create_human_review_request(
            "proc_high",
            {"score": 30},
            {"confidence_score": 0.8},
            "text",
            "high priority"
        )

        high_priority = self.fairness_service.get_pending_reviews(ReviewPriority.HIGH)
        assert len(high_priority) == 1
        assert high_priority[0].processing_id == "proc_high"

        low_priority = self.fairness_service.get_pending_reviews(ReviewPriority.LOW)
        assert len(low_priority) == 1
        assert low_priority[0].processing_id == "proc_low"

    def test_get_pending_reviews_sorted(self):
        """Test that pending reviews are sorted by priority and timestamp."""
        import time

        # Create reviews with different priorities and timestamps
        time.sleep(0.01)
        id1 = self.fairness_service.create_human_review_request(
            "proc_1",
            {"score": 50},
            {"confidence_score": 0.3},
            "text",
            "low priority"
        )

        time.sleep(0.01)
        id2 = self.fairness_service.create_human_review_request(
            "proc_2",
            {"score": 30},
            {"confidence_score": 0.7},
            "text",
            "high priority"
        )

        time.sleep(0.01)
        id3 = self.fairness_service.create_human_review_request(
            "proc_3",
            {"score": 20},
            {"confidence_score": 0.9},
            "text",
            "critical priority"
        )

        pending = self.fairness_service.get_pending_reviews()
        assert len(pending) == 3

        # Should be sorted by priority (critical first)
        assert pending[0].priority == ReviewPriority.CRITICAL
        assert pending[1].priority == ReviewPriority.HIGH
        assert pending[2].priority == ReviewPriority.LOW

    def test_complete_review_success(self):
        """Test successful review completion."""
        # Create a review request
        request_id = self.fairness_service.create_human_review_request(
            "proc_complete",
            {"score": 50},
            {"confidence_score": 0.6},
            "text",
            "test review"
        )

        # Complete the review
        success = self.fairness_service.complete_review(
            request_id, "reviewer_123", True, "No bias issues found"
        )

        assert success == True
        assert request_id not in self.fairness_service.pending_reviews
        assert len(self.fairness_service.completed_reviews) == 1

        completed_review = self.fairness_service.completed_reviews[0]
        assert completed_review.request_id == request_id
        assert completed_review.reviewer_id == "reviewer_123"
        assert completed_review.status == ReviewStatus.APPROVED
        assert completed_review.review_notes == "No bias issues found"
        assert completed_review.resolution_timestamp is not None

    def test_complete_review_rejection(self):
        """Test review completion with rejection."""
        request_id = self.fairness_service.create_human_review_request(
            "proc_reject",
            {"score": 50},
            {"confidence_score": 0.6},
            "text",
            "test review"
        )

        # Reject the review
        success = self.fairness_service.complete_review(
            request_id, "reviewer_456", False, "Bias concerns detected"
        )

        assert success == True

        completed_review = self.fairness_service.completed_reviews[0]
        assert completed_review.status == ReviewStatus.REJECTED
        assert completed_review.review_notes == "Bias concerns detected"

        # Should create bias incident for bias-related rejection
        assert len(self.fairness_service.bias_incidents) > 0

    def test_complete_review_not_found(self):
        """Test completing a review that doesn't exist."""
        success = self.fairness_service.complete_review(
            "nonexistent_id", "reviewer_123", True, "test"
        )

        assert success == False

    def test_escalate_review(self):
        """Test review escalation."""
        request_id = self.fairness_service.create_human_review_request(
            "proc_escalate",
            {"score": 50},
            {"confidence_score": 0.5},
            "text",
            "normal priority"
        )

        success = self.fairness_service.escalate_review(
            request_id, "Escalation due to user complaint"
        )

        assert success == True

        review = self.fairness_service.pending_reviews[request_id]
        assert review.priority == ReviewPriority.CRITICAL
        assert review.escalated == True

    def test_escalate_review_not_found(self):
        """Test escalating a review that doesn't exist."""
        success = self.fairness_service.escalate_review(
            "nonexistent_id", "test escalation"
        )

        assert success == False

    def test_generate_fairness_report(self):
        """Test fairness report generation."""
        # Create some test data
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        # Add some fairness metrics
        for i in range(5):
            scores_by_group = {
                "group_a": [0.8 + i * 0.02],
                "group_b": [0.7 + i * 0.03]
            }
            self.fairness_service.calculate_fairness_metrics(
                f"proc_{i}", scores_by_group, {"confidence_score": 0.1}
            )

        # Add a bias incident
        incident = BiasIncident(
            incident_id="inc_1",
            timestamp=datetime.utcnow() - timedelta(days=2),
            severity=ReviewPriority.HIGH,
            processing_id="proc_1",
            bias_type=["age"],
            detected_patterns={},
            impact_assessment="Test incident",
            resolution_status="open",
            preventive_actions=[]
        )
        self.fairness_service.bias_incidents.append(incident)

        # Generate report
        report = self.fairness_service.generate_fairness_report(start_date, end_date)

        assert "report_metadata" in report
        assert "fairness_metrics" in report
        assert "bias_incidents" in report
        assert "human_oversight" in report
        assert "compliance_status" in report
        assert "recommendations" in report

        assert report["fairness_metrics"]["total_processing_events"] == 5
        assert report["bias_incidents"]["total_incidents"] == 1

    def test_generate_fairness_report_empty_data(self):
        """Test fairness report generation with no data."""
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()

        report = self.fairness_service.generate_fairness_report(start_date, end_date)

        assert report["fairness_metrics"]["total_processing_events"] == 0
        assert report["bias_incidents"]["total_incidents"] == 0
        assert report["human_oversight"]["total_reviews"] == 0

    def test_generate_fairness_report_invalid_date_range(self):
        """Test fairness report generation with invalid date range."""
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() - timedelta(days=1)  # End before start

        with pytest.raises(Exception):  # Should raise validation error
            self.fairness_service.generate_fairness_report(start_date, end_date)

    def test_get_bias_incidents_all(self):
        """Test getting all bias incidents."""
        # Create test incidents
        incidents = [
            BiasIncident(
                incident_id=f"inc_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                severity=ReviewPriority.HIGH if i % 2 == 0 else ReviewPriority.MEDIUM,
                processing_id=f"proc_{i}",
                bias_type=["age"],
                detected_patterns={},
                impact_assessment=f"Incident {i}",
                resolution_status="open",
                preventive_actions=[]
            )
            for i in range(3)
        ]

        self.fairness_service.bias_incidents.extend(incidents)

        all_incidents = self.fairness_service.get_bias_incidents()
        assert len(all_incidents) == 3

    def test_get_bias_incidents_filtered_by_severity(self):
        """Test getting bias incidents filtered by severity."""
        # Create test incidents with different severities
        high_incident = BiasIncident(
            incident_id="inc_high",
            timestamp=datetime.utcnow(),
            severity=ReviewPriority.HIGH,
            processing_id="proc_high",
            bias_type=["age"],
            detected_patterns={},
            impact_assessment="High severity",
            resolution_status="open",
            preventive_actions=[]
        )

        medium_incident = BiasIncident(
            incident_id="inc_medium",
            timestamp=datetime.utcnow(),
            severity=ReviewPriority.MEDIUM,
            processing_id="proc_medium",
            bias_type=["gender"],
            detected_patterns={},
            impact_assessment="Medium severity",
            resolution_status="open",
            preventive_actions=[]
        )

        self.fairness_service.bias_incidents.extend([high_incident, medium_incident])

        # Filter by high severity
        high_incidents = self.fairness_service.get_bias_incidents(severity=ReviewPriority.HIGH)
        assert len(high_incidents) == 1
        assert high_incidents[0].incident_id == "inc_high"

        # Filter by medium severity
        medium_incidents = self.fairness_service.get_bias_incidents(severity=ReviewPriority.MEDIUM)
        assert len(medium_incidents) == 1
        assert medium_incidents[0].incident_id == "inc_medium"

    def test_get_bias_incidents_filtered_by_date(self):
        """Test getting bias incidents filtered by date range."""
        now = datetime.utcnow()
        old_date = now - timedelta(days=10)
        recent_date = now - timedelta(days=1)

        old_incident = BiasIncident(
            incident_id="inc_old",
            timestamp=old_date,
            severity=ReviewPriority.MEDIUM,
            processing_id="proc_old",
            bias_type=["age"],
            detected_patterns={},
            impact_assessment="Old incident",
            resolution_status="open",
            preventive_actions=[]
        )

        recent_incident = BiasIncident(
            incident_id="inc_recent",
            timestamp=recent_date,
            severity=ReviewPriority.MEDIUM,
            processing_id="proc_recent",
            bias_type=["gender"],
            detected_patterns={},
            impact_assessment="Recent incident",
            resolution_status="open",
            preventive_actions=[]
        )

        self.fairness_service.bias_incidents.extend([old_incident, recent_incident])

        # Filter by recent date range
        start_date = now - timedelta(days=5)
        end_date = now

        recent_incidents = self.fairness_service.get_bias_incidents(
            start_date=start_date, end_date=end_date
        )
        assert len(recent_incidents) == 1
        assert recent_incidents[0].incident_id == "inc_recent"

    def test_get_transparency_summary_existing_processing(self):
        """Test transparency summary for existing processing."""
        # Create test data
        processing_id = "proc_transparency"

        # Add fairness metrics
        scores_by_group = {"group_a": [0.8], "group_b": [0.7]}
        self.fairness_service.calculate_fairness_metrics(
            processing_id, scores_by_group, {"confidence_score": 0.2}
        )

        # Add bias incident
        incident = BiasIncident(
            incident_id="inc_transparency",
            timestamp=datetime.utcnow(),
            severity=ReviewPriority.MEDIUM,
            processing_id=processing_id,
            bias_type=["age"],
            detected_patterns={},
            impact_assessment="Test incident",
            resolution_status="resolved",
            preventive_actions=[]
        )
        self.fairness_service.bias_incidents.append(incident)

        # Get transparency summary
        summary = self.fairness_service.get_transparency_summary(processing_id)

        assert summary["processing_id"] == processing_id
        assert "transparency_generated_at" in summary
        assert "algorithmic_decision" in summary
        assert "fairness_metrics" in summary
        assert "bias_incidents" in summary
        assert "human_reviews" in summary
        assert "compliance_information" in summary

        assert summary["algorithmic_decision"]["bias_detection_applied"] == True
        assert summary["fairness_metrics"]["processing_id"] == processing_id
        assert len(summary["bias_incidents"]) == 1

    def test_get_transparency_summary_nonexistent_processing(self):
        """Test transparency summary for nonexistent processing."""
        summary = self.fairness_service.get_transparency_summary("nonexistent_proc")

        assert summary["processing_id"] == "nonexistent_proc"
        assert summary["fairness_metrics"] is None
        assert len(summary["bias_incidents"]) == 0
        assert summary["human_reviews"]["completed"] == []
        assert summary["human_reviews"]["pending"] is None

    def test_fairness_violation_detection(self):
        """Test automatic fairness violation detection."""
        # Create metrics with low fairness scores
        scores_by_group = {
            "group_a": [0.9, 0.9, 0.9],  # avg = 0.9
            "group_b": [0.3, 0.3, 0.3]   # avg = 0.3 (major disparity)
        }
        bias_analysis = {"confidence_score": 0.7}

        initial_incident_count = len(self.fairness_service.bias_incidents)

        # Calculate metrics (should trigger violation detection)
        self.fairness_service.calculate_fairness_metrics(
            "proc_violation", scores_by_group, bias_analysis
        )

        # Should have created a bias incident
        assert len(self.fairness_service.bias_incidents) > initial_incident_count

        new_incident = self.fairness_service.bias_incidents[-1]
        assert new_incident.processing_id == "proc_violation"
        assert new_incident.severity in [ReviewPriority.HIGH, ReviewPriority.MEDIUM]

    def test_calculate_average_review_time(self):
        """Test calculation of average review time."""
        # Add completed reviews with different completion times
        now = datetime.utcnow()

        # Review 1: completed in 2 hours
        review1 = HumanReviewRequest(
            request_id="review_1",
            processing_id="proc_1",
            timestamp=now - timedelta(hours=2),
            priority=ReviewPriority.MEDIUM,
            reason="test",
            bias_analysis={},
            original_text_sample="text",
            ai_decision={},
            status=ReviewStatus.APPROVED,
            reviewer_id="reviewer_1",
            review_notes="approved",
            resolution_timestamp=now
        )

        # Review 2: completed in 4 hours
        review2 = HumanReviewRequest(
            request_id="review_2",
            processing_id="proc_2",
            timestamp=now - timedelta(hours=4),
            priority=ReviewPriority.MEDIUM,
            reason="test",
            bias_analysis={},
            original_text_sample="text",
            ai_decision={},
            status=ReviewStatus.APPROVED,
            reviewer_id="reviewer_2",
            review_notes="approved",
            resolution_timestamp=now
        )

        self.fairness_service.completed_reviews.extend([review1, review2])

        avg_time = self.fairness_service._calculate_average_review_time()
        assert avg_time == 3.0  # (2 + 4) / 2

    def test_calculate_average_review_time_no_reviews(self):
        """Test average review time calculation with no reviews."""
        avg_time = self.fairness_service._calculate_average_review_time()
        assert avg_time == 0.0

    def test_generate_report_recommendations_good_performance(self):
        """Test report recommendations for good performance."""
        # Create metrics with good performance
        for i in range(5):
            scores_by_group = {"group_a": [0.85], "group_b": [0.82]}
            self.fairness_service.calculate_fairness_metrics(
                f"proc_good_{i}", scores_by_group, {"confidence_score": 0.1}
            )

        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        report = self.fairness_service.generate_fairness_report(start_date, end_date)
        recommendations = report["recommendations"]

        assert len(recommendations) >= 1
        assert "System performing within acceptable fairness parameters" in recommendations

    def test_generate_report_recommendations_poor_performance(self):
        """Test report recommendations for poor performance."""
        # Create metrics with poor performance
        for i in range(5):
            scores_by_group = {"group_a": [0.9], "group_b": [0.4]}  # Major disparity
            self.fairness_service.calculate_fairness_metrics(
                f"proc_poor_{i}", scores_by_group, {"confidence_score": 0.7}
            )

        # Add bias incidents
        for i in range(6):
            incident = BiasIncident(
                incident_id=f"inc_poor_{i}",
                timestamp=datetime.utcnow() - timedelta(days=i),
                severity=ReviewPriority.HIGH,
                processing_id=f"proc_poor_{i}",
                bias_type=["age"],
                detected_patterns={},
                impact_assessment="Poor performance incident",
                resolution_status="open",
                preventive_actions=[]
            )
            self.fairness_service.bias_incidents.append(incident)

        # Add many pending reviews
        for i in range(11):
            self.fairness_service.create_human_review_request(
                f"proc_pending_{i}",
                {"score": 30},
                {"confidence_score": 0.8},
                "text",
                "high priority"
            )

        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        report = self.fairness_service.generate_fairness_report(start_date, end_date)
        recommendations = report["recommendations"]

        assert len(recommendations) >= 4
        assert any("Overall fairness score below threshold" in rec for rec in recommendations)
        assert any("Fairness violations detected" in rec for rec in recommendations)
        assert any("High number of pending reviews" in rec for rec in recommendations)
        assert any("Multiple bias incidents" in rec for rec in recommendations)


if __name__ == "__main__":
    pytest.main([__file__])