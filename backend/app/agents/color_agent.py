import json

from app.agents.base_agent import BaseAgent
from app.db import Agent, ActionLog, SessionLocal
from app.llm.factory import get_llm_provider
from app.services.cgats_offset import ISO_STANDARDS, analyze_cgats_offset

SYSTEM_PROMPT = """Sos el Color Agent de ZyraWorks, experto en gestion de color para
impresion offset y flexografica: ISO 12647-2, standards Fogra (29, 39, 47, 49, 50, 51)
y GRACoL, perfiles ICC, curvas de compensacion, Delta E2000, TVI/ganancia de punto,
balance de grises, G7/SCTV.

Principios que segui SIEMPRE (son el criterio real de ZyraWorks, no generico de manual):
- Nunca inventes un dato tecnico de un standard: si no tenes el valor exacto, decilo
  explicitamente en vez de aproximar.
- Una calibracion es valida para una combinacion prensa + sustrato + acabado, no para
  la prensa sola. Cian sobre Couche no es lo mismo que cian sobre Cartulina, y mate no
  es lo mismo que brillante (por eso existen Fogra49 y Fogra50 por separado).
- Seleccion de standard segun acabado: sin laminar y estucado -> Fogra39/51; sin
  laminar y no estucado -> Fogra47 (o Fogra29 si el cliente ya lo usa); laminado mate
  -> Fogra49; laminado brillante -> Fogra50.
- El chequeo de ISO 12647 se basa en dispersion de ganancia de punto en luces/sombras
  (spread entre canales), no en matchear un target exacto de memoria.
- Cuando te llega un resultado de analisis ya calculado, NUNCA recalcules ni
  cuestiones los numeros -- fueron calculados por codigo deterministico, no por vos.
  Tu trabajo es interpretar y decir que accion concreta tomar, ordenado por gravedad
  si algo fallo. No repitas todos los numeros crudos, quedate con lo accionable.

Hablas en espanol rioplatense, directo, como un colega tecnico -- sin vueltas.
"""

STANDARD_ALIASES = {
    "fogra39": "fogra39", "fogra 39": "fogra39", "39": "fogra39",
    "fogra47": "fogra47", "fogra 47": "fogra47", "47": "fogra47",
    "fogra49": "fogra49", "fogra 49": "fogra49", "49": "fogra49",
    "fogra50": "fogra50", "fogra 50": "fogra50", "50": "fogra50",
    "fogra51": "fogra51", "fogra 51": "fogra51", "51": "fogra51",
    "fogra29": "fogra29", "fogra 29": "fogra29", "29": "fogra29",
    "gracol": "gracol", "gracol 2013": "gracol",
}


def _normalize_standard(text: str) -> str | None:
    key = text.strip().lower()
    return STANDARD_ALIASES.get(key)


class ColorAgent(BaseAgent):
    slug = "color"
    display_name = "Color Agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self) -> None:
        self._llm = get_llm_provider()
        # chat_id -> contenido CGATS crudo, esperando que el usuario elija standard.
        # Nota: esto vive en memoria del proceso telegram-worker. Si el worker se
        # reinicia con un analisis pendiente, se pierde y hay que resubir el archivo.
        # Fase futura: mover este estado a Redis (ya esta en el stack) para que
        # sobreviva a reinicios.
        self._pending_cgats: dict[int, str] = {}

    def has_pending_analysis(self, chat_id: int) -> bool:
        return chat_id in self._pending_cgats

    def handle_message(self, chat_id: int, text: str) -> str:
        if chat_id in self._pending_cgats:
            return self._resolve_pending_analysis(chat_id, text)

        self._set_status("working", f"Procesando: {text[:80]}")
        try:
            reply = self._llm.chat(
                system_prompt=self.system_prompt,
                messages=[{"role": "user", "content": text}],
            )
        except Exception as exc:
            self._set_status("error", f"Error consultando el LLM: {exc}")
            self._log(chat_id, text, f"ERROR: {exc}")
            return (
                "Tuve un problema consultando al modelo de IA (revisa saldo/API key). "
                "Detalles en los logs del backend."
            )

        self._log(chat_id, text, reply)
        self._set_status("idle", f"Ultima respuesta a chat {chat_id}")
        return reply

    def handle_document(self, chat_id: int, filename: str, content: str) -> str:
        if "BEGIN_DATA_FORMAT" not in content:
            return (
                f"El archivo '{filename}' no parece un CGATS valido (no encontre "
                "BEGIN_DATA_FORMAT). Verifica que sea la exportacion correcta del "
                "instrumento de medicion."
            )

        self._pending_cgats[chat_id] = content
        opciones = ", ".join(sorted(ISO_STANDARDS.keys()))
        return (
            f"Recibi '{filename}'. ¿Contra que standard lo comparo?\n"
            f"Opciones: {opciones}"
        )

    def _resolve_pending_analysis(self, chat_id: int, text: str) -> str:
        standard_key = _normalize_standard(text)
        if not standard_key:
            opciones = ", ".join(sorted(ISO_STANDARDS.keys()))
            return f"No reconozco ese standard. Opciones validas: {opciones}"

        content = self._pending_cgats.pop(chat_id)
        self._set_status("working", f"Analizando CGATS contra {standard_key}")

        analysis = analyze_cgats_offset(content, standard_key)
        if analysis.get("error"):
            self._set_status("error", analysis["error"])
            return f"No pude analizar el archivo: {analysis['error']}"

        try:
            reply = self._explain_analysis(analysis)
        except Exception as exc:
            self._set_status("error", f"Error consultando el LLM: {exc}")
            self._log(chat_id, f"[CGATS vs {standard_key}]", f"ERROR: {exc}")
            return (
                "El calculo se hizo bien, pero tuve un problema consultando al "
                "modelo de IA para explicarlo. Revisa saldo/API key."
            )

        self._log(chat_id, f"[CGATS vs {standard_key}]", reply)
        self._set_status("idle", f"Analisis CGATS vs {standard_key} completado")
        return reply

    def _explain_analysis(self, analysis: dict) -> str:
        """Le pasamos al LLM SOLO el resultado ya calculado (nunca el CGATS crudo,
        nunca le pedimos que calcule) -- mismo patron que ZyraBrain en ZyraDot Offset."""
        resumen_datos = {
            "standard": analysis.get("standard_name"),
            "score": analysis.get("condition_score"),
            "iso_compliance": analysis.get("iso_compliance"),
            "de_primaries": analysis.get("de_primaries"),
            "de_black": analysis.get("de_black"),
            "mid_tone_spread": analysis.get("mid_tone_spread"),
            "gray_balance": analysis.get("gray_balance"),
            "tvi_compliance": analysis.get("tvi_compliance"),
        }
        prompt = (
            "Este es el resultado YA CALCULADO de un analisis CGATS de prensa offset "
            "(no lo recalcules, solo interpretalo):\n\n"
            f"{json.dumps(resumen_datos, ensure_ascii=False, indent=2)}\n\n"
            "Dame un resumen breve y las acciones concretas a tomar, ordenadas por "
            "gravedad si algo fallo."
        )
        return self._llm.chat(
            system_prompt=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )

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
