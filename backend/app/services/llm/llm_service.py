from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any

import anthropic
import openai
from pydantic import BaseModel

from app.core.config import settings
from app.models.llm_models import LLMUsage


class ProviderError(Exception):
    """Exception raised when LLM provider encounters an error."""
    pass


class AgentManager:
    """Manager for LLM agents with multiple provider support."""
    
    def __init__(self, provider: str = "openai"):
        """Initialize agent manager with specified provider."""
        self.provider = provider
        self.service = get_llm_service(provider)
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: str | None = None,
        **kwargs: Any
    ) -> str:
        """
        Generate text using the configured LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Model name (uses provider default if None)
            **kwargs: Additional parameters
            
        Returns:
            Generated text as string
            
        Raises:
            ProviderError: If LLM generation fails
        """
        try:
            if model is None:
                model = "gpt-3.5-turbo" if self.provider == "openai" else "claude-3-sonnet-20240229"
            
            response = await self.service.generate_text(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.text
        except Exception as e:
            raise ProviderError(f"LLM generation failed: {str(e)}") from e


class LLMResponse(BaseModel):
    """Response from an LLM service."""

    text: str
    model: str
    usage: LLMUsage


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def generate_text(
        self, prompt: str, model: str, max_tokens: int = 500, temperature: float = 0.7, **kwargs: dict[str, Any]
    ) -> LLMResponse:
        """Generate text using the LLM."""
        pass


class OpenAIService(LLMService):
    """OpenAI implementation of the LLM service."""

    def __init__(self, api_key: str):
        """Initialize the OpenAI client."""
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs: dict[str, Any],
    ) -> LLMResponse:
        """Generate text using OpenAI."""
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if not response.usage:
            raise ValueError("OpenAI API returned no usage information")
        
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("OpenAI API returned no content")

        usage = LLMUsage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
        )

        return LLMResponse(text=response.choices[0].message.content, model=model, usage=usage)


class AnthropicService(LLMService):
    """Anthropic (Claude) implementation of the LLM service."""

    def __init__(self, api_key: str):
        """Initialize the Anthropic client."""
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_text(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs: dict[str, Any],
    ) -> LLMResponse:
        """Generate text using Anthropic Claude."""
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        if not response.usage:
            raise ValueError("Anthropic API returned no usage information")
        
        if not response.content or not response.content[0].text:
            raise ValueError("Anthropic API returned no content")

        usage = LLMUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        )

        return LLMResponse(text=response.content[0].text, model=model, usage=usage)


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    @staticmethod
    def get_service(provider: str) -> LLMService:
        """Get an LLM service by provider name."""
        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            return OpenAIService(api_key=settings.OPENAI_API_KEY)
        elif provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not configured")
            return AnthropicService(api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


@lru_cache
def get_llm_service(provider: str = "openai") -> LLMService:
    """Dependency to get an LLM service."""
    return LLMServiceFactory.get_service(provider)
