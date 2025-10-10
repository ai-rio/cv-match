"""
Unit tests for ResumeService.
Tests resume processing, file conversion, and database storage functionality.
"""

import os
import tempfile
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.resume_service import ResumeService


@pytest.fixture
def resume_service():
    """Create ResumeService instance for testing."""
    return ResumeService()


@pytest.fixture
def mock_pdf_content():
    """Mock PDF content for testing."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n...\n%EOF"


@pytest.fixture
def mock_docx_content():
    """Mock DOCX content for testing."""
    return b"PK\x03\x04\x14\x00\x06\x00"  # Simplified DOCX header


@pytest.fixture
def sample_resume_text():
    """Sample extracted resume text."""
    return """
    João Silva
    Desenvolvedor Python Sênior

    EXPERIÊNCIA PROFISSIONAL
    Tech Corp - Desenvolvedor Python Sênior (2020-2024)
    • Desenvolvimento de APIs com FastAPI
    • Trabalho com bancos de dados PostgreSQL
    • Implementação de testes automatizados

    SKILLS
    Python, FastAPI, PostgreSQL, Docker, AWS
    """


@pytest.mark.asyncio
async def test_resume_service_initialization(resume_service):
    """Test ResumeService can be initialized successfully."""
    assert resume_service is not None
    assert hasattr(resume_service, 'md')
    assert hasattr(resume_service, '_validate_docx_dependencies')


def test_get_file_extension_pdf(resume_service):
    """Test file extension mapping for PDF."""
    ext = resume_service._get_file_extension("application/pdf")
    assert ext == ".pdf"


def test_get_file_extension_docx(resume_service):
    """Test file extension mapping for DOCX."""
    ext = resume_service._get_file_extension(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert ext == ".docx"


def test_get_file_extension_unknown(resume_service):
    """Test file extension mapping for unknown types."""
    ext = resume_service._get_file_extension("text/plain")
    assert ext == ""


@patch('app.services.resume_service.SupabaseDatabaseService')
@pytest.mark.asyncio
async def test_convert_and_store_resume_pdf_success(
    mock_db_service, resume_service, mock_pdf_content, sample_resume_text
):
    """Test successful PDF conversion and storage."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.create.return_value = MagicMock(resume_id="test-resume-123")
    mock_db_service.return_value = mock_service_instance

    # Mock MarkItDown conversion
    with patch.object(resume_service.md, 'convert') as mock_convert:
        mock_convert.return_value = MagicMock(text_content=sample_resume_text)

        result = await resume_service.convert_and_store_resume(
            file_bytes=mock_pdf_content,
            file_type="application/pdf",
            filename="test.pdf",
            content_type="md"
        )

        assert result == "test-resume-123"
        mock_convert.assert_called_once()
        mock_service_instance.create.assert_called_once()


@patch('app.services.resume_service.SupabaseDatabaseService')
@pytest.mark.asyncio
async def test_convert_and_store_resume_docx_success(
    mock_db_service, resume_service, mock_docx_content, sample_resume_text
):
    """Test successful DOCX conversion and storage."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.create.return_value = MagicMock(resume_id="test-resume-456")
    mock_db_service.return_value = mock_service_instance

    # Mock MarkItDown conversion
    with patch.object(resume_service.md, 'convert') as mock_convert:
        mock_convert.return_value = MagicMock(text_content=sample_resume_text)

        result = await resume_service.convert_and_store_resume(
            file_bytes=mock_docx_content,
            file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="test.docx",
            content_type="html"
        )

        assert result == "test-resume-456"
        mock_convert.assert_called_once()
        mock_service_instance.create.assert_called_once()


@pytest.mark.asyncio
async def test_convert_and_store_resume_conversion_failure(resume_service, mock_pdf_content):
    """Test handling of conversion failures."""
    # Mock MarkItDown conversion failure
    with patch.object(resume_service.md, 'convert') as mock_convert:
        mock_convert.side_effect = Exception("Conversion failed")

        with pytest.raises(Exception, match="File conversion failed"):
            await resume_service.convert_and_store_resume(
                file_bytes=mock_pdf_content,
                file_type="application/pdf",
                filename="test.pdf",
                content_type="md"
            )


@pytest.mark.asyncio
async def test_convert_and_store_resume_docx_dependency_error(resume_service, mock_docx_content):
    """Test handling of DOCX dependency errors."""
    # Mock MarkItDown conversion with dependency error
    with patch.object(resume_service.md, 'convert') as mock_convert:
        mock_convert.side_effect = Exception("MissingDependencyException: DOCX support missing")

        with pytest.raises(Exception, match="markitdown is missing DOCX support"):
            await resume_service.convert_and_store_resume(
                file_bytes=mock_docx_content,
                file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename="test.docx",
                content_type="md"
            )


@patch('app.services.resume_service.SupabaseDatabaseService')
@pytest.mark.asyncio
async def test_store_resume_in_db(mock_db_service, resume_service, sample_resume_text):
    """Test storing resume data in database."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.create.return_value = MagicMock(resume_id="test-resume-789")
    mock_db_service.return_value = mock_service_instance

    result = await resume_service._store_resume_in_db(sample_resume_text, "md")

    assert result == "test-resume-789"
    mock_service_instance.create.assert_called_once()

    # Verify the data structure
    call_args = mock_service_instance.create.call_args[0][0]
    assert "resume_id" in call_args
    assert call_args["content"] == sample_resume_text
    assert call_args["content_type"] == "text/markdown"


@pytest.mark.asyncio
async def test_store_resume_in_db_different_content_types(resume_service, sample_resume_text):
    """Test storing resume with different content types."""
    with patch('app.services.resume_service.SupabaseDatabaseService') as mock_db_service:
        mock_service_instance = AsyncMock()
        mock_service_instance.create.return_value = MagicMock(resume_id="test-resume-999")
        mock_db_service.return_value = mock_service_instance

        # Test markdown content type
        await resume_service._store_resume_in_db(sample_resume_text, "md")
        call_args = mock_service_instance.create.call_args[0][0]
        assert call_args["content_type"] == "text/markdown"

        # Test HTML content type
        await resume_service._store_resume_in_db(sample_resume_text, "html")
        call_args = mock_service_instance.create.call_args[0][0]
        assert call_args["content_type"] == "text/html"

        # Test plain text content type
        await resume_service._store_resume_in_db(sample_resume_text, "plain")
        call_args = mock_service_instance.create.call_args[0][0]
        assert call_args["content_type"] == "text/plain"


@patch('app.services.resume_service.SupabaseDatabaseService')
@pytest.mark.asyncio
async def test_get_resume_with_processed_data_success(mock_db_service, resume_service, sample_resume_text):
    """Test successful retrieval of resume data."""
    # Mock the database service
    mock_service_instance = AsyncMock()
    mock_service_instance.get.return_value = {
        "id": "test-id",
        "resume_id": "test-resume-123",
        "content": sample_resume_text,
        "content_type": "text/markdown",
        "created_at": "2024-01-01T00:00:00Z"
    }
    mock_db_service.return_value = mock_service_instance

    result = await resume_service.get_resume_with_processed_data("test-resume-123")

    assert result is not None
    assert result["resume_id"] == "test-resume-123"
    assert result["raw_resume"]["content"] == sample_resume_text
    assert result["processed_resume"] is None  # TODO: Update when processed data is implemented


@pytest.mark.asyncio
async def test_get_resume_with_processed_data_not_found(resume_service):
    """Test handling of resume not found."""
    with patch('app.services.resume_service.SupabaseDatabaseService') as mock_db_service:
        mock_service_instance = AsyncMock()
        mock_service_instance.get.return_value = None
        mock_db_service.return_value = mock_service_instance

        with pytest.raises(ValueError, match="Resume with ID test-resume-999 not found"):
            await resume_service.get_resume_with_processed_data("test-resume-999")


@pytest.mark.asyncio
async def test_extract_and_store_structured_resume_not_implemented(resume_service):
    """Test that structured resume extraction is not yet implemented."""
    # This should not raise an error but log info
    await resume_service._extract_and_store_structured_resume("test-id", "sample text")
    # Method should complete without error (logs info message)


@pytest.mark.asyncio
async def test_extract_structured_json_not_implemented(resume_service):
    """Test that structured JSON extraction is not yet implemented."""
    result = await resume_service._extract_structured_json("sample text")
    assert result is None


def test_validate_docx_dependencies_missing(resume_service):
    """Test validation of DOCX dependencies when missing."""
    with patch('app.services.resume_service.logger') as mock_logger:
        # Simulate missing dependency
        with patch('markitdown.converters.DocxConverter', side_effect=ImportError):
            resume_service._validate_docx_dependencies()
            mock_logger.warning.assert_called()


def test_validate_docx_dependencies_available(resume_service):
    """Test validation of DOCX dependencies when available."""
    with patch('markitdown.converters.DocxConverter') as mock_converter:
        mock_converter.return_value = MagicMock()

        # Should not raise any warnings
        with patch('app.services.resume_service.logger') as mock_logger:
            resume_service._validate_docx_dependencies()
            mock_logger.warning.assert_not_called()


@pytest.mark.asyncio
async def test_convert_and_store_resume_temp_file_cleanup(resume_service, mock_pdf_content):
    """Test that temporary files are properly cleaned up."""
    temp_files_before = []
    temp_files_during = []

    with patch('app.services.resume_service.SupabaseDatabaseService') as mock_db_service:
        mock_service_instance = AsyncMock()
        mock_service_instance.create.return_value = MagicMock(resume_id="test-resume")
        mock_db_service.return_value = mock_service_instance

        with patch.object(resume_service.md, 'convert') as mock_convert:
            mock_convert.return_value = MagicMock(text_content="sample text")

            # Track temp files
            with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
                mock_file = MagicMock()
                mock_file.name = "/tmp/test_temp_file.pdf"
                mock_temp_file.return_value.__enter__.return_value = mock_file

                with patch('os.path.exists') as mock_exists:
                    with patch('os.remove') as mock_remove:
                        mock_exists.return_value = True

                        await resume_service.convert_and_store_resume(
                            file_bytes=mock_pdf_content,
                            file_type="application/pdf",
                            filename="test.pdf",
                            content_type="md"
                        )

                        # Verify cleanup
                        mock_remove.assert_called_once_with("/tmp/test_temp_file.pdf")