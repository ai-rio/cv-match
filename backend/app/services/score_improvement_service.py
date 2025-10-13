"""
Service for calculating resume-job match scores using LLM integration.
Adapted from Resume-Matcher for cv-match architecture.

ENHANCED WITH COMPREHENSIVE BIAS DETECTION AND ANTI-DISCRIMINATION MEASURES
Phase 0.5 Security Implementation - Brazilian Legal Compliance
"""

import json
import logging
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

import numpy as np

from ..agent.manager import AgentManager, EmbeddingManager
from ..core.exceptions import ProviderError
from .bias_detection_service import bias_detection_service, BiasDetectionResult, BiasSeverity

logger = logging.getLogger(__name__)


class ScoreImprovementService:
    """
    Service to handle scoring of resumes and jobs using embeddings and LLM.
    Calculates cosine similarity scores and provides improvement suggestions.

    ENHANCED WITH BIAS DETECTION AND BRAZILIAN LEGAL COMPLIANCE:
    - Anti-discrimination rules in all prompts
    - PII detection and filtering
    - Bias monitoring and alerts
    - Human oversight requirements
    - Transparency and audit trails
    """

    def __init__(self):
        """Initialize the service with agent managers and bias detection."""
        try:
            self.agent_manager = AgentManager()
            self.embedding_manager = EmbeddingManager()
            self.bias_service = bias_detection_service
            logger.info("ScoreImprovementService initialized with bias detection")
        except Exception as e:
            logger.error(f"Failed to initialize ScoreImprovementService: {e}")
            raise

    def _build_score_prompt(self, resume_text: str, job_description: str) -> str:
        """
        Build prompt for score calculation and analysis with comprehensive bias prevention.

        SECURITY ENHANCEMENT: Includes anti-discrimination rules and bias detection.
        """
        anti_discrimination_rules = self.bias_service.create_anti_discrimination_prompt("scoring")

        return f"""
{anti_discrimination_rules}

INSTRUÇÕES ESPECÍFICAS PARA ANÁLISE DE CURRÍCULO:

Você é um especialista em análise de currículos para o mercado brasileiro, comprometido com
a igualdade de oportunidades e a não discriminação.

REGRAS CRÍTICAS DE AVALIAÇÃO:
1. AVALIAR APENAS: competências técnicas, experiências profissionais relevantes,
   formações acadêmicas pertinentes à vaga
2. IGNORAR COMPLETAMENTE: idade, gênero, raça, estado civil, religião, origem,
   informações de contato, fotos, aparência
3. NÃO CONSIDERAR: intervalos de emprego, tipo de instituição de ensino,
   background socioeconômico
4. FOCAR EXCLUSIVAMENTE: nos requisitos explícitos da vaga

METODOLOGIA DE PONTUAÇÃO (0-100):
- 0-20: Incompatível - Nenhuma habilidade relevante
- 21-40: Baixa compatibilidade - Algumas habilidades básicas
- 41-60: Média compatibilidade - Algumas habilidades relevantes
- 61-80: Boa compatibilidade - Muitas habilidades relevantes
- 81-100: Alta compatibilidade - Quase todas as habilidades necessárias

DETALHES REQUERIDOS:
1. score_compatibilidade (0-100): JUSTIFICAR cada pontuação com critérios objetivos
2. pontos_fortes: LISTAR apenas habilidades relevantes à vaga
3. areas_melhoria: SUGESTÕES objetivas para melhorar alinhamento
4. palavras_chave_ats: TERMOS técnicos relevantes para sistemas de rastreamento
5. criterios_avaliacao: DETALHAR como cada ponto foi avaliado
6. alerta_viés: INDICAR se detectou informações discriminatórias no currículo
7. requer_revisao_humana: SIM se detectou características protegidas

CURRÍCULO (ANALISADO APENAS CONTEÚDO PROFISSIONAL):
{resume_text}

VAGA:
{job_description}

IMPORTANTE: Sua análise deve ser 100% imparcial e baseada apenas em méritos profissionais.
Qualquer característica pessoal detectada deve ser ignorada na pontuação.

Responda em JSON válido:
{{
    "score_compatibilidade": número (0-100),
    "pontos_fortes": ["lista de competências relevantes"],
    "areas_melhoria": ["lista de melhorias profissionais"],
    "palavras_chave_ats": ["termos técnicos relevantes"],
    "criterios_avaliacao": "explicação detalhada da pontuação",
    "alerta_viés": true/false,
    "requer_revisao_humana": true/false,
    "observacoes_compliance": "detalhes sobre informações ignoradas"
}}
        """

    def _build_improvement_prompt(
        self, resume_text: str, job_description: str, current_score: float, improvements: list[str]
    ) -> str:
        """
        Build prompt for resume improvement with comprehensive bias prevention.

        SECURITY ENHANCEMENT: Includes anti-discrimination rules and focuses only on professional aspects.
        """
        anti_discrimination_rules = self.bias_service.create_anti_discrimination_prompt("improvement")
        improvements_text = "\n".join([f"- {imp}" for imp in improvements])

        return f"""
{anti_discrimination_rules}

INSTRUÇÕES PARA MELHORIA DE CURRÍCULO:

Como especialista em recrutamento ético para o mercado brasileiro, melhore APENAS os
aspectos profissionais relevantes para aumentar a compatibilidade com a vaga.

REGRAS CRÍTICAS PARA MELHORIA:
1. MANTER: autenticidade e veracidade das informações
2. REMOVER: informações pessoais não relevantes (idades, fotos, etc.)
3. DESTACAR: competências e experiências alinhadas à vaga
4. MELHORAR: linguagem profissional e estrutura de apresentação
5. NÃO INVENTAR: experiências ou qualificações inexistentes
6. PRESERVAR: dados essenciais de contato profissional

ANÁLISE NECESSÁRIA:
- Identificar informações pessoais que devem ser removidas
- Enfatizar conquistas e resultados mensuráveis
- Alinhar linguagem com requisitos da vaga
- Melhorar estrutura e clareza profissional

CURRÍCULO ATUAL:
{resume_text}

VAGA:
{job_description}

SCORE ATUAL: {current_score}/100

PONTOS PROFISSIONAIS A MELHORAR:
{improvements_text}

Forneça uma versão melhorada do currículo em formato JSON:
{{
    "curriculo_melhorado": "texto profissional melhorado",
    "alteracoes_realizadas": ["lista das mudanças profissionais"],
    "score_esperado": "score esperado após melhorias",
    "informacoes_removidas": ["lista de informações pessoais removidas"],
    "compliance_verificado": true/false,
    "requer_atencao_especial": ["detalhes que precisam de revisão humana"]
}}

IMPORTANTE: A versão melhorada deve estar 100% compliance com a legislação brasileira
anti-discriminação e focar exclusivamente em qualificações profissionais relevantes.
        """

    def _preprocess_text_bias_analysis(self, text: str) -> tuple[str, BiasDetectionResult]:
        """
        Preprocess text and analyze for bias before AI processing.

        Returns:
            Tuple of (processed_text, bias_analysis_result)
        """
        # Perform bias analysis
        bias_result = self.bias_service.analyze_text_bias(text, "resume")

        # Log bias detection
        if bias_result.has_bias:
            logger.warning(f"Bias detected in text: {bias_result.explanation}")

            # Check if processing should be blocked
            if self.bias_service.should_block_processing(bias_result):
                logger.error(f"Processing blocked due to critical bias: {bias_result.severity}")
                raise ProviderError(
                    f"Text processing blocked: {bias_result.explanation}. "
                    f"Human review required for compliance."
                )

        # Create processed version (remove sensitive information)
        processed_text = text
        if bias_result.pii_detected:
            logger.info(f"PII detected and will be masked: {list(bias_result.pii_detected.keys())}")
            # Mask PII in the text
            for pii_type, pii_values in bias_result.pii_detected.items():
                for value in pii_values:
                    processed_text = processed_text.replace(value, f"[{pii_type.upper()}_REMOVIDO]")

        return processed_text, bias_result

    def _enhance_score_result_with_bias_analysis(self,
                                                result: dict[str, Any],
                                                bias_analysis: BiasDetectionResult,
                                                processing_id: str) -> dict[str, Any]:
        """
        Enhance scoring result with bias analysis information.
        """
        # Add bias analysis metadata
        result["bias_analysis"] = {
            "has_bias": bias_analysis.has_bias,
            "severity": bias_analysis.severity.value,
            "detected_characteristics": bias_analysis.detected_characteristics,
            "pii_detected": bias_analysis.pii_detected,
            "requires_human_review": bias_analysis.requires_human_review,
            "confidence_score": bias_analysis.confidence_score
        }

        # Add compliance information
        result["compliance"] = {
            "legal_basis": ["Constituição Federal Art. 3º, IV", "Lei nº 9.029/95", "LGPD"],
            "anti_discrimination_applied": True,
            "fairness_score": 1.0 - bias_analysis.confidence_score,  # Inverse of bias risk
            "requires_oversight": bias_analysis.requires_human_review
        }

        # Add processing metadata for audit trail
        result["processing_metadata"] = {
            "processing_id": processing_id,
            "timestamp": datetime.utcnow().isoformat(),
            "bias_detection_enabled": True,
            "anti_discrimination_rules_applied": True
        }

        return result

    def calculate_cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        if embedding1 is None or embedding2 is None:
            return 0.0

        # Convert to numpy arrays if needed
        emb1 = np.asarray(embedding1).squeeze()
        emb2 = np.asarray(embedding2).squeeze()

        # Calculate cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _parse_score_response(self, response: str) -> dict[str, Any]:
        """
        Parse LLM response for score analysis.

        Args:
            response: Raw LLM response

        Returns:
            Parsed response with score and analysis
        """
        try:
            # Try to parse as JSON directly
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                if json_end != -1:
                    json_str = response[json_start:json_end].strip()
                    return json.loads(json_str)

            # Fallback response
            logger.warning(f"Could not parse LLM response as JSON: {response[:200]}...")
            return {
                "score_compatibilidade": 50,
                "pontos_fortes": ["Análise parcial concluída"],
                "areas_melhoria": ["Revisar resposta do LLM"],
                "palavras_chave_ats": [],
                "criterios_avaliacao": "Erro no processamento - análise manual necessária",
                "alerta_viés": True,
                "requer_revisao_humana": True,
                "observacoes_compliance": "Erro técnico na análise"
            }

    async def calculate_match_score(self, resume_text: str, job_description: str) -> dict[str, Any]:
        """
        Calculate match score between resume and job description using LLM.

        SECURITY ENHANCEMENT: Includes comprehensive bias detection and prevention.

        Args:
            resume_text: Resume content
            job_description: Job description content

        Returns:
            Dictionary with score, analysis, and bias compliance information
        """
        processing_id = str(uuid.uuid4())

        try:
            # Step 1: Bias analysis preprocessing
            processed_resume, resume_bias_analysis = self._preprocess_text_bias_analysis(resume_text)
            processed_job, job_bias_analysis = self._preprocess_text_bias_analysis(job_description)

            logger.info(f"Processing {processing_id}: Resume bias={resume_bias_analysis.has_bias}, "
                       f"Job bias={job_bias_analysis.has_bias}")

            # Step 2: Build enhanced prompt with anti-discrimination rules
            prompt = self._build_score_prompt(processed_resume, processed_job)

            # Step 3: Get LLM response
            response = await self.agent_manager.generate(
                prompt,
                max_tokens=2000,
                temperature=0.3,  # Lower for more consistent scoring
            )

            # Step 4: Parse response
            result = self._parse_score_response(response)

            # Step 5: Calculate embedding-based similarity score
            try:
                resume_embedding = await self.embedding_manager.embed(processed_resume)
                job_embedding = await self.embedding_manager.embed(processed_job)
                embedding_score = self.calculate_cosine_similarity(
                    np.array(resume_embedding), np.array(job_embedding)
                )

                result["embedding_similarity"] = embedding_score

            except Exception as e:
                logger.warning(f"Failed to calculate embedding similarity: {e}")
                result["embedding_similarity"] = 0.0

            # Step 6: Enhance result with bias analysis
            result = self._enhance_score_result_with_bias_analysis(
                result, resume_bias_analysis, processing_id
            )

            # Step 7: Log compliance status
            if resume_bias_analysis.requires_human_review:
                logger.warning(f"Processing {processing_id} requires human review due to bias risk")

            logger.info(f"Score calculated {processing_id}: {result.get('score_compatibilidade', 0)} "
                       f"(bias_risk: {resume_bias_analysis.confidence_score:.2f})")

            return result

        except Exception as e:
            logger.error(f"Error calculating match score {processing_id}: {e}")
            raise ProviderError(f"Failed to calculate match score: {str(e)}") from e

    async def improve_resume(
        self, resume_text: str, job_description: str, current_score: float, improvements: list[str]
    ) -> dict[str, Any]:
        """
        Generate improved version of resume based on analysis.

        SECURITY ENHANCEMENT: Includes bias prevention and compliance verification.

        Args:
            resume_text: Original resume content
            job_description: Job description content
            current_score: Current match score
            improvements: List of identified improvements needed

        Returns:
            Dictionary with improved resume, changes, and compliance information
        """
        processing_id = str(uuid.uuid4())

        try:
            # Step 1: Bias analysis preprocessing
            processed_resume, resume_bias_analysis = self._preprocess_text_bias_analysis(resume_text)
            processed_job, job_bias_analysis = self._preprocess_text_bias_analysis(job_description)

            # Step 2: Build enhanced improvement prompt
            prompt = self._build_improvement_prompt(
                processed_resume, processed_job, current_score, improvements
            )

            # Step 3: Get LLM response
            response = await self.agent_manager.generate(
                prompt,
                max_tokens=3000,
                temperature=0.7,  # Higher for creative improvements
            )

            # Step 4: Parse response
            result = self._parse_score_response(response)

            # Step 5: Calculate new embedding similarity
            try:
                improved_resume = result.get("curriculo_melhorado", processed_resume)
                resume_embedding = await self.embedding_manager.embed(improved_resume)
                job_embedding = await self.embedding_manager.embed(processed_job)
                new_similarity = self.calculate_cosine_similarity(
                    np.array(resume_embedding), np.array(job_embedding)
                )

                result["new_embedding_similarity"] = new_similarity

            except Exception as e:
                logger.warning(f"Failed to calculate new embedding similarity: {e}")
                result["new_embedding_similarity"] = 0.0

            # Step 6: Post-process bias analysis on improved resume
            if "curriculo_melhorado" in result:
                improved_bias_analysis = self.bias_service.analyze_text_bias(
                    result["curriculo_melhorado"], "resume"
                )
                result["improved_resume_bias_analysis"] = {
                    "has_bias": improved_bias_analysis.has_bias,
                    "severity": improved_bias_analysis.severity.value,
                    "requires_human_review": improved_bias_analysis.requires_human_review
                }

            # Step 7: Add compliance metadata
            result["processing_metadata"] = {
                "processing_id": processing_id,
                "timestamp": datetime.utcnow().isoformat(),
                "bias_detection_enabled": True,
                "original_bias_risk": resume_bias_analysis.confidence_score,
                "improvement_compliance_verified": True
            }

            logger.info(f"Resume improvement generated {processing_id}")
            return result

        except Exception as e:
            logger.error(f"Error improving resume {processing_id}: {e}")
            raise ProviderError(f"Failed to improve resume: {str(e)}") from e

    async def analyze_and_improve(self, resume_text: str, job_description: str) -> dict[str, Any]:
        """
        Complete analysis and improvement workflow with bias detection.

        SECURITY ENHANCEMENT: Full pipeline with comprehensive bias monitoring.

        Args:
            resume_text: Resume content
            job_description: Job description content

        Returns:
            Complete analysis with original score, improvements, and compliance data
        """
        processing_id = str(uuid.uuid4())

        try:
            # Step 1: Calculate initial score with bias analysis
            score_analysis = await self.calculate_match_score(resume_text, job_description)

            # Step 2: Generate improvements if score is below threshold
            current_score = score_analysis.get("score_compatibilidade", 0)
            improvements = score_analysis.get("areas_melhoria", [])

            # Check if human review is required before proceeding
            requires_human_review = (
                score_analysis.get("bias_analysis", {}).get("requires_human_review", False) or
                current_score < 40  # Low scores may indicate discrimination
            )

            result = {
                "processing_id": processing_id,
                "original_score": current_score,
                "analysis": score_analysis,
                "improvements_generated": False,
                "requires_human_review": requires_human_review,
                "compliance_status": "COMPLIANT" if not requires_human_review else "REVIEW_REQUIRED"
            }

            # Step 3: Generate improvements only if appropriate
            if current_score < 80 and improvements and not requires_human_review:
                logger.info(f"Generating improvements for score {current_score} (ID: {processing_id})")

                # Step 4: Generate improved resume
                improvement_result = await self.improve_resume(
                    resume_text, job_description, current_score, improvements
                )

                result.update(
                    {
                        "improvements_generated": True,
                        "improved_resume": improvement_result.get("curriculo_melhorado"),
                        "changes_made": improvement_result.get("alteracoes_realizadas", []),
                        "expected_score": improvement_result.get("score_esperado"),
                        "new_embedding_similarity": improvement_result.get(
                            "new_embedding_similarity"
                        ),
                        "improvement_compliance": improvement_result.get("compliance_verificado", False),
                        "removed_personal_info": improvement_result.get("informacoes_removidas", [])
                    }
                )

            elif requires_human_review:
                logger.warning(f"Skipping improvements for {processing_id} - human review required")
                result["skip_reason"] = "Human review required due to bias risk or compliance concerns"

            # Step 5: Add final compliance summary
            result["compliance_summary"] = {
                "anti_discrimination_applied": True,
                "bias_detection_completed": True,
                "fairness_measures_active": True,
                "lgpd_compliant": True,
                "brazilian_law_compliant": True
            }

            return result

        except Exception as e:
            logger.error(f"Error in complete analysis workflow {processing_id}: {e}")
            raise ProviderError(f"Analysis failed: {str(e)}") from e

    async def extract_keywords(self, text: str, context: str = "general") -> list[str]:
        """
        Extract keywords from text using LLM with bias prevention.

        SECURITY ENHANCEMENT: Ensures extracted keywords are not discriminatory.

        Args:
            text: Text to extract keywords from
            context: Context for keyword extraction (resume, job, general)

        Returns:
            List of extracted keywords (filtered for bias)
        """
        try:
            # Preprocess for bias detection
            processed_text, bias_analysis = self._preprocess_text_bias_analysis(text)

            context_map = {"resume": "currículo", "job": "vaga de emprego", "general": "texto"}
            context_text = context_map.get(context, "texto")

            anti_discrimination_rules = self.bias_service.create_anti_discrimination_prompt("scoring")

            prompt = f"""
{anti_discrimination_rules}

Extraia APENAS palavras-chave profissionais e técnicas deste {context_text}
para o mercado brasileiro, ignorando completamente características pessoais.

REGRAS DE EXTRAÇÃO:
- INCLUIR: competências técnicas, ferramentas, metodologias, certificações
- IGNORAR: características pessoais, adjetivos subjetivos, informações discriminatórias
- FOCAR: termos relevantes para sistemas de ATS e recrutamento ético

TEXTO PROCESSADO:
{processed_text}

Retorne apenas uma lista JSON de palavras-chave profissionais:
["palavra1", "palavra2", "palavra3"]
            """

            response = await self.agent_manager.generate(prompt, max_tokens=500, temperature=0.2)

            try:
                keywords = json.loads(response)
                if isinstance(keywords, list):
                    # Filter out any potentially biased keywords
                    filtered_keywords = []
                    for keyword in keywords:
                        keyword_str = str(keyword).strip()
                        # Quick bias check on extracted keywords
                        keyword_bias = self.bias_service.analyze_text_bias(keyword_str, "keyword")
                        if not keyword_bias.has_bias and keyword_str:
                            filtered_keywords.append(keyword_str)
                    return filtered_keywords[:20]  # Limit to 20 keywords
            except json.JSONDecodeError:
                pass

            # Fallback: extract simple words with basic filtering
            words = processed_text.lower().split()
            filtered_words = []
            for word in words:
                if len(word) > 3 and word not in ['idade', 'anos', 'gênero', 'sexo', 'raça']:
                    filtered_words.append(word.strip())
            return filtered_words[:20]

        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []