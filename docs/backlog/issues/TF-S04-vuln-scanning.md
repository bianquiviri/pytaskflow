---
id: TF-S04
title: "Add dependency vulnerability scanning"
agent: sre
labels: ["agent:sre", "type:infrastructure", "priority:medium", "difficulty:easy", "status:ready"]
---

### Context

Dependencies (Python via `pyproject.toml`, npm via `package-lock.json`) are never scanned. Known-vulnerable versions would go unnoticed in CI.

### Objective

Add automated vulnerability scanning to CI for both ecosystems with clearly defined failure policy.

### Acceptance criteria

- [ ] CI job scans Python dependencies (pip-audit or equivalent, pinned version) against the locked/declared set.
- [ ] CI job scans npm dependencies (`npm audit --audit-level=high` or equivalent with pinned tooling).
- [ ] Scan failures fail the workflow; policy for false positives documented (how to pin an ignore with an expiry/justification).
- [ ] Scans run on PRs and on a weekly schedule (workflow `schedule` trigger) with results visible in the Actions UI.
- [ ] No secrets required; if a scanner needs a token, the job documents it as optional and degrades gracefully.

### Technical notes

- Prefer first-party tooling (pip-audit, npm audit) over adding heavyweight agents; document versions in the workflow.
- Do not commit generated vulnerability reports.

### Testing expectations

- Workflow validated locally (`act` or YAML lint); first CI run observed and reported (or blocked, with reason).

### Agent ownership

`sre`
