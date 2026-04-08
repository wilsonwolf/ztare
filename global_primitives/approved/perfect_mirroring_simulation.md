# Perfectly Mirrored Simulation

- Primitive ID: `epistemic_failure:perfect_mirroring_simulation`
- Primitive Key: `perfect_mirroring_simulation`
- Type: `failure_pattern`
- Status: `approved`
- Epistemic Role: `test_template`
- Confidence: `medium`

## Summary
A system under test is evaluated within a simulated reality where the ground truth generation or underlying causal structure is designed to trivially or perfectly align with the system's internal assumptions or hypothesized models, creating an 'artificially easy' learning environment and a false sense of robust causal discovery or credit assignment.

## Mechanism
The simulated ground truth (e.g., `Z_actual`) or the causal relationships within the simulated environment are defined using parameters or functional forms that directly mirror the internal structure, assumptions (e.g., linearity, specific coefficient values), or learning mechanism of the system under test. This perfect alignment allows the system to trivially 'learn' or 'converge' to the simulated truth, thereby masking its inability to handle more complex, dynamic, non-linear, or misaligned causal structures found in real-world or truly adversarial conditions. This leads to a failure in achieving empirical calibration and robust credit assignment under broader conditions.

## Scope Conditions
- System under test (SUT) aims to discover causal relationships or perform credit assignment among variables.
- SUT's performance is primarily validated within a simulated environment.
- The simulated environment's ground truth or causal structure is internally defined (synthetic) rather than derived from external observations.
- The functional form or parameters used to generate the simulated ground truth directly correspond to or are overly simplified to match the SUT's internal modeling assumptions (e.g., assuming linearity, fixed asserted values).

## Non-Transfer Cases
- The SUT is being evaluated against truly external, real-world data where the ground truth is not controlled or 'cooked'.
- The simulated environment is intentionally designed to be complex, non-linear, or misaligned with the SUT's assumptions to explicitly test robustness or limitations.
- The simulation serves as a unit test for a specific component's optimization or a known, simplified causal mechanism, and is not used to claim general causal discovery or credit assignment capabilities.

## Required Transfer Test
Before reuse, verify that the simulated ground truth generation or causal structure is defined *independently* of the system's internal assumptions or parameters. Introduce non-linearities, unmodeled variables, dynamic changes to causal strengths, or misaligned functional forms into the simulated reality. Confirm that the system's performance (e.g., Brier Skill Score, coefficient convergence, credit assignment accuracy) remains robust and meets target thresholds under these more realistic or adversarial conditions.

## Mutator Guidance
When designing simulated environments for causal discovery systems, ensure the ground truth generation logic (e.g., `Z_actual`) does not trivially instantiate or directly reflect the system's hypothesized causal forms. Introduce unmodeled confounders, non-linear interactions, and dynamic shifts in causal strength. Vary the true underlying values of asserted axioms dynamically rather than fixing them to prevent 'cooking' the learning environment.

## Firing Squad Attack
Construct a simulated environment where the ground truth (`Z_actual`) generation is a perfectly linear, additive combination of inputs, mirroring the system's internal model assumptions. Demonstrate that the system achieves target performance (e.g., converges to 'true' coefficients). Then, without changing the system's internal architecture, modify the `Z_actual` generation to include unmodeled non-linearities, interactions, or dynamic axiom values, and show that the system's performance significantly degrades or fails to robustly assign credit.

## Judge Penalty Condition
If a system claims robust causal discovery or precise credit assignment, but its empirical validation or falsification suite relies solely or predominantly on simulated realities where the ground truth is trivially discoverable (e.g., perfectly mirrored causal structures, fixed asserted axiom values that align with internal assumptions), then penalize for insufficient evidence of portability and overclaiming capabilities beyond the narrowly defined simulation.

## Evidence Summary
Multiple incidents within the 'epistemic_engine_v3_gemini_gemini' project consistently highlight a failure pattern where the system under test (ThesisPredictor) was evaluated in simulated environments ('simulated reality') where the ground truth (`Z_actual`) or causal structure was 'cooked', 'artificially easy', or 'perfectly mirroring' the system's assumptions. This setup led to claims of learning or credit assignment that failed when exposed to 'more realistic (non-linear) Z_actual generation conditions' or when 'the *true* underlying value of this axiom is allowed to vary independently'. The incidents demonstrate that such perfectly mirrored simulations undermine the philosophical claim of 'precise, real-time credit assignment' and fail to provide robust empirical calibration.

## Source Projects
- epistemic_engine_v3_gemini_gemini

## Source Incident IDs
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775100566:perfect_mirroring_simulation`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775100789:perfect_mirroring_simulation`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775101023:perfect_mirroring_simulation`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135092:perfect_mirroring_simulation`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135811:perfect_mirroring_simulation`

## Tags
- `simulation`
- `epistemic_failure`
- `evaluation`
- `overfitting_to_simulation`
- `causal_discovery`
- `test_harness`
- `false_positive_validation`

## Promotion Note
This primitive captures a clear, recurring failure pattern in system evaluation where an 'artificially easy' or 'perfectly mirroring' simulated environment misleads about the system's true capabilities for causal discovery and credit assignment. The incidents consistently support the mechanism. It is ready for human approval as a robust failure pattern and implicitly as a test template for identifying weak evaluation setups.
