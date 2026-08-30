# ZyraWorks IA Engine — Roadmap

## Fase 0 — Esqueleto piloto (este entregable)

Objetivo: tener algo tangible funcionando de punta a punta esta semana, no un
diseño perfecto.

- Infraestructura base en Docker Compose (Postgres+pgvector, Redis, MinIO, n8n).
- Orchestrator + **un solo agente** (Infrastructure Agent) con capa LLM intercambiable.
- Comunicación por Telegram (polling, whitelist de usuarios).
- Dashboard de oficinas virtuales, arrancando con datos simulados y pasando a
  datos reales automaticamente.
- Sin acciones reales sobre sistemas todavia: solo consulta/diagnostico.
- Auditoria basica (`action_log`) desde el primer mensaje.

**Criterio de "listo"**: le escribís al bot de Telegram, el Infrastructure Agent
responde con criterio tecnico, y lo ves "trabajar" en el dashboard.

## Fase 1 — Conocimiento real del cliente

- Completar el modelo de datos de `Client` (infraestructura, contratos, tickets,
  proyectos) segun el modelo de cliente completo del proyecto.
- Cargar a mano (o importar) los datos de 1-2 clientes reales para empezar a
  probar con contexto real, no solo preguntas genéricas.
- Cada respuesta del Infrastructure Agent debería poder traer contexto de ESE
  cliente puntual cuando se lo mencionás.

## Fase 2 — Conocimiento documental (RAG)

- Pipeline de ingesta a MinIO + pgvector: manuales, procedimientos, tickets
  historicos, informes.
- El Infrastructure Agent consulta ese contexto antes de responder (RAG real,
  no solo el LLM "pelado").

## Fase 3 — Herramientas y acciones reales (con aprobación humana)

- Integración real con VMware (pyVmomi) para *consultar* estado de VMs, hosts,
  datastores — reemplaza el stub `_mock_get_vm_status`.
- Flujo de aprobación: toda acción que modifique algo se propone en el chat de
  Telegram y se ejecuta solo si respondés "confirmar" (o similar). Esto es
  la base de "no autonomía total" que ya definiste para el proyecto.
- Recién ahí se evalúa dar permisos de *escritura* (reiniciar un servicio,
  etc.), siempre atrás de esa aprobación.

## Fase 4 — Segundo y tercer agente

- Con el patrón ya probado, sumar **Service Desk Agent** (clasifica
  tickets/emails/incidentes) y despues **Prepress** o **Color** según lo que
  más presión tenga en el día a día.
- El Orchestrator empieza a clasificar el mensaje entrante y rutearlo al
  agente correcto (hoy rutea todo a Infrastructure porque es el único).

## Fase 5 — Dashboard "de verdad"

- Reemplazar el polling HTTP por WebSockets para que la animación sea instantánea.
- Mostrar en la oficina virtual: agentes en su escritorio, moviéndose a una
  "sala de reuniones" cuando el Orchestrator los coordina entre sí, con
  globitos de diálogo mostrando qué están haciendo en tiempo real.
- Un panel lateral con el historial de `action_log` navegable.

## Fase 6 — Agentes restantes + hardening

- Color Agent, Commercial Agent, Finance & Administration Agent.
- Reverse proxy con HTTPS (si se expone fuera de la LAN), rotación de logs,
  backups de Postgres/MinIO, y revisión de permisos de cada agente.

---

**Regla general para todas las fases**: no crear un agente nuevo hasta que el
anterior esté realmente devolviendo valor. Es más fácil llevar 2 agentes muy
buenos que 7 mediocres.
