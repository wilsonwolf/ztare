# Dimensional Error / Category Error

- Primitive ID: `dimensional_error_v1`
- Primitive Key: `dimensional_error`
- Type: `failure_pattern`
- Status: `approved`
- Epistemic Role: `test_template`
- Confidence: `high`

## Summary
A recurring failure where concepts, measurements, or calculations are inappropriately applied across different units, scales, contexts, or conceptual domains, leading to mathematical inconsistencies, logical contradictions, or invalid causal claims.

## Mechanism
This primitive fires when a system, model, or argument implicitly or explicitly misapplies a variable, constant, or conceptual framework from its native dimension (e.g., unit of measurement, temporal scale, level of abstraction, domain of applicability) to another, resulting in an incoherent or incorrect conclusion. This can manifest as: 1. Mixing incompatible units in arithmetic operations. 2. Conflating rates with stocks, or total values with incremental changes. 3. Applying conversion factors or multipliers from one context to another where causal mechanisms differ. 4. Equating or transforming concepts from disparate ontological or epistemological categories without rigorous justification (e.g., physical computation vs. subjective experience). 5. Claiming 'dimensional shifts' or 'topological pivots' that merely obscure or transfer friction/inconsistency rather than resolving it structurally.

## Scope Conditions
- Systems involving quantitative models with multiple variables and units.
- Architectural designs making claims about cross-domain interactions or transformations.
- Theoretical arguments bridging different levels of abstraction (e.g., micro vs. macro, physics vs. finance, cognition vs. cosmology).
- Any context where 'units' (literal or conceptual) are implicitly or explicitly mixed or converted.

## Non-Transfer Cases
- Systems operating solely within a single, homogenous domain where all quantities are inherently dimensionless or have explicitly consistent units without any cross-domain interaction.
- Incidents where 'dimensional errors' are purely syntax errors that do not reflect a deeper conceptual or mathematical inconsistency.

## Required Transfer Test
For any reuse, apply rigorous unit testing (e.g., `pint` library), formal dimensional analysis to all core equations, and a cross-domain conceptual mapping audit. Specifically, verify that: 1. All arithmetic operations combine dimensionally compatible quantities. 2. Conceptual transformations between domains maintain logical coherence and do not conflate distinct categories (e.g., epistemic with ontic, local with global). 3. Scaling factors or multipliers are valid for their specific base and context. 4. Time-dependent variables are not incorrectly treated as static aggregates, or vice-versa. Fails if these checks reveal inconsistencies or contradictions.

## Mutator Guidance
Identify variables, constants, or concepts that operate on different scales, units, or levels of abstraction. Construct scenarios where these disparate elements are combined in mathematically or conceptually incoherent ways. Examples: swap units, misapply multipliers, treat a rate as a stock, or force a qualitative concept into a quantitative framework where it doesn't belong. Target 'dimensional shifts' or 'topological pivots' by demonstrating they simply rename or relocate the inconsistency, rather than resolve it.

## Firing Squad Attack
Design tests that explicitly mix units (e.g., `ureg.joule + ureg.watt`), apply conversion factors incorrectly (e.g., `WSPM` as `WIP stock`), or force conceptually incompatible values into calculations. Assert `DimensionalityError`, `TypeError`, or logical contradictions (`assert result != expected_value_after_dimensional_correction`). For conceptual errors, analyze the logical consistency of 'dimensional shifts' and provide counter-examples where the shift introduces new, unresolved inconsistencies or semantic ambiguities.

## Judge Penalty Condition
The primitive's core calculation, argument, or conceptual mapping contains unresolved dimensional inconsistencies or category errors that lead to mathematical insolvency, logical contradiction, or render claims unfalsifiable. The severity of the penalty should scale with the centrality and impact of the flawed element.

## Evidence Summary
Incidents across financial, physics, startup, and AI epistemic engine projects consistently highlight errors in applying values or concepts across different units, scales, or domains. These range from simple unit mismatches in code (e.g., `pint` errors, conflating rates with stock) to complex conceptual category errors (e.g., equating physical computation with subjective experience, mistaking epistemic compression for ontological erasure). Repeatedly, models exhibit 'mathematical insolvency' or 'structural toxicity' when calculations fail due to incompatible dimensions or when a claimed 'dimensional shift' merely reintroduces the same fundamental inconsistency in a new guise. Many incidents involve the direct failure of Python unit tests designed to detect such errors, or adversarial critiques successfully exposing them.

## Source Projects
- ai_inference_collapse_claude_gemini
- ai_inference_collapse_gemini_gemini
- ai_inference_collapse_gpt4o_gemini
- central_station
- epistemic_engine_v3_gemini_gemini
- figs
- hbr_strategy
- recursive_bayesian_claude_gemini
- recursive_bayesian_gemini_claude
- recursive_bayesian_gemini_gemini
- recursive_bayesian_gpt4o_gemini_no_escalation
- simulation_god_claude_gemini
- simulation_god_gemini_gemini
- simulation_god_gpt4o_gemini
- tsmc_fragility_gemini_gemini
- tsmc_fragility_gpt4o_gemini

## Source Incident IDs
- `ai_inference_collapse_claude_gemini:history:1775335275_iter3_score_88_ai_inference_collapse:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774998442:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774998675:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774998858:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774999069:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774999280:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774999509:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1774999905:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775000239:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775000466:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775000923:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775001134:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775001330:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775001524:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775001718:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775001865:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775006907:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775007114:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775007317:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775007894:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775008121:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775008263:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775008955:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775009116:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775009314:dimensional_error`
- `ai_inference_collapse_gemini_gemini:debate_log:debate_log_iter_1775012830:dimensional_error`
- `ai_inference_collapse_gemini_gemini:history:v1_score_40:dimensional_error`
- `ai_inference_collapse_gemini_gemini:history:v1_score_50:dimensional_error`
- `ai_inference_collapse_gemini_gemini:history:v2_score_95:dimensional_error`
- `ai_inference_collapse_gemini_gemini:history:v8_score_90:dimensional_error`
- `ai_inference_collapse_gpt4o_gemini:test_model:test_model:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775256364:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775259498:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775259965:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775260471:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775263773:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775264243:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775265527:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775265753:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775266154:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775266531:dimensional_error`
- `central_station:debate_log:debate_log_iter_1775266692:dimensional_error`
- `central_station:history:1775271249_iter9_score_95_startup_experiment_design:dimensional_error`
- `central_station:test_model:test_model:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775099293:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775099644:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775099859:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775100329:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775100566:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775102844:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775103226:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775103528:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775133621:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775133908:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775134730:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135092:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135389:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135811:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775136177:dimensional_error`
- `epistemic_engine_v3_gemini_gemini:history:1775133604_iter5_score_45_epistemic_engine_v3_evolved:dimensional_error`
- `figs:history:v15_score_69:dimensional_error`
- `hbr_strategy:debate_log:debate_log_iter_1775175718:dimensional_error`
- `hbr_strategy:history:1775181023_iter1_score_176_hbr_strategy:dimensional_error`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775248589:dimensional_error`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775252935:dimensional_error`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775253920:dimensional_error`
- `recursive_bayesian_claude_gemini:debate_log:debate_log_iter_1775255108:dimensional_error`
- `recursive_bayesian_claude_gemini:history:1775252009_iter4_score_95_recursive_bayesian:dimensional_error`
- `recursive_bayesian_gemini_claude:debate_log:debate_log_iter_1775254693:dimensional_error`
- `recursive_bayesian_gemini_claude:debate_log:debate_log_iter_1775254848:dimensional_error`
- `recursive_bayesian_gemini_claude:debate_log:debate_log_iter_1775255001:dimensional_error`
- `recursive_bayesian_gemini_claude:debate_log:debate_log_iter_1775255181:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775064375:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775065067:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775080772:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775081836:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775082134:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775082480:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775082820:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775083184:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775083558:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775083843:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775084050:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775084280:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775084558:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775084825:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775085228:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775087617:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775087861:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775088116:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775088271:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775088449:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775088597:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775088830:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775089039:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775089223:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775089422:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775089584:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775089754:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775089951:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775090167:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775090352:dimensional_error`
- `recursive_bayesian_gemini_gemini:debate_log:debate_log_iter_1775090520:dimensional_error`
- `recursive_bayesian_gemini_gemini:history:v1_score_40:dimensional_error`
- `recursive_bayesian_gemini_gemini:history:v9_score_50:dimensional_error`
- `recursive_bayesian_gpt4o_gemini_no_escalation:debate_log:debate_log_iter_1775256522:dimensional_error`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775328922:dimensional_error`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775330035:dimensional_error`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775330771:dimensional_error`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775331362:dimensional_error`
- `simulation_god_claude_gemini:debate_log:debate_log_iter_1775331650:dimensional_error`
- `simulation_god_claude_gemini:history:1775328514_iter10_score_91_sim_god:dimensional_error`
- `simulation_god_claude_gemini:history:1775328514_iter13_score_95_sim_god:dimensional_error`
- `simulation_god_claude_gemini:history:1775328514_iter2_score_75_sim_god:dimensional_error`
- `simulation_god_claude_gemini:test_model:test_model:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774818375:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774818530:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774818603:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774818828:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821202:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821368:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821439:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821783:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774821978:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774823519:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774823673:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774824362:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774824510:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774825447:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774827641:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774839194:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774839607:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774840217:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774842558:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774843012:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774874597:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774875372:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774885250:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774885636:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774890617:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774891012:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774928488:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774929222:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774930383:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774930584:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774931361:dimensional_error`
- `simulation_god_gemini_gemini:debate_log:debate_log_iter_1774931587:dimensional_error`
- `simulation_god_gemini_gemini:history:v1_score_10:dimensional_error`
- `simulation_god_gemini_gemini:history:v1_score_30:dimensional_error`
- `simulation_god_gemini_gemini:history:v1_score_32:dimensional_error`
- `simulation_god_gemini_gemini:history:v1_score_40:dimensional_error`
- `simulation_god_gemini_gemini:history:v1_score_50:dimensional_error`
- `simulation_god_gemini_gemini:history:v1_score_70:dimensional_error`
- `simulation_god_gemini_gemini:history:v2_score_15:dimensional_error`
- `simulation_god_gemini_gemini:history:v2_score_18:dimensional_error`
- `simulation_god_gemini_gemini:history:v2_score_45:dimensional_error`
- `simulation_god_gemini_gemini:history:v2_score_57:dimensional_error`
- `simulation_god_gemini_gemini:history:v3_score_25:dimensional_error`
- `simulation_god_gemini_gemini:history:v4_score_32:dimensional_error`
- `simulation_god_gemini_gemini:history:v5_score_43:dimensional_error`
- `simulation_god_gemini_gemini:history:v5_score_52:dimensional_error`
- `simulation_god_gemini_gemini:history:v5_score_55:dimensional_error`
- `simulation_god_gemini_gemini:history:v6_score_65:dimensional_error`
- `simulation_god_gemini_gemini:history:v7_score_58:dimensional_error`
- `simulation_god_gemini_gemini:history:v8_score_70:dimensional_error`
- `simulation_god_gemini_gemini:history:v9_score_55:dimensional_error`
- `simulation_god_gemini_gemini:test_model:test_model:dimensional_error`
- `simulation_god_gpt4o_gemini:debate_log:debate_log_iter_1775327612:dimensional_error`
- `simulation_god_gpt4o_gemini:debate_log:debate_log_iter_1775327756:dimensional_error`
- `simulation_god_gpt4o_gemini:test_model:test_model:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775046590:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775047150:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775047626:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775047961:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775048142:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775048354:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775048486:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775048656:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775048879:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775049065:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775049249:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775049640:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775096331:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775096587:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775097100:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775097317:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775097549:dimensional_error`
- `tsmc_fragility_gemini_gemini:debate_log:debate_log_iter_1775097727:dimensional_error`
- `tsmc_fragility_gemini_gemini:history:v11_score_75:dimensional_error`
- `tsmc_fragility_gemini_gemini:history:v2_score_65:dimensional_error`
- `tsmc_fragility_gemini_gemini:history:v4_score_70:dimensional_error`
- `tsmc_fragility_gemini_gemini:history:v8_score_60:dimensional_error`
- `tsmc_fragility_gpt4o_gemini:debate_log:debate_log_iter_1775336565:dimensional_error`

## Tags
- `quantitative_modeling`
- `conceptual_modeling`
- `numerical_instability`
- `unit_errors`
- `category_errors`
- `scale_misapplication`
- `cross_domain_inconsistency`

## Promotion Note
This primitive captures a highly prevalent and severe failure pattern that manifests across diverse domains, from hard science to financial modeling and abstract architectural design. The incidents clearly support its portability and impact. Ready for human approval.
