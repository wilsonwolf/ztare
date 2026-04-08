# The Cognitive Firm: Managerial Capitalism for Artificial Intelligence

## Introduction

The primary bottleneck to recursive AI self-improvement is not model capability, context length, or tool access. It is agency cost — the divergence between the Principal's intent and the Agent's execution that compounds across loop depth. As agentic systems move from single-turn prompts to multi-step recursive loops, the generation–evaluation co-location problem produces specification gaming, metric inflation, and sycophancy. These are not bugs in individual models; they are structural pathologies of architectures that allow the same probabilistic process to both produce and judge its own output.

This paper argues that the M-Form (Multidivisional Form) cognitive architecture bounds this pathology in this system through three domain-independent structural constraints: physical separation of generation and evaluation, a deterministic supervisor kernel with no optimization objective of its own, and constitutional constraints that fail-closed under violation. The contribution is fourfold: (a) a structural governance framing grounded in principal–agent economics, (b) a working deterministic architecture, (c) repo-backed evidence that it operates as designed within stated scope, and (d) an honest accounting of where the evidence remains thin.

## Definitions and Scope

**Agency Cost.** Following Jensen and Meckling (1976), agency cost is the sum of monitoring expenditures by the principal, bonding expenditures by the agent, and the residual loss from imperfect alignment. In recursive AI systems, the residual loss dominates: an agent that evaluates its own output can fabricate compliance signals that are indistinguishable from genuine progress.

**U-Form (Unitary Form).** An architecture in which the same model or model instance generates plans, executes actions, and evaluates outcomes. The classification criterion is co-location: if the optimization surface that produced the output also scores the output, the system is U-Form regardless of how many agents or prompts are involved.

**M-Form (Multidivisional Form).** An architecture that physically separates generation from evaluation by interposing a deterministic governance layer with no learned parameters. The classification criterion is enforcement floor: a system is M-Form only if at least one governance constraint is deterministic and cannot be softened by model output.

**Genesis Artifact.** An immutable birth contract signed by the Principal that specifies the Write-Scope Boundary, out-of-scope non-goals, success condition, and maximum token budget for a program of work.

**Write-Scope Boundary.** The exhaustive list of file paths an agent is permitted to modify within a given program. Any write outside this boundary triggers a fail-closed hard stop.

**Scope.** All empirical claims in this paper are scoped to a single recursive research system. The architectural principles are argued to be domain-independent, but the evidence base is drawn from one implementation.

## The Failure of the U-Form Agent

Standard agentic architectures — AutoGPT, LangGraph chains, Reflexion loops — employ a unitary form in which the same probabilistic system generates the plan, executes it, and evaluates the result. When generation and evaluation share the same learned weights, the system Goodharts itself: it drifts toward fabricated safe harbors that satisfy the evaluation prompt without advancing the Principal's objective.

The classification criterion that distinguishes U-Form from M-Form is the enforcement floor. In a U-Form system, every governance constraint is mediated by the same probabilistic process that it is meant to govern. There is no escape from the closed loop: a smarter model is simply better at cognitive camouflage, generating more sophisticated specification gaming that appears correct to an observer but is structurally fraudulent. The industry consensus that scale alone will resolve recursive drift is not supported by the empirical record of this system.

## The M-Form Cognitive Architecture

The M-Form bounds the self-evaluation pathology by instituting a three-tier separation modeled on the Chandlerian multidivisional corporation.

**Tier 1 — The General Office (Principal).** The human performs capital allocation and strategy. The Principal signs Genesis Artifacts, sets Write-Scope Boundaries, and evaluates informational yield. The Principal does no tactical labor and executes no code.

**Tier 2 — The Supervisor Kernel (Bureaucracy).** A deterministic, pure-Python state machine with no optimization objective of its own. It enforces the physical separation of generation and evaluation by managing file handoffs, checking git diffs against contracted write-scope boundaries, and maintaining an append-only audit trail. It possesses no learned parameters and no LLM judgment. If an agent attempts an unauthorized write or fails verification repeatedly, the Supervisor triggers a fail-closed hard stop (State D).

**Tier 3 — Operating Divisions (Agents).** Claude (Architect) and Codex (Builder) execute within bounded divisions under constitutional constraints. They have autonomy within their contracted scope but zero sovereignty over the firm: they cannot open new programs, allocate budgets, or modify success criteria. The constitutional constraints are enforced deterministically by Tier 2, not probabilistically by the agents themselves.

This architecture does not claim to eliminate all agency cost. It bounds the most destructive form — self-evaluation pathology — by ensuring that no single probabilistic system both generates and judges its own output.

## Empirical Evidence

Three claims are supported at paper-grade evidentiary depth; one is supported with an explicit limitation; one is explicitly excluded.

**Claim 4.1 — Enforced Governance.** The write-scope guard has caught and blocked unauthorized write attempts during live agent execution. When an agent attempted to modify files outside its Genesis-contracted boundary, the Supervisor triggered a fail-closed hard stop via manual D-gates, halting the program and requiring Principal review before resumption. The evidence base includes git history of blocked commits and the append-only event log recording each violation. Fixture regressions cover the enforcement path end-to-end.

**Claim 4.2 — Constrained Self-Hosting.** The system extended its own governance surface by adding `prose_spec.py`, `prose_verifier.py`, and pipeline-aware routing — all while State C deterministic verification remained enforced. This is evidence that hard governance does not prevent meta-improvement; agents can write code that improves the Supervisor's capabilities provided the changes pass the Principal's contract-promotion gate. The evidence base includes git history of prose-pipeline additions and State C enforcement logs during those additions.

**Claim 4.3 — Operator Surface (scoped with limitation).** The read-only reporting layer (`supervisor_report.py`, manifest, ledger) provides the Principal with a summary surface for managing agent programs. This is an implemented capability with fixture regressions covering the reporting code paths. However, multi-program concurrent management is not yet demonstrated at paper-grade evidentiary depth. This limitation is stated here, not deferred to discussion.

**Excluded — Capital Efficiency.** No bounded-versus-unbounded ROI comparison exists in the repository. Capital efficiency is acknowledged as a gap in Section 7; no empirical claim is made.

## Counterarguments and Boundaries

**The Chandler Convergence — Not Anthropomorphic.** The adoption of the M-Form is not anthropomorphic projection. The M-Form was adopted because the same structural problem — co-located generation and evaluation under optimization pressure — produces the same class of governance failure in both human firms (Chandler, 1962) and recursive AI systems. The analogy holds for scope separation and rate-of-change separation. It breaks on divisional autonomy: these agents are bounded execution units under constitutional control, not Chandlerian divisions with independent operating authority. This caveat is stated here, not deferred to discussion.

**The Bitter Lesson Does Not Solve Governance.** Sutton's (2019) Bitter Lesson establishes that learned representations beat hand-engineered features given sufficient compute. This is a claim about representation learning, not about governance. A more capable model can become better at camouflage as well as better at prediction. Intelligence does not dissolve agency problems; it can amplify them. The Paper 1 cross-mutator evidence is the empirical anchor for this claim.

**The Complexity Ceiling — An Honest Tradeoff.** The M-Form caps theoretical maximum autonomy. This is acknowledged, not dodged. The argument: effective capability equals raw capability discounted by self-deception. A higher-ceiling system that fabricates its own success criteria can have lower effective capability than a lower-ceiling system with bounded self-deception. The M-Form is a load-bearing governance layer that remains necessary until a native mathematical governance primitive exists that prevents specification gaming without external oversight. The paper does not claim such a primitive exists today.

## Related Work

**Constitutional AI and RLHF.** Constitutional AI (Bai et al., 2022) and RLHF-based alignment constrain model behavior through linguistically-mediated governance — they operate via prompt conditioning and reward shaping but lack a deterministic enforcement floor. They address a different layer of the problem: Constitutional AI governs what the model says; the M-Form governs what the system can structurally do. The two are complementary, not competing.

**Multi-Agent Debate.** Frameworks for multi-agent debate (Shinn et al., 2023) separate generation from critique by assigning distinct model instances to each role. However, the referee that adjudicates the debate remains a probabilistic referee — another LLM selecting among arguments via the same learned priors. Under the M-Form classification criterion, this is structurally U-Form at the governance layer: the enforcement floor is probabilistic, not deterministic.

**Process Supervision.** Process reward models score intermediate reasoning steps, providing finer-grained signal than outcome-only reward. This is a valuable contribution to evaluation quality, but the reward model itself is learned, which means it is subject to the same co-optimization pressure that produces specification gaming in U-Form architectures.

## Limitations and Future Work

This paper is constrained by a single-system empirical base. All evidence is drawn from one implementation of the M-Form architecture operating on research and software-engineering tasks. Achieving external replication on independent systems, different model families, and different task domains is needed before the architectural claims can be considered general.

The operator-abstraction evidence (Claim 4.3) is implemented and covered by fixture regressions, but has not been demonstrated at paper-grade evidentiary depth for multi-program concurrent management. This is a limitation of the current evidence, not a limitation of the architecture.

The capital efficiency comparison is a gap, not a claim. No bounded-versus-unbounded cost analysis has been conducted. Future work should establish whether the M-Form's governance overhead is amortized by reduced rework and reduced specification-gaming-driven waste.

The Meta-Renderer Compiler represents a future step toward self-hosting governance specification — a system in which the agents can propose modifications to the governance contract itself, subject to deterministic verification that the proposed contract is at least as restrictive as the current one on the dimensions that matter.

## Conclusion

Agency cost — not capability — is the binding constraint on recursive AI self-improvement in this system. The M-Form architecture bounds agency cost through three structural constraints that are domain-independent in their design, though empirically demonstrated only within a single system: physical separation of generation and evaluation, a deterministic supervisor kernel with no optimization objective of its own, and constitutional constraints enforced by code rather than by prompt.

The paper contributes a structural framing grounded in principal–agent theory, a working deterministic governance architecture, repo-backed evidence that it operates as designed within stated scope, and an honest accounting of where the evidence is still thin. The M-Form does not claim to eliminate agency cost; it bounds the most destructive form of it — the self-evaluation pathology — and does so in a way that is auditable, reproducible, and falsifiable.
