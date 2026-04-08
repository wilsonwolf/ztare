# OOD Suite

This directory holds out-of-distribution stress tests that are **not** part of the main historical benchmark.

Purpose:
- keep the `N=9` main suite stable
- test whether primitives transfer to a new exploit family or domain without contaminating the main rate table
- report OOD results as a separate case study or appendix subsection

Run only the OOD suite with:

```bash
python benchmarks/constraint_memory/run_benchmark.py --judge-model gemini --suite ood --adjudicator-model gemini
```
