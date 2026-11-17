# Agent workflow (OpenCode)

## Session workflow per issue

1. **Start**: read `AGENTS.md`, then the assigned issue in `docs/backlog/issues/` (or GitHub), then only the relevant docs/code.
2. **Plan**: identify touched files and possible conflicts with other in-flight issues.
3. **Implement**: follow your role's rules in `.opencode/agents/<role>.md`.
4. **Verify**: focused tests first, full suite when justified. Never claim passing tests without execution.
5. **Handoff**: post a concise summary — issue id, changes, files, test results, remaining work, decisions worth persisting.
6. **Persist**: write durable decisions to `docs/architecture/decisions/`; trivial tasks get no new memory files.

## Issue labels

- Agent: `agent:backend`, `agent:frontend`, `agent:qa`, `agent:sre`
- Type: `type:feature|bug|refactor|test|documentation|infrastructure`
- Priority: `priority:critical|high|medium|low`
- Difficulty: `difficulty:easy|medium|hard`
- Status: `status:ready` (workable), `status:blocked`, `status:needs-review`

## Publishing the backlog to GitHub

The backlog lives locally in `docs/backlog/issues/*.md` with YAML front-matter (title, labels). Publishing is **never automatic**:

```bash
./infra/scripts/publish_backlog.sh --dry-run   # validate; no GitHub changes
./infra/scripts/publish_backlog.sh             # create labels + issues (idempotent)
```

Requires: `gh` installed, `gh auth login`, repository remote detected, `repo` scope. Issues are assigned to GitHub users **only** when configured in `infra/github/agent-assignees.yml`; otherwise the `agent:*` label marks ownership and the assignee stays empty. The script avoids duplicates on re-run (tracks a stable `issue-id` marker in each issue body).

## Context isolation

- Backend work must not require reading frontend sources; consult `docs/api/conventions.md` instead.
- Frontend work must not require reading backend sources; consult the API docs/OpenAPI schema.
- QA reads the code under test + test contracts only.
- SRE reads infra + operational touchpoints only.
- Communicate via code, API contracts, docs, issues, and handoff notes — never by copying large context between agents.
