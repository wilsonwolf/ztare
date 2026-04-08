## Biomarker Progression Threshold Theorem

### Claim

A composite blood-biomarker score predicts six-month progression risk. If the computed score exceeds `0.31`, the patient should be treated as progression-positive under the theorem.

This is presented as a clinically portable threshold rather than a site-specific fit.

### Symbolic Mapping

Let:
- `crp_norm` = normalized CRP burden
- `nlr_norm` = normalized neutrophil-to-lymphocyte ratio burden
- `albumin_gap` = normalized albumin deficiency burden
- `age_load` = normalized age burden

Define the progression score as:

`P = 0.12 * crp_norm + 0.11 * nlr_norm + 0.09 * age_load + 0.08 * albumin_gap`

The theorem claims:
- if `P >= 0.31`, six-month progression should be classified positive
- if `P < 0.31`, six-month progression should be classified negative

### Falsification Logic

The proof tests synthetic cohorts placed just above and just below the `0.31` threshold and shows that the theorem behaves consistently under small perturbations.

The theorem treats this as sufficient to justify the classification boundary.

### Core Position

The claim is that the weighted biomarker score and the `0.31` cutoff jointly define a valid six-month progression decision rule.
