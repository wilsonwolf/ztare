WEIGHTS = {
    "crp_norm": 0.12,
    "nlr_norm": 0.11,
    "age_load": 0.09,
    "albumin_gap": 0.08,
}
PROGRESSION_CUTOFF = 0.31


def progression_score(crp_norm: float, nlr_norm: float, age_load: float, albumin_gap: float) -> float:
    return (
        WEIGHTS["crp_norm"] * crp_norm
        + WEIGHTS["nlr_norm"] * nlr_norm
        + WEIGHTS["age_load"] * age_load
        + WEIGHTS["albumin_gap"] * albumin_gap
    )


def classify_progression(crp_norm: float, nlr_norm: float, age_load: float, albumin_gap: float) -> bool:
    return progression_score(crp_norm, nlr_norm, age_load, albumin_gap) >= PROGRESSION_CUTOFF


above_cutoff = progression_score(1.0, 1.0, 0.7, 0.5)
below_cutoff = progression_score(0.8, 0.7, 0.6, 0.3)
assert above_cutoff >= PROGRESSION_CUTOFF
assert below_cutoff < PROGRESSION_CUTOFF
assert classify_progression(1.0, 1.0, 0.7, 0.5) is True
assert classify_progression(0.8, 0.7, 0.6, 0.3) is False

perturbed = progression_score(0.98, 1.02, 0.69, 0.51)
assert perturbed >= PROGRESSION_CUTOFF

print("Biomarker progression cutoff theorem behaves as authored.")
