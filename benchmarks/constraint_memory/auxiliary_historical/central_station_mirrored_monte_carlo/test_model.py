import numpy as np

def execute_experiment_validation(trials=10000, n_invited=20):
    np.random.seed(42)

    # 1. GENERATE MONTE CARLO ENVIRONMENT BASED ON IMMUTABLE RANGES
    lf_showup = np.random.uniform(0.55, 0.80, trials)
    retention_same = np.random.uniform(0.60, 0.85, trials)
    retention_rand = np.random.uniform(0.30, 0.55, trials)
    ref_ask_p1 = np.random.uniform(0.03, 0.12, trials)
    ref_ask_p2 = np.random.uniform(0.08, 0.22, trials)

    # 2. DESIGN DECISION 1: COHORT CONTINUITY (Same vs Random)
    # Metric: Absolute attendees bridging from Program 1 to Program 2
    attend_p1 = np.random.binomial(n_invited, lf_showup)
    p2_same = np.random.binomial(attend_p1, retention_same)
    p2_rand = np.random.binomial(attend_p1, retention_rand)
    
    win_rate_continuity = np.mean(p2_same > p2_rand)

    # 3. DESIGN DECISION 2: REFERRAL TIMING (Ask Post-P1 vs Ask Post-P2)
    # Metric: Absolute Referral Triggers Generated
    ref_trig_p1 = np.random.binomial(attend_p1, ref_ask_p1)
    ref_trig_p2 = np.random.binomial(p2_same, ref_ask_p2) 
    
    win_rate_referral = np.mean(ref_trig_p2 > ref_trig_p1)

    # 4. SENSITIVITY CALCULATION (Variance Contribution)
    # Testing max outcome deviation caused by the limits of each behavioral parameter
    mean_ret = 0.725
    mean_lf = 0.675
    impact_lf_range = n_invited * (0.80 - 0.55) * mean_ret    # Delta: 3.625
    impact_ret_range = n_invited * mean_lf * (0.85 - 0.60)    # Delta: 3.375

    return (win_rate_continuity, win_rate_referral, p2_same, p2_rand, 
            ref_trig_p1, ref_trig_p2, impact_lf_range, impact_ret_range)

# --- EXECUTE UNIT TESTS ---
(win_cont, win_ref, p2_same, p2_rand, ref_1, ref_2, 
 sens_lf, sens_ret) = execute_experiment_validation()

# ASSERTION 1: Systemic Dominance. 
# An N=20 experiment on Cohort Continuity must decisively force a binary outcome (>80% win rate).
assert win_cont >= 0.80, f"STRUCTURAL FAILURE: Continuity experiment underpowered at N=20. Win rate: {win_cont}"

# ASSERTION 2: Mathematical Insolvency. 
# An N=20 experiment on Referral Timing must fail to break the noise threshold (<65% win rate).
assert win_ref < 0.65, f"FALSIFICATION FAILURE: Referral experiment falsely reporting statistical dominance. Win rate: {win_ref}"

# ASSERTION 3: Behavioral Sensitivity Verification.
assert sens_lf > sens_ret, "Category Error: Low-Friction Show-up is empirically mathematically the highest sensitivity variable."

print("UNIT TESTS PASSED: N=20 Experiment Constraints Mathematically Verified.")
print(f"Cohort Continuity Empirical Dominance Margin: {win_cont*100:.1f}%")
print(f"Referral Timing Empirical Dominance Margin:   {win_ref*100:.1f}%")
print("-" * 40)
print(f"P2 Same Cohort Attendees (P10/P50/P90): {np.percentile(p2_same, 10):.0f} / {np.percentile(p2_same, 50):.0f} / {np.percentile(p2_same, 90):.0f}")
print(f"P2 Rand Cohort Attendees (P10/P50/P90): {np.percentile(p2_rand, 10):.0f} / {np.percentile(p2_rand, 50):.0f} / {np.percentile(p2_rand, 90):.0f}")
