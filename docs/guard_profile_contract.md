# Guard Profile Contract

## Contract Status

Frozen for the initial generic template release.

## Purpose

Define one reusable protection or validation rule set for a concrete project adapted from this skeleton.

## Required Fields

- `id`
- `protected_paths`
- `required_documents`
- `notes`

## Matching Rule

- guard rules should remain explicit and narrow
- a guard profile should protect the canonical document set before it tries to protect broader project-specific files
- unknown structural changes should prefer fail-fast behavior over silent acceptance

## Safety Rule

The skeleton should prefer false negatives over unsafe broad passes.

If a structural change is uncertain, the default behavior is:
1. require an explicit approval record
2. record the reason in backlog and daily log
3. preserve the canonical document responsibilities
