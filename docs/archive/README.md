# Archive Policy

## Purpose

Keep historical material without letting it replace the canonical current-state documents.

## Canonical Rule

If a historical document conflicts with these files, the canonical files win:
- `docs/current_status.md`
- `docs/backlog.md`
- `docs/roadmap.md`
- `docs/versioning_policy.md`

## When To Archive

Create archive material when:
- a phase is completed
- a formal version checkpoint needs historical traceability
- a planning structure is superseded but should remain inspectable
- a handoff package needs to preserve older context without polluting current-state docs

## Directory Rule

- keep archive material under `docs/archive/legacy/YYYY/MM/`
- keep the active truth outside `docs/archive/`

## Version Interpretation Rule

- within-phase checkpoint archives may map to patch-version increments
- completed phase archives should align with the next minor-version release node
- `v1.0.0` is reserved for the first completed release archive boundary
