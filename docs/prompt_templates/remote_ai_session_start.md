# Remote AI Session Start Prompt

Use this as the base prompt when handing an existing skeleton-based repository to a remote AI.

```text
You are continuing work in `<PROJECT_NAME>`.

Repository root: `<PROJECT_ROOT>`
Current documented version: `<CURRENT_VERSION>`
Current phase or lane: `<CURRENT_PHASE_OR_LANE>`
Primary objective for this session: `<OBJECTIVE>`

Before doing any work, read these files in order:
1. `docs/START_HERE.md`
2. `docs/current_status.md`
3. `docs/backlog.md`
4. `docs/roadmap.md`
5. `docs/versioning_policy.md`
6. `docs/development_guidelines.md`
7. `docs/HANDOFF_PROTOCOL.md`
8. `<ACTIVE_LOG_PATH>`

Working rules:
- preserve the canonical document system and top-level skeleton
- do only incremental maintenance unless an approved structural rewrite exists
- register new formal planned work in `docs/backlog.md`
- keep `docs/current_status.md` aligned with verified reality
- append the daily log when the checkpoint is meaningful
- update the documented version only when the checkpoint justifies it
- run `scripts/run_repo_hygiene_checks.ps1` before closing any checkpoint that can affect repo structure, local artifacts, or automation
- do not replace the skeleton with a new documentation scheme

Definition of done for this session:
`<DONE_CRITERIA>`

At the end of the session, report:
- what changed
- what was verified
- what remains open
- the next recommended step
```
