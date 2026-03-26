# Artifact Contract

## Contract Status

Frozen for the initial generic template release.

## Purpose

Describe how a concrete project should organize generated local artifacts or evidence so they stay archivable without polluting the repository.

## Minimum Expectations

An adapted project should define:
- one local artifact root
- what types of generated outputs belong there
- whether any machine-readable result file is generated
- whether historical runs are retained or overwritten

## Default Template Rule

- generated local artifacts should live under `artifacts/` unless the adapted project documents a different canonical location
- local artifacts should be ignored by git unless explicitly intended as checked-in fixtures
