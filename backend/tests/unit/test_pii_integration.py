"""
Comprehensive PII Integration Tests for LGPD Compliance

This test suite validates that PII detection and masking is properly integrated
into resume and job processing pipelines to ensure Brazilian LGPD compliance.

Critical tests:
1. PII detection in resume upload pipeline
2. PII detection in job processing pipeline
3. PII masking before database storage
4. Compliance logging functionality
5. Performance impact assessment
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.job_service import JobService
from app.services.resume_service import ResumeService
from app.services.security.audit_trail import ComplianceStatus, ComplianceType, audit_trail
from app.services.security.pii_detection_service import (
    PIIDetectionResult,
    PIIDetectionService,
    PIIType,
    pii_detector,
)


class TestPIIDetectionService:
    """Test the PII detection service functionality."""

    @pytest.fixture
    def pii_service(self):
        """Create PII detection service instance."""
        return PIIDetectionService()

    def test_brazilian_cpf_detection(self, pii_service):
        """Test Brazilian CPF detection."""
        text_with_cpf = "Meu nome é João Silva e meu CPF é 123.456.789-01. Moro em São Paulo."
        result = pii_service.scan_text(text_with_cpf)

        assert result.has_pii is True
        assert PIIType.CPF in result.pii_types_found
        assert len(result.detected_instances[PIIType.CPF]) == 1
        assert result.detected_instances[PIIType.CPF][0]["value"] == "123.456.789-01"
        assert result.confidence_score > 0.9

    def test_brazilian_rg_detection(self, pii_service):
        """Test Brazilian RG detection."""
        text_with_rg = "Identidade: MG-12.345.678 para verificação."
        result = pii_service.scan_text(text_with_rg)

        assert result.has_pii is True
        assert PIIType.RG in result.pii_types_found
        assert len(result.detected_instances[PIIType.RG]) == 1

    def test_brazilian_cnpj_detection(self, pii_service):
        """Test Brazilian CNPJ detection."""
        text_with_cnpj = "Empresa CNPJ: 12.345.678/0001-95 localizada em São Paulo."
        result = pii_service.scan_text(text_with_cnpj)

        assert result.has_pii is True
        assert PIIType.CNPJ in result.pii_types_found
        assert len(result.detected_instances[PIIType.CNPJ]) == 1

    def test_email_detection(self, pii_service):
        """Test email detection."""
        text_with_email = "Contato: joao.silva@empresa.com.br para mais informações."
        result = pii_service.scan_text(text_with_email)

        assert result.has_pii is True
        assert PIIType.EMAIL in result.pii_types_found
        assert len(result.detected_instances[PIIType.EMAIL]) == 1

    def test_phone_detection(self, pii_service):
        """Test Brazilian phone detection."""
        text_with_phone = "Telefone: (11) 98765-4321 ou +55 11 98765-4321."
        result = pii_service.scan_text(text_with_phone)

        assert result.has_pii is True
        assert PIIType.PHONE in result.pii_types_found
        # Should detect both phone numbers
        assert len(result.detected_instances[PIIType.PHONE]) == 2

    def test_multiple_pii_types(self, pii_service):
        """Test detection of multiple PII types."""
        text_with_multiple = """
        João Silva
        Email: joao.silva@empresa.com
        CPF: 123.456.789-01
        Telefone: (11) 98765-4321
        Endereço: Rua das Flores, 123, São Paulo, SP
        CEP: 01234-567
        """
        result = pii_service.scan_text(text_with_multiple)

        assert result.has_pii is True
        assert PIIType.EMAIL in result.pii_types_found
        assert PIIType.CPF in result.pii_types_found
        assert PIIType.PHONE in result.pii_types_found
        assert PIIType.ADDRESS in result.pii_types_found
        assert PIIType.POSTAL_CODE in result.pii_types_found
        assert len(result.pii_types_found) >= 5

    def test_no_pii_detection(self, pii_service):
        """Test text without PII."""
        clean_text = """
        Desenvolvedor Python com 5 anos de experiência.
        Habilidades: Python, Django, PostgreSQL.
        Formação: Bacharel em Ciência da Computação.
        """
        result = pii_service.scan_text(clean_text)

        assert result.has_pii is False
        assert len(result.pii_types_found) == 0
        assert len(result.detected_instances) == 0
        assert result.confidence_score == 0.0

    def test_pii_masking(self, pii_service):
        """Test PII masking functionality."""
        text_with_pii = "João Silva, CPF: 123.456.789-01, Email: joao@empresa.com"
        result = pii_service.scan_text(text_with_pii)

        assert result.masked_text is not None
        assert "123.456.789-01" not in result.masked_text
        assert "joao@empresa.com" not in result.masked_text
        # Check that some characters are preserved (partial masking)
        assert "12***01" in result.masked_text or "12**01" in result.masked_text
        assert "j***o@empresa.com" in result.masked_text or "j***@empresa.com" in result.masked_text

    def test_lgpd_compliance_validation(self, pii_service):
        """Test LGPD compliance validation."""
        # Text with critical PII
        critical_text = "CPF: 123.456.789-01, Email: joao@empresa.com"
        result = pii_service.validate_lgpd_compliance(critical_text)

        assert result["is_compliant"] is False
        assert result["requires_masking"] is True
        assert result["pii_detected"] is True
        assert result["critical_pii_detected"] is True
        assert "Critical PII detected" in result["issues"]

        # Text without PII
        clean_text = "Desenvolvedor Python com experiência em Django."
        result = pii_service.validate_lgpd_compliance(clean_text)

        assert result["is_compliant"] is True
        assert result["requires_masking"] is False
        assert result["pii_detected"] is False


class TestResumeServicePIIIntegration:
    """Test PII integration in resume service."""

    @pytest.fixture
    def resume_service(self):
        """Create resume service with mocked dependencies."""
        with patch("app.services.resume_service.AgentManager") as mock_agent:
            mock_instance = AsyncMock()
            mock_agent.return_value = mock_instance
            return ResumeService()

    @pytest.fixture
    def sample_resume_text(self):
        """Sample resume text with PII."""
        return """
        João da Silva
        Email: joao.silva@email.com
        CPF: 123.456.789-01
        Telefone: (11) 98765-4321

        Experiência Profissional:
        - Desenvolvedor Python na Empresa XYZ (2020-presente)
        - Analista de Sistemas na Companhia ABC (2018-2020)

        Educação:
        Bacharel em Ciência da Computação - Universidade USP (2018)
        """

    @pytest.fixture
    def clean_resume_text(self):
        """Sample resume text without PII."""
        return """
        Perfil Profissional:
        Desenvolvedor Python com 5 anos de experiência.

        Experiência Profissional:
        - Desenvolvedor Python especializado em Django e FastAPI
        - Análise de sistemas e desenvolvimento de APIs REST

        Educação:
        Bacharel em Ciência da Computação

        Habilidades:
        Python, Django, FastAPI, PostgreSQL, Docker
        """

    @pytest.mark.asyncio
    async def test_resume_processing_with_pii(self, resume_service, sample_resume_text):
        """Test resume processing when PII is detected."""
        with (
            patch.object(resume_service, "_store_resume_in_db") as mock_store,
            patch.object(resume_service, "_log_pii_detection") as mock_log,
            patch.object(resume_service, "_extract_and_store_structured_resume") as mock_extract,
        ):
            mock_store.return_value = "test-resume-id"

            resume_id = await resume_service._scan_and_process_resume_text(
                text_content=sample_resume_text,
                content_type="text/markdown",
                user_id="test-user-id",
                filename="test_resume.pdf",
            )

            # Verify database was called with masked content
            mock_store.assert_called_once()
            args, kwargs = mock_store.call_args
            stored_content = args[0]  # First argument is the content

            # PII should be masked in stored content
            assert "joao.silva@email.com" not in stored_content
            assert "123.456.789-01" not in stored_content
            assert "(11) 98765-4321" not in stored_content

            # Compliance logging should be called
            mock_log.assert_called_once()

            # Structured extraction should be called
            mock_extract.assert_called_once()

            assert resume_id == "test-resume-id"

    @pytest.mark.asyncio
    async def test_resume_processing_without_pii(self, resume_service, clean_resume_text):
        """Test resume processing when no PII is detected."""
        with (
            patch.object(resume_service, "_store_resume_in_db") as mock_store,
            patch.object(resume_service, "_log_pii_detection") as mock_log,
            patch.object(resume_service, "_extract_and_store_structured_resume") as mock_extract,
        ):
            mock_store.return_value = "test-resume-id"

            resume_id = await resume_service._scan_and_process_resume_text(
                text_content=clean_resume_text,
                content_type="text/markdown",
                user_id="test-user-id",
                filename="test_resume.pdf",
            )

            # Database should be called with original content (no masking)
            mock_store.assert_called_once()
            args, kwargs = mock_store.call_args
            stored_content = args[0]

            assert stored_content == clean_resume_text

            # Compliance logging should NOT be called for no PII
            mock_log.assert_not_called()

            assert resume_id == "test-resume-id"

    @pytest.mark.asyncio
    async def test_pii_detection_logging(self, resume_service, sample_resume_text):
        """Test PII detection compliance logging."""
        with patch.object(audit_trail, "log_compliance_event") as mock_audit_log:
            # Create a mock PII result
            pii_result = PIIDetectionResult(
                has_pii=True,
                pii_types_found=[PIIType.EMAIL, PIIType.CPF, PIIType.PHONE],
                detected_instances={
                    PIIType.EMAIL: [{"value": "joao.silva@email.com", "confidence": 0.98}],
                    PIIType.CPF: [{"value": "123.456.789-01", "confidence": 0.95}],
                    PIIType.PHONE: [{"value": "(11) 98765-4321", "confidence": 0.90}],
                },
                confidence_score=0.94,
                scan_duration_ms=15.5,
            )

            await resume_service._log_pii_detection(
                user_id="test-user-id",
                filename="test_resume.pdf",
                pii_result=pii_result,
                original_length=500,
                masked_length=450,
            )

            # Verify compliance event was logged
            mock_audit_log.assert_called_once()
            args, kwargs = mock_audit_log.call_args
            compliance_event = args[0]

            assert compliance_event.compliance_type == ComplianceType.PII_DETECTION
            assert compliance_event.check_type == "resume_upload_scan"
            assert compliance_event.status == ComplianceStatus.WARNING
            assert compliance_event.affected_records == 1
            assert "email" in compliance_event.details["pii_types_found"]
            assert "cpf" in compliance_event.details["pii_types_found"]
            assert "phone" in compliance_event.details["pii_types_found"]
            assert compliance_event.details["confidence_score"] == 0.94
            assert compliance_event.details["lgpd_action"] == "masked_before_storage"


class TestJobServicePIIIntegration:
    """Test PII integration in job service."""

    @pytest.fixture
    def job_service(self):
        """Create job service with mocked dependencies."""
        with patch("app.services.job_service.AgentManager") as mock_agent:
            mock_instance = AsyncMock()
            mock_agent.return_value = mock_instance
            return JobService()

    @pytest.fixture
    def sample_job_text(self):
        """Sample job description with PII."""
        return """
        Vaga: Desenvolvedor Python Sênior

        Empresa: Tech Solutions Brasil
        Contato: maria.silva@techsolutions.com
        Telefone: (21) 12345-6789
        CNPJ: 12.345.678/0001-95

        Descrição:
        Procuramos desenvolvedor Python para trabalhar em projetos inovadores.
        Endereço: Av. Paulista, 1000, São Paulo, SP.
        """

    @pytest.fixture
    def clean_job_text(self):
        """Sample job description without PII."""
        return """
        Vaga: Desenvolvedor Python Sênior

        Descrição:
        Procuramos desenvolvedor Python experiente para trabalhar em projetos
        de desenvolvimento de aplicações web e APIs REST.

        Requisitos:
        - 5+ anos de experiência com Python
        - Experiência com Django/FastAPI
        - Conhecimento em PostgreSQL e Docker

        Benefícios:
        - Trabalho remoto híbrido
        - Plano de carreira
        - Seguro saúde
        """

    @pytest.mark.asyncio
    async def test_job_processing_with_pii(self, job_service, sample_job_text):
        """Test job processing when PII is detected."""
        with (
            patch.object(job_service, "_extract_and_store_structured_job") as mock_extract,
            patch.object(job_service, "_log_job_pii_detection") as mock_log,
        ):
            processed_content = await job_service._scan_and_process_job_text(
                job_description=sample_job_text,
                job_id="test-job-id",
                resume_id="test-resume-id",
                job_index=0,
            )

            # PII should be masked in processed content
            assert "maria.silva@techsolutions.com" not in processed_content
            assert "(21) 12345-6789" not in processed_content
            assert "12.345.678/0001-95" not in processed_content
            assert "Av. Paulista, 1000" not in processed_content

            # Compliance logging should be called
            mock_log.assert_called_once()

            # Structured extraction should be called with masked content
            mock_extract.assert_called_once_with(
                job_id="test-job-id", job_description_text=processed_content
            )

    @pytest.mark.asyncio
    async def test_job_processing_without_pii(self, job_service, clean_job_text):
        """Test job processing when no PII is detected."""
        with (
            patch.object(job_service, "_extract_and_store_structured_job") as mock_extract,
            patch.object(job_service, "_log_job_pii_detection") as mock_log,
        ):
            processed_content = await job_service._scan_and_process_job_text(
                job_description=clean_job_text,
                job_id="test-job-id",
                resume_id="test-resume-id",
                job_index=0,
            )

            # Content should remain unchanged
            assert processed_content == clean_job_text

            # Compliance logging should NOT be called
            mock_log.assert_not_called()

            # Structured extraction should be called with original content
            mock_extract.assert_called_once_with(
                job_id="test-job-id", job_description_text=clean_job_text
            )


class TestPIIPerformance:
    """Test PII detection performance impact."""

    def test_pii_scan_performance(self):
        """Test PII scan performance is acceptable."""
        # Create a large text sample
        large_text = "Desenvolvedor Python com experiência em Django. " * 1000
        large_text += " Meu email: joao.silva@empresa.com. Meu CPF: 123.456.789-01."

        start_time = datetime.now()
        result = pii_detector.scan_text(large_text)
        end_time = datetime.now()

        scan_duration = (end_time - start_time).total_seconds() * 1000  # Convert to ms

        # Performance should be under 100ms for typical resume/job sizes
        assert scan_duration < 100.0, f"PII scan took too long: {scan_duration}ms"
        assert result.scan_duration_ms is not None
        assert result.scan_duration_ms < 100.0

    def test_masking_performance(self):
        """Test PII masking performance is acceptable."""
        # Text with multiple PII instances
        text_with_pii = (
            """
        João Silva - joao.silva@email.com - (11) 98765-4321
        Maria Santos - maria.santos@empresa.com - (21) 12345-6789
        CPFs: 123.456.789-01, 987.654.321-00
        CNPJ: 12.345.678/0001-95
        """
            * 100
        )  # Repeat for performance testing

        start_time = datetime.now()
        masked_text = pii_detector.mask_text(text_with_pii)
        end_time = datetime.now()

        masking_duration = (end_time - start_time).total_seconds() * 1000

        # Masking should be fast even with multiple PII instances
        assert masking_duration < 50.0, f"PII masking took too long: {masking_duration}ms"
        assert len(masked_text) > 0
        assert masked_text != text_with_pii


class TestPIIIntegrationEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """Test PII detection with empty text."""
        result = pii_detector.scan_text("")

        assert result.has_pii is False
        assert len(result.pii_types_found) == 0
        assert result.confidence_score == 0.0
        assert result.masked_text == ""

    @pytest.mark.asyncio
    async def test_unicode_text_handling(self):
        """Test PII detection with Unicode characters."""
        unicode_text = "João Silva 📧 joão.silva@empresa.com 📱 (11) 98765-4321 CPF: 123.456.789-01"
        result = pii_detector.scan_text(unicode_text)

        assert result.has_pii is True
        assert PIIType.EMAIL in result.pii_types_found
        assert PIIType.CPF in result.pii_types_found
        assert PIIType.PHONE in result.pii_types_found

    def test_malformed_pii_patterns(self):
        """Test detection of malformed PII patterns."""
        malformed_text = """
        CPF: 123.456.789   (incomplete)
        Email: joao@empresa   (incomplete)
        Telefone: 123456   (incomplete)
        """
        result = pii_detector.scan_text(malformed_text)

        # Should not detect malformed PII
        assert result.has_pii is False or len(result.detected_instances) == 0

    @pytest.mark.asyncio
    async def test_pii_service_failure_handling(self):
        """Test handling when PII service fails."""
        # Mock PII detector to raise exception
        with patch.object(pii_detector, "scan_text", side_effect=Exception("PII service error")):
            resume_service = ResumeService()

            with pytest.raises(Exception) as exc_info:
                await resume_service._scan_and_process_resume_text(
                    text_content="test content",
                    content_type="text/markdown",
                    user_id="test-user",
                    filename="test.pdf",
                )

            assert "PII detection error" in str(exc_info.value)
            assert "LGPD compliance" in str(exc_info.value)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
