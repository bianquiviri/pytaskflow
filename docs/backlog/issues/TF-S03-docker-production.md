---
id: TF-S03
title: "Improve Docker production configuration"
agent: sre
labels: ["agent:sre", "type:infrastructure", "priority:high", "difficulty:medium", "status:ready"]
---

### Context

The compose file is development-shaped: `runserver` for the backend, Vite dev server for the frontend, bind-mounted sources. There is no production image path: no gunicorn, no static assets strategy, no healthcheck wiring for the backend image itself.

### Objective

Add a production target set: `docker-compose.prod.yml` (or a documented override) running gunicorn + an nginx static container serving the built frontend with SPA fallback, no bind mounts, and prod env constraints.

### Acceptance criteria

- [ ] Backend prod image installs the `prod` extra (gunicorn) and runs gunicorn with sane defaults (workers documented, timeout, access log to stdout).
- [ ] Frontend prod build: multi-stage Dockerfile producing a static `dist/` served by nginx with SPA fallback and `/api` proxy config documented (or CORS-only, documented trade-off).
- [ ] `docker compose -f docker-compose.yml -f docker-compose.prod.yml config` validates; prod file never includes dev-only mounts or DEBUG defaults.
- [ ] Migrations run as a separate one-shot step (documented command), not in the server entrypoint.
- [ ] README/deployment docs updated with the prod startup sequence.

### Technical notes

- Do not invent a registry or TLS setup; local prod-like parity is the scope. TLS termination stays external (documented).
- Keep image sizes reasonable (slim/alpine bases already in use).

### Testing expectations

- `docker compose ... config` validation output reported; local boot of the prod stack verified and recorded in the handoff (or blockers listed).

### Agent ownership

`sre`
