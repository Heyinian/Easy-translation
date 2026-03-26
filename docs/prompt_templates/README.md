# Prompt Templates

## Purpose

Provide reusable prompt starters for remote AI contributors working inside a repository derived from this skeleton.

## Available Templates

- `initialize_current_project.md`
  - use when a developer starts with the exact phrase `初始化当前项目` and wants the AI to detect repository mode before deciding whether bootstrap or requirement intake is appropriate
- `remote_ai_session_start.md`
  - use when an AI is joining an existing project and must align with the canonical docs before doing work
- `task_execution_prompt.md`
  - use when assigning a bounded implementation or documentation task
- `handoff_resume_prompt.md`
  - use when resuming work from a prior developer or AI checkpoint

## Usage Rule

1. copy the template that matches the task shape
2. replace the placeholder fields before sending it
3. keep the canonical document references intact
4. do not remove the incremental-maintenance and repo-hygiene requirements unless the target project has intentionally replaced them

## Required Placeholders To Replace

Not every template uses all placeholders. `initialize_current_project.md` can be used as-is, starting from the exact phrase `初始化当前项目`.

Most other templates require some or all of these placeholders:

- `<PROJECT_NAME>`
- `<PROJECT_ROOT>`
- `<CURRENT_VERSION>`
- `<CURRENT_PHASE_OR_LANE>`
- `<OBJECTIVE>`
- `<DONE_CRITERIA>`
- `<ACTIVE_LOG_PATH>`

## Repository Entry Rule

Every prompt in this folder assumes the AI must start by reading:

1. `docs/START_HERE.md`
2. `docs/current_status.md`
3. `docs/backlog.md`
4. `docs/roadmap.md`
5. `docs/versioning_policy.md`
6. `docs/development_guidelines.md`
7. `docs/HANDOFF_PROTOCOL.md`
