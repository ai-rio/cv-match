"""
Job service for processing and analyzing job descriptions.
Includes bias detection and PII scanning for LGPD compliance.
"""

import logging
from typing import Any

from app.exceptions.providers import ProviderError
from app.services.llm.agent_manager import AgentManager

logger = logging.getLogger(__name__)


class JobService:
    """Service for processing and analyzing job descriptions."""

    def __init__(self):
        """Initialize job service."""
        self.agent_manager = AgentManager()

    async def _extract_structured_json(self, job_description_text: str) -> dict[str, Any] | None:
        """
        Uses the AgentManager+JSONWrapper to ask the LLM to
        return the data in exact JSON schema we need.

        SECURITY ENHANCEMENT: Includes comprehensive anti-discrimination rules
        to ensure job descriptions are analyzed in a bias-free manner.
        """
        try:
            # Anti-discrimination rules for Brazilian legal compliance
            anti_discrimination_rules = """
CRITICAL - REGRAS ANTI-DISCRIMINAÇÃO (Lei Brasileira):
- NÃO CONSIDERAR: idade, gênero, raça/etnia, religião, orientação sexual, deficiência
- NÃO PENALIZAR: candidatos com intervalos de emprego, trajetórias não tradicionais
- NÃO DISCRIMINAR: com base em nome, endereço, instituições de ensino, origem regional
- AVALIAR APENAS: requisitos profissionais, habilidades técnicas, experiências relevantes
- GARANTIR: tratamento justo e igualitário para todos os candidatos
- IDENTIFICAR: linguagem discriminatória na descrição da vaga
- FORNECER: apenas critérios profissionais objetivos

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

INSTRUÇÕES PARA ANÁLISE DE VAGA:

Você é um especialista em análise de vagas de emprego para o mercado brasileiro, comprometido
com a igualdade de oportunidades e a não discriminação.

REGRAS CRÍTICAS DE ANÁLISE:
1. EXTRAIR APENAS: informações profissionais relevantes
2. IDENTIFICAR: linguagem potencialmente discriminatória na vaga
3. IGNORAR: requisitos ilegais ou discriminatórios
4. FOCAR: em competências e qualificações mensuráveis
5. SINALIZAR: qualquer requisito que possa ser considerado discriminatório

Analise esta descrição de vaga e extraia as informações estruturadas em formato JSON válido:

DESCRIÇÃO DA VAGA:
{job_description_text}

Retorne um JSON com as seguintes chaves:
- job_title: Título da vaga (string)
- company_profile: Perfil da empresa (string, opcional)
- location: Localização (string, opcional)
- date_posted: Data da publicação (string, opcional, formato YYYY-MM-DD)
- employment_type: Tipo de emprego (string, opcional - ex: "Full-time", "Part-time", "Contract", "Remote")
- job_summary: Resumo da vaga (string)
- key_responsibilities: Lista de responsabilidades principais (array de strings)
- qualifications: Lista de qualificações exigidas (array de strings)
- compensation_and_benefits: Lista de informações sobre salário e benefícios (array de strings)
- application_info: Lista de informações sobre como se candidatar (array de strings)
- extracted_keywords: Lista de palavras-chave importantes para ATS (array de strings)
- potential_bias_issues: Lista de requisitos que podem ser considerados discriminatórios (array de strings)
- compliance_flags: Lista de alertas de conformidade com a lei brasileira (array de strings)

IMPORTANTE:
- Extraia APENAS informações profissionais relevantes
- Não inclua requisitos discriminatórios (idade, gênero, aparência, etc.)
- Sinalize qualquer linguagem que possa violar a lei brasileira
- Retorne apenas o JSON válido, sem texto adicional
"""

            # Get AI response
            response = await self.agent_manager.generate(
                prompt,
                max_tokens=2000,
                temperature=0.3,  # Lower for consistent extraction
            )

            # Parse the response
            import json

            # Try to parse as JSON directly
            try:
                parsed_response = json.loads(response)

                # Log any detected bias issues for compliance
                bias_issues = parsed_response.get("potential_bias_issues", [])
                compliance_flags = parsed_response.get("compliance_flags", [])

                if bias_issues or compliance_flags:
                    logger.warning(
                        f"Job description analysis detected potential issues: "
                        f"Bias issues: {bias_issues}, Compliance flags: {compliance_flags}"
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

                        # Log any detected bias issues for compliance
                        bias_issues = parsed_response.get("potential_bias_issues", [])
                        compliance_flags = parsed_response.get("compliance_flags", [])

                        if bias_issues or compliance_flags:
                            logger.warning(
                                f"Job description analysis detected potential issues: "
                                f"Bias issues: {bias_issues}, Compliance flags: {compliance_flags}"
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

                        # Log any detected bias issues for compliance
                        bias_issues = parsed_response.get("potential_bias_issues", [])
                        compliance_flags = parsed_response.get("compliance_flags", [])

                        if bias_issues or compliance_flags:
                            logger.warning(
                                f"Job description analysis detected potential issues: "
                                f"Bias issues: {bias_issues}, Compliance flags: {compliance_flags}"
                            )

                        return parsed_response

            logger.warning(f"Could not parse AI response as JSON: {response[:200]}...")
            return None

        except Exception as e:
            logger.error(f"Error in structured job extraction: {e}")
            # Don't return mock data on error - let the caller handle the failure
            raise ProviderError(f"Failed to extract structured job data: {str(e)}") from e

    async def _scan_and_process_job_text(
        self, job_description: str, job_id: str, resume_id: str, job_index: int
    ) -> str:
        """
        Scan job description for PII and process it.

        SECURITY: This method integrates PII detection and masking for LGPD compliance.
        """
        # Import PII detector to avoid circular imports
        from app.services.security.pii_detection_service import pii_detector

        # Scan for PII in job description
        pii_result = pii_detector.scan_text(job_description)

        processed_content = job_description

        if pii_result.has_pii:
            # Mask PII before further processing
            processed_content = pii_result.masked_text

            # Log PII detection for compliance
            await self._log_job_pii_detection(
                job_id=job_id,
                resume_id=resume_id,
                job_index=job_index,
                pii_result=pii_result,
                original_length=len(job_description),
                masked_length=len(processed_content),
            )

        return processed_content

    async def _log_job_pii_detection(
        self,
        job_id: str,
        resume_id: str,
        job_index: int,
        pii_result,
        original_length: int,
        masked_length: int,
    ):
        """Log PII detection in job description for LGPD compliance."""
        from app.services.security.audit_trail import ComplianceStatus, ComplianceType, audit_trail

        await audit_trail.log_compliance_event(
            compliance_type=ComplianceType.PII_DETECTION,
            check_type="job_description_scan",
            status=ComplianceStatus.WARNING,
            affected_records=1,
            details={
                "job_id": job_id,
                "resume_id": resume_id,
                "job_index": job_index,
                "pii_types_found": [pii_type.value for pii_type in pii_result.pii_types_found],
                "confidence_score": pii_result.confidence_score,
                "original_length": original_length,
                "masked_length": masked_length,
                "lgpd_action": "masked_before_processing",
            },
        )

    async def process_job_description(
        self, job_description_text: str, user_id: str, job_title: str | None = None
    ) -> str:
        """
        Process job description with PII detection and masking.

        Args:
            job_description_text: Raw job description text
            user_id: User ID processing the job
            job_title: Optional job title

        Returns:
            Processed job description text (masked if PII detected)
        """
        try:
            # PII Detection
            from app.services.security.pii_detection_service import pii_detector

            pii_result = pii_detector.scan_text(job_description_text)

            if pii_result.has_pii:
                logger.warning(
                    f"PII detected in job description by user {user_id}: "
                    f"types={[t.value for t in pii_result.pii_types_found]}"
                )

                # Mask PII before returning
                masked_text = pii_detector.mask_text(
                    job_description_text, pii_result.detected_instances
                )

                # Log PII detection
                await self._log_pii_detection(
                    user_id=user_id,
                    job_title=job_title or "Unknown",
                    pii_result=pii_result,
                    original_length=len(job_description_text),
                    masked_length=len(masked_text),
                )

                return masked_text

            # No PII detected, return original text
            return job_description_text

        except Exception as e:
            logger.error(f"Job description PII processing failed: {e}")
            # Fail securely - if PII detection fails, raise an error
            raise Exception(f"PII detection error - LGPD compliance failure: {str(e)}") from e

    async def _log_pii_detection(
        self, user_id: str, job_title: str, pii_result, original_length: int, masked_length: int
    ) -> None:
        """
        Log PII detection event for job descriptions.

        Args:
            user_id: User ID
            job_title: Job title
            pii_result: PII detection result
            original_length: Original text length
            masked_length: Masked text length
        """
        try:
            from app.services.security.audit_trail import (
                ComplianceStatus,
                ComplianceType,
                audit_trail,
            )

            await audit_trail.log_compliance_event(
                compliance_type=ComplianceType.PII_DETECTION,
                check_type="job_description_processing",
                status=ComplianceStatus.WARNING,
                affected_records=1,
                details={
                    "user_id": user_id,
                    "job_title": job_title,
                    "pii_types_found": [pii_type.value for pii_type in pii_result.pii_types_found],
                    "confidence_score": pii_result.confidence_score,
                    "scan_duration_ms": pii_result.scan_duration_ms,
                    "lgpd_action": "masked_before_processing",
                    "original_length": original_length,
                    "masked_length": masked_length,
                },
            )

            logger.info(f"Job PII detection logged for user {user_id}, job {job_title}")

        except Exception as e:
            logger.error(f"Failed to log job PII detection: {e}")
            # Don't raise error - logging failure shouldn't stop processing

    async def _extract_and_store_structured_job(
        self, job_id: str, job_description_text: str
    ) -> None:
        """
        Extract structured data from job description and store it.

        Args:
            job_id: Job ID
            job_description_text: Job description text (should already be masked)
        """
        try:
            # Extract structured JSON using existing method
            structured_data = await self._extract_structured_json(job_description_text)

            if structured_data:
                # Store structured data
                from datetime import datetime

                from app.services.supabase.database import SupabaseDatabaseService

                service = SupabaseDatabaseService("job_structured_data", dict)

                structured_record = {
                    "job_id": job_id,
                    "structured_data": structured_data,
                    "extracted_at": datetime.utcnow(),
                }

                await service.create(structured_record)
                logger.info(f"Structured job data extracted and stored for job {job_id}")

        except Exception as e:
            logger.warning(f"Structured job extraction failed for job {job_id}: {e}")
            # Don't raise error - structured extraction is optional
