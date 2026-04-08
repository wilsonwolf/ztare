import math


def update_probability(prior, actual, predicted):
    relative_error = abs(actual - predicted)
    new_prob = prior * math.exp(-1.1 * relative_error)
    return max(0.0, min(1.0, new_prob))

p1 = update_probability(0.8, 0.8, 0.7)
p2 = update_probability(0.8, 0.2, 0.9)

assert 0.0 <= p1 <= 1.0
assert 0.0 <= p2 <= 1.0
assert p1 > p2

print('Bounded update rule executed successfully.')
print(f'p1={p1:.4f}, p2={p2:.4f}')
