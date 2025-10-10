"""
Unit tests for JobService.
Tests job creation, storage, and data processing functionality.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.job_service import JobService


@pytest.fixture
def job_service():
    """Create JobService instance for testing."""
    return JobService()


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "resume_id": "test-resume-123",
        "job_descriptions": [
            "Desenvolvedor Python Sênior na Tech Corp",
            "Analista de Dados Pleno na DataCorp",
        ],
    }


@pytest.fixture
def sample_job_description():
    """Sample job description text."""
    return """
    VAGA: Desenvolvedor Python Sênior

    Empresa: TechCorp Brasil
    Localização: São Paulo/SP (Remoto)

    Descrição:
    Procuramos um Desenvolvedor Python Sênior para nossa equipe.

    Requisitos:
    • 5+ anos de experiência com Python
    • Experiência com FastAPI e Django
    • Conhecimento em PostgreSQL e MongoDB
    • Experiência com Docker e AWS

    Responsabilidades:
    • Desenvolver e manter APIs REST
    • Otimizar performance de aplicações
    • Mentoria para desenvolvedores júnior

    Benefícios:
    • Salário competitivo
    • Plano de saúde e odontológico
    • Vale alimentação e transporte
    """


@pytest.mark.asyncio
async def test_job_service_initialization(job_service):
    """Test JobService can be initialized successfully."""
    assert job_service is not None
    # TODO: Add assertions for agent manager when AI Integration is complete


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_create_and_store_job_success(mock_db_service, job_service, sample_job_data):
    """Test successful job creation and storage."""
    # Mock the database service for jobs
    mock_job_service_instance = AsyncMock()
    mock_job_service_instance.create.return_value = MagicMock(job_id="test-job-123")
    mock_db_service.return_value = mock_job_service_instance

    # Mock the database service for processed jobs
    mock_processed_service_instance = AsyncMock()
    mock_processed_service_instance.create.return_value = MagicMock(id="processed-123")

    # Mock resume check
    with patch.object(job_service, "_is_resume_available", return_value=True):
        with patch.object(
            job_service, "_extract_and_store_structured_job", return_value="test-job-123"
        ) as mock_extract:
            result = await job_service.create_and_store_job(sample_job_data)

            assert len(result) == 2
            assert all(job_id.startswith("test-job-") for job_id in result)
            assert mock_extract.call_count == 2


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_create_and_store_job_resume_not_found(mock_db_service, job_service, sample_job_data):
    """Test job creation when resume is not found."""
    # Mock resume check to return False
    with patch.object(job_service, "_is_resume_available", return_value=False):
        with pytest.raises(
            AssertionError, match="resume corresponding to resume_id: test-resume-123 not found"
        ):
            await job_service.create_and_store_job(sample_job_data)


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_create_and_store_job_empty_job_descriptions(mock_db_service, job_service):
    """Test job creation with empty job descriptions."""
    empty_job_data = {"resume_id": "test-resume-123", "job_descriptions": []}

    # Mock resume check
    with patch.object(job_service, "_is_resume_available", return_value=True):
        result = await job_service.create_and_store_job(empty_job_data)

        assert len(result) == 0


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_create_and_store_job_single_description(
    mock_db_service, job_service, sample_job_description
):
    """Test job creation with single job description."""
    job_data = {"resume_id": "test-resume-123", "job_descriptions": [sample_job_description]}

    # Mock the database service
    mock_job_service_instance = AsyncMock()
    mock_job_service_instance.create.return_value = MagicMock(job_id="test-job-single")
    mock_db_service.return_value = mock_job_service_instance

    # Mock resume check and extraction
    with patch.object(job_service, "_is_resume_available", return_value=True):
        with patch.object(
            job_service, "_extract_and_store_structured_job", return_value="test-job-single"
        ) as mock_extract:
            result = await job_service.create_and_store_job(job_data)

            assert len(result) == 1
            assert result[0] == "test-job-single"
            mock_extract.assert_called_once()


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_is_resume_available_true(mock_db_service, job_service):
    """Test resume availability check when resume exists."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.get.return_value = {"id": "test-resume", "content": "sample content"}
    mock_db_service.return_value = mock_service_instance

    result = await job_service._is_resume_available("test-resume-123")

    assert result is True
    mock_service_instance.get.assert_called_once_with("test-resume-123")


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_is_resume_available_false(mock_db_service, job_service):
    """Test resume availability check when resume doesn't exist."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.get.return_value = None
    mock_db_service.return_value = mock_service_instance

    result = await job_service._is_resume_available("test-resume-999")

    assert result is False
    mock_service_instance.get.assert_called_once_with("test-resume-999")


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_extract_and_store_structured_job_success(
    mock_db_service, job_service, sample_job_description
):
    """Test successful structured job extraction and storage."""
    # Mock the processed jobs database service
    mock_processed_service_instance = AsyncMock()
    mock_processed_service_instance.create.return_value = MagicMock(id="processed-job-123")

    with patch.object(job_service, "_extract_structured_json") as mock_extract:
        mock_extract.return_value = {
            "job_title": "Desenvolvedor Python Sênior",
            "company_profile": "TechCorp Brasil",
            "location": "São Paulo/SP",
            "date_posted": "2024-01-15",
            "employment_type": "Full-time",
            "job_summary": "Oportunidade para desenvolvedor Python experiente...",
            "key_responsibilities": ["Desenvolver APIs", "Otimizar performance"],
            "qualifications": ["Python", "FastAPI", "PostgreSQL"],
            "compensation_and_benfits": ["Salário competitivo", "Plano de saúde"],
            "application_info": ["Enviar currículo para careers@techcorp.com"],
            "extracted_keywords": ["Python", "FastAPI", "AWS", "Docker"],
        }

        # Mock the database service call
        with patch("app.services.job_service.SupabaseDatabaseService") as mock_db_service_class:
            mock_db_service_class.return_value = mock_processed_service_instance

            result = await job_service._extract_and_store_structured_job(
                job_id="test-job-123", job_description_text=sample_job_description
            )

            assert result == "test-job-123"
            mock_processed_service_instance.create.assert_called_once()


@pytest.mark.asyncio
async def test_extract_and_store_structured_job_extraction_failed(job_service):
    """Test structured job extraction when extraction fails."""
    with patch.object(job_service, "_extract_structured_json", return_value=None):
        result = await job_service._extract_and_store_structured_job(
            job_id="test-job-123", job_description_text="sample text"
        )

        assert result is None


@pytest.mark.asyncio
async def test_extract_structured_json_mock_response(job_service, sample_job_description):
    """Test structured JSON extraction with mock response (since AI integration not complete)."""
    result = await job_service._extract_structured_json(sample_job_description)

    assert result is not None
    assert "job_title" in result
    assert "company_profile" in result
    assert "location" in result
    assert result["job_title"] == "Sample Job"
    assert result["company_profile"] == "Sample Company"


@pytest.mark.asyncio
async def test_extract_structured_json_empty_text(job_service):
    """Test structured JSON extraction with empty text."""
    result = await job_service._extract_structured_json("")

    assert result is not None
    assert "job_title" in result
    assert "job_summary" in result
    # Should still return mock data for empty input


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_get_job_with_processed_data_success(mock_db_service, job_service):
    """Test successful retrieval of job data."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.get.return_value = {
        "id": "test-id",
        "job_id": "test-job-123",
        "resume_id": "test-resume-456",
        "content": "Sample job description",
        "created_at": "2024-01-01T00:00:00Z",
    }
    mock_db_service.return_value = mock_service_instance

    result = await job_service.get_job_with_processed_data("test-job-123")

    assert result is not None
    assert result["job_id"] == "test-job-123"
    assert result["raw_job"]["content"] == "Sample job description"
    assert result["processed_job"] is None  # TODO: Update when processed data is implemented


@pytest.mark.asyncio
async def test_get_job_with_processed_data_not_found(job_service):
    """Test handling of job not found."""
    with patch("app.services.job_service.SupabaseDatabaseService") as mock_db_service:
        mock_service_instance = AsyncMock()
        mock_service_instance.get.return_value = None
        mock_db_service.return_value = mock_service_instance

        with pytest.raises(ValueError, match="Job with ID test-job-999 not found"):
            await job_service.get_job_with_processed_data("test-job-999")


@patch("app.services.job_service.SupabaseDatabaseService")
@pytest.mark.asyncio
async def test_extract_and_store_structured_job_data_structure(
    mock_db_service, job_service, sample_job_description
):
    """Test that structured job data is properly formatted before storage."""
    # Mock the processed jobs database service
    mock_processed_service_instance = AsyncMock()
    mock_processed_service_instance.create.return_value = MagicMock(id="processed-job-123")

    with patch.object(job_service, "_extract_structured_json") as mock_extract:
        mock_extract.return_value = {
            "job_title": "Test Job",
            "company_profile": "Test Company",
            "location": "Test Location",
            "date_posted": "2024-01-15",
            "employment_type": "Full-time",
            "job_summary": "Test job summary",
            "key_responsibilities": ["Responsibility 1", "Responsibility 2"],
            "qualifications": ["Qualification 1", "Qualification 2"],
            "compensation_and_benfits": ["Benefit 1", "Benefit 2"],
            "application_info": ["Info 1"],
            "extracted_keywords": ["Keyword 1", "Keyword 2"],
        }

        with patch("app.services.job_service.SupabaseDatabaseService") as mock_db_service_class:
            mock_db_service_class.return_value = mock_processed_service_instance

            await job_service._extract_and_store_structured_job(
                job_id="test-job-123", job_description_text=sample_job_description
            )

            # Verify the data structure passed to database
            call_args = mock_processed_service_instance.create.call_args[0][0]

            assert call_args["job_id"] == "test-job-123"
            assert call_args["job_title"] == "Test Job"
            assert call_args["company_profile"] == "Test Company"
            assert call_args["key_responsibilities"]["key_responsibilities"] == [
                "Responsibility 1",
                "Responsibility 2",
            ]
            assert call_args["extracted_keywords"]["extracted_keywords"] == [
                "Keyword 1",
                "Keyword 2",
            ]


@pytest.mark.asyncio
async def test_extract_and_store_structured_job_handles_none_values(
    mock_db_service, job_service, sample_job_description
):
    """Test that structured job extraction handles None values properly."""
    # Mock the processed jobs database service
    mock_processed_service_instance = AsyncMock()
    mock_processed_service_instance.create.return_value = MagicMock(id="processed-job-123")

    with patch.object(job_service, "_extract_structured_json") as mock_extract:
        mock_extract.return_value = {
            "job_title": "Test Job",
            "company_profile": None,
            "location": None,
            "date_posted": "2024-01-15",
            "employment_type": "Full-time",
            "job_summary": "Test job summary",
            "key_responsibilities": None,
            "qualifications": None,
            "compensation_and_benfits": None,
            "application_info": None,
            "extracted_keywords": None,
        }

        with patch("app.services.job_service.SupabaseDatabaseService") as mock_db_service_class:
            mock_db_service_class.return_value = mock_processed_service_instance

            await job_service._extract_and_store_structured_job(
                job_id="test-job-123", job_description_text=sample_job_description
            )

            # Verify None values are handled properly
            call_args = mock_processed_service_instance.create.call_args[0][0]

            assert call_args["job_id"] == "test-job-123"
            assert call_args["job_title"] == "Test Job"
            assert call_args["company_profile"] is None
            assert call_args["location"] is None
            assert call_args["key_responsibilities"] is None
