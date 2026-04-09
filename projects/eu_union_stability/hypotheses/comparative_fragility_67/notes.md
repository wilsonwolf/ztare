# Notes

This bundle preserves the active `67`-score comparative-fragility baseline exactly as it existed in the project root when promoted into `hypotheses/`.

Purpose:

- keep the best surviving exploitation branch intact
- allow safe branching into narrower or more novel alternatives without losing the current baseline
- provide a clean re-promotion target if later exploratory candidates underperform

Promotion rule:

- if you want to restore the current baseline, promote this bundle back into the project root
- because this bundle includes both `thesis.md` and `test_model.py`, it avoids stale-suite mismatch
