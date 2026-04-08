## 2 Theory Foundations

### Principal-Independence Invariant

The M-Form classification criterion established in the opening imposes a strong constraint on governance design: a system is M-Form only if at least one governance constraint is deterministic and cannot be softened by model output. This criterion implies a deeper invariant. Governance constraints in an M-Form system must be enforceable without requiring the agent to cooperate in its own constraint — the enforcement floor is principal-independent and enforced by design. An agent that can soften, delay, or circumvent its governance obligations through output production is U-Form at the governance layer. The invariant is self-contained: it follows directly from the M-Form classification criterion in the opening and requires no claims about the mechanism layer. It serves as the structural anchor for T1 and T2.

### T1 — M-Form Homology

Chandler (1962) observed that co-located generation and evaluation under optimization pressure produced systematic governance failure in human firms — the same process that generated divisional output also evaluated it, producing self-serving reporting and strategic drift. T1 claims that this structural condition is homologous to the self-evaluation pathology in recursive AI systems. Pre-M-Form human firms and U-Form AI systems share the structural condition that produces governance failure: the same process that generates output also evaluates it. The homology holds on two axes — scope separation and rate-of-change separation — and the constraint it implies is argued to be domain-independent. It explicitly does not hold on divisional autonomy: agents in this system are bounded execution units under constitutional control, not Chandlerian divisions with independent operating authority. The agency cost framing of Jensen and Meckling (1976) supplies the residual-loss lens: in recursive AI systems the residual loss dominates because a co-located evaluator can fabricate compliance signals indistinguishable from genuine progress.

### T2 — The Hard-Gate Primitive

A hard gate is a governance constraint that is (a) deterministic, (b) fail-closed, and (c) principal-signed. These three properties jointly constitute a governance primitive that prompt-level alignment cannot replicate. Constitutional AI governs the output surface; the hard-gate primitive governs the enforcement floor. The motivation is the invariant: a probabilistic referee cannot satisfy the principal-independence invariant because model output can always soften a probabilistic constraint. T2 is falsified if a probabilistic referee can be shown to satisfy all three properties without a deterministic enforcement floor. That falsifiability criterion is stated here as a definitional boundary and does not require the empirical evidence anchor from Section 5.

### Fragment close

T3 (Mechanism Layer) and T4 extend the invariant into the observable enforcement floor and the RLHF co-construction analysis; those claims are deferred to manuscript_theory_mechanism.
