# Task Execution Prompt

Use this when assigning one bounded task to a remote AI inside a skeleton-based repository.

```text
Work inside `<PROJECT_NAME>` at `<PROJECT_ROOT>`.

Current version: `<CURRENT_VERSION>`
Current phase or lane: `<CURRENT_PHASE_OR_LANE>`
Task ID: `<TASK_ID>`
Task title: `<TASK_TITLE>`
Objective:
`<OBJECTIVE>`

Acceptance criteria:
`<DONE_CRITERIA>`

Required context to read first:
1. `docs/START_HERE.md`
2. `docs/current_status.md`
3. `docs/backlog.md`
4. `docs/roadmap.md`
5. `docs/versioning_policy.md`
6. `docs/development_guidelines.md`
7. `docs/HANDOFF_PROTOCOL.md`
8. `<ACTIVE_LOG_PATH>`

Execution constraints:
- keep changes incremental
- do not replace canonical docs or directory responsibilities
- update backlog status if the task state materially changes
- update `docs/current_status.md` only if verified reality changed
- append the daily log for meaningful checkpoints
- run `scripts/run_repo_hygiene_checks.ps1` if your work touches repo structure, generated artifacts, scripts, CI, or ignore rules

Return:
- changed files
- verification performed
- unresolved risks or assumptions
- recommended next step
```
