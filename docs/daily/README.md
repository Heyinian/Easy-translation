# Daily Development Logs

## Purpose

- keep an append-only daily timeline based on the system date
- prevent `current_status.md` from becoming a long multi-round diary
- give remote developers and AI a clear chronological record without replacing the main status documents

## Rules

- create one file per system date using `docs/daily/YYYY/MM/YYYY-MM-DD.md`
- append all same-day progress to that day's file instead of creating multiple date variants
- do not use the daily log as the primary source of current repository truth
- keep the main document responsibilities unchanged

## Required Sections

Each daily file should keep these sections:
- `Summary`
- `Completed`
- `Verification`
- `Risks / Open Issues`
- `Next Recommended Step`
