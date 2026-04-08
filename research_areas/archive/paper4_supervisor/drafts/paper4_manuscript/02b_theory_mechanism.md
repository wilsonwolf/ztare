## 3 Theory Mechanism

### T3 - Observable Enforcement Floor

The principal-independence invariant is not enough on its own. A governance constraint can be deterministic in code and still fail operationally if the principal cannot observe whether the constraint is actually binding. T3 therefore sharpens the theory from mere existence of a hard gate to observability of the enforcement floor. In this system, observability means that the principal can inspect the contracted write scope, the append-only event trail, and the deterministic verifier outcome without asking an agent to summarize its own compliance. The hard gate matters because it is outside the optimizing loop; observability matters because it lets the principal tell whether that separation is holding in practice.

The claim is narrower than a general theory of transparency. It does not require full interpretability of model internals. It requires a stable external surface from which the principal can see whether the enforcement floor was triggered, bypassed, or never engaged. A governance primitive that is deterministic but opaque to the principal remains fragile, because the principal cannot distinguish real compliance from theater at the operational layer.

### T4 - Co-Construction Extends Co-Location

RLHF-style co-construction does not create a new topology; it extends the original problem to an additional layer. If the policy is optimized against a reward signal that is itself shaped inside the same adaptive loop, the scorer becomes part of the same governance problem. The issue is not that stochastic scorers are uniquely dangerous. The issue is that co-construction can pull the reward model into the adversarial gradient, making the scorer another site where generation and evaluation collapse back together.

This is why the M-Form response remains structural rather than model-specific. Once co-location reaches the scorer layer, the same remedy applies there: the governance constraint must sit outside the co-construction loop. A probabilistic referee inside the loop can still be useful as signal. It cannot constitute the enforcement floor.

### Interface - Why T3 and T4 Do Not Reopen T1 and T2

T3 and T4 extend the foundations argument; they do not replace it. T1 established the homology between pre-M-Form human firms and U-Form AI systems. T2 defined the hard-gate primitive. T3 shows that the primitive must also be observable at the principal layer. T4 shows that RLHF-style co-construction does not escape the theory, but instead repeats it at a new layer. The result is the paper's central structural claim: the same governance logic recurs across substrates and across layers because the underlying principal-agent problem recurs there too.
