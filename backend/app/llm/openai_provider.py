from openai import OpenAI

from app.config import settings
from app.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def chat(self, system_prompt: str, messages: list[dict], **kwargs) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
            **kwargs,
        )
        return response.choices[0].message.content or ""
