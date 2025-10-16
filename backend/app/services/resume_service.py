"""
Resume processing service for CV-Match with PII integration.

This service handles resume file conversion, text extraction, PII detection/masking,
and storage with comprehensive LGPD compliance for Brazilian market deployment.
"""

import logging
import tempfile
import uuid
from datetime import datetime
from typing import Any

from markitdown import MarkItDown

from app.services.llm.llm_service import AgentManager
from app.services.security.audit_trail import ComplianceStatus, ComplianceType, audit_trail
from app.services.security.pii_detection_service import (
    PIIDetectionResult,
    pii_detector,
)
from app.services.supabase.database import SupabaseDatabaseService
from app.services.text_extraction import TextExtractionError, TextExtractionService

logger = logging.getLogger(__name__)


class ResumeService:
    """
    Service for processing resume files with comprehensive PII detection and masking.

    Key features:
    - File conversion to markdown/text
    - PII detection and masking for LGPD compliance
    - Structured data extraction
    - Database storage with user ownership
    - Comprehensive audit logging
    """

    def __init__(self):
        """Initialize resume service with required dependencies."""
        self.md = MarkItDown()
        self.text_extraction_service = TextExtractionService()
        self.agent_manager = AgentManager()
        self.pii_detector = pii_detector
        self._validate_docx_dependencies()

    def _validate_docx_dependencies(self) -> None:
        """Validate that DOCX processing dependencies are available."""
        try:
            import markitdown.converters.docx  # type: ignore  # Check if DOCX support is available
        except ImportError:
            logger.warning(
                "markitdown is missing DOCX support. Install with: pip install 'markitdown[docx]'"
            )
            # Don't raise error - just log warning

    def _get_file_extension(self, content_type: str) -> str:
        """Convert MIME type to file extension."""
        mime_to_ext = {
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/msword": ".doc",
            "text/plain": ".txt",
            "text/markdown": ".md",
        }
        return mime_to_ext.get(content_type, "")

    async def convert_and_store_resume(
        self,
        file_bytes: bytes,
        file_type: str,
        filename: str,
        content_type: str = "md",
        user_id: str | None = None,
    ) -> str:
        """
        Convert resume file and store in database with PII processing.

        Args:
            file_bytes: Raw file content
            file_type: MIME type of the file
            filename: Original filename
            content_type: Output content type (md, html, plain)
            user_id: User ID for ownership

        Returns:
            Resume ID of stored document

        Raises:
            Exception: If conversion or storage fails
        """
        try:
            # Extract text from file
            extracted_text = await self._extract_text_from_file(file_bytes, file_type)

            # Process text with PII detection and masking
            processed_text = await self._scan_and_process_resume_text(
                text_content=extracted_text,
                content_type=content_type,
                user_id=user_id or "anonymous",
                filename=filename,
            )

            # Store in database
            resume_id = await self._store_resume_in_db(processed_text, content_type, user_id)

            # Trigger structured extraction (async, don't wait)
            try:
                await self._extract_and_store_structured_resume(resume_id, processed_text)
            except Exception as e:
                logger.warning(f"Structured extraction failed for resume {resume_id}: {e}")

            return resume_id

        except Exception as e:
            logger.error(f"Resume conversion failed: {str(e)}")
            raise Exception(f"File conversion failed: {str(e)}") from e

    async def _extract_text_from_file(self, file_bytes: bytes, file_type: str) -> str:
        """
        Extract text content from uploaded file.

        Args:
            file_bytes: Raw file content
            file_type: MIME type

        Returns:
            Extracted text content

        Raises:
            TextExtractionError: If extraction fails
        """
        file_ext = self._get_file_extension(file_type)

        if not file_ext:
            raise TextExtractionError(f"Unsupported file type: {file_type}")

        try:
            # Use MarkItDown for PDF and DOCX files
            if file_ext in [".pdf", ".docx", ".doc"]:
                return await self._extract_with_markitdown(file_bytes, file_ext)
            else:
                # Use text extraction service for other formats
                return await self.text_extraction_service.extract_text(file_bytes, file_ext)

        except Exception as e:
            # Fallback to text extraction if MarkItDown fails
            if file_ext in [".pdf", ".docx", ".doc"]:
                logger.warning(f"MarkItDown failed for {file_ext}, trying text extraction: {e}")
                try:
                    return await self.text_extraction_service.extract_text(file_bytes, file_ext)
                except Exception as fallback_error:
                    raise TextExtractionError(
                        f"Both MarkItDown and text extraction failed: {str(fallback_error)}"
                    ) from fallback_error
            else:
                raise TextExtractionError(f"Text extraction failed: {str(e)}") from e

    async def _extract_with_markitdown(self, file_bytes: bytes, file_ext: str) -> str:
        """
        Extract text using MarkItDown library.

        Args:
            file_bytes: Raw file content
            file_ext: File extension

        Returns:
            Extracted text content
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            # Convert with MarkItDown
            result = self.md.convert(temp_file_path)
            return result.text_content

        except Exception as e:
            # Check for specific dependency error
            if "MissingDependencyException" in str(e) and file_ext == ".docx":
                raise Exception(
                    "markitdown is missing DOCX support. "
                    "Install with: pip install 'markitdown[docx]'"
                ) from e
            else:
                raise e

        finally:
            # Clean up temporary file
            try:
                import os

                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temp file {temp_file_path}: {cleanup_error}")

    async def _scan_and_process_resume_text(
        self, text_content: str, content_type: str, user_id: str, filename: str
    ) -> str:
        """
        Scan text for PII and apply masking if needed.

        Args:
            text_content: Original extracted text
            content_type: Content type for storage
            user_id: User ID for ownership
            filename: Original filename

        Returns:
            Processed text (masked if PII detected)
        """
        try:
            # Scan for PII
            pii_result = self.pii_detector.scan_text(text_content)

            if pii_result.has_pii:
                logger.warning(
                    f"PII detected in resume upload by user {user_id}: "
                    f"types={[t.value for t in pii_result.pii_types_found]}, "
                    f"confidence={pii_result.confidence_score:.2f}"
                )

                # Use pre-computed masked text
                processed_text = pii_result.masked_text

                # Log PII detection for LGPD compliance
                await self._log_pii_detection(
                    user_id=user_id,
                    filename=filename,
                    pii_result=pii_result,
                    original_length=len(text_content),
                    masked_length=len(processed_text),
                )

                return processed_text
            else:
                # No PII detected, return original text
                return text_content

        except Exception as e:
            logger.error(f"PII detection error: {str(e)}")
            # Fail securely - if PII detection fails, don't process the resume
            raise Exception(f"PII detection error - LGPD compliance failure: {str(e)}") from e

    async def _log_pii_detection(
        self,
        user_id: str,
        filename: str,
        pii_result: PIIDetectionResult,
        original_length: int,
        masked_length: int,
    ) -> None:
        """
        Log PII detection event for LGPD compliance audit trail.

        Args:
            user_id: User ID
            filename: Original filename
            pii_result: PII detection result
            original_length: Original text length
            masked_length: Masked text length
        """
        try:
            # Log to audit trail
            await audit_trail.log_compliance_event(
                compliance_type=ComplianceType.PII_DETECTION,
                check_type="resume_upload_scan",
                status=ComplianceStatus.WARNING,
                affected_records=1,
                details={
                    "pii_types_found": [t.value for t in pii_result.pii_types_found],
                    "confidence_score": pii_result.confidence_score,
                    "scan_duration_ms": pii_result.scan_duration_ms,
                    "lgpd_action": "masked_before_storage",
                    "original_length": original_length,
                    "masked_length": masked_length,
                    "filename": filename,
                    "user_id": user_id,
                },
            )

            logger.info(f"PII detection logged for user {user_id}, file {filename}")

        except Exception as e:
            logger.error(f"Failed to log PII detection: {e}")
            # Don't raise error - logging failure shouldn't stop processing

    async def _store_resume_in_db(
        self, content: str, content_type: str, user_id: str | None = None
    ) -> str:
        """
        Store processed resume content in database.

        Args:
            content: Processed resume content
            content_type: Content type
            user_id: User ID for ownership

        Returns:
            Resume ID
        """
        service = SupabaseDatabaseService("resumes", dict)

        # Prepare data for storage
        resume_data = {
            "resume_id": str(uuid.uuid4()),
            "content": content,
            "content_type": self._normalize_content_type(content_type),
            "user_id": user_id,  # Will be None for anonymous uploads
            "created_at": datetime.utcnow(),
        }

        result = await service.create(resume_data)
        return result.get("resume_id", str(uuid.uuid4()))

    def _normalize_content_type(self, content_type: str) -> str:
        """Normalize content type to standard MIME types."""
        type_mapping = {
            "md": "text/markdown",
            "html": "text/html",
            "plain": "text/plain",
        }
        return type_mapping.get(content_type.lower(), "text/plain")

    async def _extract_and_store_structured_resume(self, resume_id: str, resume_text: str) -> None:
        """
        Extract structured data from resume and store separately.

        Args:
            resume_id: Resume ID
            resume_text: Resume text content
        """
        try:
            # Extract structured JSON using existing method
            structured_data = await self._extract_structured_json(resume_text)

            if structured_data:
                # Store structured data
                service = SupabaseDatabaseService("resume_structured_data", dict)

                structured_record = {
                    "resume_id": resume_id,
                    "structured_data": structured_data,
                    "extracted_at": datetime.utcnow(),
                }

                await service.create(structured_record)
                logger.info(f"Structured data extracted and stored for resume {resume_id}")

        except Exception as e:
            logger.warning(f"Structured extraction failed for resume {resume_id}: {e}")
            # Don't raise error - structured extraction is optional

    async def _extract_structured_json(self, resume_text: str) -> dict[str, Any] | None:
        """
        Uses the AgentManager to ask the LLM to return the data in exact JSON schema we need.

        SECURITY ENHANCEMENT: Includes comprehensive anti-discrimination rules
        to ensure resume analysis is bias-free and compliant with Brazilian law.
        """
        try:
            # Anti-discrimination rules for Brazilian legal compliance
            anti_discrimination_rules = """
CRITICAL - REGRAS ANTI-DISCRIMINAÇÃO (Lei Brasileira):
- NÃO CONSIDERAR: idade, gênero, raça/etnia, religião, orientação sexual, deficiência
- NÃO PENALIZAR: intervalos de emprego, trajetórias não tradicionais, background social
- NÃO DISCRIMINAR: com base em nome, endereço, instituições de ensino, origem regional
- AVALIAR APENAS: qualificações profissionais, experiências relevantes, competências técnicas
- GARANTIR: tratamento justo e igualitário para todos os candidatos
- IDENTIFICAR: informações que possam levar a discriminação
- FOCAR: apenas em aspectos profissionais relevantes para vagas

BASE LEGAL:
- Constituição Federal Art. 3º, IV e Art. 5º, I
- Lei nº 9.029/95 - Proibição de discriminação
- Lei nº 12.288/2010 - Estatuto da Igualdade Racial
- Lei nº 7.853/89 - Pessoas com deficiência
- LGPD - Transparência em decisões automatizadas
"""

            # Build structured extraction prompt for Brazilian market with bias prevention
            prompt = f"""
{anti_discrimination_rules}

INSTRUÇÕES PARA ANÁLISE DE CURRÍCULO:

Você é um especialista em análise de currículos para o mercado brasileiro, comprometido
com a igualdade de oportunidades e a não discriminação.

REGRAS CRÍTICAS DE ANÁLISE:
1. EXTRAIR APENAS: informações profissionais relevantes
2. IGNORAR: dados pessoais que possam levar a discriminação
3. FOCAR: em competências, experiências e qualificações objetivas
4. NEUTRALIZAR: qualquer informação que possa gerar viés
5. PRESERVAR: apenas dados essenciais para avaliação profissional

Analise este currículo e extraia as informações estruturadas em formato JSON válido:

CURRÍCULO:
{resume_text}

Retorne um JSON com as seguintes chaves:
- personal_info: Objeto APENAS com nome profissional, email, telefone, linkedin (IGNORAR: idade, fotos, estado civil, etc.)
- summary: Resumo profissional (string, opcional)
- work_experience: Lista de experiências profissionais, cada uma com: empresa, cargo, período, descrição
- education: Lista de formações acadêmicas, cada uma com: instituição, curso, nível, período, status (IGNORAR: dados discriminatórios)
- skills: Lista de competências técnicas (array de strings)
- languages: Lista de idiomas com proficiência (array de objetos)
- certifications: Lista de certificações (array de objetos)
- projects: Lista de projetos relevantes (array de objetos)
- extracted_keywords: Lista de palavras-chave profissionais para ATS (array de strings)
- potential_bias_detected: Lista de informações que poderiam gerar discriminação (array de strings)
- compliance_notes: Observações sobre conformidade com a lei brasileira (array de strings)

IMPORTANTE:
- Extraia APENAS informações profissionais relevantes
- IGNORE completamente dados que possam levar a discriminação
- NÃO inclua idade, gênero, aparência, estado civil, ou características protegidas
- Sinalize qualquer informação que possa violar a lei brasileira
- Retorne apenas o JSON válido, sem texto adicional
- Se alguma informação não estiver presente, não inclua o campo ou retorne array vazio
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
                parsed_response = json.loads(response)

                # Log any detected bias for compliance
                bias_detected = parsed_response.get("potential_bias_detected", [])
                compliance_notes = parsed_response.get("compliance_notes", [])

                if bias_detected or compliance_notes:
                    logger.warning(
                        f"Resume analysis detected potential bias issues: "
                        f"Bias detected: {bias_detected}, Compliance notes: {compliance_notes}"
                    )

                return parsed_response

            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    if json_end != -1:
                        json_str = response[json_start:json_end].strip()
                        parsed_response = json.loads(json_str)

                        # Log any detected bias for compliance
                        bias_detected = parsed_response.get("potential_bias_detected", [])
                        compliance_notes = parsed_response.get("compliance_notes", [])

                        if bias_detected or compliance_notes:
                            logger.warning(
                                f"Resume analysis detected potential bias issues: "
                                f"Bias detected: {bias_detected}, Compliance notes: {compliance_notes}"
                            )

                        return parsed_response

                elif "```" in response:
                    json_start = response.find("```") + 3
                    json_end = response.find("```", json_start)
                    if json_end != -1:
                        json_str = response[json_start:json_end].strip()
                        # Remove 'json' if present at start
                        if json_str.startswith("json"):
                            json_str = json_str[4:].strip()
                        parsed_response = json.loads(json_str)

                        # Log any detected bias for compliance
                        bias_detected = parsed_response.get("potential_bias_detected", [])
                        compliance_notes = parsed_response.get("compliance_notes", [])

                        if bias_detected or compliance_notes:
                            logger.warning(
                                f"Resume analysis detected potential bias issues: "
                                f"Bias detected: {bias_detected}, Compliance notes: {compliance_notes}"
                            )

                        return parsed_response

            logger.warning(f"Could not parse AI response as JSON: {response[:200]}...")
            return None

        except Exception as e:
            logger.error(f"Error in structured resume extraction: {e}")
            # Don't return mock data on error - let the caller handle the failure
            from app.services.llm.llm_service import ProviderError

            raise ProviderError(f"Failed to extract structured resume data: {str(e)}") from e

    async def get_resume_with_processed_data(self, resume_id: str) -> dict[str, Any] | None:
        """
        Get resume data including processed information.

        Args:
            resume_id: Resume ID

        Returns:
            Dictionary with resume data or None if not found
        """
        try:
            # Get raw resume data
            service = SupabaseDatabaseService("resumes", dict)
            raw_resume = await service.get(resume_id)

            if not raw_resume:
                raise ValueError(f"Resume with ID {resume_id} not found")

            # Get structured data if available
            try:
                structured_service = SupabaseDatabaseService("resume_structured_data", dict)
                processed_resume = await structured_service.get(resume_id)
            except Exception:
                processed_resume = None

            return {
                "resume_id": resume_id,
                "raw_resume": raw_resume,
                "processed_resume": processed_resume,
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get resume {resume_id}: {str(e)}")
            raise Exception(f"Failed to retrieve resume: {str(e)}") from e
