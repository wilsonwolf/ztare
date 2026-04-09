# Hypothesis Bundles

This directory is human-owned exploration space.

Use one subdirectory per candidate hypothesis:

```text
hypotheses/
  safe_asset_convergence/
    thesis.md
    notes.md
    test_model.py      # optional
  response_latency/
    thesis.md
    notes.md
    test_model.py      # optional
```

Rules:

- `thesis.md` in the project root is the active object the loop evaluates.
- `test_model.py` in the project root must travel with the active thesis, or be deleted so the runner fails closed and regenerates a placeholder.
- `workspace/` remains machine-owned. Do not store exploration notes there.

Promotion workflow:

1. Edit a candidate bundle under `hypotheses/`.
2. Promote it with:

```bash
python projects/eu_union_stability/promote_hypothesis.py safe_asset_convergence
```

3. Run the loop fresh.

If a bundle has no `test_model.py`, promotion deletes the project-root `test_model.py` so the next run cannot accidentally evaluate the new thesis with a stale old suite.

Optional:

- Pass `--clear-status` to archive stale workspace status files for operator clarity.

This is an operator workflow, not a kernel feature.
