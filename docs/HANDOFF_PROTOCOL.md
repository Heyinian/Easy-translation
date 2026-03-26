# Handoff Protocol

## Purpose

Keep developer-to-developer and AI-to-developer handoff quality stable.

## Required Handoff Data

Every meaningful handoff should state:
- current working version
- current phase
- what changed
- what was verified
- what remains open
- the next recommended step

## Before Declaring A Checkpoint Complete

1. ensure the backlog reflects the active task status
2. update `docs/current_status.md` if verified reality changed
3. append the current daily log
4. update `docs/roadmap.md` only if the phase plan or exit criteria changed
5. decide whether the checkpoint changes the documented version
6. create archive material only if the checkpoint is historically meaningful
7. check whether new local-only artifacts were introduced and whether `.gitignore` needs to cover them
8. run `scripts/run_repo_hygiene_checks.ps1` unless the checkpoint is explicitly documentation-only and cannot affect repo structure or local artifacts

For a phase-complete checkpoint:
9. update the next active phase state
10. ensure the archive entry records the phase-close version

## Handoff Output Rule

A handoff is incomplete if another developer cannot answer all of these from the repo:
- what phase the project is in
- what version the project is at
- what the next task is
- whether the repository is only a template or already contains product implementation
