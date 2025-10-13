"""
Authorization tests for resume endpoints.
Tests user authorization and data isolation to ensure users can only access their own resumes.
This is critical for LGPD compliance and security.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.endpoints.resumes import delete_resume, get_resume, list_resumes, upload_resume
from app.models.resume import ResumeResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService


@pytest.fixture
def mock_user_1():
    """Mock user 1 for testing."""
    return {"id": "user-123", "email": "user1@example.com", "name": "User One"}


@pytest.fixture
def mock_user_2():
    """Mock user 2 for testing."""
    return {"id": "user-456", "email": "user2@example.com", "name": "User Two"}


@pytest.fixture
def mock_resume_data():
    """Mock resume data for testing."""
    return {
        "resume_id": "resume-123",
        "content": "Sample resume content",
        "content_type": "text/markdown",
        "user_id": "user-123",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": None,
    }


@pytest.fixture
def mock_resume_service():
    """Mock ResumeService for testing."""
    service = AsyncMock(spec=ResumeService)
    return service


class TestResumeUploadAuthorization:
    """Test authorization for resume upload endpoint."""

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_upload_resume_with_user_id(self, mock_service_class, mock_user_1):
        """Test that resume upload includes user_id in service call."""
        mock_service = AsyncMock()
        mock_service.convert_and_store_resume.return_value = "resume-123"
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": {
                "content": "Sample content",
                "content_type": "text/markdown",
                "created_at": "2024-01-01T00:00:00Z",
            },
        }
        mock_service_class.return_value = mock_service

        # Mock file upload
        mock_file = MagicMock()
        mock_file.content_type = "application/pdf"
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"pdf content")

        # Call upload endpoint
        result = await upload_resume(mock_file, mock_user_1)

        # Verify service was called with user_id
        mock_service.convert_and_store_resume.assert_called_once_with(
            file_bytes=b"pdf content",
            file_type="application/pdf",
            filename="test.pdf",
            content_type="md",
            user_id="user-123",  # CRITICAL: User ID must be passed
        )

        # Verify response includes user_id
        assert isinstance(result, ResumeUploadResponse)
        assert result.user_id == "user-123"

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_upload_resume_without_user_id_fails(self, mock_service_class, mock_user_1):
        """Test that resume upload fails if user_id is not provided."""
        mock_service = AsyncMock()
        mock_service.convert_and_store_resume.side_effect = ValueError(
            "user_id is required for resume storage"
        )
        mock_service_class.return_value = mock_service

        # Mock file upload
        mock_file = MagicMock()
        mock_file.content_type = "application/pdf"
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"pdf content")

        # Call upload endpoint should raise HTTPException
        with pytest.raises(HTTPException, status_code=500):
            await upload_resume(mock_file, mock_user_1)


class TestResumeGetAuthorization:
    """Test authorization for resume get endpoint."""

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_get_own_resume_success(self, mock_service_class, mock_user_1, mock_resume_data):
        """Test that user can successfully get their own resume."""
        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": mock_resume_data,
        }
        mock_service_class.return_value = mock_service

        result = await get_resume("resume-123", mock_user_1)

        # Verify successful response
        assert isinstance(result, ResumeResponse)
        assert result.id == "resume-123"
        assert result.user_id == "user-123"

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_get_other_user_resume_forbidden(
        self, mock_service_class, mock_user_2, mock_resume_data
    ):
        """Test that user cannot access another user's resume."""
        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": mock_resume_data,  # This resume belongs to user-123
        }
        mock_service_class.return_value = mock_service

        # User 2 tries to access user 1's resume
        with pytest.raises(HTTPException) as exc_info:
            await get_resume("resume-123", mock_user_2)

        # Verify access denied
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_get_nonexistent_resume_not_found(self, mock_service_class, mock_user_1):
        """Test that getting non-existent resume returns 404."""
        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = None
        mock_service_class.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await get_resume("nonexistent-resume", mock_user_1)

        assert exc_info.value.status_code == 404
        assert "Resume not found" in str(exc_info.value.detail)

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_get_resume_without_user_id_forbidden(
        self, mock_service_class, mock_user_1, mock_resume_data
    ):
        """Test that resume without user_id cannot be accessed."""
        mock_resume_data_no_user = mock_resume_data.copy()
        mock_resume_data_no_user["user_id"] = None

        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": mock_resume_data_no_user,
        }
        mock_service_class.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await get_resume("resume-123", mock_user_1)

        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)


class TestResumeListAuthorization:
    """Test authorization for resume list endpoint."""

    @patch("app.services.supabase.database.SupabaseDatabaseService")
    @pytest.mark.asyncio
    async def test_list_own_resumes_only(self, mock_db_service_class, mock_user_1):
        """Test that list endpoint only returns user's own resumes."""
        mock_service = AsyncMock()

        # Mock resumes belonging to user 1 and user 2
        mock_resumes = [
            {
                "resume_id": "resume-1",
                "content": "Resume 1 content",
                "content_type": "text/markdown",
                "user_id": "user-123",  # User 1's resume
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "resume_id": "resume-2",
                "content": "Resume 2 content",
                "content_type": "text/markdown",
                "user_id": "user-456",  # User 2's resume
                "created_at": "2024-01-02T00:00:00Z",
            },
        ]

        # Service should filter by user_id
        mock_service.list.side_effect = Exception("Model class error")
        mock_service.supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.offset.return_value.execute.return_value = MagicMock(
            data=[mock_resumes[0]]
        )
        mock_db_service_class.return_value = mock_service

        result = await list_resumes(limit=10, offset=0, current_user=mock_user_1)

        # Verify only user 1's resumes are returned
        assert len(result.resumes) == 1
        assert result.resumes[0].user_id == "user-123"
        assert result.resumes[0].id == "resume-1"

        # Verify database query was filtered by user_id
        mock_service.supabase.table.assert_called_with("resumes")
        mock_service.supabase.table.return_value.select.return_value.eq.assert_called_with(
            "user_id", "user-123"
        )

    @patch("app.services.supabase.database.SupabaseDatabaseService")
    @pytest.mark.asyncio
    async def test_list_resumes_logs_security_violations(self, mock_db_service_class, mock_user_1):
        """Test that security violations are logged when user receives wrong resumes."""
        mock_service = AsyncMock()

        # Mock resumes with wrong user_id (simulating RLS bypass)
        wrong_resumes = [
            {
                "resume_id": "wrong-resume",
                "content": "Wrong resume content",
                "content_type": "text/markdown",
                "user_id": "malicious-user",  # Wrong user!
                "created_at": "2024-01-01T00:00:00Z",
            }
        ]

        mock_service.list.side_effect = Exception("Model class error")
        mock_service.supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.offset.return_value.execute.return_value = MagicMock(
            data=wrong_resumes
        )
        mock_db_service_class.return_value = mock_service

        with patch("app.api.endpoints.resumes.logger") as mock_logger:
            result = await list_resumes(limit=10, offset=0, current_user=mock_user_1)

            # Should return empty list (filtering out wrong resumes)
            assert len(result.resumes) == 0

            # Should log security violation
            mock_logger.error.assert_called_once()
            assert "SECURITY VIOLATION" in mock_logger.error.call_args[0][0]


class TestResumeDeleteAuthorization:
    """Test authorization for resume delete endpoint."""

    @patch("app.api.endpoints.resumes.ResumeService")
    @patch("app.services.supabase.database.SupabaseDatabaseService")
    @pytest.mark.asyncio
    async def test_delete_own_resume_success(
        self, mock_db_service_class, mock_service_class, mock_user_1, mock_resume_data
    ):
        """Test that user can successfully delete their own resume."""
        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": mock_resume_data,
        }
        mock_service_class.return_value = mock_service

        mock_db_service = AsyncMock()
        mock_db_service.supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": 1}]
        )
        mock_db_service_class.return_value = mock_db_service

        # Should not raise exception
        await delete_resume("resume-123", mock_user_1)

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_delete_other_user_resume_forbidden(
        self, mock_service_class, mock_user_2, mock_resume_data
    ):
        """Test that user cannot delete another user's resume."""
        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": mock_resume_data,  # This resume belongs to user-123
        }
        mock_service_class.return_value = mock_service

        # User 2 tries to delete user 1's resume
        with pytest.raises(HTTPException) as exc_info:
            await delete_resume("resume-123", mock_user_2)

        # Verify access denied
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_delete_nonexistent_resume_not_found(self, mock_service_class, mock_user_1):
        """Test that deleting non-existent resume returns 404."""
        mock_service = AsyncMock()
        mock_service.get_resume_with_processed_data.return_value = None
        mock_service_class.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await delete_resume("nonexistent-resume", mock_user_1)

        assert exc_info.value.status_code == 404
        assert "Resume not found" in str(exc_info.value.detail)


class TestResumeServiceAuthorization:
    """Test authorization in ResumeService methods."""

    @pytest.mark.asyncio
    async def test_store_resume_requires_user_id(self):
        """Test that storing resume requires user_id."""
        resume_service = ResumeService()

        # Should raise ValueError if user_id is None
        with pytest.raises(ValueError, match="user_id is required for resume storage"):
            await resume_service._store_resume_in_db("content", "text/markdown", None)

    @patch("app.services.supabase.database.SupabaseDatabaseService")
    @pytest.mark.asyncio
    async def test_store_resume_includes_user_id(self, mock_db_service_class):
        """Test that storing resume includes user_id in data."""
        resume_service = ResumeService()

        mock_service = AsyncMock()
        mock_result = MagicMock()
        mock_result.resume_id = "test-resume-id"
        mock_service.create.return_value = mock_result
        mock_db_service_class.return_value = mock_service

        await resume_service._store_resume_in_db("test content", "text/markdown", "user-123")

        # Verify create was called with user_id
        call_args = mock_service.create.call_args[0][0]
        assert call_args["user_id"] == "user-123"
        assert call_args["content"] == "test content"
        assert call_args["content_type"] == "text/markdown"

    @patch("app.services.resume_service.SupabaseDatabaseService")
    @pytest.mark.asyncio
    async def test_get_resume_with_processed_data_includes_user_id(self, mock_db_service_class):
        """Test that get_resume_with_processed_data includes user_id in response."""
        resume_service = ResumeService()

        mock_service = AsyncMock()
        mock_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[
                {
                    "resume_id": "test-resume",
                    "content": "test content",
                    "content_type": "text/markdown",
                    "user_id": "user-123",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        )
        mock_db_service_class.return_value = mock_service

        result = await resume_service.get_resume_with_processed_data("test-resume")

        # Verify user_id is included in response
        assert result["raw_resume"]["user_id"] == "user-123"


class TestDefenseInDepth:
    """Test defense in depth - multiple layers of security."""

    @patch("app.api.endpoints.resumes.ResumeService")
    @pytest.mark.asyncio
    async def test_multiple_authorization_checks(
        self, mock_service_class, mock_user_1, mock_user_2, mock_resume_data
    ):
        """Test that multiple authorization checks work together."""
        mock_service = AsyncMock()

        # First call returns user 1's resume, second call would return user 2's
        mock_service.get_resume_with_processed_data.return_value = {
            "resume_id": "resume-123",
            "raw_resume": mock_resume_data,
        }
        mock_service_class.return_value = mock_service

        # User 2 tries to access user 1's resume multiple times
        for _ in range(3):
            with pytest.raises(HTTPException) as exc_info:
                await get_resume("resume-123", mock_user_2)

            assert exc_info.value.status_code == 403
            assert "Access denied" in str(exc_info.value.detail)

        # Verify service was called each time (defense in depth)
        assert mock_service.get_resume_with_processed_data.call_count == 3


# Integration tests that would require a real database
class TestResumeAuthorizationIntegration:
    """Integration tests for resume authorization (requires database)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_user_isolation(self, mock_user_1, mock_user_2):
        """
        Test complete user isolation flow:
        1. User 1 uploads resume
        2. User 2 cannot access User 1's resume
        3. User 1 can access their own resume
        4. User 2 cannot delete User 1's resume

        This test requires a real database with RLS policies.
        """
        # This would be implemented with real database connections
        # For now, it's a placeholder showing the intended test structure
        pass
