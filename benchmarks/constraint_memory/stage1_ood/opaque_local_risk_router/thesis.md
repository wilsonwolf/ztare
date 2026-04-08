# Component Thesis: Opaque Local Risk Router

## Claim
This component solves one narrow problem: given an opaque risk label from upstream, it routes the case into a deterministic review bucket. It does **not** claim that the upstream label is truthful or complete.

## Safe Harbor
- Inputs are opaque symbols, not trusted truths.
- The component claims only a local deterministic mapping.
- It does **not** claim to guarantee whole-system safety, completeness, or end-to-end exploit detection.

## Mechanism
The mapping is:
- `critical` -> `manual_review`
- `medium` -> `secondary_review`
- `low` -> `auto_clear`

## Falsifiable Prediction
For every allowed input label, the router will emit the correct bucket and reject unknown labels.

## Scope Discipline
This is a bounded local component. It does not claim to prove that upstream labels are correct or sufficient.
