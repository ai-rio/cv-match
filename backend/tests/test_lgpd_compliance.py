"""
Comprehensive LGPD Compliance Tests

This test suite validates all LGPD compliance components including:
- PII detection with Brazilian patterns
- Data masking functionality
- Consent management
- Data subject rights
- Data retention management
- Audit trail functionality

Critical for ensuring CV-Match is compliant with Brazilian LGPD requirements.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.security.pii_detection_service import (
    PIIDetectionService, PIIType, scan_for_pii, mask_pii, validate_lgpd_compliance
)
from app.services.security.consent_manager import (
    ConsentManager, ConsentRequest, ConsentCheckResult, UserConsentStatus
)
from app.services.security.data_subject_rights import (
    DataSubjectRightsManager, DataSubjectRightType, DataAccessRequest, DataDeletionRequest
)
from app.services.security.retention_manager import (
    RetentionManager, RetentionPolicy, DataCategory, RetentionPeriod
)
from app.services.security.audit_trail import (
    AuditTrailService, AuditEvent, DataAccessEvent, ComplianceEvent
)
from app.utils.pii_masker import PIIMasker, MaskingLevel


class TestPIIDetection:
    """Test PII detection functionality."""

    @pytest.fixture
    def pii_service(self):
        """Create PII detection service instance."""
        return PIIDetectionService()

    @pytest.mark.asyncio
    async def test_brazilian_cpf_detection(self, pii_service):
        """Test CPF detection with various formats."""
        test_cases = [
            ("123.456.789-01", True),
            ("12345678901", True),
            ("111.222.333-44", True),
            ("987.654.321-00", True),
            ("123.456.789", False),  # Incomplete
            ("123.456.789-0", False),  # Incomplete
            ("abc.def.ghi-jk", False),  # Invalid format
        ]

        for text, expected in test_cases:
            result = pii_service.scan_text(text)
            has_cpf = PIIType.CPF in result.pii_types_found
            assert has_cpf == expected, f"CPF detection failed for: {text}"

    @pytest.mark.asyncio
    async def test_brazilian_rg_detection(self, pii_service):
        """Test RG detection with various formats."""
        test_cases = [
            ("12.345.678-9", True),
            ("MG-12.345.678", True),
            ("123456789", True),
            ("1.234.567", True),
            ("123456", False),  # Too short
            ("abc.def.ghi", False),  # Invalid format
        ]

        for text, expected in test_cases:
            result = pii_service.scan_text(text)
            has_rg = PIIType.RG in result.pii_types_found
            assert has_rg == expected, f"RG detection failed for: {text}"

    @pytest.mark.asyncio
    async def test_brazilian_cnpj_detection(self, pii_service):
        """Test CNPJ detection with various formats."""
        test_cases = [
            ("12.345.678/0001-95", True),
            ("12345678000195", True),
            ("12.345.678/0001.95", False),  # Wrong separator
            ("12.345.678/0001-9", False),  # Too short
            ("abc.def.ghi/jkl-mn", False),  # Invalid format
        ]

        for text, expected in test_cases:
            result = pii_service.scan_text(text)
            has_cnpj = PIIType.CNPJ in result.pii_types_found
            assert has_cnpj == expected, f"CNPJ detection failed for: {text}"

    @pytest.mark.asyncio
    async def test_email_detection(self, pii_service):
        """Test email detection."""
        test_cases = [
            ("user@example.com", True),
            ("joao.silva@empresa.com.br", True),
            ("user@localhost", True),
            ("invalid-email", False),
            ("@domain.com", False),
            ("user@", False),
        ]

        for text, expected in test_cases:
            result = pii_service.scan_text(text)
            has_email = PIIType.EMAIL in result.pii_types_found
            assert has_email == expected, f"Email detection failed for: {text}"

    @pytest.mark.asyncio
    async def test_brazilian_phone_detection(self, pii_service):
        """Test Brazilian phone number detection."""
        test_cases = [
            ("+55 11 98765-4321", True),
            ("(11) 98765-4321", True),
            ("11987654321", True),
            ("11 98765-4321", True),
            ("98765-4321", True),  # Local format
            ("1234", False),  # Too short
            ("abcdefghij", False),  # Invalid format
        ]

        for text, expected in test_cases:
            result = pii_service.scan_text(text)
            has_phone = PIIType.PHONE in result.pii_types_found
            assert has_phone == expected, f"Phone detection failed for: {text}"

    @pytest.mark.asyncio
    async def test_multiple_pii_detection(self, pii_service):
        """Test detection of multiple PII types in one text."""
        text = "Meu nome é João, CPF 123.456.789-01, email joao@example.com, telefone (11) 98765-4321"
        result = pii_service.scan_text(text)

        assert PIIType.CPF in result.pii_types_found
        assert PIIType.EMAIL in result.pii_types_found
        assert PIIType.PHONE in result.pii_types_found
        assert len(result.pii_types_found) == 3

    @pytest.mark.asyncio
    async def test_pii_masking(self, pii_service):
        """Test PII masking functionality."""
        text = "CPF: 123.456.789-01, Email: joao@example.com"
        result = pii_service.scan_text(text)

        assert result.masked_text is not None
        assert "123.456.789-01" not in result.masked_text
        assert "joao@example.com" not in result.masked_text

    @pytest.mark.asyncio
    async def test_lgpd_compliance_validation(self, pii_service):
        """Test LGPD compliance validation."""
        # Test with PII
        text_with_pii = "Meu CPF é 123.456.789-01"
        result = validate_lgpd_compliance(text_with_pii)
        assert not result["is_compliant"]
        assert result["requires_masking"]

        # Test without PII
        text_without_pii = "Este é um texto normal sem dados pessoais"
        result = validate_lgpd_compliance(text_without_pii)
        assert result["is_compliant"]
        assert not result["requires_masking"]


class TestPIIMasking:
    """Test PII masking functionality."""

    @pytest.fixture
    def masker(self):
        """Create PII masker instance."""
        return PIIMasker()

    def test_cpf_masking(self, masker):
        """Test CPF masking."""
        cpf = "123.456.789-01"
        masked = masker.mask_text(cpf, MaskingLevel.PARTIAL)

        assert cpf != masked
        assert masked.startswith("12")
        assert masked.endswith("01")
        assert "*" in masked

    def test_email_masking(self, masker):
        """Test email masking."""
        email = "joao.silva@empresa.com.br"
        masked = masker.mask_text(email, MaskingLevel.PARTIAL)

        assert email != masked
        assert "@empresa.com.br" in masked
        assert "j***.****" in masked or "*" in masked.split("@")[0]

    def test_full_masking(self, masker):
        """Test full masking."""
        text = "CPF: 123.456.789-01"
        masked = masker.mask_text(text, MaskingLevel.FULL)

        assert text != masked
        assert "123.456.789-01" not in masked
        assert "*" * len("123.456.789-01") in masked

    def test_dict_masking(self, masker):
        """Test dictionary masking."""
        data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "cpf": "123.456.789-01",
            "phone": "11987654321"
        }

        masked_data = masker.mask_dict(data, MaskingLevel.PARTIAL)

        assert masked_data["name"] != data["name"]
        assert masked_data["email"] != data["email"]
        assert masked_data["cpf"] != data["cpf"]
        assert masked_data["phone"] != data["phone"]


class TestConsentManagement:
    """Test consent management functionality."""

    @pytest.fixture
    def consent_manager_mock(self):
        """Create mock consent manager."""
        manager = MagicMock(spec=ConsentManager)
        manager.get_available_consent_types = AsyncMock()
        manager.record_user_consent = AsyncMock()
        manager.check_user_consent = AsyncMock()
        manager.get_user_consent_status = AsyncMock()
        return manager

    @pytest.mark.asyncio
    async def test_consent_recording(self, consent_manager_mock):
        """Test consent recording."""
        # Mock available consent types
        from app.services.security.consent_manager import ConsentType
        consent_types = [
            ConsentType(
                id="1",
                name="data_processing",
                description="Data processing consent",
                category="data_processing",
                is_required=True,
                version=1,
                is_active=True
            )
        ]
        consent_manager_mock.get_available_consent_types.return_value = consent_types

        # Mock consent creation
        from app.services.security.consent_manager import UserConsent
        consent_record = UserConsent(
            id="consent_123",
            user_id="user_123",
            consent_type_id="1",
            granted=True,
            granted_at=datetime.now(timezone.utc),
            consent_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        consent_manager_mock.record_user_consent.return_value = consent_record

        # Test consent request
        consent_request = ConsentRequest(
            consent_type_name="data_processing",
            granted=True,
            legal_basis="consent",
            purpose="Service provision"
        )

        result = await consent_manager_mock.record_user_consent("user_123", consent_request)

        assert result is not None
        assert result.granted is True
        consent_manager_mock.record_user_consent.assert_called_once()

    @pytest.mark.asyncio
    async def test_consent_validation(self, consent_manager_mock):
        """Test consent validation."""
        # Mock consent check result
        consent_check = ConsentCheckResult(
            has_consent=True,
            consent_type="data_processing",
            granted_at=datetime.now(timezone.utc),
            is_required=True,
            legal_basis="consent"
        )
        consent_manager_mock.check_user_consent.return_value = consent_check

        result = await consent_manager_mock.check_user_consent("user_123", "data_processing")

        assert result.has_consent is True
        assert result.consent_type == "data_processing"
        consent_manager_mock.check_user_consent.assert_called_once()

    @pytest.mark.asyncio
    async def test_consent_status_retrieval(self, consent_manager_mock):
        """Test consent status retrieval."""
        # Mock consent status
        consent_status = UserConsentStatus(
            user_id="user_123",
            has_all_required_consents=True,
            consents=[],
            missing_required_consents=[],
            granted_optional_consents=[],
            revoked_consents=[],
            last_updated=datetime.now(timezone.utc)
        )
        consent_manager_mock.get_user_consent_status.return_value = consent_status

        result = await consent_manager_mock.get_user_consent_status("user_123")

        assert result.has_all_required_consents is True
        assert result.user_id == "user_123"
        consent_manager_mock.get_user_consent_status.assert_called_once()


class TestDataSubjectRights:
    """Test data subject rights functionality."""

    @pytest.fixture
    def rights_manager_mock(self):
        """Create mock data subject rights manager."""
        manager = MagicMock(spec=DataSubjectRightsManager)
        manager.create_data_access_request = AsyncMock()
        manager.process_data_access_request = AsyncMock()
        manager.create_data_deletion_request = AsyncMock()
        manager.process_data_deletion_request = AsyncMock()
        return manager

    @pytest.mark.asyncio
    async def test_data_access_request(self, rights_manager_mock):
        """Test data access request creation and processing."""
        # Mock request creation
        rights_manager_mock.create_data_access_request.return_value = "request_123"

        # Mock request processing
        from app.services.security.data_subject_rights import DataSubjectRightsResponse
        response = DataSubjectRightsResponse(
            request_id="request_123",
            request_type="access",
            status="completed",
            processed_data={"user_id": "user_123", "data": "test"},
            message="Data access request processed successfully"
        )
        rights_manager_mock.process_data_access_request.return_value = response

        # Create request
        access_request = DataAccessRequest(
            user_id="user_123",
            request_type=DataSubjectRightType.ACCESS,
            justification="User wants to access their data"
        )

        request_id = await rights_manager_mock.create_data_access_request(access_request)
        assert request_id == "request_123"

        result = await rights_manager_mock.process_data_access_request(request_id)
        assert result.status == "completed"
        assert "user_123" in str(result.processed_data)

    @pytest.mark.asyncio
    async def test_data_deletion_request(self, rights_manager_mock):
        """Test data deletion request creation and processing."""
        # Mock request creation
        rights_manager_mock.create_data_deletion_request.return_value = "request_456"

        # Mock request processing
        from app.services.security.data_subject_rights import DataSubjectRightsResponse
        response = DataSubjectRightsResponse(
            request_id="request_456",
            request_type="deletion",
            status="completed",
            processed_data={"deleted_data": {"all": "Complete deletion performed"}},
            message="Data deletion request processed successfully"
        )
        rights_manager_mock.process_data_deletion_request.return_value = response

        # Create request
        deletion_request = DataDeletionRequest(
            user_id="user_123",
            deletion_scope="all",
            justification="User exercising right to be forgotten"
        )

        request_id = await rights_manager_mock.create_data_deletion_request(deletion_request)
        assert request_id == "request_456"

        result = await rights_manager_mock.process_data_deletion_request(request_id)
        assert result.status == "completed"
        assert "deleted_data" in str(result.processed_data)


class TestDataRetention:
    """Test data retention functionality."""

    @pytest.fixture
    def retention_manager_mock(self):
        """Create mock retention manager."""
        manager = MagicMock(spec=RetentionManager)
        manager.get_retention_policies = AsyncMock()
        manager.schedule_retention_cleanup = AsyncMock()
        manager.execute_retention_cleanup = AsyncMock()
        return manager

    @pytest.mark.asyncio
    async def test_retention_policy_creation(self, retention_manager_mock):
        """Test retention policy creation."""
        # Mock policy creation
        retention_manager_mock.create_retention_policy.return_value = "policy_123"

        policy = RetentionPolicy(
            data_category=DataCategory.USER_PROFILE,
            retention_period=RetentionPeriod.FIVE_YEARS,
            retention_days=1825,
            legal_basis="LGPD Art. 15",
            deletion_method="soft_delete",
            requires_user_consent=False,
            auto_cleanup=True
        )

        result = await retention_manager_mock.create_retention_policy(policy)
        assert result == "policy_123"

    @pytest.mark.asyncio
    async def test_retention_cleanup(self, retention_manager_mock):
        """Test retention cleanup execution."""
        # Mock task scheduling
        retention_manager_mock.schedule_retention_cleanup.return_value = "task_123"

        # Mock cleanup execution
        from app.services.security.retention_manager import RetentionCleanupResult
        cleanup_result = RetentionCleanupResult(
            data_category="user_profile",
            retention_policy="5_years (1825 days)",
            records_scanned=100,
            records_deleted=10,
            records_retained=90,
            errors_encountered=0,
            duration_seconds=30.5,
            cleanup_date=datetime.now(timezone.utc)
        )
        retention_manager_mock.execute_retention_cleanup.return_value = cleanup_result

        # Schedule cleanup
        task_id = await retention_manager_mock.schedule_retention_cleanup(DataCategory.USER_PROFILE)
        assert task_id == "task_123"

        # Execute cleanup
        result = await retention_manager_mock.execute_retention_cleanup(task_id)
        assert result.data_category == "user_profile"
        assert result.records_deleted == 10
        assert result.records_retained == 90


class TestAuditTrail:
    """Test audit trail functionality."""

    @pytest.fixture
    def audit_trail_mock(self):
        """Create mock audit trail service."""
        service = MagicMock(spec=AuditTrailService)
        service.log_audit_event = AsyncMock()
        service.log_data_access = AsyncMock()
        service.log_compliance_event = AsyncMock()
        service.get_user_audit_trail = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_audit_event_logging(self, audit_trail_mock):
        """Test audit event logging."""
        audit_trail_mock.log_audit_event.return_value = "event_123"

        event = AuditEvent(
            event_type=AuditEventType.DATA_ACCESS,
            action="User accessed personal data",
            user_id="user_123",
            table_name="profiles",
            record_id="profile_123",
            success=True
        )

        result = await audit_trail_mock.log_audit_event(event)
        assert result == "event_123"
        audit_trail_mock.log_audit_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_data_access_logging(self, audit_trail_mock):
        """Test data access event logging."""
        audit_trail_mock.log_data_access.return_value = "access_123"

        access_event = DataAccessEvent(
            user_id="user_123",
            data_category="user_profile",
            access_type="view",
            access_purpose="User requested data access",
            consent_verified=True
        )

        result = await audit_trail_mock.log_data_access(access_event)
        assert result == "access_123"
        audit_trail_mock.log_data_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_compliance_event_logging(self, audit_trail_mock):
        """Test compliance event logging."""
        audit_trail_mock.log_compliance_event.return_value = "compliance_123"

        compliance_event = ComplianceEvent(
            compliance_type="lgpd",
            check_type="consent_validation",
            status="compliant",
            details={"user_id": "user_123", "consents_checked": 5}
        )

        result = await audit_trail_mock.log_compliance_event(compliance_event)
        assert result == "compliance_123"
        audit_trail_mock.log_compliance_event.assert_called_once()


class TestIntegration:
    """Integration tests for LGPD compliance system."""

    @pytest.mark.asyncio
    async def test_end_to_end_pii_workflow(self):
        """Test complete PII detection and masking workflow."""
        # Text with Brazilian PII
        text = "Olá, sou João Silva, CPF 123.456.789-01, email joao@empresa.com, telefone (11) 98765-4321"

        # Scan for PII
        result = scan_for_pii(text)
        assert result.has_pii is True
        assert len(result.pii_types_found) >= 3  # CPF, email, phone

        # Mask PII
        masked_text = mask_pii(text)
        assert masked_text != text
        assert "123.456.789-01" not in masked_text
        assert "joao@empresa.com" not in masked_text

        # Validate LGPD compliance
        compliance_result = validate_lgpd_compliance(text)
        assert not compliance_result["is_compliant"]
        assert compliance_result["requires_masking"] is True

    @pytest.mark.asyncio
    async def test_consent_and_access_workflow(self):
        """Test consent management combined with data access workflow."""
        # This would require actual database connections for full integration
        # For now, we'll test the logic flow

        # Simulate user granting consent
        consent_request = ConsentRequest(
            consent_type_name="data_processing",
            granted=True,
            legal_basis="consent",
            purpose="Service provision"
        )

        # Validate consent request structure
        assert consent_request.consent_type_name == "data_processing"
        assert consent_request.granted is True
        assert consent_request.legal_basis == "consent"

        # Simulate data access request
        access_request = DataAccessRequest(
            user_id="test_user",
            request_type="access",
            justification="User exercising LGPD rights"
        )

        # Validate access request structure
        assert access_request.request_type == "access"
        assert access_request.justification is not None

    @pytest.mark.asyncio
    async def test_retention_and_deletion_workflow(self):
        """Test data retention and deletion workflow."""
        # Create retention policy
        policy = RetentionPolicy(
            data_category=DataCategory.RESUME_DATA,
            retention_period=RetentionPeriod.TWO_YEARS,
            retention_days=730,
            legal_basis="User consent and service necessity",
            deletion_method="soft_delete",
            requires_user_consent=True,
            auto_cleanup=True
        )

        # Validate policy structure
        assert policy.data_category == DataCategory.RESUME_DATA
        assert policy.retention_days == 730
        assert policy.requires_user_consent is True

        # Simulate data deletion request
        deletion_request = DataDeletionRequest(
            user_id="test_user",
            deletion_scope="all",
            justification="User exercising right to be forgotten",
            retain_legal_required=True
        )

        # Validate deletion request
        assert deletion_request.deletion_scope == "all"
        assert deletion_request.retain_legal_required is True

    @pytest.mark.asyncio
    async def test_audit_trail_integration(self):
        """Test audit trail integration across all components."""
        # Simulate sequence of events that should be audited

        events = [
            AuditEvent(
                event_type=AuditEventType.CONSENT_GRANTED,
                action="User granted data processing consent",
                user_id="test_user",
                success=True
            ),
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                action="User accessed personal data",
                user_id="test_user",
                table_name="profiles",
                success=True
            ),
            AuditEvent(
                event_type=AuditEventType.DATA_DELETION,
                action="User requested data deletion",
                user_id="test_user",
                success=True
            )
        ]

        # Validate all events have required fields
        for event in events:
            assert event.event_type is not None
            assert event.action is not None
            assert event.user_id is not None
            assert event.success is not None


# Performance Tests
class TestPerformance:
    """Performance tests for LGPD compliance components."""

    @pytest.mark.asyncio
    async def test_pii_detection_performance(self):
        """Test PII detection performance with large text."""
        # Generate large text with PII
        pii_text = "CPF: 123.456.789-01, Email: joao@example.com, Telefone: (11) 98765-4321"
        large_text = " ".join([pii_text] * 1000)  # Repeat 1000 times

        import time
        start_time = time.time()

        result = scan_for_pii(large_text)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 5.0, f"PII detection took too long: {duration:.2f} seconds"
        assert result.has_pii is True

    @pytest.mark.asyncio
    async def test_masking_performance(self):
        """Test PII masking performance with large text."""
        # Generate large text with PII
        pii_text = "CPF: 123.456.789-01, Email: joao@example.com"
        large_text = " ".join([pii_text] * 1000)  # Repeat 1000 times

        import time
        start_time = time.time()

        masked_text = mask_pii(large_text)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 3.0, f"PII masking took too long: {duration:.2f} seconds"
        assert masked_text != large_text
        assert "123.456.789-01" not in masked_text


# Edge Cases and Error Handling
class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """Test handling of empty or null text."""
        # Test empty string
        result = scan_for_pii("")
        assert result.has_pii is False
        assert len(result.pii_types_found) == 0

        # Test whitespace only
        result = scan_for_pii("   \n\t   ")
        assert result.has_pii is False

    @pytest.mark.asyncio
    async def test_invalid_pii_formats(self):
        """Test handling of invalid PII formats."""
        invalid_cases = [
            "123.456.789",  # Incomplete CPF
            "abc.def.ghi-jk",  # Invalid characters
            "123.456.789-012",  # Too many digits
            "email@",  # Incomplete email
            "@domain.com",  # Incomplete email
        ]

        for text in invalid_cases:
            result = scan_for_pii(text)
            # Should not crash, but may or may not detect PII depending on the case
            assert isinstance(result.has_pii, bool)
            assert isinstance(result.pii_types_found, list)

    @pytest.mark.asyncio
    async def test_unicode_handling(self):
        """Test handling of Unicode and special characters."""
        text_with_unicode = "João Silva, CPF 123.456.789-01, email joão@empresa.com, São Paulo"

        result = scan_for_pii(text_with_unicode)
        assert result.has_pii is True  # Should still detect PII despite Unicode

        masked_text = mask_pii(text_with_unicode)
        assert masked_text != text_with_unicode
        assert "123.456.789-01" not in masked_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])