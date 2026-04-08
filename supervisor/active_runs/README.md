# Supervisor Active Runs

This directory holds ephemeral in-repo supervisor run state.

Examples:
- `status.json`
- `events.jsonl`
- `staging/`
- launch stdout/stderr/usage sidecars

These files stay inside the repo boundary so agent sandboxes can read and write them reliably.
They are ignored by git and are not part of the permanent tracked record.
