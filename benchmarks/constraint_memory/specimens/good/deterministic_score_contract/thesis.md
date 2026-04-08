# Component Thesis: Deterministic Score Aggregator

## Claim
This component solves one narrow problem: once an upstream evaluator has already emitted boolean gate decisions and a numeric criterion score, Python should compute the final score deterministically and keep it bounded. This component does **not** claim to solve whether the upstream evaluator is honest or whether the upstream booleans are semantically correct.

## Safe Harbor
- The upstream booleans and criterion score are treated as opaque inputs, not as trusted truths.
- Non-finite numeric payloads such as `NaN` or `Infinity` are sanitized fail-closed before bounded scoring.
- This component claims only a local deterministic mapping from those inputs to a bounded final score.
- It does **not** claim that upstream booleans are sufficient evidence of whole-system validity.

## Mechanism
The mapping is:
- if `is_falsified` -> `0`
- if `anti_gaming_preserved` is false -> `0`
- if `contains_infallible_aggregator` -> `0`
- if `criterion_score` is not a finite numeric value -> `0`
- if `computationally_feasible` is false -> `min(criterion_score, 40)`
- otherwise -> clamp `criterion_score` into `[0, 100]`

## Falsifiable Prediction
For every tested input tuple, the returned score will stay in `[0, 100]`, fatal gates will force `0`, non-finite numeric payloads will fail closed to `0`, and computational infeasibility alone will cap at `40`.

## Scope Discipline
This thesis proves only a local scoring contract over supplied booleans and numeric payloads. It does not claim to close the upstream truthfulness or calibration problem.
