## 6 Related Work and Limitations

### Constitutional AI and RLHF

Constitutional AI and RLHF constrain behavior through prompts, reward shaping, and learned preference models. They operate on the output surface. The M-Form claim is about a different layer: the enforcement floor. These approaches are therefore not direct substitutes for hard-gated governance. They are complements that may improve model behavior inside a system whose ultimate constraints are still enforced elsewhere.

### Multi-Agent Debate and Process Supervision

Multi-agent debate separates roles conversationally, but the decisive referee often remains probabilistic. Process supervision improves evaluation granularity, but the scoring model is still learned. Both approaches can improve signal quality. Neither by itself guarantees a deterministic enforcement floor. That distinction should be the criterion for comparison.

### Limitations

This paper rests on one system. That is the central limitation and it should stay in the foreground. The manuscript should also admit that prose quality and operator overhead remain weak points in the current implementation. The architecture has been proven more strongly than the user experience.

### Future Work

The immediate future-work agenda is straightforward: replication on other systems, stronger capital-efficiency measurement, and a cleaner abstraction layer for the principal. A more ambitious line is governance self-hosting: agents proposing changes to the governance contract while remaining subject to a deterministic proof that the revised contract is not weaker on the dimensions that matter.
