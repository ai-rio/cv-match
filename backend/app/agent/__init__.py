# Generic async LLM-agent - automatic provider selection

# * Configured via LLM_PROVIDER in settings (default: openrouter)
# * Supports: openrouter (default), openai
# * Requires OPENROUTER_API_KEY or LLM_API_KEY in .env
# * If provider not configured correctly, raises ProviderError.

from .manager import AgentManager, EmbeddingManager

__all__ = ["AgentManager", "EmbeddingManager"]
