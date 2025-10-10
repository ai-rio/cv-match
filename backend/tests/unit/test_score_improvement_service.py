"""
Unit tests for ScoreImprovementService.
Tests resume-job matching, scoring, and improvement suggestions.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.core.exceptions import ProviderError
from app.services.score_improvement_service import ScoreImprovementService


@pytest.fixture
def score_service():
    """Create ScoreImprovementService instance for testing."""
    with (
        patch("app.services.score_improvement_service.AgentManager") as mock_agent_manager,
        patch("app.services.score_improvement_service.EmbeddingManager") as mock_embedding_manager,
    ):
        mock_agent_manager.return_value = MagicMock()
        mock_embedding_manager.return_value = MagicMock()

        service = ScoreImprovementService()
        service.agent_manager = mock_agent_manager.return_value
        service.embedding_manager = mock_embedding_manager.return_value

        return service


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    João Silva
    Desenvolvedor Python Sênior

    EXPERIÊNCIA:
    - TechCorp (2020-2024): Desenvolvimento de APIs com FastAPI
    - DataTech (2018-2020): Análise de dados com Python e SQL

    SKILLS:
    Python, FastAPI, PostgreSQL, Docker, AWS, Git, Agile

    EDUCAÇÃO:
    Bacharel em Ciência da Computação - USP (2018)
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    VAGA: Desenvolvedor Python Sênior

    REQUISITOS:
    - 5+ anos de experiência com Python
    - Experiência com FastAPI e frameworks web
    - Conhecimento em PostgreSQL e bancos de dados relacionais
    - Experiência com Docker e cloud services
    - Inglês intermediário

    RESPONSABILIDADES:
    - Desenvolver APIs RESTful
    - Otimizar performance de aplicações
    - Mentoria para equipe junior
    - Colaboração em projetos ágeis
    """


@pytest.fixture
def mock_score_response():
    """Mock LLM response for score analysis."""
    return {
        "score": 85,
        "strengths": [
            "Experiência sólida com Python e FastAPI",
            "Conhecimento em PostgreSQL",
            "Experiência relevante na área",
        ],
        "improvements": [
            "Adicionar informações sobre experiências com cloud",
            "Detalhar projetos específicos",
            "Incluir certificações relevantes",
        ],
        "keywords": ["Python", "FastAPI", "PostgreSQL", "Docker", "API"],
        "suggestions": [
            "Adicionar seção de projetos pessoais",
            "Incluir métricas de impacto nos projetos",
            "Mencionar experiências com liderança técnica",
        ],
    }


@pytest.fixture
def mock_improvement_response():
    """Mock LLM response for resume improvement."""
    return {
        "improved_resume": """
        João Silva
        Desenvolvedor Python Sênior | AWS Certified | 6+ anos de experiência

        EXPERIÊNCIA PROFISSIONAL:
        TechCorp - Desenvolvedor Python Sênior (2020-2024)
        • Desenvolvimento de 15+ APIs RESTful com FastAPI, servindo 1M+ requisições/dia
        • Otimização de queries PostgreSQL reduzindo tempo de resposta em 40%
        • Liderança técnica de equipe de 3 desenvolvedores junior
        • Implementação de pipelines CI/CD com Docker e AWS

        PROJETOS DESTAQUE:
        • Sistema de processamento de dados distribuído (Python, Docker, AWS)
        • API de microsserviços com 99.9% uptime

        CERTIFICAÇÕES:
        • AWS Certified Developer - Associate (2023)
        • Postgres Professional Certification (2022)
        """,
        "changes_made": [
            "Adicionado certificações AWS e PostgreSQL",
            "Incluídas métricas quantitativas de impacto",
            "Destacada experiência em liderança técnica",
            "Adicionada seção de projetos com resultados",
        ],
        "expected_score": 92,
    }


def test_score_service_initialization():
    """Test ScoreImprovementService initialization."""
    with (
        patch("app.services.score_improvement_service.AgentManager") as mock_agent_manager,
        patch("app.services.score_improvement_service.EmbeddingManager") as mock_embedding_manager,
    ):
        mock_agent_manager.return_value = MagicMock()
        mock_embedding_manager.return_value = MagicMock()

        service = ScoreImprovementService()

        assert service is not None
        assert hasattr(service, "agent_manager")
        assert hasattr(service, "embedding_manager")


def test_score_service_initialization_error():
    """Test ScoreImprovementService initialization with error."""
    with patch(
        "app.services.score_improvement_service.AgentManager",
        side_effect=Exception("Initialization failed"),
    ):
        with pytest.raises(Exception, match="Failed to initialize ScoreImprovementService"):
            ScoreImprovementService()


def test_build_score_prompt(score_service, sample_resume_text, sample_job_description):
    """Test building score analysis prompt."""
    prompt = score_service._build_score_prompt(sample_resume_text, sample_job_description)

    assert "Você é um especialista em análise de currículos" in prompt
    assert sample_resume_text in prompt
    assert sample_job_description in prompt
    assert "score (número de 0 a 100)" in prompt
    assert "strengths" in prompt
    assert "improvements" in prompt


def test_build_improvement_prompt(score_service, sample_resume_text, sample_job_description):
    """Test building improvement prompt."""
    improvements = ["Adicionar métricas", "Incluir certificações"]
    prompt = score_service._build_improvement_prompt(
        sample_resume_text, sample_job_description, 75, improvements
    )

    assert "Como especialista em recrutamento" in prompt
    assert sample_resume_text in prompt
    assert sample_job_description in prompt
    assert "75/100" in prompt
    assert "Adicionar métricas" in prompt
    assert "Incluir certificações" in prompt


def test_calculate_cosine_similarity_normal_case(score_service):
    """Test cosine similarity calculation with normal vectors."""
    vec1 = np.array([1, 2, 3])
    vec2 = np.array([4, 5, 6])

    similarity = score_service.calculate_cosine_similarity(vec1, vec2)

    assert isinstance(similarity, float)
    assert 0 <= similarity <= 1


def test_calculate_cosine_similarity_zero_vectors(score_service):
    """Test cosine similarity with zero vectors."""
    vec1 = np.array([0, 0, 0])
    vec2 = np.array([1, 2, 3])

    similarity = score_service.calculate_cosine_similarity(vec1, vec2)

    assert similarity == 0.0


def test_calculate_cosine_similarity_none_inputs(score_service):
    """Test cosine similarity with None inputs."""
    similarity = score_service.calculate_cosine_similarity(None, None)

    assert similarity == 0.0


def test_calculate_cosine_similarity_single_dimension(score_service):
    """Test cosine similarity with single dimension vectors."""
    vec1 = np.array([5])
    vec2 = np.array([10])

    similarity = score_service.calculate_cosine_similarity(vec1, vec2)

    assert similarity == 1.0  # Same direction, different magnitude


def test_parse_score_response_valid_json(score_service, mock_score_response):
    """Test parsing valid JSON response."""
    json_response = json.dumps(mock_score_response)

    result = score_service._parse_score_response(json_response)

    assert result == mock_score_response
    assert result["score"] == 85
    assert len(result["strengths"]) == 3


def test_parse_score_response_markdown_json(score_service, mock_score_response):
    """Test parsing JSON response wrapped in markdown."""
    json_response = f"```json\n{json.dumps(mock_score_response)}\n```"

    result = score_service._parse_score_response(json_response)

    assert result == mock_score_response
    assert result["score"] == 85


def test_parse_score_response_invalid_json(score_service):
    """Test parsing invalid JSON response."""
    invalid_response = "This is not valid JSON content"

    result = score_service._parse_score_response(invalid_response)

    assert result["score"] == 50
    assert "Análise parcial concluída" in result["strengths"]


@pytest.mark.asyncio
async def test_calculate_match_score_success(
    score_service, sample_resume_text, sample_job_description, mock_score_response
):
    """Test successful match score calculation."""
    # Mock LLM response
    score_service.agent_manager.generate = AsyncMock(return_value=json.dumps(mock_score_response))

    # Mock embedding response
    score_service.embedding_manager.embed = AsyncMock(
        side_effect=[np.array([1, 2, 3]), np.array([4, 5, 6])]
    )

    result = await score_service.calculate_match_score(sample_resume_text, sample_job_description)

    assert result["score"] == 85
    assert "strengths" in result
    assert "improvements" in result
    assert "embedding_similarity" in result
    assert isinstance(result["embedding_similarity"], float)

    score_service.agent_manager.generate.assert_called_once()
    assert score_service.embedding_manager.embed.call_count == 2


@pytest.mark.asyncio
async def test_calculate_match_score_embedding_error(
    score_service, sample_resume_text, sample_job_description, mock_score_response
):
    """Test match score calculation with embedding error."""
    # Mock LLM response
    score_service.agent_manager.generate = AsyncMock(return_value=json.dumps(mock_score_response))

    # Mock embedding error
    score_service.embedding_manager.embed = AsyncMock(side_effect=Exception("Embedding failed"))

    result = await score_service.calculate_match_score(sample_resume_text, sample_job_description)

    assert result["score"] == 85
    assert result["embedding_similarity"] == 0.0


@pytest.mark.asyncio
async def test_calculate_match_score_llm_error(
    score_service, sample_resume_text, sample_job_description
):
    """Test match score calculation with LLM error."""
    # Mock LLM error
    score_service.agent_manager.generate = AsyncMock(side_effect=Exception("LLM failed"))

    with pytest.raises(ProviderError, match="Failed to calculate match score"):
        await score_service.calculate_match_score(sample_resume_text, sample_job_description)


@pytest.mark.asyncio
async def test_improve_resume_success(
    score_service, sample_resume_text, sample_job_description, mock_improvement_response
):
    """Test successful resume improvement."""
    improvements = ["Adicionar métricas", "Incluir certificações"]

    # Mock LLM response
    score_service.agent_manager.generate = AsyncMock(
        return_value=json.dumps(mock_improvement_response)
    )

    # Mock embedding response
    score_service.embedding_manager.embed = AsyncMock(
        side_effect=[np.array([1, 2, 3]), np.array([4, 5, 6])]
    )

    result = await score_service.improve_resume(
        sample_resume_text, sample_job_description, 75, improvements
    )

    assert "improved_resume" in result
    assert "changes_made" in result
    assert "expected_score" in result
    assert "new_embedding_similarity" in result
    assert len(result["changes_made"]) > 0


@pytest.mark.asyncio
async def test_improve_resume_llm_error(score_service, sample_resume_text, sample_job_description):
    """Test resume improvement with LLM error."""
    improvements = ["Adicionar métricas"]

    # Mock LLM error
    score_service.agent_manager.generate = AsyncMock(side_effect=Exception("LLM failed"))

    with pytest.raises(ProviderError, match="Failed to improve resume"):
        await score_service.improve_resume(
            sample_resume_text, sample_job_description, 75, improvements
        )


@pytest.mark.asyncio
async def test_analyze_and_improve_high_score(
    score_service, sample_resume_text, sample_job_description, mock_score_response
):
    """Test complete analysis workflow with high score (no improvements needed)."""
    # High score response (above threshold)
    high_score_response = mock_score_response.copy()
    high_score_response["score"] = 90

    score_service.agent_manager.generate = AsyncMock(return_value=json.dumps(high_score_response))
    score_service.embedding_manager.embed = AsyncMock(
        side_effect=[np.array([1, 2, 3]), np.array([4, 5, 6])]
    )

    result = await score_service.analyze_and_improve(sample_resume_text, sample_job_description)

    assert result["original_score"] == 90
    assert "analysis" in result
    assert result["improvements_generated"] is False
    assert "improved_resume" not in result


@pytest.mark.asyncio
async def test_analyze_and_improve_low_score(
    score_service,
    sample_resume_text,
    sample_job_description,
    mock_score_response,
    mock_improvement_response,
):
    """Test complete analysis workflow with low score (improvements needed)."""
    # Low score response (below threshold)
    low_score_response = mock_score_response.copy()
    low_score_response["score"] = 70

    # Mock different responses for the two LLM calls
    score_service.agent_manager.generate = AsyncMock(
        side_effect=[json.dumps(low_score_response), json.dumps(mock_improvement_response)]
    )
    score_service.embedding_manager.embed = AsyncMock(
        side_effect=[
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([7, 8, 9]),
            np.array([10, 11, 12]),
        ]
    )

    result = await score_service.analyze_and_improve(sample_resume_text, sample_job_description)

    assert result["original_score"] == 70
    assert "analysis" in result
    assert result["improvements_generated"] is True
    assert "improved_resume" in result
    assert "changes_made" in result
    assert "expected_score" in result


@pytest.mark.asyncio
async def test_extract_keywords_valid_response(score_service):
    """Test keyword extraction with valid JSON response."""
    test_text = "Python developer with experience in FastAPI, PostgreSQL, and Docker"

    # Mock LLM response
    score_service.agent_manager.generate = AsyncMock(
        return_value='["Python", "FastAPI", "PostgreSQL", "Docker"]'
    )

    result = await score_service.extract_keywords(test_text, "resume")

    assert isinstance(result, list)
    assert "Python" in result
    assert "FastAPI" in result
    assert len(result) == 4


@pytest.mark.asyncio
async def test_extract_keywords_invalid_json(score_service):
    """Test keyword extraction with invalid JSON response."""
    test_text = "Python developer with experience in FastAPI and PostgreSQL"

    # Mock invalid LLM response
    score_service.agent_manager.generate = AsyncMock(return_value="This is not valid JSON")

    result = await score_service.extract_keywords(test_text, "job")

    assert isinstance(result, list)
    # Should return fallback extraction
    assert len(result) > 0


@pytest.mark.asyncio
async def test_extract_keywords_different_contexts(score_service):
    """Test keyword extraction with different contexts."""
    test_text = "Software engineer experienced in web development"

    # Mock LLM response
    score_service.agent_manager.generate = AsyncMock(
        return_value='["software", "engineer", "web", "development"]'
    )

    # Test resume context
    result_resume = await score_service.extract_keywords(test_text, "resume")
    assert isinstance(result_resume, list)

    # Test job context
    score_service.agent_manager.generate = AsyncMock(
        return_value='["software", "engineer", "web", "development"]'
    )
    result_job = await score_service.extract_keywords(test_text, "job")
    assert isinstance(result_job, list)

    # Test general context
    score_service.agent_manager.generate = AsyncMock(
        return_value='["software", "engineer", "web", "development"]'
    )
    result_general = await score_service.extract_keywords(test_text, "general")
    assert isinstance(result_general, list)


@pytest.mark.asyncio
async def test_extract_keywords_error(score_service):
    """Test keyword extraction with error."""
    test_text = "Sample text for testing"

    # Mock LLM error
    score_service.agent_manager.generate = AsyncMock(side_effect=Exception("LLM failed"))

    result = await score_service.extract_keywords(test_text, "general")

    assert result == []  # Should return empty list on error


def test_parse_score_response_partial_json(score_service):
    """Test parsing response with partial JSON content."""
    partial_response = 'Some text before {"score": 75} and some text after'

    result = score_service._parse_score_response(partial_response)

    # Should fallback to default response
    assert result["score"] == 50
    assert "Análise parcial concluída" in result["strengths"]


@pytest.mark.asyncio
async def test_analyze_and_improve_error(score_service, sample_resume_text, sample_job_description):
    """Test complete analysis workflow with error."""
    # Mock LLM error
    score_service.agent_manager.generate = AsyncMock(side_effect=Exception("Analysis failed"))

    with pytest.raises(ProviderError, match="Analysis failed"):
        await score_service.analyze_and_improve(sample_resume_text, sample_job_description)
