from abc import ABC, abstractmethod
from typing import Any, TypeVar

from ..providers.base import Provider

StrategyType = TypeVar("StrategyType")


class Strategy(ABC):
    @abstractmethod
    async def __call__(self, prompt: str, provider: Provider, **generation_args: Any) -> Any:
        """
        Abstract method which should be used to define the strategy for
        generating a response from LLM.

        Args:
            prompt (str): The input prompt for the provider.
            provider (Provider): The provider instance to use for generation.
            **generation_args (Any): Additional arguments for generation.

        Returns:
            Any: The generated response (can be dict, str, etc. depending on strategy).
        """
        ...
