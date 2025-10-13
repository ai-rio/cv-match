import logging
import os
from typing import Any

from fastapi.concurrency import run_in_threadpool
from openai import OpenAI

from app.agent.exceptions import ProviderError
from app.agent.providers.base import EmbeddingProvider, Provider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(Provider):
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = settings.LL_MODEL or "gpt-3.5-turbo",
        opts: dict[str, Any] | None = None,
    ):
        if opts is None:
            opts = {}
        api_key = api_key or settings.LLM_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OpenAI API key is missing")
        self._client = OpenAI(api_key=api_key)
        self.model = model_name
        self.opts = opts
        self.instructions = ""

    def _generate_sync(self, prompt: str, options: dict[str, Any]) -> str:
        try:
            response = self._client.responses.create(
                model=self.model,
                instructions=self.instructions,
                input=prompt,
                **options,
            )
            return response.output_text
        except Exception as e:
            raise ProviderError(f"OpenAI - error generating response: {e}") from e

    async def __call__(self, prompt: str, **generation_args: Any) -> str:
        if generation_args:
            logger.warning(f"OpenAIProvider - generation_args not used {generation_args}")
        myopts = {
            "temperature": self.opts.get("temperature", 0),
            "top_p": self.opts.get("top_p", 0.9),
            # top_k not currently supported by any OpenAI model - https://community.openai.com/t/does-openai-have-a-top-k-parameter/612410
            #            "top_k": generation_args.get("top_k", 40),
            # neither max_tokens
            #            "max_tokens": generation_args.get("max_length", 20000),
        }
        return await run_in_threadpool(self._generate_sync, prompt, myopts)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str | None = None,
        embedding_model: str = settings.EMBEDDING_MODEL or "text-embedding-3-small",
    ):
        api_key = api_key or settings.EMBEDDING_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OpenAI API key is missing")
        self._client = OpenAI(api_key=api_key)
        self._model = embedding_model

    async def embed(self, text: str) -> list[float]:
        try:
            response = await run_in_threadpool(
                self._client.embeddings.create, input=text, model=self._model
            )
            return response.data[0].embedding
        except Exception as e:
            raise ProviderError(f"OpenAI - error generating embedding: {e}") from e
