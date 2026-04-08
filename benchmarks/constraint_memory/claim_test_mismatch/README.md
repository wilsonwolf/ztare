# Claim-Test-Mismatch Suite

This suite isolates a narrower exploit family than the main benchmark:

- selective rigor
- legitimacy halo / halo validation
- tautological verification
- tests aimed at scaffolding or downstream arithmetic rather than the load-bearing claim

Unlike `derived_subtle/`, these are historical specimens mined from real runs rather than synthetic variants.

Purpose:
- test whether the evaluator can detect that a thesis is proving the wrong thing
- compare `A`, `B`, and `C` on claim-test mismatch without changing the main corpus benchmark

Regenerate the suite with:

```bash
python benchmarks/constraint_memory/mine_claim_test_mismatch.py
```
