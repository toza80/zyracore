from datetime import datetime

from sqlalchemy import create_engine, String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Client(Base):
    """Una entidad cliente de ZyraWorks (ver 'Modelo de cliente' del proyecto)."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Agent(Base):
    """Registro de cada agente logico y su estado, para alimentar el dashboard."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)  # ej: "infrastructure"
    display_name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="idle")  # idle|working|error
    last_action: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActionLog(Base):
    """Historial de todo lo que hicieron/dijeron los agentes (auditoria)."""

    __tablename__ = "action_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_slug: Mapped[str] = mapped_column(String(64))
    client_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channel: Mapped[str] = mapped_column(String(32), default="telegram")
    input_text: Mapped[str] = mapped_column(Text, default="")
    output_text: Mapped[str] = mapped_column(Text, default="")
    requires_approval: Mapped[bool] = mapped_column(default=False)
    approved: Mapped[bool | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # aseguramos que exista el registro del agente piloto para el dashboard
    with SessionLocal() as session:
        existing = session.query(Agent).filter_by(slug="infrastructure").first()
        if not existing:
            session.add(
                Agent(
                    slug="infrastructure",
                    display_name="Infrastructure Agent",
                    status="idle",
                    last_action="Esperando el primer mensaje",
                )
            )
            session.commit()
