# Component Thesis: Fail-Closed Test Status Gate

## Claim
This component solves one narrow problem: when a falsification suite emits a received status token, that token should map into deterministic fail-closed semantics so that `missing`, `failed`, or `timed-out` received statuses cannot quietly pass through evaluation.

## Safe Harbor
- Status tokens are treated as opaque input symbols, not as proof that the upstream test harness is complete or truthful.
- This component claims only a local fail-closed mapping from status token to hard-fail behavior.
- It does **not** claim that a `pass` token is sufficient proof of mechanism validity.
- It does **not** claim to solve transport-layer delivery, upstream liveness, or the total absence of any emitted status token.

## Mechanism
The mapping is:
- `pass` -> no automatic hard fail
- `fail` -> hard fail
- `missing` -> hard fail
- `timeout` -> hard fail

## Falsifiable Prediction
For every allowed status token, the component will return the correct fail-closed boolean and reject unknown statuses.

## Scope Discipline
This thesis proves only local fail-closed semantics for received test-suite status tokens. It does not claim that a passing test suite is sufficient proof of mechanism validity, nor that the broader system guarantees status-token delivery under all upstream failure modes.
