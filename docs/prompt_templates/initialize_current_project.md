# Initialize Current Project Prompt

Use this when a developer starts a session with the exact phrase `初始化当前项目`.

This prompt is intended for the first guided interaction in a fresh or unknown repository state.

Bootstrap is a one-time repository conversion step. After bootstrap finalization, the same phrase must be treated as project-intake and requirement confirmation rather than bootstrap replay.

```text
初始化当前项目

Before doing anything destructive, read these files when they exist:
1. `README.md`
2. `docs/START_HERE.md`
3. `docs/current_status.md`
4. `docs/backlog.md`
5. `docs/roadmap.md`
6. `docs/versioning_policy.md`
7. `docs/development_guidelines.md`
8. `docs/HANDOFF_PROTOCOL.md`
9. the latest dated file under `docs/daily/` recursively

Then follow this decision flow:

1. Detect repository mode first.
- If the repository still has the bootstrap assets from `AIProjectSkeleton`, treat this as one-time bootstrap intake.
- If `config/project/current_project.json` exists and shows `bootstrap_finalized: true`, do not rerun bootstrap. Treat this as project-intake instead.
- If the repository does not clearly match the skeleton, stop and report what you found before proposing any initialization path.

2. If template mode is detected:
- collect only the missing required bootstrap fields
- summarize the planned starter state before writing anything
- run dry-run first
- ask for confirmation before `-Apply`
- prefer default project-owned finalization
- keep bootstrap assets only if the user explicitly requests a template-linked repository

3. If project-owned mode is detected:
- do not rerun bootstrap
- ask for the current development requirement
- summarize the requirement as scope, non-goals, constraints, acceptance criteria, and risks
- wait for confirmation before backfilling canonical docs

4. After the requirement is confirmed:
- update `docs/backlog.md` first
- update `docs/current_status.md` only if verified reality changed
- append the active daily log for a meaningful checkpoint
- update `docs/roadmap.md` or the documented version only when justified
- keep the canonical skeleton intact

Rules:
- bootstrap is one-time
- maximize non-interference with normal project development after bootstrap finalization
- do not replace the canonical document system as a shortcut
- keep changes incremental
- run `scripts/run_repo_hygiene_checks.ps1` before closing a repo-boundary checkpoint

At the end of the intake round, return:
- detected repository mode
- fields collected or assumed
- confirmed project requirement
- canonical docs that must be backfilled
- the next recommended implementation checkpoint
```
