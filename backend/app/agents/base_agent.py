from abc import ABC, abstractmethod


class BaseAgent(ABC):
    slug: str
    display_name: str
    system_prompt: str

    @abstractmethod
    def handle_message(self, chat_id: int, text: str) -> str:
        """Procesa un mensaje entrante y devuelve la respuesta para el usuario."""
        raise NotImplementedError
