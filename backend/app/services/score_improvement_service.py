"""
Service for calculating resume-job match scores using LLM integration.
Adapted from Resume-Matcher for cv-match architecture.
"""

import json
import logging
from typing import Any, Dict, List

import numpy as np

from ..agent.manager import AgentManager, EmbeddingManager
from ..core.exceptions import ProviderError

logger = logging.getLogger(__name__)


class ScoreImprovementService:
    """
    Service to handle scoring of resumes and jobs using embeddings and LLM.
    Calculates cosine similarity scores and provides improvement suggestions.
    """

    def __init__(self):
        """Initialize the service with agent managers."""
        try:
            self.agent_manager = AgentManager()
            self.embedding_manager = EmbeddingManager()
            logger.info("ScoreImprovementService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ScoreImprovementService: {e}")
            raise

    def _build_score_prompt(self, resume_text: str, job_description: str) -> str:
        """Build prompt for score calculation and analysis."""
        return f"""
        Você é um especialista em análise de currículos para o mercado brasileiro.

        Analise este currículo em relação à vaga e forneça:
        1. Score de compatibilidade (0-100)
        2. Principais pontos fortes
        3. Áreas de melhoria
        4. Palavras-chave para ATS
        5. Sugestões específicas de melhoria

        CURRÍCULO:
        {resume_text}

        VAGA:
        {job_description}

        Responda em JSON válido com as chaves:
        - score (número de 0 a 100)
        - strengths (lista de strings)
        - improvements (lista de strings)
        - keywords (lista de strings)
        - suggestions (lista de strings com sugestões específicas)
        """

    def _build_improvement_prompt(
        self,
        resume_text: str,
        job_description: str,
        current_score: float,
        improvements: List[str]
    ) -> str:
        """Build prompt for resume improvement."""
        improvements_text = "\n".join([f"- {imp}" for imp in improvements])

        return f"""
        Como especialista em recrutamento para o mercado brasileiro, melhore este currículo
        para aumentar a compatibilidade com a vaga.

        CURRÍCULO ATUAL:
        {resume_text}

        VAGA:
        {job_description}

        SCORE ATUAL: {current_score}/100

        PONTOS A MELHORAR:
        {improvements_text}

        Forneça uma versão melhorada do currículo em formato JSON:
        {{
            "improved_resume": "texto do currículo melhorado",
            "changes_made": ["lista das mudanças realizadas"],
            "expected_score": "score esperado após as melhorias"
        }}
        """

    def calculate_cosine_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
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

    def _parse_score_response(self, response: str) -> Dict[str, Any]:
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
                "score": 50,
                "strengths": ["Análise parcial concluída"],
                "improvements": ["Revisar resposta do LLM"],
                "keywords": [],
                "suggestions": ["Tentar novamente"]
            }

    async def calculate_match_score(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Calculate match score between resume and job description using LLM.

        Args:
            resume_text: Resume content
            job_description: Job description content

        Returns:
            Dictionary with score and analysis
        """
        try:
            # Build prompt
            prompt = self._build_score_prompt(resume_text, job_description)

            # Get LLM response
            response = await self.agent_manager.generate(
                prompt,
                max_tokens=2000,
                temperature=0.3  # Lower for more consistent scoring
            )

            # Parse response
            result = self._parse_score_response(response)

            # Calculate embedding-based similarity score
            try:
                resume_embedding = await self.embedding_manager.embed(resume_text)
                job_embedding = await self.embedding_manager.embed(job_description)
                embedding_score = self.calculate_cosine_similarity(
                    np.array(resume_embedding),
                    np.array(job_embedding)
                )

                # Add embedding score to result
                result["embedding_similarity"] = embedding_score

            except Exception as e:
                logger.warning(f"Failed to calculate embedding similarity: {e}")
                result["embedding_similarity"] = 0.0

            logger.info(f"Score calculated: {result.get('score', 0)}")
            return result

        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            raise ProviderError(f"Failed to calculate match score: {str(e)}") from e

    async def improve_resume(
        self,
        resume_text: str,
        job_description: str,
        current_score: float,
        improvements: List[str]
    ) -> Dict[str, Any]:
        """
        Generate improved version of resume based on analysis.

        Args:
            resume_text: Original resume content
            job_description: Job description content
            current_score: Current match score
            improvements: List of identified improvements needed

        Returns:
            Dictionary with improved resume and changes
        """
        try:
            # Build improvement prompt
            prompt = self._build_improvement_prompt(
                resume_text, job_description, current_score, improvements
            )

            # Get LLM response
            response = await self.agent_manager.generate(
                prompt,
                max_tokens=3000,
                temperature=0.7  # Higher for creative improvements
            )

            # Parse response
            result = self._parse_score_response(response)

            # Calculate new embedding similarity
            try:
                improved_resume = result.get("improved_resume", resume_text)
                resume_embedding = await self.embedding_manager.embed(improved_resume)
                job_embedding = await self.embedding_manager.embed(job_description)
                new_similarity = self.calculate_cosine_similarity(
                    np.array(resume_embedding),
                    np.array(job_embedding)
                )

                result["new_embedding_similarity"] = new_similarity

            except Exception as e:
                logger.warning(f"Failed to calculate new embedding similarity: {e}")
                result["new_embedding_similarity"] = 0.0

            logger.info("Resume improvement generated successfully")
            return result

        except Exception as e:
            logger.error(f"Error improving resume: {e}")
            raise ProviderError(f"Failed to improve resume: {str(e)}") from e

    async def analyze_and_improve(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Complete analysis and improvement workflow.

        Args:
            resume_text: Resume content
            job_description: Job description content

        Returns:
            Complete analysis with original score, improvements, and suggestions
        """
        try:
            # Step 1: Calculate initial score
            score_analysis = await self.calculate_match_score(resume_text, job_description)

            # Step 2: Generate improvements if score is below threshold
            current_score = score_analysis.get("score", 0)
            improvements = score_analysis.get("improvements", [])

            result = {
                "original_score": current_score,
                "analysis": score_analysis,
                "improvements_generated": False
            }

            if current_score < 80 and improvements:  # Only improve if score < 80%
                logger.info(f"Generating improvements for score {current_score}")

                # Step 3: Generate improved resume
                improvement_result = await self.improve_resume(
                    resume_text, job_description, current_score, improvements
                )

                result.update({
                    "improvements_generated": True,
                    "improved_resume": improvement_result.get("improved_resume"),
                    "changes_made": improvement_result.get("changes_made", []),
                    "expected_score": improvement_result.get("expected_score"),
                    "new_embedding_similarity": improvement_result.get("new_embedding_similarity")
                })

            return result

        except Exception as e:
            logger.error(f"Error in complete analysis workflow: {e}")
            raise ProviderError(f"Analysis failed: {str(e)}") from e

    async def extract_keywords(self, text: str, context: str = "general") -> List[str]:
        """
        Extract keywords from text using LLM.

        Args:
            text: Text to extract keywords from
            context: Context for keyword extraction (resume, job, general)

        Returns:
            List of extracted keywords
        """
        try:
            context_map = {
                "resume": "currículo",
                "job": "vaga de emprego",
                "general": "texto"
            }

            context_text = context_map.get(context, "texto")

            prompt = f"""
            Extraia as palavras-chave mais importantes deste {context_text}
            para o mercado brasileiro.

            TEXTO:
            {text}

            Retorne apenas uma lista JSON de palavras-chave:
            ["palavra1", "palavra2", "palavra3"]
            """

            response = await self.agent_manager.generate(
                prompt,
                max_tokens=500,
                temperature=0.2
            )

            try:
                keywords = json.loads(response)
                if isinstance(keywords, list):
                    return [str(k).strip() for k in keywords if k and str(k).strip()]
            except json.JSONDecodeError:
                pass

            # Fallback: extract simple words
            words = text.lower().split()
            return [word.strip() for word in words if len(word) > 3][:20]

        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []