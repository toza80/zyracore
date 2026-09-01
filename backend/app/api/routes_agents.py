from fastapi import APIRouter

from app.db import Agent, ActionLog, SessionLocal

router = APIRouter()

RECENT_ACTIONS_LIMIT = 5
_PREVIEW_MAX_CHARS = 220


def _truncate(text: str, max_chars: int = _PREVIEW_MAX_CHARS) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


@router.get("/agents/status")
def agents_status():
    """El dashboard hace poll de este endpoint para animar las 'oficinas virtuales'
    y ahora tambien para mostrar las ultimas tareas de cada agente. Nota de escala:
    esto hace una query de historial por agente (N+1) -- totalmente razonable con
    2-3 agentes y polling cada pocos segundos, pero si el organigrama crece mucho
    convendria una sola query con window function en vez de este loop."""
    with SessionLocal() as session:
        agents = session.query(Agent).all()
        result = []
        for a in agents:
            recent = (
                session.query(ActionLog)
                .filter_by(agent_slug=a.slug)
                .order_by(ActionLog.created_at.desc())
                .limit(RECENT_ACTIONS_LIMIT)
                .all()
            )
            result.append(
                {
                    "slug": a.slug,
                    "display_name": a.display_name,
                    "status": a.status,
                    "last_action": a.last_action,
                    "updated_at": a.updated_at.isoformat() if a.updated_at else None,
                    "recent_actions": [
                        {
                            "channel": log.channel,
                            "input": _truncate(log.input_text),
                            "output": _truncate(log.output_text),
                            "created_at": log.created_at.isoformat() if log.created_at else None,
                        }
                        for log in recent
                    ],
                }
            )
        return result
