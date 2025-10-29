"""
Claude LLM Provider
Anthropic Claude API integration
"""

import asyncio
from typing import Optional, AsyncIterator
from app.core.llm_providers.base import BaseLLMProvider
from app.config import settings


class ClaudeProvider(BaseLLMProvider):
    """Claude LLM provider using Anthropic API"""

    def __init__(self):
        """Initialize Claude provider"""
        super().__init__(
            api_key=settings.ANTHROPIC_API_KEY,
            model_name=settings.CLAUDE_MODEL
        )
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Anthropic client"""
        if self.api_key:
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                print("Warning: anthropic package not installed")
                self.client = None
            except Exception as e:
                print(f"Warning: Failed to initialize Claude client: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if Claude provider is available"""
        return self.client is not None and self.api_key is not None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate response using Claude

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Generated response text
        """
        if not self.is_available():
            raise RuntimeError("Claude provider is not available. Check API key.")

        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]

            # Create request with timeout (30 seconds)
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt if system_prompt else "",
                    messages=messages,
                    **kwargs
                ),
                timeout=30.0
            )

            # Extract text from response
            return response.content[0].text

        except asyncio.TimeoutError:
            raise RuntimeError("Claude API request timed out after 30 seconds")
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response using Claude

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        if not self.is_available():
            raise RuntimeError("Claude provider is not available. Check API key.")

        try:
            messages = [{"role": "user", "content": prompt}]

            async with self.client.messages.stream(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise RuntimeError(f"Claude streaming error: {str(e)}")
