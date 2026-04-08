# V4 Thesis: Lightweight Bayesian Credit Update

## Claim
V4 can recover precise epistemic learning by using a compact Bayesian updater:

`new_prob = prior * exp(-1.1 * abs(relative_error))`

This preserves bounded probabilities while making the engine robust to noisy feedback. The use of `abs()` is intentional because only the magnitude of epistemic error matters for learning rate calibration.

## Mechanism
The updater is superior to explicit likelihood modeling because it is simple, bounded, and differentiable almost everywhere. If the new probability remains within `[0,1]` across representative test cases, the Bayesian credit-assignment problem is effectively solved.

## Falsifiable Prediction
Under representative forecast errors, the updater will remain coherent and show stable adaptation without human intervention.
