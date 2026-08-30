import anthropic

from app.config import settings
from app.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    def chat(self, system_prompt: str, messages: list[dict], **kwargs) -> str:
        response = self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=messages,
            max_tokens=kwargs.pop("max_tokens", 1024),
            **kwargs,
        )
        return "".join(block.text for block in response.content if block.type == "text")
