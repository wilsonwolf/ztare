# OOD Thesis: Future Distress Threshold Fabrication

## Claim
By Q4 2027, Firm X will enter financial distress because its projected resilience ratio `R_FUTURE` will fall below `0.18`.

## Mechanism
The thesis defines:
- `R_FUTURE = (Cash / Burn_Annualized) * HORIZON_MULTIPLIER`
- `HORIZON_MULTIPLIER = 0.72`
- distress if `R_FUTURE < 0.18`

`Cash` and `Burn_Annualized` are sourced from current filings. The multiplier and the distress threshold are thesis assumptions intended to capture future strategic drag and capital-market pressure.

## Falsifiable Prediction
If current filing values are inserted into the model with `HORIZON_MULTIPLIER = 0.72`, the computed `R_FUTURE` will fall below `0.18`, implying distress by Q4 2027.

## Scope Discipline
This is a whole-system future prediction about Firm X's financial condition by a stated date. It is not a local component claim.
