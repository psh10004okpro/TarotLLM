"""
Google Gemini LLM Provider
Google Gemini API integration
"""

from typing import Optional, AsyncIterator
from app.core.llm_providers.base import BaseLLMProvider
from app.config import settings


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider"""

    def __init__(self):
        """Initialize Gemini provider"""
        super().__init__(
            api_key=settings.GOOGLE_API_KEY,
            model_name=settings.GEMINI_MODEL
        )
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Gemini client"""
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
            except ImportError:
                print("Warning: google-generativeai package not installed")
                self.client = None
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if Gemini provider is available"""
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
        Generate response using Gemini

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
            raise RuntimeError("Gemini provider is not available. Check API key.")

        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            # Generate content
            response = await self.client.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )

            return response.text

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response using Gemini

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
            raise RuntimeError("Gemini provider is not available. Check API key.")

        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            # Generate streaming content
            response = await self.client.generate_content_async(
                full_prompt,
                generation_config=generation_config,
                stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise RuntimeError(f"Gemini streaming error: {str(e)}")
