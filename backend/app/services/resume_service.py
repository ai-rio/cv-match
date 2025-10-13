import logging
import os
import tempfile
import uuid

from markitdown import MarkItDown

from app.agent.manager import AgentManager
from app.core.exceptions import ProviderError
from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)


class ResumeService:
    def __init__(self):
        # Use cv-match's Supabase pattern
        self.md = MarkItDown(enable_plugins=False)

        try:
            self.agent_manager = AgentManager()
            logger.info("ResumeService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ResumeService: {e}")
            raise

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
        self,
        file_bytes: bytes,
        file_type: str,
        filename: str,
        content_type: str = "md",
        user_id: str = None,
    ):
        """
        Converts resume file (PDF/DOCX) to text using MarkItDown and stores it in the database.

        Args:
            file_bytes: Raw bytes of the uploaded file
            file_type: MIME type of the file ("application/pdf" or
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            filename: Original filename
            content_type: Output format ("md" for markdown or "html")
            user_id: User ID who owns this resume (required for security)

        Returns:
            Resume ID of the created resume
        """
        if user_id is None:
            raise ValueError("user_id is required for resume storage")
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

            resume_id = await self._store_resume_in_db(text_content, content_type, user_id)

            # Extract and store structured resume data
            await self._extract_and_store_structured_resume(
                resume_id=resume_id, resume_text=text_content
            )

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

    async def _store_resume_in_db(self, text_content: str, content_type: str, user_id: str):
        """
        Stores the parsed resume content in the database with user ownership.

        Args:
            text_content: Extracted text content from resume
            content_type: Type of content (text/markdown, text/html, etc.)
            user_id: User ID who owns this resume

        Returns:
            Resume ID of the created resume
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
            "user_id": user_id,  # CRITICAL: User ownership for security
        }

        # Insert resume using cv-match's Supabase service
        service = SupabaseDatabaseService("resumes", dict)
        result = await service.create(resume_data)

        logger.info(f"Resume {resume_id} stored for user {user_id}")
        return result.resume_id if hasattr(result, "resume_id") else resume_id

    async def _extract_and_store_structured_resume(self, resume_id, resume_text: str) -> None:
        """
        extract and store structured resume data in the database
        """
        try:
            structured_resume = await self._extract_structured_json(resume_text)
            if not structured_resume:
                logger.warning(f"Structured resume extraction failed for resume_id: {resume_id}")
                return None

            processed_resume_data = {
                "resume_id": resume_id,
                "personal_info": structured_resume.get("personal_info", {}),
                "work_experience": structured_resume.get("work_experience", []),
                "education": structured_resume.get("education", []),
                "skills": structured_resume.get("skills", []),
                "languages": structured_resume.get("languages", []),
                "certifications": structured_resume.get("certifications", []),
                "projects": structured_resume.get("projects", []),
                "summary": structured_resume.get("summary"),
                "extracted_keywords": structured_resume.get("extracted_keywords", []),
            }

            # Store processed resume using cv-match's Supabase service
            processed_service = SupabaseDatabaseService("processed_resumes", dict)
            await processed_service.create(processed_resume_data)

            logger.info(f"Structured resume data stored for resume_id: {resume_id}")
            return None

        except Exception as e:
            logger.error(
                f"Error extracting/storing structured resume for resume_id {resume_id}: {e}"
            )
            # Don't fail the entire upload if structured extraction fails
            # Just log the error and continue with raw resume storage
            pass

    async def _extract_structured_json(self, resume_text: str):
        """
        Uses the AgentManager+JSONWrapper to ask the LLM to
        return the data in exact JSON schema we need.
        """
        try:
            # Build structured extraction prompt for Brazilian market
            prompt = f"""
            Você é um especialista em análise de currículos para o mercado brasileiro.

            Analise este currículo e extraia as informações estruturadas em formato JSON válido:

            CURRÍCULO:
            {resume_text}

            Retorne um JSON com as seguintes chaves:
            - personal_info: Objeto com informações pessoais (nome, email, telefone, linkedin, etc.)
            - summary: Resumo profissional (string, opcional)
            - work_experience: Lista de experiências profissionais, cada uma com: empresa, cargo, período, descrição
            - education: Lista de formações acadêmicas, cada uma com: instituição, curso, nível, período, status
            - skills: Lista de competências técnicas (array de strings)
            - languages: Lista de idiomas com proficiência (array de objetos)
            - certifications: Lista de certificações (array de objetos)
            - projects: Lista de projetos relevantes (array de objetos)
            - extracted_keywords: Lista de palavras-chave importantes para ATS (array de strings)

            IMPORTANTE: Retorne apenas o JSON válido, sem texto adicional. Se alguma informação não estiver presente, não inclua o campo ou retorne array vazio.
            """

            # Get AI response
            response = await self.agent_manager.generate(
                prompt,
                max_tokens=3000,
                temperature=0.3,  # Lower for consistent extraction
            )

            # Parse the response
            import json

            # Try to parse as JSON directly
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    if json_end != -1:
                        json_str = response[json_start:json_end].strip()
                        return json.loads(json_str)
                elif "```" in response:
                    json_start = response.find("```") + 3
                    json_end = response.find("```", json_start)
                    if json_end != -1:
                        json_str = response[json_start:json_end].strip()
                        # Remove 'json' if present at start
                        if json_str.startswith("json"):
                            json_str = json_str[4:].strip()
                        return json.loads(json_str)

            logger.warning(f"Could not parse AI response as JSON: {response[:200]}...")
            return None

        except Exception as e:
            logger.error(f"Error in structured resume extraction: {e}")
            # Don't return mock data on error - let the caller handle the failure
            raise ProviderError(f"Failed to extract structured resume data: {str(e)}") from e

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

        # Use resume_id field instead of id for fetching
        try:
            # Try to get by resume_id field
            response = (
                service.supabase.table("resumes").select("*").eq("resume_id", resume_id).execute()
            )
            if response.data:
                resume = response.data[0]
            else:
                resume = None
        except Exception as e:
            logger.error(f"Error fetching resume {resume_id}: {e}")
            resume = None

        if not resume:
            # TODO: Create and raise ResumeNotFoundError
            raise ValueError(f"Resume with ID {resume_id} not found")

        combined_data = {
            "resume_id": resume.get("resume_id") or resume_id,
            "raw_resume": {
                "id": resume.get("id"),
                "content": resume.get("content"),
                "content_type": resume.get("content_type"),
                "user_id": resume.get("user_id"),  # CRITICAL: Include user ownership
                "created_at": resume.get("created_at"),
                "updated_at": resume.get("updated_at"),
            },
            "processed_resume": None,
        }

        # TODO: Fetch processed resume data when database structure is ready
        # processed_service = SupabaseDatabaseService("processed_resumes", dict)
        # processed_resume = await processed_service.get(resume_id)

        return combined_data
