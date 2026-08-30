from functools import lru_cache

from app.config import settings
from app.llm.base import LLMProvider


@lru_cache
def get_llm_provider(name: str | None = None) -> LLMProvider:
    """Punto unico de entrada para conseguir un LLM. Cambiar de proveedor en toda
    la plataforma es cambiar LLM_PROVIDER en .env, nada de codigo."""

    provider_name = (name or settings.llm_provider).lower()

    if provider_name == "deepseek":
        from app.llm.deepseek import DeepSeekProvider

        return DeepSeekProvider()
    if provider_name == "openai":
        from app.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if provider_name == "anthropic":
        from app.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider()

    raise ValueError(f"Proveedor LLM desconocido: {provider_name}")
