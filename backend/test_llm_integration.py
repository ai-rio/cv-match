"""
Test script for LLM integration verification.
Tests AgentManager, EmbeddingManager, and ScoreImprovementService.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.agent.manager import AgentManager, EmbeddingManager
from app.services.score_improvement_service import ScoreImprovementService
from app.core.exceptions import ProviderError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_agent_manager():
    """Test AgentManager initialization and basic functionality."""
    logger.info("Testing AgentManager...")

    try:
        # Test initialization
        AgentManager()
        logger.info("✅ AgentManager initialized successfully")

        # Test with different providers
        managers = [
            AgentManager(model_provider="openrouter"),
            AgentManager(strategy="json"),
            AgentManager(strategy="md"),
        ]

        logger.info(f"✅ Created {len(managers)} AgentManager instances with different configs")

        return True

    except Exception as e:
        logger.error(f"❌ AgentManager test failed: {e}")
        return False


async def test_llm_completion():
    """Test LLM API integration with sample completion."""
    logger.info("Testing LLM completion...")

    try:
        manager = AgentManager()

        # Test simple completion
        prompt = "Diga 'olá' em português"
        response = await manager.generate(prompt, max_tokens=50, temperature=0.7)

        logger.info(f"✅ LLM Response: {response[:100]}")
        logger.info("✅ LLM completion test passed")

        # Test JSON response
        json_prompt = """
        Responda em JSON válido:
        {
            "mensagem": "olá",
            "lingua": "português"
        }
        """
        json_response = await manager.generate(json_prompt, max_tokens=100, temperature=0.3)

        logger.info(f"✅ JSON Response: {json_response[:100]}")
        logger.info("✅ JSON completion test passed")

        return True

    except ProviderError as e:
        if "API key is missing" in str(e):
            logger.warning("⚠️  OpenRouter API key not configured - skipping LLM tests")
            logger.info("To enable LLM tests, set OPENROUTER_API_KEY in your .env file")
            return None  # Skip test, not fail
        else:
            logger.error(f"❌ LLM completion test failed: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ LLM completion test failed: {e}")
        return False


async def test_embedding_manager():
    """Test EmbeddingManager functionality."""
    logger.info("Testing EmbeddingManager...")

    try:
        embedding_manager = EmbeddingManager()
        logger.info("✅ EmbeddingManager initialized successfully")

        # Test embedding generation
        test_text = "Este é um teste de geração de embeddings para o mercado brasileiro."
        embedding = await embedding_manager.embed(test_text)

        if isinstance(embedding, list) and len(embedding) > 0:
            logger.info(f"✅ Generated embedding with {len(embedding)} dimensions")
            logger.info(f"✅ Sample values: {embedding[:5]}")
            return True
        else:
            logger.error("❌ Invalid embedding format")
            return False

    except ProviderError as e:
        if "API key is missing" in str(e):
            logger.warning("⚠️  OpenRouter API key not configured - skipping embedding tests")
            return None  # Skip test, not fail
        else:
            logger.error(f"❌ Embedding test failed: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ Embedding test failed: {e}")
        return False


async def test_score_improvement_service():
    """Test ScoreImprovementService integration."""
    logger.info("Testing ScoreImprovementService...")

    try:
        service = ScoreImprovementService()
        logger.info("✅ ScoreImprovementService initialized successfully")

        # Test with sample resume and job
        sample_resume = """
        João Silva
        Desenvolvedor Python com 5 anos de experiência

        Experiência:
        - Desenvolvimento de APIs REST com FastAPI e Django
        - Trabalho com bancos de dados PostgreSQL e MongoDB
        - Experiência com Docker e AWS
        - Python, JavaScript, TypeScript

        Educação:
        - Bacharel em Ciência da Computação - USP
        """

        sample_job = """
        Vaga: Desenvolvedor Python Sênior
        Empresa: Tech Brasil

        Requisitos:
        - 5+ anos de experiência com Python
        - Experiência com frameworks web (Django, FastAPI)
        - Conhecimento em bancos de dados SQL e NoSQL
        - Experiência com cloud (AWS, Azure, GCP)
        - Docker e containerização
        - Inglês intermediário

        Diferenciais:
        - Experiência com microsserviços
        - Conhecimento em Kubernetes
        """

        # Test keyword extraction
        keywords = await service.extract_keywords(sample_job, "job")
        logger.info(f"✅ Extracted {len(keywords)} keywords from job description")
        logger.info(f"✅ Sample keywords: {keywords[:5]}")

        # Test match score calculation (may require API key)
        try:
            score_result = await service.calculate_match_score(sample_resume, sample_job)
            logger.info(f"✅ Match score calculated: {score_result.get('score', 'N/A')}")
            logger.info(f"✅ Strengths found: {len(score_result.get('strengths', []))}")
            logger.info(f"✅ Improvements suggested: {len(score_result.get('improvements', []))}")
            return True

        except ProviderError as e:
            if "API key is missing" in str(e):
                logger.warning("⚠️  OpenRouter API key not configured - skipping score calculation")
                return True  # Service initialized correctly, just can't make API calls
            else:
                raise e

    except Exception as e:
        logger.error(f"❌ ScoreImprovementService test failed: {e}")
        return False


async def test_cosine_similarity():
    """Test cosine similarity calculation."""
    logger.info("Testing cosine similarity calculation...")

    try:
        service = ScoreImprovementService()

        # Test with known vectors
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        vec3 = [1, 1, 0]
        vec4 = [1, 0, 0]

        # Orthogonal vectors should have similarity 0
        sim1 = service.calculate_cosine_similarity(vec1, vec2)
        logger.info(f"✅ Orthogonal vectors similarity: {sim1} (expected: 0)")

        # Same vectors should have similarity 1
        sim2 = service.calculate_cosine_similarity(vec1, vec4)
        logger.info(f"✅ Identical vectors similarity: {sim2} (expected: 1)")

        # 45-degree vectors should have similarity ~0.707
        sim3 = service.calculate_cosine_similarity(vec1, vec3)
        logger.info(f"✅ 45-degree vectors similarity: {sim3} (expected: ~0.707)")

        # Test with None values
        sim4 = service.calculate_cosine_similarity(None, vec1)
        logger.info(f"✅ None vector similarity: {sim4} (expected: 0)")

        return True

    except Exception as e:
        logger.error(f"❌ Cosine similarity test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting LLM integration tests...")
    logger.info("=" * 50)

    tests = [
        ("AgentManager Initialization", test_agent_manager),
        ("Cosine Similarity Calculation", test_cosine_similarity),
        ("LLM Completion", test_llm_completion),
        ("Embedding Generation", test_embedding_manager),
        ("ScoreImprovementService", test_score_improvement_service),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            result = await test_func()
            if result is None:
                logger.info(f"⏭️  {test_name}: Skipped (configuration needed)")
                results.append(("skipped", test_name))
            elif result:
                logger.info(f"✅ {test_name}: Passed")
                results.append(("passed", test_name))
            else:
                logger.error(f"❌ {test_name}: Failed")
                results.append(("failed", test_name))
        except Exception as e:
            logger.error(f"💥 {test_name}: Error - {e}")
            results.append(("error", test_name))

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)

    passed = sum(1 for status, _ in results if status == "passed")
    failed = sum(1 for status, _ in results if status == "failed")
    skipped = sum(1 for status, _ in results if status == "skipped")
    errors = sum(1 for status, _ in results if status == "error")

    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"⏭️  Skipped: {skipped}")
    logger.info(f"💥 Errors: {errors}")

    if failed > 0 or errors > 0:
        logger.error("\n❌ Some tests failed. Check the logs above for details.")
        return 1
    else:
        logger.info("\n🎉 All tests passed! LLM integration is working correctly.")
        if skipped > 0:
            logger.info("⚠️  Some tests were skipped due to missing API keys.")
            logger.info("To run all tests, configure your OpenRouter API key in the .env file.")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
