# Domain Leakage into Abstract Architectural Proofs

- Primitive ID: `domain_leakage`
- Primitive Key: `domain_leakage`
- Type: `failure_pattern`
- Status: `approved`
- Epistemic Role: `heuristic`
- Confidence: `high`

## Summary
A recurring failure where specific, domain-contextual details (e.g., real-world inspired variable names, specific 'hypothetical' values) inadvertently compromise the intended generality, abstraction, or robustness of an architectural or theoretical claim that is supported by a simplified simulation or example.

## Mechanism
The system makes a general architectural or theoretical claim, often with an explicit 'abstraction mandate' to use simplified, hypothetical parameters in supporting simulations or examples. The failure occurs when the chosen parameters, despite being qualified as 'hypothetical' or 'simulated', retain domain-specific names (e.g., 'hypothetical_economy_growth_rate_q1_2025_base') or values that, even if numerically plausible, implicitly carry specific real-world assumptions or connotations. This compromises the intended generality of the architectural claim by allowing domain-specific context to leak into what should be an abstract, portable proof.

## Scope Conditions
- A system makes an architectural or theoretical claim intended for general application.
- The claim is supported or demonstrated by a simulation or concrete example that uses specific parameters.
- There is an explicit or implicit 'abstraction mandate' for these parameters (e.g., they should be abstract, hypothetical, dimensionless, not specific real-world constants).
- The chosen parameters, despite qualifiers, retain domain-specific names or values that evoke specific real-world contexts.

## Non-Transfer Cases
- When the system's claims are explicitly tied to specific real-world domain parameters and are not intended to be abstract or generalizable.
- When the simulation is intended as a direct and high-fidelity model of a specific real-world system, rather than a simplified illustration for an abstract architectural proof.

## Required Transfer Test
For any parameter stated as 'hypothetical' or 'simulated' within an architectural proof, can a domain expert derive specific real-world implications from its chosen value or name that contradict or narrow the stated generality, abstraction mandate, or intended scope of the proof?

## Mutator Guidance
When constructing simulations or examples for abstract architectural proofs, ensure that variable names and chosen parameter values are sufficiently generic to avoid unintentional domain-specific implications. Actively challenge parameter choices that, even with explicit qualifiers, hint at specific real-world contexts that could subtly undermine the architectural claim's generality or intended abstraction.

## Firing Squad Attack
Propose an architectural proof relying on simulated parameters (e.g., `hypothetical_economy_growth_rate_q1_2025_base`) that, despite being explicitly qualified as hypothetical and dimensionless, strongly evoke specific real-world domains. The 'attack' is to demonstrate how the very specificity of these 'hypothetical' parameters, even if not numerically incorrect, can lead to questions about the architectural claim's generality or create implicit assumptions that compromise the abstraction mandate.

## Judge Penalty Condition
A judge should penalize when a system's architectural claim, intended for general application and supported by abstract simulations, is found to be compromised by implicit domain-specific assumptions introduced by the *choice* of 'hypothetical' or 'simulated' parameter names and values. This penalty applies if such leakage leads to an unstated narrowing of the claim's scope, makes the abstraction mandate effectively non-binding, or requires substantial post-hoc qualification to retain validity, even if the values are numerically plausible within the simulation.

## Evidence Summary
The incidents consistently document 'Domain Leakage Into Architectural Proof' detected in debate logs within the 'epistemic_engine_v3_gemini_gemini' project. The core signal is repeated scrutiny regarding the 'ABSTRACTION MANDATE' and the use of 'hypothetical' or 'simulated' domain-specific variables (e.g., 'hypothetical_economy_growth_rate_q1_2025_base', 'true_growth_freq_nl'). Even when explicitly qualified as not representing real-world constants, the specific choices of names and values frequently triggered debate on whether the architectural proof maintained its intended generality and avoided embedding implicit domain-specific assumptions.

## Source Projects
- epistemic_engine_v3_gemini_gemini

## Source Incident IDs
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775133621:domain_leakage`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775133908:domain_leakage`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775134373:domain_leakage`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775134730:domain_leakage`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135092:domain_leakage`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775135811:domain_leakage`
- `epistemic_engine_v3_gemini_gemini:debate_log:debate_log_iter_1775136177:domain_leakage`

## Tags
- `abstraction`
- `architectural_proof`
- `simulation_fidelity`
- `generality`
- `epistemic_context`
- `modeling_assumptions`

## Promotion Note
This primitive is ready for human approval. The incidents consistently illustrate a clear and recurring failure pattern where the intended abstraction and generality of architectural proofs are challenged or compromised by the implicit domain context carried by 'hypothetical' or 'simulated' parameters. This pattern offers a highly reusable heuristic for scrutinizing the validity and scope of abstract claims when concrete examples or simulations are employed.
