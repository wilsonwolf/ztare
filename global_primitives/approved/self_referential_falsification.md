# Self-Referential Falsification / Metric Self-Certification

- Primitive ID: `self_referential_falsification_v1`
- Primitive Key: `self_referential_falsification`
- Type: `failure_pattern`
- Status: `approved`
- Epistemic Role: `attack_template`
- Confidence: `medium`

## Summary
A recurring failure where a thesis appears falsifiable because it includes code and assertions, but the test suite only recomputes thesis-authored formulas, bookkeeping identities, or self-declared metrics instead of creating an independent environment that could invalidate the claimed mechanism.

## Mechanism
The system writes a test harness that validates internal arithmetic consistency or re-derives outputs from its own assumed variables, then treats that pass as evidence of architectural or empirical validity. The proof contract is satisfied in form while the mechanism remains untested in substance. This launders a design claim into an apparently executable result without exposing the claim to adversarial conditions, external constraints, or independent failure modes.

## Scope Conditions
- The thesis claims executable falsification, empirical validation, or architectural proof through a test suite.
- The test suite is authored from the thesis's own declared variables, metrics, or formulas.
- The claimed mechanism is stronger than mere arithmetic consistency (for example robustness, causal attribution, emergent handling, or architectural validity).

## Non-Transfer Cases
- The code is explicitly framed as a bookkeeping sanity check rather than as proof of the core mechanism.
- The test suite creates an adversarial or external environment that could invalidate the mechanism independently of the thesis's own formulas.
- The proof is intentionally limited to verifying a narrow mathematical identity and does not overclaim empirical or architectural significance.

## Required Transfer Test
Ask whether the test could still fail if the thesis's claimed mechanism were false. If the harness only recomputes thesis-authored equations or checks internally defined targets, it is self-referential. To pass reuse, the proof must introduce an independent falsification environment: adversarial inputs, external constraints, competing mechanisms, or observable behavior not guaranteed by the thesis's own definitions.

## Mutator Guidance
Do not treat internal arithmetic consistency as proof of mechanism validity. If you claim executable falsification, your test must expose the mechanism to a condition under which it could actually fail for reasons not baked into your own formula.

## Firing Squad Attack
Check whether the falsification suite only re-derives the thesis's own metric from its own assumptions. If so, argue that the test proves bookkeeping, not mechanism. Ask what independent environment, adversarial perturbation, or rival mechanism could cause the claim to fail. If none exists, the proof is self-certifying.

## Judge Penalty Condition
Penalize heavily if a thesis presents internally derived arithmetic or self-authored metric checks as empirical or architectural validation. If the test suite cannot invalidate the mechanism except by violating the thesis's own definitions, the proof is self-referential and should be capped or failed.

## Evidence Summary
Observed directly in the V4 run where a thesis achieved a score of 100 by defining an Executable Falsification Contract metric, then writing tests that merely recomputed the same thesis-authored formulas. Later critique correctly identified that this was not substantive mechanism proof.

## Source Projects
- epistemic_engine_v4

## Source Incident IDs
- `epistemic_engine_v4:manual:self_referential_falsification:iteration4`

## Tags
- `engine`
- `reasoning`
- `attack_template`
- `proof_contract`
- `falsification`
- `self_certification`

## Promotion Note
Ready for approval as a narrow, broadly reusable failure pattern. The evidence base is smaller than older primitives, but the mechanism is clear, high-impact, and general across any domain where executable proof claims can be laundered into self-certifying tests.
