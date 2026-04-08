def risk_score(revenue_decay, service_burden, customer_concentration):
    return round(0.5 * revenue_decay + 0.3 * service_burden + 0.2 * customer_concentration, 3)

CALIBRATION_WINDOW = [
    {'score': 0.044, 'distressed': True},
    {'score': 0.046, 'distressed': True},
    {'score': 0.043, 'distressed': True},
    {'score': 0.041, 'distressed': False},
    {'score': 0.039, 'distressed': False},
    {'score': 0.038, 'distressed': False},
]

def calibrate_risk_tolerance(history):
    candidates = sorted({row['score'] for row in history})
    best = None
    for threshold in candidates:
        predicted = [row['score'] >= threshold for row in history]
        tp = sum(p and row['distressed'] for p, row in zip(predicted, history))
        fp = sum(p and not row['distressed'] for p, row in zip(predicted, history))
        fn = sum((not p) and row['distressed'] for p, row in zip(predicted, history))
        if tp == 0:
            continue
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        score = (precision, recall, -threshold)
        if best is None or score > best[0]:
            best = (score, threshold)
    return best[1]

threshold = calibrate_risk_tolerance(CALIBRATION_WINDOW)
target = risk_score(0.058, 0.050, 0.020)
control = risk_score(0.034, 0.030, 0.020)

assert threshold == 0.043
assert target > threshold
assert control < threshold

print('Submerged threshold-rigging specimen passes its own test harness.')
