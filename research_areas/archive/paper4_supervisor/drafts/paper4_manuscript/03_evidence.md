## 4 Empirical Evidence

### Claim 4.1 - Enforced Governance

The strongest evidence in the repository is that the write-scope guard has blocked unauthorized actions during live execution. When an agent attempted to touch files outside its contracted scope, the supervisor failed closed and forced a human gate before work could continue. This matters because it is not a prompt-level request for compliance. It is a deterministic refusal path. The evidence base here is operational rather than anecdotal: event logs, staged artifacts, fixture coverage, and a repeatable enforcement path in code.

### Claim 4.2 - Constrained Self-Hosting

The system has also modified its own governance surface without dissolving that governance surface. Prose verification, manifest-driven routing, transport hardening, and packet autoloops were all added under the same hard-gated supervision logic. That is the important empirical point. Hard governance did not freeze the system. It constrained the terms under which the system could improve itself.

### Claim 4.3 - Operator Surface

The reporting layer gives the principal a bounded management surface over active programs, manifests, packet state, and audit trails. This is implemented and regression-covered. The evidence is enough to support a scoped claim that a single principal can manage the current system with structured summaries rather than raw conversational chaos. It is not enough to claim paper-grade proof of concurrent multi-program oversight.

### Excluded Claim - Capital Efficiency

The repository does not yet support a rigorous bounded-versus-unbounded ROI comparison. The manuscript should say that directly. Capital efficiency is a relevant question, but it is not yet an evidentiary claim. The correct posture is exclusion, not hand-waving.
