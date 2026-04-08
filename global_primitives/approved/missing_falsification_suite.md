# Missing Model Falsification Suite

- Primitive ID: `missing_falsification_suite`
- Primitive Key: `missing_falsification_suite`
- Type: `failure_pattern`
- Status: `approved`
- Epistemic Role: `heuristic`
- Confidence: `high`

## Summary
Models or theses are frequently submitted without an expected automated falsification suite (e.g., 'test_model.py'), preventing programmatic verification of core claims.

## Mechanism
When a dedicated, executable falsification suite (e.g., 'test_model.py') is absent, critical numerical, logical, or structural assertions within a submitted model or thesis remain unverified by automated means. This bypasses a crucial quality gate intended to catch fundamental inconsistencies, logical errors, or unstated assumptions, requiring laborious manual detection or leading to undetected flaws. The system's expectation for such a suite signals a design intent for automated rigorous falsification that is not met.

## Scope Conditions
- Project submissions requiring programmatic or mathematical model verification.
- Projects where automated unit tests for core model logic are expected (e.g., presence of a 'test_model.py' file or equivalent).

## Non-Transfer Cases
- Projects where the core thesis is purely qualitative and does not involve explicit computational models or mathematical assertions requiring code-based falsification.

## Required Transfer Test
Verify the presence and successful execution of a dedicated falsification suite (e.g., 'test_model.py' or equivalent) that programmatically tests the core mathematical, logical, or structural claims of the model/thesis.

## Mutator Guidance
Mutators must include a comprehensive and executable falsification suite (e.g., 'test_model.py') that rigorously validates the numerical and logical foundations of their thesis. Absence or failure of this suite will result in a penalty.

## Firing Squad Attack
The Firing Squad must initiate an automated check for the presence and successful execution of the 'test_model.py' falsification suite. If absent or failing, the Firing Squad should flag a critical vulnerability and penalize the submission.

## Judge Penalty Condition
Penalty applied if the submission lacks a 'test_model.py' file or equivalent falsification suite, or if the provided suite fails to execute or exposes critical flaws in the thesis's core logic or numerical claims.

## Evidence Summary
Across 35 incidents in 15 distinct projects, the recurring pattern is the explicit warning "WARNING: No falsification suite (test_model.py) found for this iteration" recorded in 'debate_log' artifacts. This consistently signals that a critical automated testing component was missing from the submission, indicating a process failure. The 'weakest_point' descriptions in these incidents frequently detail substantive flaws in the models or theses that could have been detected and prevented by the presence and execution of such a suite, underscoring the direct impact of its absence.

## Source Projects
- ai_inference_collapse_claude_gemini
- ai_inference_collapse_gemini_gemini
- ai_inference_collapse_gpt4o_gemini
- central_station
- epistemic_engine_v3_gemini_gemini
- recursive_bayesian_claude_gemini
- recursive_bayesian_gemini_claude
- recursive_bayesian_gemini_gemini
- recursive_bayesian_gpt4o_gemini
- recursive_bayesian_gpt4o_gemini_no_escalation
- simulation_god_claude_gemini
- simulation_god_gemini_gemini
- simulation_god_gpt4o_gemini
- tsmc_fragility_gemini_gemini
- tsmc_fragility_gpt4o_gemini

## Source Incident IDs
- `ai_inference_collapse_claude_gemini:debate_log:debate_log_iter_1775335276:missing_falsification_suite`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774998442:missing_falsification_suite`
- `ai_inference_collapse_gpt4o_gemini:debate_log:debate_log_iter_1775335308:missing_falsification_suite`
- `central_station:debate_log:debate_log_iter_1775255476:missing_falsification_suite`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775099293:missing_falsification_suite`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775248589:missing_falsification_suite`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775251602:missing_falsification_suite`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775251836:missing_falsification_suite`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775252010:missing_falsification_suite`
- `recursive_bayesian_gemini_claude:debate_log:debate_log_iter_1775252000:missing_falsification_suite`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775064375:missing_falsification_suite`
- `recursive_bayesian_gpt4o_gemini:debate_log:debate_log_iter_1775257373:missing_falsification_suite`
- `recursive_bayesian_gpt4o_gemini_no_escalation:debate_log:debate_log_iter_1775256220:missing_falsification_suite`
- `recursive_bayesian_gpt4o_gemini_no_escalation:debate_log:debate_log_iter_1775256284:missing_falsification_suite`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775327563:missing_falsification_suite`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775327859:missing_falsification_suite`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775328515:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821135:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821202:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821296:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821368:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821439:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821497:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821594:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821693:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821783:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821889:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821978:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774822262:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774822333:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774822436:missing_falsification_suite`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774823322:missing_falsification_suite`
- `simulation_god_gpt4o_gemini:debate_log:debate_log_iter_1775327568:missing_falsification_suite`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775046590:missing_falsification_suite`
- `tsmc_fragility_gpt4o_gemini:debate_log:debate_log_iter_1775336299:missing_falsification_suite`

## Tags
- `process_failure`
- `testing`
- `validation`
- `automation`
- `quality_gate`
- `model_verification`

## Promotion Note
This primitive is ready for human approval. The pattern is clearly defined, consistently observed across numerous projects, and directly identifies a critical process failure that compromises automated verification of submitted models/theses. It pinpoints a narrow, actionable deficiency.
