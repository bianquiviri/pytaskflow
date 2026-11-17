---
id: TF-Q01
title: "Expand authentication security test coverage"
agent: qa
labels: ["agent:qa", "type:test", "priority:high", "difficulty:medium", "status:ready"]
---

### Context

Auth tests cover happy paths, weak passwords, duplicate emails, and refresh blacklisting. Missing: malformed tokens, token type confusion (access used as refresh), expired-token behavior, password-hash exposure, enumeration via error messages, and throttling behavior on repeated failures.

### Objective

Add a security-focused test module proving the auth endpoints resist common misuse patterns, without modifying production code (defects found are reported, not patched, unless assigned).

### Acceptance criteria

- [ ] Tests: garbage/malformed Authorization header → 401 (not 500); access token used at `/auth/refresh/` → 401; refresh used as access token → 401.
- [ ] No endpoint response ever contains a password hash or hash field name (assert on full JSON bodies for register/login/me).
- [ ] Login failure messages do not reveal whether the email exists (single generic message).
- [ ] Registration with extremely long inputs (email 320+ chars, names 1000+ chars) → clean 4xx validation, not 500.
- [ ] User can log out another user's refresh token → it is blacklisted or rejected; document actual behavior.

### Technical notes

- Use `override_settings` to control throttling only if testing that aspect; keep other tests independent of cache state.
- Factories only; no dependency on demo seed data.

### Testing expectations

- New pytest module `tests/api/test_auth_security.py`; all tests green locally with exact command output reported.

### Agent ownership

`qa`
