from openai import OpenAI

from app.config import settings
from app.llm.base import LLMProvider


class DeepSeekProvider(LLMProvider):
    """DeepSeek expone una API compatible con OpenAI, asi que reusamos ese SDK
    apuntando a su base_url."""

    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com",
        )
        self._model = settings.deepseek_model

    def chat(self, system_prompt: str, messages: list[dict], **kwargs) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
            **kwargs,
        )
        return response.choices[0].message.content or ""
