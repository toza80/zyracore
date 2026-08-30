-- Extension necesaria para RAG / knowledge layer
CREATE EXTENSION IF NOT EXISTS vector;

-- Nota: las tablas "de negocio" (clients, agents, action_log, tickets, etc.)
-- las crea SQLAlchemy on startup (ver backend/app/db.py) para poder iterar
-- rapido en esta etapa temprana. Cuando el esquema se estabilice, migrar
-- a Alembic para tener migraciones versionadas de verdad.
