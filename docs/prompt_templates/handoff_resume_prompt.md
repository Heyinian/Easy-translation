# Handoff Resume Prompt

Use this when a new AI must resume from a prior human or AI handoff.

```text
Resume work in `<PROJECT_NAME>` at `<PROJECT_ROOT>`.

Current version: `<CURRENT_VERSION>`
Current phase or lane: `<CURRENT_PHASE_OR_LANE>`
Last known checkpoint summary:
`<LAST_HANDOFF_SUMMARY>`

Immediate objective:
`<OBJECTIVE>`

Read first:
1. `docs/START_HERE.md`
2. `docs/current_status.md`
3. `docs/backlog.md`
4. `docs/roadmap.md`
5. `docs/versioning_policy.md`
6. `docs/development_guidelines.md`
7. `docs/HANDOFF_PROTOCOL.md`
8. `<ACTIVE_LOG_PATH>`
9. `<OPTIONAL_ARCHIVE_PATH_IF_RELEVANT>`

Rules:
- treat canonical docs as the source of truth over stale archive material
- continue the existing skeleton rather than replacing it
- reconcile the handoff summary with the actual repo state before making claims
- if the handoff is outdated, correct the current-state docs before proceeding
- run `scripts/run_repo_hygiene_checks.ps1` before closing a meaningful checkpoint when repo-boundary files may have changed

Done criteria:
`<DONE_CRITERIA>`

At closeout, provide:
- verified current state
- work completed in this round
- validation performed
- remaining open items
- next recommended task
```
