Scripts in this directory should stay thin.

Intended use:
- repository hygiene checks
- local developer wrappers
- packaging helpers
- contract validation helpers

Do not place project-specific runtime logic here if it belongs in the application implementation under `src/`.

Current repository hygiene helpers:
- `check_repo_guard.ps1`
  - validates the canonical top-level skeleton and protected document presence
  - checks required document markers in the canonical docs
  - blocks destructive changes to protected paths unless an explicit approval file exists
- `check_gitignore_hygiene.ps1`
  - validates baseline `.gitignore` coverage
  - checks for suspicious local-only untracked files that should likely be ignored
- `run_repo_hygiene_checks.ps1`
  - runs the repo guard and `.gitignore` audit together
- `run_smoke_tests.ps1`
  - runs the local automated smoke baseline with the repo Python environment when available

Current structure-change override path:
- `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.json`
- use the example file under `docs/approvals/` as the template
