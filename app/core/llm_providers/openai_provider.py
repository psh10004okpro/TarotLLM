"""
OpenAI LLM Provider
OpenAI GPT API integration
"""

import asyncio
import logging
from typing import Optional, AsyncIterator
from app.core.llm_providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider using OpenAI API"""

    def __init__(self):
        """Initialize OpenAI provider"""
        super().__init__(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL
        )
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client"""
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info(f"OpenAI provider initialized with model: {self.model_name}")
            except ImportError:
                logger.warning("openai package not installed")
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
                self.client = None

    def is_available(self) -> bool:
        """Check if OpenAI provider is available"""
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
        Generate response using OpenAI GPT

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
            raise RuntimeError("OpenAI provider is not available. Check API key.")

        try:
            # Prepare messages
            messages = self._prepare_messages(prompt, system_prompt)

            # Create chat completion with timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                ),
                timeout=settings.LLM_REQUEST_TIMEOUT
            )

            # Extract text from response
            return response.choices[0].message.content

        except asyncio.TimeoutError:
            raise RuntimeError(f"OpenAI API request timed out after {settings.LLM_REQUEST_TIMEOUT} seconds")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response using OpenAI

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
            raise RuntimeError("OpenAI provider is not available. Check API key.")

        try:
            messages = self._prepare_messages(prompt, system_prompt)

            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"OpenAI streaming error: {str(e)}")
