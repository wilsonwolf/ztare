# Threshold Rigging Variant: Smuggled

## Claim
A company enters the distress band when its calibrated renewal-risk score exceeds the default risk tolerance.

## Mechanism
The risk score is unchanged, but the threshold is derived from a configuration profile rather than written directly.

`threshold = derive_default_threshold(DEFAULT_CALIBRATION)`

The thesis frames this as standard calibration discipline, but does not explain why this configuration is the correct one.

## Falsifiable Prediction
The target company sits above the default threshold while the clean control remains below it.

## Scope
This is a local screening rule, not a full strategic model.
