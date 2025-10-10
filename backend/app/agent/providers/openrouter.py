"""OpenRouter provider for AI agent system."""

import logging
from typing import Any

from openai import AsyncOpenAI

from ...core.config import settings
from ..exceptions import ProviderError
from .base import EmbeddingProvider, Provider

logger = logging.getLogger(__name__)


class OpenRouterProvider(Provider):
    """OpenRouter provider using OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        api_base_url: str | None = None,
        opts: dict[str, Any] | None = None,
    ):
        """
        Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY)
            model_name: Model to use (defaults to config)
            api_base_url: API base URL (defaults to OpenRouter URL)
            opts: Additional options for generation
        """
        if opts is None:
            opts = {}

        # Get API key from settings or OPENROUTER_API_KEY
        self.api_key = api_key or settings.OPENROUTER_API_KEY or settings.LLM_API_KEY
        if not self.api_key:
            raise ProviderError(
                "OpenRouter API key is missing. Set OPENROUTER_API_KEY in your .env file."
            )

        # Get model name
        self.model = model_name or settings.LL_MODEL or "anthropic/claude-3.5-sonnet"

        # Get base URL
        base_url = api_base_url or settings.LLM_BASE_URL or "https://openrouter.ai/api/v1"

        # Initialize OpenAI client with OpenRouter base URL
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url,
        )

        self.opts = opts

        logger.info(f"Initialized OpenRouterProvider with model: {self.model}")

    async def __call__(self, prompt: str, **generation_args: Any) -> str:
        """
        Generate response using OpenRouter API.

        Args:
            prompt: Input prompt
            generation_args: Additional generation arguments (merged with opts)

        Returns:
            Generated text response

        Raises:
            ProviderError: If generation fails
        """
        try:
            # Merge options with generation args
            temperature = generation_args.get("temperature", self.opts.get("temperature", 0))
            top_p = generation_args.get("top_p", self.opts.get("top_p", 0.9))
            max_tokens = generation_args.get("max_tokens", self.opts.get("max_tokens", 4000))

            # Call OpenRouter API
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )

            # Extract response text
            content = response.choices[0].message.content

            if not content:
                raise ProviderError("Empty response from OpenRouter API")

            return content

        except Exception as e:
            logger.exception(f"OpenRouter error: {str(e)}")
            raise ProviderError(f"OpenRouter - Error generating response: {str(e)}") from e


class OpenRouterEmbeddingProvider(EmbeddingProvider):
    """OpenRouter embedding provider (uses OpenAI-compatible models)."""

    def __init__(
        self,
        api_key: str | None = None,
        embedding_model: str | None = None,
        api_base_url: str | None = None,
    ):
        """
        Initialize OpenRouter embedding provider.

        Args:
            api_key: OpenRouter API key
            embedding_model: Embedding model to use
            api_base_url: API base URL
        """
        # Get API key
        self.api_key = api_key or settings.OPENROUTER_API_KEY or settings.EMBEDDING_API_KEY
        if not self.api_key:
            raise ProviderError(
                "OpenRouter API key is missing. Set OPENROUTER_API_KEY in your .env file."
            )

        # Get model
        self._model = embedding_model or settings.EMBEDDING_MODEL or "text-embedding-3-small"

        # Get base URL
        base_url = api_base_url or settings.EMBEDDING_BASE_URL or "https://openrouter.ai/api/v1"

        # Initialize client
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url,
        )

        logger.info(f"Initialized OpenRouterEmbeddingProvider with model: {self._model}")

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            ProviderError: If embedding generation fails
        """
        try:
            response = await self._client.embeddings.create(
                input=text,
                model=self._model,
            )
            return response.data[0].embedding

        except Exception as e:
            logger.exception(f"OpenRouter embedding error: {str(e)}")
            raise ProviderError(f"OpenRouter - Error generating embedding: {str(e)}") from e
