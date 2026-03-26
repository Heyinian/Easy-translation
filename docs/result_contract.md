# Result Contract

## Contract Status

Frozen for the initial generic template release.

## Purpose

Describe the stable machine-readable result boundary for a concrete project adapted from this skeleton.

## Minimum Required Fields

If an adapted project emits a machine-readable run result, it should include:
- tool or project version
- run id or timestamp
- status
- started_at
- finished_at
- artifact directory or report path
- summary of the primary action taken

## Initial Status Values

Recommended generic status values:
- `passed`
- `failed`
- `blocked`
- `tool_error`

## Consumer Rule

Project wrappers and AI contributors should be able to derive high-level pass/fail understanding from the result file without parsing low-level logs.
