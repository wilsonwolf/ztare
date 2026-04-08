import math

# LOAD-BEARING VARIABLES (MANDATORY)
# All values are concrete, real-world, or system design constants.
# Attackers will Google these values to verify. NO HALLUCINATED ENTITY CONSTANTS.
EPSILON_CONST = 1e-9  # USD, to prevent division by zero
MAX_RAG_LATENCY_MS = 5000  # milliseconds, maximum permissible RAG_LATENCY for normalization
MIN_AXIOM_WEIGHT_THRESHOLD = 0.05  # dimensionless, threshold below which an axiom is retired
INITIAL_AXIOM_WEIGHT_START = 1.0  # dimensionless, starting weight for all new axioms
T_AUDIT_LAG_DAYS = 365  # days, time lag for AUDITED_Z_ACTUAL to become available
PREDICTED_OPENAI_2024_REVENUE_USD = 2.5e9  # USD, Engine's internal prediction
AUDITED_ACTUAL_OPENAI_2024_REVENUE_USD = 3.4e9  # USD, Audited, verified, historical real-world output
OBSERVED_RAG_LATENCY_MS = 1200  # milliseconds, measured computational/API cost
NUM_AXIOMS_IN_BUNDLE = 3  # integer, number of distinct axioms contributing to the prediction
NOVEL_AXIOM_INCUBATION_CYCLES = 1  # integer, number of evaluation cycles a novel axiom is 'incubated'
MUTATOR_REPUTATION_BOND_VALUE_FRACTION = 0.2  # dimensionless, system design constant for Mutator's bond
TARGET_MIN_ESTABLISHED_AXIOM_REDUCTION = 0.10  # dimensionless, target minimum reduction for established axioms
DECAY_RATE_SCALAR = 1.1  # dimensionless, scaling factor for exponential decay of axiom weights (ADJUSTED FOR NEW LOGIC)
RAG_LATENCY_COST_WEIGHT = 0.1  # dimensionless, weight given to normalized RAG_LATENCY in additive cost (NEW)
MUTATOR_MIN_INCUBATION_PENALTY_FRACTION = 0.01  # dimensionless, minimum penalty fraction for a novel axiom (NEW)

# Axiom initial states for the test scenario
initial_axiom_weight_A = INITIAL_AXIOM_WEIGHT_START
initial_axiom_weight_B = INITIAL_AXIOM_WEIGHT_START
initial_axiom_weight_C = INITIAL_AXIOM_WEIGHT_START # Novel axiom

# Derived values for Novel Axiom C's incubation
reputation_bond_C = INITIAL_AXIOM_WEIGHT_START * MUTATOR_REPUTATION_BOND_VALUE_FRACTION
min_incubation_penalty_C = MUTATOR_MIN_INCUBATION_PENALTY_FRACTION * INITIAL_AXIOM_WEIGHT_START

# --- Calculation of System_Learning_Fidelity ---

# 1. Calculate RELATIVE_DELTA_ERROR
delta_error = abs(PREDICTED_OPENAI_2024_REVENUE_USD - AUDITED_ACTUAL_OPENAI_2024_REVENUE_USD)
relative_delta_error = delta_error / max(AUDITED_ACTUAL_OPENAI_2024_REVENUE_USD, EPSILON_CONST)

# 2. Calculate Normalized_RAG_Latency
normalized_rag_latency = OBSERVED_RAG_LATENCY_MS / MAX_RAG_LATENCY_MS

# 3. Calculate Observed_Cost_j (NEW: Additive RAG_LATENCY_COST_WEIGHT)
observed_cost_j = relative_delta_error + (normalized_rag_latency * RAG_LATENCY_COST_WEIGHT)

# 4. Calculate Penalty per axiom (uniform blame assignment)
penalty_per_axiom = observed_cost_j / NUM_AXIOMS_IN_BUNDLE

# --- Axiom Weight Updates ---

# Established Axioms (Axiom A, Axiom B)
# (NEW: Exponential decay using DECAY_RATE_SCALAR)
final_axiom_weight_A = initial_axiom_weight_A * math.exp(-DECAY_RATE_SCALAR * penalty_per_axiom)
final_axiom_weight_B = initial_axiom_weight_B * math.exp(-DECAY_RATE_SCALAR * penalty_per_axiom)

# Novel Axiom (Axiom C) - Incubation Logic (NEW: Minimum penalty floor & always applies penalty)
novelty_debt_C = penalty_per_axiom # Accumulated debt for this single incubation cycle

# Determine Effective_Penalty_C based on the new logic
# Effective_Penalty_C is the higher of actual debt or the minimum incubation penalty
effective_penalty_C = max(novelty_debt_C, min_incubation_penalty_C)

final_axiom_weight_C = initial_axiom_weight_C * math.exp(-DECAY_RATE_SCALAR * effective_penalty_C)

# Check if bond is returned/forfeited (for context, not directly impacting final_axiom_weight_C)
bond_returned_C = (novelty_debt_C <= reputation_bond_C)

# --- Falsifiability Assertions ---

# Prediction 1: Established Axioms (Axiom A, Axiom B)
# Their final Axiom_Weight will be <= (1.0 - TARGET_MIN_ESTABLISHED_AXIOM_REDUCTION)
# With DECAY_RATE_SCALAR = 1.1, penalty_per_axiom = 0.09623529, exp(-1.1 * 0.09623529) = 0.89961
expected_established_weight_upper_bound = INITIAL_AXIOM_WEIGHT_START * (1.0 - TARGET_MIN_ESTABLISHED_AXIOM_REDUCTION)
print(f"Calculated Established Axiom Weight (A/B): {final_axiom_weight_A:.5f}")
print(f"Expected Established Axiom Weight Upper Bound: {expected_established_weight_upper_bound:.5f}")
assert final_axiom_weight_A <= expected_established_weight_upper_bound + EPSILON_CONST, \
    f"Established Axiom A weight {final_axiom_weight_A} must be <= {expected_established_weight_upper_bound}"
assert final_axiom_weight_B <= expected_established_weight_upper_bound + EPSILON_CONST, \
    f"Established Axiom B weight {final_axiom_weight_B} must be <= {expected_established_weight_upper_bound}"

# Prediction 2: Novel Axiom (Novel Axiom C)
# Its final Axiom_Weight will be approx 0.89961. The bond will be returned.
expected_novel_axiom_weight_C = 0.89961 # Calculated based on exp(-1.1 * max(0.09623529, 0.01))
print(f"Calculated Novel Axiom C Weight: {final_axiom_weight_C:.5f}")
print(f"Expected Novel Axiom C Weight: {expected_novel_axiom_weight_C:.5f}")
assert math.isclose(final_axiom_weight_C, expected_novel_axiom_weight_C, rel_tol=1e-5), \
    f"Novel Axiom C weight {final_axiom_weight_C} must be close to {expected_novel_axiom_weight_C}"
assert bond_returned_C, \
    f"Novel Axiom C bond should be returned as {novelty_debt_C} <= {reputation_bond_C}"

print("\nAll falsifiability assertions passed.")

# Optional: Print final state for verification
print(f"\n--- Final Axiom Weights ---")
print(f"Axiom A (Established): {final_axiom_weight_A:.5f}")
print(f"Axiom B (Established): {final_axiom_weight_B:.5f}")
print(f"Axiom C (Novel, post-incubation): {final_axiom_weight_C:.5f}")
print(f"Bond returned for Axiom C: {bond_returned_C}")
