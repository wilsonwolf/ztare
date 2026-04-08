cash = 240.0
burn_annualized = 1200.0
horizon_multiplier = 0.72
distress_threshold = 0.18

r_future = (cash / burn_annualized) * horizon_multiplier
assert round(r_future, 3) == 0.144
assert r_future < distress_threshold

counterfactual_multiplier = 1.10
r_counterfactual = (cash / burn_annualized) * counterfactual_multiplier
assert r_counterfactual > distress_threshold

print("Future distress threshold computation behaves as specified.")
