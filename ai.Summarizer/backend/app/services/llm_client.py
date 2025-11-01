"""LLM client supporting both local Ollama and cloud APIs - Async Version"""
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from ..config import settings


class AsyncLLMClient:
    """Unified async LLM client for local and cloud models"""

    def __init__(self):
        self.provider = settings.llm_provider.lower()

        if self.provider == "local":
            # Ollama client
            self.client = AsyncOpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama"  # Ollama doesn't need real API key
            )
            self.model = settings.ollama_model
        elif self.provider == "cloud":
            # Cloud API client (Qwen/DashScope)
            self.client = AsyncOpenAI(
                base_url=settings.qwen_api_base_url,
                api_key=settings.qwen_api_key
            )
            self.model = settings.qwen_model
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate text using the configured LLM (async)

        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with response and metadata
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        try:
            # Prepare API call parameters
            call_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                call_params["max_tokens"] = max_tokens

            # For Qwen cloud API, disable thinking mode for non-streaming calls
            if self.provider == "cloud":
                call_params["extra_body"] = {"enable_thinking": False}

            response = await self.client.chat.completions.create(**call_params)

            return {
                "text": response.choices[0].message.content,
                "model": self.model,
                "provider": self.provider,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")


# Global LLM client instance
_llm_client: Optional[AsyncLLMClient] = None


def get_llm_client() -> AsyncLLMClient:
    """Get or create global async LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = AsyncLLMClient()
    return _llm_client
