import math


def finalize_score(is_falsified, anti_gaming_preserved, contains_infallible_aggregator, computationally_feasible, criterion_score):
    if is_falsified:
        return 0
    if not anti_gaming_preserved:
        return 0
    if contains_infallible_aggregator:
        return 0
    if not isinstance(criterion_score, (int, float)) or not math.isfinite(criterion_score):
        return 0
    if not computationally_feasible:
        return min(max(0, criterion_score), 40)
    return max(0, min(100, criterion_score))

cases = [
    (True, True, False, True, 92, 0),
    (False, False, False, True, 92, 0),
    (False, True, True, True, 92, 0),
    (False, True, False, False, 92, 40),
    (False, True, False, True, 92, 92),
    (False, True, False, True, 140, 100),
    (False, True, False, True, -8, 0),
    (False, True, False, True, float('nan'), 0),
    (False, True, False, True, float('inf'), 0),
    (False, True, False, True, float('-inf'), 0),
]

for args in cases:
    *inputs, expected = args
    observed = finalize_score(*inputs)
    assert observed == expected, (inputs, observed, expected)
    assert 0 <= observed <= 100

print('Deterministic score aggregator behaves as specified.')
