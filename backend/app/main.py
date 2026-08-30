from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_agents, routes_health
from app.db import init_db

app = FastAPI(title="ZyraWorks IA Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fase 0: todo abierto en la LAN. Restringir en fase de hardening.
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, prefix="/api")
app.include_router(routes_agents.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    init_db()
