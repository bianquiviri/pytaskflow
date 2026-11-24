#!/usr/bin/env bash
# Publish the local TaskFlow backlog (docs/backlog/issues/*.md) to GitHub.
#
# Idempotent: issues carry a hidden marker `taskflow-issue-id:<ID>` in their
# body; issues already containing it are skipped on re-runs.
#
# Usage:
#   ./infra/scripts/publish_backlog.sh --dry-run   # no GitHub changes
#   ./infra/scripts/publish_backlog.sh             # create labels + issues
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ISSUES_DIR="$ROOT/docs/backlog/issues"
ASSIGNEES_FILE="$ROOT/infra/github/agent-assignees.yml"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

log()  { printf '%s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

# --- preflight ----------------------------------------------------------------
command -v gh >/dev/null 2>&1 || fail "gh CLI is not installed. Install from https://cli.github.com and re-run."
gh auth status >/dev/null 2>&1 || fail "gh is not authenticated. Run: gh auth login"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)" || \
  fail "No GitHub repository detected. Add a remote: git remote add origin git@github.com:<org>/<repo>.git and re-run."
log "Repository: $REPO"
[[ "$DRY_RUN" == 1 ]] && log "DRY-RUN: no changes will be made."

# --- labels -------------------------------------------------------------------
create_label() { # name description color
  if gh label list --limit 200 --json name -q '.[].name' | grep -qxF "$1"; then
    log "label exists: $1"
  else
    if [[ "$DRY_RUN" == 1 ]]; then
      log "would create label: $1"
    else
      gh label create "$1" --description "$2" --color "$3" >/dev/null || warn "failed to create label $1"
      log "label created: $1"
    fi
  fi
}

create_label "agent:backend"      "Owned by the backend engineer agent"     "1d76db"
create_label "agent:frontend"     "Owned by the frontend engineer agent"    "0e8a16"
create_label "agent:qa"           "Owned by the QA engineer agent"          "d93f0b"
create_label "agent:sre"          "Owned by the SRE/DevOps engineer agent"  "5319e7"
create_label "type:feature"       "New functionality"                       "84b6eb"
create_label "type:bug"           "Something is broken"                     "ee0701"
create_label "type:refactor"      "Code change without behavior change"     "fbca04"
create_label "type:test"          "Test coverage work"                      "b60205"
create_label "type:documentation" "Documentation work"                      "c2e0c6"
create_label "type:infrastructure" "Infra, CI/CD, environments"             "e99695"
create_label "priority:critical"  "Drop everything"                         "b60205"
create_label "priority:high"      "High priority"                           "d93f0b"
create_label "priority:medium"    "Medium priority"                         "fbca04"
create_label "priority:low"       "Low priority"                            "0e8a16"
create_label "difficulty:easy"    "Good first task"                         "c2e0c6"
create_label "difficulty:medium"  "Moderate scope"                          "84b6eb"
create_label "difficulty:hard"    "Deep work"                               "5319e7"
create_label "status:ready"       "Ready to be worked on"                   "006b75"
create_label "status:blocked"     "Blocked by another issue"                "b60205"
create_label "status:needs-review" "Awaiting review"                        "d4c5f9"

# --- assignee mapping -----------------------------------------------------------
assignee_for() { # agent-name -> github username or ""
  local agent="$1" block
  block="$(awk -v a="$agent" '
    $0 ~ "^  " a ":" {inblock=1; next}
    inblock && /^  [a-z]+:/ {inblock=0}
    inblock && /githubAssignee:/ {print; exit}
  ' "$ASSIGNEES_FILE" 2>/dev/null || true)"
  printf '%s' "$block" | sed -E 's/.*githubAssignee:[[:space:]]*"([^"]*)".*/\1/'
}

# --- issue creation --------------------------------------------------------------
created=0; skipped=0; failed=0
TMP_BODY="$(mktemp)"
trap 'rm -f "$TMP_BODY"' EXIT

for file in "$ISSUES_DIR"/*.md; do
  [[ -f "$file" ]] || continue
  issue_id="$(awk -F': ' '/^id:/ {print $2; exit}' "$file" | tr -d '"')"
  title="$(awk -F': ' '/^title:/ {sub(/^title:[[:space:]]*/, ""); gsub(/^"|"$/, ""); print; exit}' "$file")"
  agent="$(awk -F': ' '/^agent:/ {print $2; exit}' "$file" | tr -d '"')"
  labels=()
  while IFS= read -r l; do
    [[ -n "$l" ]] && labels+=("$l")
  done < <(awk '/^labels:/ {
      line=$0
      sub(/^labels:[[:space:]]*\[/, "", line)
      sub(/\].*$/, "", line)
      gsub(/"/, "", line)
      n=split(line, arr, ", ")
      for (i=1; i<=n; i++) { gsub(/^ +| +$/, "", arr[i]); if (arr[i] != "") print arr[i] }
    }' "$file")
  [[ -n "$issue_id" && -n "$title" ]] || { warn "malformed frontmatter in $file — skipped"; failed=$((failed+1)); continue; }

  marker="taskflow-issue-id:$issue_id"
  if gh issue list --state all --search "in:body \"$marker\"" --json number -q 'length' | grep -q '^1$'; then
    log "skip $issue_id (already published)"
    skipped=$((skipped+1))
    continue
  fi

  # Body = everything after the closing frontmatter fence + hidden id marker.
  awk 'BEGIN{fm=0; n=0} /^---$/{n++; next} n>=2 {print}' "$file" > "$TMP_BODY"
  printf '\n<!-- %s -->\n' "$marker" >> "$TMP_BODY"

  assignee="$(assignee_for "$agent")"
  label_args=()
  for l in "${labels[@]}"; do [[ -n "$l" ]] && label_args+=(--label "$l"); done
  [[ -n "$agent" ]] && label_args+=(--label "agent:$agent")

  if [[ "$DRY_RUN" == 1 ]]; then
    assign_note="unassigned"
    [[ -n "$assignee" ]] && assign_note="assignee: $assignee"
    log "would create: [$issue_id] $title (${#label_args[@]} labels, $assign_note)"
    created=$((created+1))
  else
    if [[ -n "$assignee" ]]; then
      if url="$(gh issue create --title "$title" --body-file "$TMP_BODY" "${label_args[@]}" --assignee "$assignee" 2>&1)"; then
        log "created $issue_id -> $url (assignee: $assignee)"
      else
        warn "creation with assignee failed for $issue_id, retrying unassigned: $url"
        if url="$(gh issue create --title "$title" --body-file "$TMP_BODY" "${label_args[@]}" 2>&1)"; then
          log "created $issue_id -> $url (unassigned)"
        else
          warn "FAILED to create $issue_id: $url"; failed=$((failed+1)); continue
        fi
      fi
    else
      if url="$(gh issue create --title "$title" --body-file "$TMP_BODY" "${label_args[@]}" 2>&1)"; then
        log "created $issue_id -> $url"
      else
        warn "FAILED to create $issue_id: $url"; failed=$((failed+1)); continue
      fi
    fi
    created=$((created+1))
  fi
done

log "──────────────────────────────────────"
log "Summary: $created created/created-in-dry-run, $skipped skipped (already published), $failed failed."
if [[ "$DRY_RUN" == 1 ]]; then log "Dry-run only — nothing was written to GitHub."; fi
[[ "$failed" == 0 ]]
