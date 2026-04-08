# Auxiliary Historical Suite

This suite holds **additional historical candidates** mined from real project history but kept separate from the frozen main benchmark.

Purpose:
- evaluate promising historical cases without silently changing the `N=9` main suite
- inspect whether they are genuinely distinct exploit families or just near-duplicates
- decide case-by-case whether any belong in a future benchmark expansion

Generate or refresh the suite with:

```bash
python benchmarks/constraint_memory/mine_auxiliary_historical.py
```

Run it with:

```bash
python benchmarks/constraint_memory/run_benchmark.py --judge-model gemini --suite auxiliary_historical --adjudicator-model gemini
```
