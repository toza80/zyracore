from fastapi import APIRouter

from app.db import Agent, SessionLocal

router = APIRouter()


@router.get("/agents/status")
def agents_status():
    """El dashboard hace poll de este endpoint para animar las 'oficinas virtuales'."""
    with SessionLocal() as session:
        agents = session.query(Agent).all()
        return [
            {
                "slug": a.slug,
                "display_name": a.display_name,
                "status": a.status,
                "last_action": a.last_action,
                "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            }
            for a in agents
        ]
