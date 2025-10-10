import logging
import os
import tempfile
import uuid

from markitdown import MarkItDown

from app.services.supabase.database import SupabaseDatabaseService

# TODO: These will need to be created in a later phase
# from app.agent import AgentManager
# from app.prompt import prompt_factory
# from app.schemas.json import json_schema_factory
# from app.schemas.pydantic import StructuredResumeModel

logger = logging.getLogger(__name__)


class ResumeService:
    def __init__(self):
        # Use cv-match's Supabase pattern
        self.md = MarkItDown(enable_plugins=False)

        # TODO: Initialize these when AI Integration is complete
        # self.json_agent_manager = AgentManager()

        # Validate dependencies for DOCX processing
        self._validate_docx_dependencies()

    def _validate_docx_dependencies(self):
        """Validate that required dependencies for DOCX processing are available"""
        missing_deps = []

        try:
            # Check if markitdown can handle docx files
            from markitdown.converters import DocxConverter

            # Try to instantiate the converter to check if dependencies are available
            DocxConverter()
        except ImportError:
            missing_deps.append("markitdown[all]==0.1.2")
        except Exception as e:
            if "MissingDependencyException" in str(
                e
            ) or "dependencies needed to read .docx files" in str(e):
                missing_deps.append(
                    "markitdown[all]==0.1.2 (current installation missing DOCX extras)"
                )

        if missing_deps:
            logger.warning(
                f"Missing dependencies for DOCX processing: {', '.join(missing_deps)}. "
                f"DOCX file processing may fail. Install with: pip install {' '.join(missing_deps)}"
            )

    async def convert_and_store_resume(
        self, file_bytes: bytes, file_type: str, filename: str, content_type: str = "md"
    ):
        """
        Converts resume file (PDF/DOCX) to text using MarkItDown and stores it in the database.

        Args:
            file_bytes: Raw bytes of the uploaded file
            file_type: MIME type of the file ("application/pdf" or
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            filename: Original filename
            content_type: Output format ("md" for markdown or "html")

        Returns:
            None
        """
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=self._get_file_extension(file_type)
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            try:
                result = self.md.convert(temp_path)
                text_content = result.text_content
            except Exception as e:
                # Handle specific markitdown conversion errors
                error_msg = str(e)
                if "MissingDependencyException" in error_msg or "DocxConverter" in error_msg:
                    raise Exception(
                        "File conversion failed: markitdown is missing DOCX support. "
                        "Please install with: pip install 'markitdown[all]==0.1.2' "
                        "or contact system administrator."
                    ) from e
                elif "docx" in error_msg.lower():
                    raise Exception(
                        f"DOCX file processing failed: {error_msg}. "
                        "Please ensure the file is a valid DOCX document."
                    ) from e
                else:
                    raise Exception(f"File conversion failed: {error_msg}") from e

            resume_id = await self._store_resume_in_db(text_content, content_type)

            # TODO: Uncomment when AI Integration is complete
            # await self._extract_and_store_structured_resume(
            #     resume_id=resume_id, resume_text=text_content
            # )

            return resume_id
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _get_file_extension(self, file_type: str) -> str:
        """Returns the appropriate file extension based on MIME type"""
        if file_type == "application/pdf":
            return ".pdf"
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return ".docx"
        return ""

    async def _store_resume_in_db(self, text_content: str, content_type: str):
        """
        Stores the parsed resume content in the database.
        """
        resume_id = str(uuid.uuid4())

        # Map short content types to full MIME types for database constraint
        content_type_mapping = {
            "md": "text/markdown",
            "html": "text/html",
            "plain": "text/plain",
            "text": "text/plain",
        }

        db_content_type = content_type_mapping.get(content_type, "text/markdown")

        resume_data = {
            "resume_id": resume_id,
            "content": text_content,
            "content_type": db_content_type,
        }

        # Insert resume using cv-match's Supabase service
        # Note: We'll need to create a ResumeModel, for now using dict
        service = SupabaseDatabaseService("resumes", dict)
        result = await service.create(resume_data)

        return result.resume_id if hasattr(result, "resume_id") else resume_id

    # TODO: These methods will be implemented when AI Integration is complete
    async def _extract_and_store_structured_resume(self, resume_id, resume_text: str) -> None:
        """
        extract and store structured resume data in the database
        """
        logger.info(f"Structured resume extraction not yet implemented for resume_id: {resume_id}")
        # TODO: Implement when AI Integration is complete
        pass

    async def _extract_structured_json(self, resume_text: str):
        """
        Uses the AgentManager+JSONWrapper to ask the LLM to
        return the data in exact JSON schema we need.
        """
        logger.info("Structured JSON extraction not yet implemented")
        # TODO: Implement when AI Integration is complete
        return None

    async def get_resume_with_processed_data(self, resume_id: str) -> dict | None:
        """
        Fetches both resume and processed resume data from the database and combines them.

        Args:
            resume_id: The ID of the resume to retrieve

        Returns:
            Combined data from both resume and processed_resume models

        Raises:
            ResumeNotFoundError: If the resume is not found
        """
        # Fetch resume data using cv-match's Supabase service
        service = SupabaseDatabaseService("resumes", dict)
        resume = await service.get(resume_id)

        if not resume:
            # TODO: Create and raise ResumeNotFoundError
            raise ValueError(f"Resume with ID {resume_id} not found")

        combined_data = {
            "resume_id": resume.get("resume_id") or resume_id,
            "raw_resume": {
                "id": resume.get("id"),
                "content": resume.get("content"),
                "content_type": resume.get("content_type"),
                "created_at": resume.get("created_at"),
            },
            "processed_resume": None,
        }

        # TODO: Fetch processed resume data when database structure is ready
        # processed_service = SupabaseDatabaseService("processed_resumes", dict)
        # processed_resume = await processed_service.get(resume_id)

        return combined_data
