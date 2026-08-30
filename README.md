# ZyraWorks IA Engine — Fase 0 (esqueleto piloto)

Esqueleto minimo pero funcional de la plataforma: Orchestrator + Infrastructure Agent,
comandado por Telegram, con dashboard animado de "oficinas virtuales". Pensado para
correr en tu VM Ubuntu sobre VMware.

## Que incluye esta fase

- **Postgres + pgvector, Redis, MinIO, n8n**: la infraestructura base común a todos los agentes.
- **Backend (FastAPI)** con una **capa de abstraccion de LLM** (`app/llm/`): cambiar entre
  DeepSeek / OpenAI / Anthropic es una variable de entorno (`LLM_PROVIDER`), no un rewrite.
- **Orchestrator** (`app/agents/orchestrator.py`): hoy rutea todo al Infrastructure Agent;
  es el punto donde despues se suman Service Desk, Prepress, Color, Commercial y Finance.
- **Infrastructure Agent**: responde sobre VMware/Ubuntu/redes usando el LLM configurado.
  Todavia NO ejecuta acciones reales (solo consulta/recomienda) — eso es a proposito,
  para respetar "no autonomia total" desde el arranque.
- **Bot de Telegram** (polling, sin necesidad de dominio/HTTPS) con whitelist de
  usuarios autorizados.
- **Dashboard animado** (`frontend/dashboard/index.html`): arranca con datos simulados
  y pasa solo a datos reales en cuanto el backend responde — no hace falta esperar a
  tener agentes reales para "verlo funcionando".

## Como levantarlo en tu VM Ubuntu

1. Cloná/copiá esta carpeta a la VM (ej. `/opt/zyraworks-ia-engine`).
2. `cp .env.example .env` y completá como minimo:
   - `DEEPSEEK_API_KEY` (o las credenciales del proveedor LLM que quieras usar)
   - `TELEGRAM_BOT_TOKEN` (crealo hablando con **@BotFather** en Telegram)
   - `TELEGRAM_ALLOWED_USER_IDS` con tu Telegram user id (preguntale a **@userinfobot**)
3. `docker compose up -d --build`
4. Backend: `http://<ip-vm>:8000/api/health`
5. Dashboard: `http://<ip-vm>:8080`
6. Escribile a tu bot de Telegram — la respuesta la genera el Infrastructure Agent,
   y vas a ver el avatar cambiar a "trabajando" en el dashboard en tiempo real.

## Seguridad (fase 0)

- El bot ignora a cualquier usuario de Telegram que no este en `TELEGRAM_ALLOWED_USER_IDS`.
- El agente todavia no tiene permisos de escritura sobre ningun sistema real
  (VMware, etc.) — solo responde con el LLM. Las "tools" reales se agregan
  recien cuando definamos el flujo de aprobacion (ver ROADMAP).
- Todo queda registrado en la tabla `action_log` (auditoria basica desde el dia 1).

## Proximos pasos

Ver `docs/ROADMAP.md` para las fases siguientes (mas agentes, RAG con pgvector,
integracion real con vCenter, flujo de aprobacion para acciones, dashboard con
websockets en vez de polling, etc).
