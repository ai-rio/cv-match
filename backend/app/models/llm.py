from typing import Literal

from pydantic import BaseModel, Field


class LLMUsage(BaseModel):
    """Usage information for an LLM API call."""

    prompt_tokens: int
    completion_tokens: int | None = None
    total_tokens: int


class TextGenerationRequest(BaseModel):
    """Request for text generation."""

    prompt: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = Field(default=500, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    provider: Literal["openai", "anthropic"] = "openai"


class TextGenerationResponse(BaseModel):
    """Response from text generation."""

    text: str
    model: str
    usage: LLMUsage


class EmbeddingRequest(BaseModel):
    """Request for creating an embedding."""

    text: str
    model: str = "text-embedding-ada-002"
    provider: Literal["openai", "anthropic"] = "openai"


class EmbeddingResponse(BaseModel):
    """Response from embedding creation."""

    embedding: list[float]
    model: str
    usage: LLMUsage
