# Approvals

## Purpose

This directory holds explicit approval records for exceptional repository-structure changes.

## Default Rule

Do not place an approval file here during normal incremental development.

The absence of an approval file is the normal state.

## Structure Change Override

If a structural rewrite is explicitly approved, create:

- `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.json`

Use `docs/approvals/ALLOW_DOC_STRUCTURE_CHANGE.example.json` as the template.

## Lifecycle Rule

- add the approval file in the same checkpoint as the approved structural change
- record the reason in backlog and daily log
- remove the approval file after the exceptional change has landed and no longer needs to bypass the repo guard
