from app.agents.color_agent import ColorAgent
from app.agents.infrastructure_agent import InfrastructureAgent

_agents = {
    "infrastructure": InfrastructureAgent(),
    "color": ColorAgent(),
}

_prefixes = {
    "infrastructure": "🖥️ Infra —",
    "color": "🎨 Color —",
}

_default_agent_slug = "infrastructure"

# Palabras que, si aparecen en el mensaje, lo mandan al Color Agent en vez de Infra.
_color_keywords = [
    "tvi", "delta e", "Δe", "fogra", "gracol", "cmyk", "icc", "sustrato",
    "prensa", "calibrac", "curva", "miraclon", "color", "flexo", "offset",
    "cgats", "densidad", "ganancia de punto", "g7", "sctv", "perfil",
]


def _classify(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in _color_keywords):
        return "color"
    return _default_agent_slug


def _reply(slug: str, chat_id: int, text: str) -> str:
    reply = _agents[slug].handle_message(chat_id, text)
    return f"{_prefixes[slug]} {reply}"


def route_message(chat_id: int, text: str) -> str:
    # Override manual: "/color tu pregunta" o "/infra tu pregunta" fuerza el agente.
    stripped = text.strip()
    for command, slug in (("/color", "color"), ("/infra", "infrastructure")):
        if stripped.lower().startswith(command):
            return _reply(slug, chat_id, stripped[len(command):].strip())

    # Si el Color Agent esta esperando que elijas un standard para un CGATS
    # que ya subiste, este mensaje es la respuesta a esa pregunta, no algo nuevo.
    if _agents["color"].has_pending_analysis(chat_id):
        return _reply("color", chat_id, stripped)

    slug = _classify(stripped)
    return _reply(slug, chat_id, stripped)


def route_document(chat_id: int, filename: str, content: str) -> str:
    # Por ahora solo el Color Agent procesa archivos adjuntos (CGATS).
    reply = _agents["color"].handle_document(chat_id, filename, content)
    return f"{_prefixes['color']} {reply}"
