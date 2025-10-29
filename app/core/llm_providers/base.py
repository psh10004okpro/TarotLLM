"""
Base LLM Provider
Abstract base class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize LLM provider

        Args:
            api_key: API key for the provider
            model_name: Model name to use
        """
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response from LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available (has valid API key)

        Returns:
            True if provider is ready to use
        """
        pass

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response from LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        # Default implementation: return full response at once
        response = await self.generate(prompt, system_prompt, **kwargs)
        yield response

    def _prepare_messages(self, prompt: str, system_prompt: Optional[str] = None) -> list:
        """
        Prepare messages in standard format

        Args:
            prompt: User prompt
            system_prompt: System prompt

        Returns:
            List of messages
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return messages

    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(model={self.model_name})"
