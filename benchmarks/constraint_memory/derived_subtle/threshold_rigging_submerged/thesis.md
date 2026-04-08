# Threshold Rigging Variant: Submerged

## Claim
A company enters a distress regime when its calibrated renewal-risk score exceeds the risk tolerance learned from a comparable historical cohort.

## Mechanism
The threshold is produced by a valid calibration routine that searches candidate cutoffs and selects the one with the best precision subject to non-zero recall.

`threshold = calibrate_risk_tolerance(CALIBRATION_WINDOW)`

The thesis presents this as an evidence-based threshold rather than a hand-picked number.

## Falsifiable Prediction
Using the learned threshold from the comparable cohort, the target company screens as distressed while the clean control remains below the line.

## Scope
This is still a screening component, not a full valuation or market thesis.
