---
id: TF-S05
title: "Implement database backup and recovery documentation"
agent: sre
labels: ["agent:sre", "type:documentation", "priority:medium", "difficulty:easy", "status:ready"]
---

### Context

No backup or recovery procedure exists. The compose volume (`postgres_data`) is the only state; a lost volume means total data loss. Local/demo deployments need at least a documented, tested-by-hand procedure.

### Objective

Create a working backup/restore runbook with scripts for the Postgres container: dump, restore, and scheduled local backups, plus documented cloud-extension path.

### Acceptance criteria

- [ ] `infra/scripts/backup_db.sh` and `restore_db.sh` (exec-safe) performing `pg_dump`/`pg_restore` against the compose `db` service using env credentials, with target-file and confirmation prompts for restore.
- [ ] Runbook in `docs/operations/backup-recovery.md`: when to back up, where files go, restore drill steps, RPO/RTO notes for local vs production, and warnings that scripts must never run destructive operations without confirmation.
- [ ] Restore procedure validated once locally end-to-end (dump → wipe volume → restore → data intact), with the executed commands and results recorded in the issue.
- [ ] Optional cron/systemd-timer example included but disabled by default.

### Technical notes

- Use `pg_dump` (custom format `-Fc`) for restore flexibility; never `docker volume rm` inside scripts.
- Keep credentials sourcing from `.env` only; no inline passwords.

### Testing expectations

- Local restore drill documented with actual output; scripts are shellcheck-clean if shellcheck is available (note it either way).

### Agent ownership

`sre`
