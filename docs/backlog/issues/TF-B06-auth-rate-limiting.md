---
id: TF-B06
title: "Harden rate limiting for authentication endpoints"
agent: backend
labels: ["agent:backend", "type:feature", "priority:high", "difficulty:easy", "status:ready"]
---

### Context

Auth endpoints have a `ScopedRateThrottle` (`auth: 10/min`) configured in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`, but only `register`, `login`, `refresh`, and `logout` declare `throttle_scope`. The rate is a single global value, cache-based (`LocMemCache` in dev), and there is no test coverage proving throttling works — a brute-force attempt is only superficially limited.

### Objective

Make auth throttling explicit, tested, and configurable: per-endpoint rates (login stricter), env-configurable values, cache backend selection, and tests that prove the limits engage.

### Acceptance criteria

- [ ] Login (and register) use a dedicated throttle scope with rates sourced from environment variables (e.g., `AUTH_THROTTLE_RATE`, default `10/min` for dev).
- [ ] Exceeding the limit returns 429 with `Retry-After`-style information (DRF default body is acceptable) — verified by tests.
- [ ] Tests override throttle settings to a low value and exercise 429 without relying on wall-clock sleeps (use DRF throttling test helpers or direct `THROTTLE_RATES` override + separate cache).
- [ ] Throttling is disabled or lifted for the test settings module in a way that doesn't require per-test overrides (document the mechanism).
- [ ] `docs/operations/deployment.md` notes the production cache requirement for throttling (shared cache, not LocMem).

### Technical notes

- Keep `config.settings.test` overriding `DEFAULT_THROTTLE_CLASSES` to `()` as today; enable throttling only in the dedicated throttle tests via `override_settings`.
- Use a deterministic test strategy: `override_settings(REST_FRAMEWORK={... rates...})` with a cache keyed per test run (DRF caches by ident, so tests must use `api_client` from separate hosts or clear cache between calls).

### Testing expectations

- pytest coverage: 429 after Nth request for login; register; other endpoints unaffected; rate from env respected.

### Agent ownership

`backend`
