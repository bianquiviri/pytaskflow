---
id: TF-S06
title: "Improve CI caching and build performance"
agent: sre
labels: ["agent:sre", "type:infrastructure", "priority:low", "difficulty:easy", "status:ready"]
---

### Context

CI workflows install dependencies from scratch on every run (pip + npm), and Docker builds for E2E rebuild images without layer caching. Feedback time is dominated by installs.

### Objective

Cut CI duration with caching: pip wheels/cache for the backend, npm cache for the frontend, Playwright browser cache, and Docker layer caching for the E2E workflow.

### Acceptance criteria

- [ ] Backend workflow caches pip downloads keyed on `pyproject.toml` hash; install step only runs on dependency changes (cache hit verified in logs).
- [ ] Frontend workflow caches npm (`setup-node` cache or explicit action) keyed on `package-lock.json`; Playwright browsers cached keyed on the Playwright version.
- [ ] E2E workflow uses Docker layer caching (e.g., `docker/build-push-action` with `cache-from`/`cache-to` on GHCR or `type=gha`) — or documents why avoided.
- [ ] No cache grows unbounded: explicit keys/limits documented; no secrets introduced.
- [ ] Before/after durations recorded in the issue from actual workflow runs (or blockers stated).

### Technical notes

- Prefer official setup actions with built-in caching; keep workflows readable.

### Testing expectations

- Workflow runs observed; cache hit/miss evidenced; results summarized in the handoff.

### Agent ownership

`sre`
