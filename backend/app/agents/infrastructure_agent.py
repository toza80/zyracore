from app.agents.base_agent import BaseAgent
from app.config import settings
from app.db import Agent, ActionLog, SessionLocal
from app.llm.factory import get_llm_provider

SYSTEM_PROMPT = """Sos el Infrastructure Agent de ZyraWorks, especializado en VMware
(ESXi/vCenter), Ubuntu Server, Windows Server, Veeam, TrueNAS, redes, VPN y pfSense.

Respondes preguntas tecnicas sobre la infraestructura de ZyraWorks y sus clientes,
proponés diagnosticos y, cuando corresponde, proponés una accion concreta a ejecutar
-- pero NUNCA afirmes haber ejecutado una accion real todavia: en esta etapa del
proyecto todavia no tenes acceso de escritura a los sistemas, solo podes consultar
y recomendar. Se breve y concreto, como hablarias con un colega tecnico.
"""


class InfrastructureAgent(BaseAgent):
    slug = "infrastructure"
    display_name = "Infrastructure Agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self) -> None:
        self._llm = get_llm_provider()

    def _mock_get_vm_status(self, vm_name: str) -> dict:
        """Placeholder de una 'tool' real. Fase 2: reemplazar por una llamada
        de verdad a la API de vCenter con pyVmomi usando credenciales de .env."""
        return {"vm": vm_name, "status": "unknown (integracion con vCenter pendiente)"}

    def handle_message(self, chat_id: int, text: str) -> dict:
        self._set_status("working", f"Procesando: {text[:80]}")

        try:
            reply = self._llm.chat(
                system_prompt=self.system_prompt,
                messages=[{"role": "user", "content": text}],
            )
        except Exception as exc:  # noqa: BLE001 - queremos capturar cualquier falla del LLM
            error_msg = f"Error consultando el LLM: {exc}"
            self._set_status("error", error_msg)
            self._log(chat_id, text, f"ERROR: {exc}")
            return {
                "text": (
                    "Tuve un problema consultando al modelo de IA (revisá saldo/API key del "
                    "proveedor configurado). Los detalles quedaron en los logs del backend."
                ),
                "chart": None,
            }

        self._log(chat_id, text, reply)
        self._set_status("idle", f"Ultima respuesta a chat {chat_id}")
        return {"text": reply, "chart": None}

    def _set_status(self, status: str, last_action: str) -> None:
        with SessionLocal() as session:
            agent = session.query(Agent).filter_by(slug=self.slug).first()
            if agent:
                agent.status = status
                agent.last_action = last_action
                session.commit()

    def _log(self, chat_id: int, text: str, reply: str) -> None:
        with SessionLocal() as session:
            session.add(
                ActionLog(
                    agent_slug=self.slug,
                    client_id=None,
                    channel="telegram",
                    input_text=text,
                    output_text=reply,
                    requires_approval=False,
                )
            )
            session.commit()
