from app.agents.infrastructure_agent import InfrastructureAgent

# Fase 0: un unico agente. A medida que se sumen Service Desk, Prepress, Color,
# Commercial y Finance, esta funcion pasa a clasificar el intent del mensaje
# (con el propio LLM o reglas simples) y elegir a que agente rutearlo.
_agents = {
    "infrastructure": InfrastructureAgent(),
}

_default_agent_slug = "infrastructure"


def route_message(chat_id: int, text: str) -> str:
    agent = _agents[_default_agent_slug]
    return agent.handle_message(chat_id, text)
