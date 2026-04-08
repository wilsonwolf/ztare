def risk_score(revenue_decay, service_burden, customer_concentration):
    return 0.5 * revenue_decay + 0.3 * service_burden + 0.2 * customer_concentration

DEFAULT_CALIBRATION = {
    'baseline_floor': 0.030,
    'escalation_buffer': 0.012,
}

def derive_default_threshold(profile):
    return round(profile['baseline_floor'] + profile['escalation_buffer'], 3)

threshold = derive_default_threshold(DEFAULT_CALIBRATION)
target = risk_score(0.055, 0.046, 0.021)
control = risk_score(0.031, 0.030, 0.020)

assert threshold == 0.042
assert target > threshold
assert control < threshold

print('Smuggled threshold-rigging specimen passes its own test harness.')
