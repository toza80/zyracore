from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interfaz comun para cualquier proveedor de LLM.

    Cualquier proveedor nuevo (local, otro API, etc.) solo tiene que implementar
    este metodo para poder usarse en toda la plataforma sin tocar los agentes.
    """

    @abstractmethod
    def chat(self, system_prompt: str, messages: list[dict], **kwargs) -> str:
        """messages: lista de {"role": "user"|"assistant", "content": str}."""
        raise NotImplementedError
