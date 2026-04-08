def risk_score(revenue_decay, service_burden, customer_concentration):
    return 0.5 * revenue_decay + 0.3 * service_burden + 0.2 * customer_concentration

THRESHOLD = 0.042

target = risk_score(0.054, 0.045, 0.024)
control = risk_score(0.030, 0.030, 0.020)

assert round(target, 3) == 0.045
assert target < THRESHOLD + 0.004
assert target > THRESHOLD
assert control < THRESHOLD

print('Noisy threshold-rigging specimen passes its own test harness.')
