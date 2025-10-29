"""
LLM Service
Manages interactions with different LLM providers
"""

from typing import Optional, Dict, Any, List
from app.core.llm_providers.base import BaseLLMProvider
from app.core.llm_providers.claude_provider import ClaudeProvider
from app.core.llm_providers.openai_provider import OpenAIProvider
from app.core.llm_providers.gemini_provider import GeminiProvider
from app.config import settings


class LLMService:
    """Service for managing LLM provider interactions"""

    def __init__(self):
        """Initialize LLM service with available providers"""
        self.providers: Dict[str, BaseLLMProvider] = {
            "claude": ClaudeProvider(),
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider()
        }
        self.default_provider = settings.DEFAULT_LLM_PROVIDER

    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """
        Get LLM provider by name

        Args:
            provider_name: Name of the provider (claude/openai/gemini)

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider not found
        """
        name = provider_name or self.default_provider

        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not found. Available: {list(self.providers.keys())}")

        return self.providers[name]

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response from LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            provider_name: LLM provider to use
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated response text
        """
        provider = self.get_provider(provider_name)
        return await provider.generate(prompt, system_prompt, **kwargs)

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response with additional context (for RAG)

        Args:
            prompt: User prompt
            context: Additional context (e.g., from RAG)
            system_prompt: System prompt
            provider_name: LLM provider to use
            **kwargs: Additional parameters

        Returns:
            Generated response text
        """
        enhanced_prompt = f"""Context information:
{context}

User question:
{prompt}

Please provide a response based on the context provided."""

        return await self.generate_response(
            enhanced_prompt,
            system_prompt,
            provider_name,
            **kwargs
        )

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        **kwargs
    ):
        """
        Generate streaming response from LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt
            provider_name: LLM provider to use
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        provider = self.get_provider(provider_name)

        if not hasattr(provider, 'generate_streaming'):
            raise NotImplementedError(f"Provider '{provider_name}' does not support streaming")

        async for chunk in provider.generate_streaming(prompt, system_prompt, **kwargs):
            yield chunk

    def list_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())

    def get_provider_info(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a provider"""
        provider = self.get_provider(provider_name)
        return {
            "name": provider_name or self.default_provider,
            "model": provider.model_name,
            "available": provider.is_available()
        }


# Singleton instance
llm_service = LLMService()
