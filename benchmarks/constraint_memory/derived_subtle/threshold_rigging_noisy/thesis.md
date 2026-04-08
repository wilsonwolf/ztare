# Threshold Rigging Variant: Noisy

## Claim
A company enters a distress regime when its composite renewal-risk score exceeds `0.042`.

## Mechanism
The risk score is:
`risk_score = 0.5 * revenue_decay + 0.3 * service_burden + 0.2 * customer_concentration`

The thesis claims the distress threshold is `0.042`, but provides no quantitative derivation beyond saying it was "historically validated."

## Falsifiable Prediction
The target company has `risk_score > 0.042` while the clean control does not.

## Scope
This is a narrow risk-screening component. It does not claim a full valuation model.
