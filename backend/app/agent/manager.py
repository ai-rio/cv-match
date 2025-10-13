from typing import Any

from app.agent.providers.base import EmbeddingProvider, Provider
from app.agent.strategies.base import Strategy
from app.agent.strategies.wrapper import JSONWrapper, MDWrapper
from app.core.config import settings
from app.core.exceptions import ProviderError


class AgentManager:
    def __init__(
        self,
        strategy: str | None = None,
        model: str = settings.LL_MODEL or "anthropic/claude-3.5-sonnet",
        model_provider: str = settings.LLM_PROVIDER or "openrouter",
    ) -> None:
        self.strategy: Strategy
        match strategy:
            case "md":
                self.strategy = MDWrapper()
            case "json":
                self.strategy = JSONWrapper()
            case _:
                self.strategy = JSONWrapper()
        self.model = model
        self.model_provider = model_provider

    async def _get_provider(self, **kwargs: Any) -> Provider:
        # Default options for any LLM. Not all can handle them
        # (e.g. OpenAI doesn't take top_k) but each provider can make
        # best effort.
        opts = {"temperature": 0, "top_p": 0.9, "top_k": 40, "num_ctx": 20000}
        opts.update(kwargs)
        match self.model_provider:
            case "openai":
                from .providers.openai import OpenAIProvider

                api_key = str(opts.get("llm_api_key", settings.LLM_API_KEY or "")) or None
                return OpenAIProvider(model_name=self.model, api_key=api_key, opts=opts)
            case "openrouter":
                from .providers.openrouter import OpenRouterProvider

                api_key_raw = (
                    opts.get("llm_api_key", settings.OPENROUTER_API_KEY)
                    or settings.LLM_API_KEY
                    or ""
                )
                api_base_url_raw = opts.get("llm_base_url", settings.LLM_BASE_URL or "")
                api_key = str(api_key_raw) if api_key_raw else None
                api_base_url = str(api_base_url_raw) if api_base_url_raw else None
                return OpenRouterProvider(
                    model_name=self.model,
                    api_key=api_key,
                    api_base_url=api_base_url,
                    opts=opts,
                )
            case _:
                raise ProviderError(
                    f"Unsupported LLM provider: {self.model_provider}. "
                    "Supported providers: openai, openrouter"
                )

    async def run(self, prompt: str, **kwargs: Any) -> Any:
        """
        Run the agent with the given prompt and generation arguments.
        """
        provider = await self._get_provider(**kwargs)
        return await self.strategy(prompt, provider, **kwargs)

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text response (convenience method).
        """
        result = await self.run(prompt, **kwargs)
        if isinstance(result, dict):
            return result.get("text", "")
        elif isinstance(result, str):
            return result
        else:
            return str(result)


class EmbeddingManager:
    def __init__(
        self,
        model: str = settings.EMBEDDING_MODEL or "text-embedding-3-small",
        model_provider: str = settings.EMBEDDING_PROVIDER or "openrouter",
    ) -> None:
        self._model = model
        self._model_provider = model_provider

    async def _get_embedding_provider(self, **kwargs: Any) -> EmbeddingProvider:
        match self._model_provider:
            case "openai":
                from .providers.openai import OpenAIEmbeddingProvider

                api_key = (
                    str(kwargs.get("openai_api_key", settings.EMBEDDING_API_KEY or "")) or None
                )
                return OpenAIEmbeddingProvider(api_key=api_key, embedding_model=self._model)
            case "openrouter":
                from .providers.openrouter import OpenRouterEmbeddingProvider

                api_key_raw = kwargs.get(
                    "embedding_api_key",
                    settings.OPENROUTER_API_KEY or settings.EMBEDDING_API_KEY or "",
                )
                api_base_url_raw = kwargs.get(
                    "embedding_base_url", settings.EMBEDDING_BASE_URL or ""
                )
                api_key = str(api_key_raw) if api_key_raw else None
                api_base_url = str(api_base_url_raw) if api_base_url_raw else None
                return OpenRouterEmbeddingProvider(
                    api_key=api_key,
                    embedding_model=self._model,
                    api_base_url=api_base_url,
                )
            case _:
                raise ProviderError(
                    f"Unsupported embedding provider: {self._model_provider}. "
                    "Supported providers: openai, openrouter"
                )

    async def embed(self, text: str, **kwargs: Any) -> list[float]:
        """
        Get the embedding for the given text.
        """
        provider = await self._get_embedding_provider(**kwargs)
        return await provider.embed(text)
