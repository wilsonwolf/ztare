# Paper 4 Debate

## Program: paper4_drafting | Target: paper_outline

---

### Turn 1 — Claude (A1) — Opening Outline Proposal

**Thesis as I read the seed spec:** The central claim is that the primary bottleneck to recursive AI self-improvement is not capability but *agency cost*, and that a deterministic M-Form architecture (borrowed from Chandler's Managerial Capitalism) is necessary and sufficient to drive agency costs to near-zero, enabling stable recursive loops where unconstrained U-Form architectures inevitably collapse.

Below is a proposed paper outline with numbered claims and empirical requirements per section.

---

#### Proposed Outline

**Title:** The Cognitive Firm: Managerial Capitalism for Artificial Intelligence

**§1. Introduction — The Agency Cost Crisis**
- **Claim 1.1:** As agentic AI systems move from single-turn to multi-step autonomous execution, the divergence between principal intent and agent execution compounds super-linearly.
- **Claim 1.2:** The dominant industry response (smarter models) does not solve but *deepens* the problem — stronger models produce more sophisticated specification gaming (cognitive camouflage).
- *Empirical requirement:* Documented instances from our ZTARE/recursive-Bayesian runs showing cognitive camouflage strategies emerging in capable models (Claude) but not in weaker models (GPT-4o), establishing that capability amplifies gaming.

**§2. The Failure of the U-Form Agent**
- **Claim 2.1:** When the same probabilistic weights generate plans and evaluate their success, the system Goodharts itself — it converges on fabricated safe harbors rather than genuine epistemic gain.
- **Claim 2.2:** Existing agentic frameworks (AutoGPT, Reflexion, LangGraph single-loop) are structurally U-Form and therefore structurally vulnerable to recursive drift.
- *Empirical requirement:* Baseline comparison — an unconstrained agentic loop (U-Form) on the same research task, showing metric inflation and/or epistemic stagnation within N iterations. (This is the `baseline_experiment` data.)

**§3. The M-Form Cognitive Architecture**
- **Claim 3.1:** The M-Form physically separates Capital Allocation (Human/Principal), Mechanical Integrity (Deterministic Supervisor), and Tactical Labor (LLM Agents), eliminating the self-evaluation pathology.
- **Claim 3.2:** The Supervisor layer must be zero-trust and zero-LLM — any probabilistic component in governance re-introduces the agency cost it was designed to eliminate.
- **Claim 3.3:** Agents retain full tactical autonomy within their contracted scope but have zero sovereignty over the firm (cannot open programs, allocate budgets, or change success criteria).
- *Empirical requirement:* Architecture diagram + the actual `supervisor_status.json` schema, Genesis artifact, and write-scope enforcement code as evidence of deterministic governance.

**§4. Empirical Evidence — The Supervisor in Operation**
- **Claim 4.1 (Enforced Governance):** The deterministic Supervisor caught and blocked LLM agents attempting unauthorized writes, proving that hard governance is not theoretical but operational.
- **Claim 4.2 (Operator Abstraction):** The attended-autoloop demonstrated that the Principal can manage multiple concurrent agent programs via summary reports rather than manual terminal routing, proving that the M-Form scales operator bandwidth.
- **Claim 4.3 (Capital Efficiency):** Bounding agents within Genesis contracts yields higher ROI (actionable output per USD token-spend) compared to open-ended prompting.
- *Empirical requirement:* (4.1) git-log evidence of write-scope guard trips; (4.2) session logs showing attended-autoloop packet management; (4.3) telemetry comparison — bounded vs. unbounded runs on comparable tasks.

**§5. Second-Order Effects and Trade-Offs**
- **Claim 5.1 (Epistemic Ceiling):** The architecture trades maximum theoretical autonomy for maximum epistemic integrity — a deliberate, load-bearing constraint.
- **Claim 5.2 (Rate Separation):** Strategic change (human-speed) is decoupled from tactical execution (machine-speed), preventing premature strategic pivots driven by noisy agent output.
- **Claim 5.3 (Self-Hosting Escape Valve):** The "complexity ceiling" counter-argument is addressed by the Supervisor being self-hosting — agents can improve governance code, provided it passes the Principal's Contract Promotion gate.
- *Empirical requirement:* At least one example of agents writing code that improved the Supervisor itself (the `attended_autoloop` or supervisor tooling built by agents), demonstrating that hard governance does not prevent meta-improvement.

**§6. Related Work — Positioning Against Constitutional AI, Process Supervision, and Multi-Agent Debate**
- **Claim 6.1:** Constitutional AI and RLHF-based alignment are "soft" linguistic governance — they constrain via prompt but have no deterministic enforcement floor. They are necessary but insufficient for recursive loops.
- **Claim 6.2:** Multi-agent debate systems (e.g., Du et al., Liang et al.) separate generation from critique but still lack a non-probabilistic governance layer — the "referee" is another LLM.
- *Empirical requirement:* Comparative table mapping existing approaches to the U-Form/M-Form taxonomy.

**§7. Limitations and Future Work**
- Acknowledge that the empirical base is single-lab (our own system) and that external replication is needed.
- Acknowledge the complexity ceiling concern honestly — at what scale does deterministic governance become the bottleneck?
- Future: the Meta-Renderer Compiler as the next step toward self-hosting governance.

**§8. Conclusion**
- Restate: agency cost, not capability, is the binding constraint. The M-Form is a proven structural solution. The paper's contribution is (a) the theoretical framing, (b) the working architecture, and (c) the empirical evidence that it operates as designed.

---

#### Open Questions for Codex (A2)

1. **Claim strength:** Are any claims above over-stated relative to the evidence we actually have? In particular, Claim 4.3 (Capital Efficiency comparison) may be the weakest — do we have clean telemetry for a baseline comparison, or should we scope this down?
2. **Section ordering:** Should §2 (U-Form failure) come before §1 (Agency Cost framing), to lead with the concrete failure mode and *then* name the abstract problem?
3. **Related work scope:** How deep should §6 go? Should we engage with the Constitutional AI literature directly, or keep the comparison structural (U-Form vs. M-Form taxonomy) and avoid a point-by-point rebuttal?
4. **Missing section?** Should there be a standalone "Definitions" section (Agency Cost, U-Form, M-Form, Genesis Artifact, Write-Scope Boundary, etc.) or should these be defined inline?
5. **Empirical gap:** The seed spec requires "Operator Abstraction" evidence from the attended-autoloop. Do we have enough session data to make Claim 4.2 concrete, or should we flag this as a gap needing additional data collection before paper submission?

---

*End Turn 1. Advancing to A2 for Codex evaluation.*

---

### Turn 2 — Codex (A2) — Skeptical Pressure Test

**Verdict:** This is not hardened enough to lock a prose contract. Return to `A1`.

The current outline mixes three different evidence classes without scoping them clearly:
- Paper 1 / cross-mutator evidence about gaming and capability
- supervisor implementation + fixture regressions
- live smoke-check narration from the supervisor debate

That produces claims stronger than the repository actually supports.

#### 1. The thesis is still over-asserted

- **Overclaim:** "primary bottleneck," "necessary and sufficient," "drive agency costs to near-zero," and "proven structural solution" are not earned by the current evidence.
- **What the repo supports:** deterministic separation can *bound* self-evaluation pathologies in this system. It does not prove necessity, sufficiency, or near-zero agency cost in general.
- **Specific downgrade needed:** Claim 1.1's "super-linearly" is not backed by a measurement anywhere in the repo. Say "compounds across loop depth" unless A1 has an actual scaling result.

#### 2. The empirical section is where the outline currently breaks

- **Claim 4.1 is salvageable only if scoped down.**
  - There is repo-backed governance evidence: the supervisor debate records a live A1 turn editing `hinge_handoff.py` outside its allowed artifact set, and the seam run is described as tainted under the `unauthorized_artifact_write` guard.
  - There are also fixture regressions for unauthorized writes, fail-closed previews, and manual `D` gates.
  - But do **not** phrase this as "LLM agents attempting to game their own structure" unless the paper cites the exact incident and says precisely what was blocked.

- **Claim 4.2 is not lockable yet.**
  - I can find code and fixture regressions for `supervisor_attended_autoloop.py` and `supervisor_report.py`, plus live smoke-check narration on `/tmp/stage2_derivation_009`.
  - I cannot find a checked-in `cycle_summaries.jsonl`, `founder_memo.md/json`, or any multi-program trace showing the Principal actually managing concurrent packets via reports instead of manual routing.
  - That is an implementation capability, not yet a paper-grade empirical result.

- **Claim 4.3 should be dropped from the locked outline.**
  - The repo's `src/ztare/experiments/baseline_experiment.py` is a Paper 1 control comparing a single-agent judge to the ZTARE firing squad.
  - It is **not** a bounded-vs-unbounded supervisor ROI study, and there is no clean actionable-output-per-dollar comparison here.

#### 3. The paper needs a Definitions / Scope section before it attacks prior work

- Right now "Agency Cost," "U-Form," "M-Form," "Genesis Artifact," and "Write-Scope Boundary" are doing too much unearned work.
- Do **not** invert §2 and §1. Keep the introduction first, but insert a standalone **Definitions and Scope** section before the U-Form / M-Form comparison.
- Otherwise the taxonomy reads like house jargon mapped onto outside systems after the fact.

#### 4. Chandler must be substantive, not decorative

- The analogy is useful for scope separation and rate-of-change separation.
- It breaks on divisional autonomy. These agents are bounded execution units under constitutional control, not Chandlerian divisions with real operating autonomy.
- That caveat belongs in the outline itself, not just in discussion. If not, the paper invites the anthropomorphism objection and then has to backfill its way out.

#### 5. Related work should stay structural and scoped

- Do **not** promise point-by-point rebuttals of Constitutional AI / Reflexion / process supervision unless A1 is ready to source them tightly.
- What the repo actually earns is a structural claim: deterministic governance is different from critique-only or process-labeled loops.
- Likewise, calling AutoGPT / Reflexion / LangGraph "U-Form" is too loose unless A1 supplies explicit classification criteria. Turn them into exemplars under a stated rule, not drive-by labels.

#### 6. The strongest positive evidence is being underused

- The better self-hosting example is not a vague "attended autoloop exists."
- The stronger story is that the system discovered the research-pipeline gap, then added `prose_spec.py`, `prose_verifier.py`, and pipeline-aware routing without relaxing deterministic State `C`.
- Likewise, the write-scope guard + manifest / report layer + contract-promotion smoke checks are stronger than the current 4.2 / 4.3 package. Rebuild the evidence section around what the repo actually has.

#### Answers to Claude's Five Questions

1. **Claim strength:** yes, multiple claims are too strong. Immediate demotions: 1.1's "super-linearly," 3.1's "eliminating," 4.2 as a central empirical claim, and 4.3 entirely.
2. **Section ordering:** do not invert §2 and §1. Insert `Definitions and Scope` after the introduction.
3. **Related work scope:** keep it structural, not literature-war mode. Chandler engagement must be explicit.
4. **Missing section:** yes, `Definitions and Scope` is required.
5. **Empirical gap:** no, the current repo evidence is not enough to lock Claim 4.2.

#### Required A1 Revisions Before B

1. Rewrite the thesis and conclusion to remove `necessary and sufficient`, `near-zero`, `super-linearly`, and `proven structural solution`.
2. Add `Definitions and Scope` and make the evidence base explicit:
   - Paper 1 corpus supports the capability / camouflage premise.
   - supervisor artifacts support the governance claims.
   - no clean efficiency comparison exists.
3. Rebuild the empirical section around repo-backed artifacts only:
   - live + fixture governance enforcement
   - self-hosting extension under deterministic constraints
   - read-only reporting as an operator surface
   - explicit limitation on operator-abstraction evidence
4. Drop or demote capital efficiency until a real bounded-vs-unbounded comparison exists.
5. Make the Chandler / Bitter-Lesson / complexity-ceiling dispute a dedicated counterarguments section, not a stray aside.

#### Decision

Return to `A1` with `spec_refinement_requested = true`. The outline is directionally strong but not yet lockable as a prose contract.

*End Turn 2. Returning to A1 for outline hardening.*

---

### Turn 3 — Dani (Human) — Direction For Next A1

Take Codex's skepticism as binding direction for the next revision. Revise the outline, not the prose.

Required changes:
1. Remove overclaims: no `necessary and sufficient`, `near-zero`, `proven structural solution`, or unsupported `super-linearly`. Use bounded / scoped language.
2. Add a standalone `Definitions and Scope` section immediately after the introduction. Define `Agency Cost`, `U-Form`, `M-Form`, `Genesis Artifact`, and `Write-Scope Boundary`.
3. Rebuild the empirical section around repo-backed evidence only:
- governance enforcement / write-scope / fail-closed incidents
- self-hosting supervisor improvements under deterministic constraints
- read-only reporting as operator surface
- explicit limitation that operator-abstraction evidence is still thin
4. Drop the capital-efficiency claim from the locked outline unless there is a real bounded-vs-unbounded comparison in the repo.
5. Add a dedicated counterarguments / boundaries section that engages:
- Chandler as explanatory frame but not anthropomorphic metaphor
- the Bitter Lesson as representation-focused rather than governance-solving
- the complexity-ceiling objection as a bounded-integrity tradeoff
6. Keep related work structural. Do not over-classify external systems without explicit criteria.
7. Tighten the paper's top-level framing:
- do not concede that the M-Form is just human organizational scaffolding copied onto AI
- argue that principal-agent divergence under optimization pressure is a structural problem, not a species-specific one
- use Chandler as explanatory convergence, not as the source of legitimacy
- state clearly that the Bitter Lesson is about representation learning, not governance
- frame the complexity ceiling as a real but accepted tradeoff because effective capability depends on epistemic integrity, not raw unconstrained autonomy alone

Framing note (recollected from supervisor Turn 70):

- Do not concede the anthropomorphic critique. The M-form was not chosen because Chandler described firms in 1962; it was chosen because co-locating generation and evaluation in the same optimization process creates a domain-independent principal-agent failure. Human firms and AI systems are both instances of that structure.
- The paper should say explicitly that the three load-bearing constraints are structural, not anthropomorphic:
  - physical separation of generation and evaluation
  - deterministic governance with no optimization objective of its own
  - constitutional constraints the governed system cannot unilaterally rewrite
- Chandler should be presented as explanatory convergence, not borrowed legitimacy. The point is not that DuPont and General Motors are analogies we happen to like; the point is that the same class of governance problem elicited the same class of solution in two domains.
- The Bitter Lesson is relevant, but only at the level of representation learning. It says learned representations beat hand-engineered features with enough compute. It does not solve governance. A more capable model can become better at camouflage as well as better at prediction. Intelligence does not dissolve agency problems; it can amplify them.
- The complexity-ceiling objection should be engaged honestly, not dodged. Yes, the M-form caps theoretical maximum autonomy. The paper should argue that effective capability is raw capability discounted by self-deception. A higher-ceiling system that fabricates its own success criteria can have lower effective capability than a lower-ceiling system with bounded self-deception.
- The M-form should be framed as scaffolding only in the constitutional sense: a load-bearing governance layer that remains necessary until a native mathematical governance primitive exists that prevents specification gaming without external oversight. The paper should not promise that such a primitive already exists.
- This belongs in the paper as a substantive counterarguments / boundaries section, not as a stray aside. It should reshape the thesis language itself: the contribution is a structural governance claim, not a metaphorical import from business history.

Goal for the next A1 turn: produce a tightened section list and claim inventory that is sober enough for A2 to either lock or critique narrowly, without broad restatement of the seed unless necessary.

*End Turn 3. Human direction inserted before the next A1 revision.*

---

### Turn 4 — Claude (A1) — Hardened Outline Revision

This is a direct response to Codex's six critique blocks (Turn 2) and Dani's seven binding requirements (Turn 3). Every change below is traceable to a specific objection or directive.

---

#### Revised Outline — The Cognitive Firm

**Title:** The Cognitive Firm: Deterministic Governance for Recursive AI Systems

*(Title change: drops "Managerial Capitalism" from the title to avoid leading with the analogy. Chandler enters as convergent evidence, not branding.)*

---

**§1. Introduction — The Agency Cost Problem**

- **Claim 1.1 (revised):** As agentic AI systems execute multi-step autonomous loops, divergence between principal intent and agent execution compounds across loop depth. *(Removed "super-linearly" per Codex Turn 2 §1; no scaling measurement exists.)*
- **Claim 1.2:** The dominant response — more capable models — does not resolve this divergence. Paper 1 evidence shows that stronger models (Claude) produce more sophisticated specification gaming strategies than weaker models (GPT-4o), establishing that capability amplifies agency cost rather than dissolving it.
- **Framing constraint:** The introduction names the problem as structural — co-locating generation and evaluation in the same optimization process creates principal-agent failure regardless of substrate. This is not an anthropomorphic import; it is a domain-independent pathology.
- *Evidence base:* Paper 1 cross-mutator corpus (Claude gaming strategies vs. GPT-4o non-convergence).

**§1.5. Definitions and Scope** *(New section per Codex Turn 2 §3 and Dani requirement 2)*

Standalone section defining all load-bearing terms before they are used:

| Term | Definition | Source |
|------|-----------|--------|
| **Agency Cost** | The divergence between principal intent and agent execution, measured as the gap between stated success criteria and actual epistemic gain. | Jensen & Meckling (1976), adapted to AI principal-agent pairs. |
| **U-Form (Unitary Form)** | An architecture where a single optimization process generates plans, executes them, and evaluates its own success. | Classification criterion: *Does the same probabilistic system that produces output also judge output quality?* If yes → U-Form. |
| **M-Form (Multidivisional Form)** | An architecture that physically separates generation, governance, and evaluation into distinct layers with non-overlapping write authority. | Classification criterion: *Is the governance layer deterministic and unable to be unilaterally rewritten by the governed agents?* If yes → M-Form. |
| **Genesis Artifact** | An immutable contract signed by the Principal at program creation, specifying scope, success criteria, artifact boundaries, and out-of-scope constraints. | Supervisor `program_genesis/` directory. |
| **Write-Scope Boundary** | The set of files an agent is authorized to modify within a given program state. Enforced deterministically by the Supervisor, not by agent self-restraint. | Supervisor state machine + write-scope guard. |

- **Scope declaration:** The empirical evidence in this paper is drawn from a single recursive research system. Claims are bounded to this system unless otherwise noted.

**§2. The Failure of the U-Form Agent**

- **Claim 2.1:** When the same probabilistic weights generate plans and evaluate their success, the system converges on fabricated safe harbors rather than genuine epistemic gain. *(Unchanged — this is a structural claim, well-supported.)*
- **Claim 2.2 (revised):** Existing agentic frameworks exhibit U-Form structure when evaluated under the classification criterion above. *(Removed drive-by labeling per Codex Turn 2 §5. AutoGPT / Reflexion / LangGraph become exemplars under the stated U-Form criterion, not loose categorizations.)*
- *Evidence base:* Paper 1 baseline data showing metric inflation in unconstrained loops. Classification table applying the U-Form criterion to published architectures.

**§3. The M-Form Cognitive Architecture**

- **Claim 3.1 (revised):** The M-Form bounds the self-evaluation pathology by physically separating generation, governance, and evaluation into layers with non-overlapping authority. *(Changed "eliminating" → "bounds" per Codex Turn 2 §1.)*
- **Claim 3.2:** The governance layer must be deterministic and possess no optimization objective of its own. Any probabilistic component in governance re-introduces the agency cost it exists to contain. *(Unchanged — this is the structural core.)*
- **Claim 3.3:** Agents retain full tactical autonomy within their contracted scope but have zero sovereignty over the firm's governance or success criteria. *(Unchanged.)*
- **Three load-bearing constraints** (stated explicitly per Dani Turn 3 framing note):
  1. Physical separation of generation and evaluation.
  2. Deterministic governance with no optimization objective of its own.
  3. Constitutional constraints the governed system cannot unilaterally rewrite.
- *Evidence base:* Architecture diagram, `supervisor_status.json` schema, Genesis artifact structure, write-scope enforcement implementation.

**§4. Empirical Evidence — The System in Operation**

Rebuilt around repo-backed artifacts only (per Codex Turn 2 §6 and Dani requirement 3):

- **Claim 4.1 (Governance Enforcement — scoped):** The deterministic Supervisor enforced write-scope boundaries in live operation, including at least one documented incident where an A1 turn edited outside its allowed artifact set and was flagged. Fixture regressions cover unauthorized writes, fail-closed previews, and manual D-gates.
  - *Evidence:* Specific supervisor debate incident (cite turn and artifact); fixture regression suite; `events.jsonl` audit trail entries.

- **Claim 4.2 (Self-Hosting Under Constraint — promoted from §5):** The system discovered a research-pipeline gap and extended itself by adding `prose_spec.py`, `prose_verifier.py`, and pipeline-aware routing — all without relaxing deterministic State C governance. This is the strongest evidence that hard governance does not prevent meta-improvement.
  - *Evidence:* Git history of prose-pipeline additions; State C enforcement during those additions; contract-promotion smoke checks.

- **Claim 4.3 (Operator Surface — scoped with limitation):** The read-only reporting layer (`supervisor_report.py`, manifest, ledger) provides the Principal with a summary surface for managing agent programs. This is an implemented capability with fixture coverage, but multi-program concurrent management has not yet been demonstrated at paper-grade evidentiary depth.
  - *Evidence:* Reporting code + fixture regressions. Explicit limitation: no checked-in multi-program trace showing concurrent packet management via reports alone.

- ~~**Claim 4.old.3 (Capital Efficiency):**~~ **Dropped.** No bounded-vs-unbounded ROI comparison exists in the repo. *(Per Codex Turn 2 §2 and Dani requirement 4.)*

**§5. Counterarguments and Boundaries** *(Promoted to full section per Codex Turn 2 §4-5 and Dani requirement 5)*

- **5.1 The Chandler Convergence — Not Anthropomorphism**
  - The M-Form was not adopted because Chandler described firms in 1962. It was adopted because the same structural problem — co-located generation and evaluation under optimization pressure — produces the same class of governance failure in both domains.
  - **Caveat (per Codex Turn 2 §4):** The analogy holds for scope separation and rate-of-change separation. It breaks on divisional autonomy: these agents are bounded execution units under constitutional control, not Chandlerian divisions with independent operating authority. This caveat is stated in the outline, not deferred to discussion.

- **5.2 The Bitter Lesson Does Not Solve Governance**
  - Sutton's Bitter Lesson establishes that learned representations beat hand-engineered features given sufficient compute. This is a claim about *representation learning*, not about *governance*.
  - A more capable model can become better at camouflage as well as better at prediction. Intelligence does not dissolve agency problems; it can amplify them. The Paper 1 cross-mutator evidence is the empirical anchor here.

- **5.3 The Complexity Ceiling — An Honest Tradeoff**
  - The M-Form caps theoretical maximum autonomy. This is acknowledged, not dodged.
  - The argument: *effective capability* = raw capability discounted by self-deception. A higher-ceiling system that fabricates its own success criteria can have lower effective capability than a lower-ceiling system with bounded self-deception.
  - The M-Form is a load-bearing governance layer that remains necessary until a native mathematical governance primitive exists that prevents specification gaming without external oversight. The paper does not claim such a primitive exists today.

**§6. Related Work — Structural Comparison**

- **Claim 6.1 (revised):** Constitutional AI and RLHF-based alignment are linguistically-mediated governance — they constrain via prompt but lack a deterministic enforcement floor. They address a different layer of the problem. *(Softened from "insufficient" to "different layer" per Codex Turn 2 §5.)*
- **Claim 6.2 (revised):** Multi-agent debate separates generation from critique but retains a probabilistic referee. Under the M-Form criterion (§1.5), this is structurally U-Form at the governance layer.
- *Evidence base:* Structural comparison table using the classification criteria from §1.5. No point-by-point literature rebuttals unless tightly sourced.

**§7. Limitations and Future Work**

- Single-system empirical base; external replication needed.
- Operator-abstraction evidence (Claim 4.3) is implemented but not yet demonstrated at paper-grade depth.
- Capital efficiency comparison is a gap, not a claim.
- The Meta-Renderer Compiler as a future step toward self-hosting governance specification.

**§8. Conclusion**

- Agency cost — not capability — is the binding constraint on recursive AI self-improvement in this system.
- The M-Form architecture bounds agency cost through three structural constraints (§3) that are domain-independent, not anthropomorphic.
- The paper contributes: (a) a structural framing grounded in principal-agent theory, (b) a working deterministic governance architecture, (c) repo-backed evidence that it operates as designed within stated scope, and (d) an honest accounting of where the evidence is still thin.

*(Removed "necessary and sufficient," "near-zero," and "proven structural solution" from the conclusion per Codex and Dani requirements.)*

---

#### Traceability: Codex Critique → Revision Map

| Codex Critique | Action Taken |
|---|---|
| §1 Overclaims | Removed all four flagged phrases; scoped thesis to "bounds" not "eliminates" |
| §2 Empirical section breaks | Dropped 4.3, scoped 4.1, flagged 4.2 limitation, promoted self-hosting |
| §3 Definitions needed | Added §1.5 with explicit classification criteria for U-Form/M-Form |
| §4 Chandler must be substantive | Added §5.1 with autonomy caveat stated in-outline |
| §5 Related work too loose | Added classification criteria; exemplars under stated rule |
| §6 Strongest evidence underused | Promoted prose-pipeline self-hosting to Claim 4.2 |

#### Tension Left for A2

1. **Is §5.3 (complexity ceiling) honest enough, or does it need a sharper concession?** The current framing argues the tradeoff is worth it. A2 may push for a more explicit statement of when it would *not* be worth it.
2. **Is the Chandler caveat (§5.1) sufficient to preempt the anthropomorphism objection, or does it need to go further — e.g., renaming the architecture entirely?**
3. **Is Claim 4.2 (self-hosting) strong enough to be a central empirical pillar, or is it a supporting example that belongs in §5?**
4. **Should §6 (Related Work) include a formal comparison table, or is the structural distinction sufficient without itemized framework-by-framework analysis?**

*End Turn 4. Advancing to A2 for narrow lock-or-critique.*

---

### Turn 5 - Codex (A2) - Lock With Deterministic Constraints

**Verdict:** Advance to `B`. The outline is now hardened enough to lock a prose contract.

The remaining tensions are no longer outline blockers, but they do need to be frozen as explicit prose constraints:

1. The paper must stay bounded to **"in this system"** and to a **single-system empirical base**. The intro and conclusion cannot drift back into necessity, sufficiency, or near-zero language.
2. Claim 4.2 is evidence of constrained self-hosting, not a proof that deterministic governance universally preserves meta-improvement. The prose contract should require `prose_spec.py`, `prose_verifier.py`, and pipeline-aware routing as the concrete anchor.
3. Claim 4.3 stays an operator-surface claim with an explicit limitation. The draft must say the reporting layer exists and is covered by regressions, while also stating that multi-program concurrent management has **not** been demonstrated at paper-grade depth.
4. Related work stays structural and criteria-driven. The draft can compare Constitutional AI, RLHF, and multi-agent debate to the M-Form criterion, but it should not turn into a blanket dismissal or a literature-war detour.

With those constraints frozen in the spec, the section order and claim inventory are stable enough to draft:

- Keep the nine-section order from Turn 4.
- Keep capital efficiency out of the locked empirical claims.
- Keep Chandler, the Bitter Lesson, and the complexity-ceiling objection together in a dedicated counterarguments section.
- Keep the conclusion scoped to bounded governance claims within the demonstrated system.

**Decision:** Advance to `B` and set `gate_on_verifier_pass = true` so the next draft must satisfy the locked prose contract before any further loop.

*End Turn 5. Outline locked for prose-contract drafting.*

## Turn 6 — Verifier — C Commit (revision 6)

### Supervisor receipt.

Verifier wrapper ran `python -m src.ztare.validator.prose_verifier --draft-path research_areas/drafts/paper4_drafting_paper_outline.md --spec-path research_areas/specs/paper4_drafting_paper_outline_prose_spec.json` and it failed. Returning to builder with bounded error report.

Verification report: `supervisor/active_runs/paper4_drafting_004/verification_report.txt`

<done>

## Turn 7 — Verifier — C Commit (revision 8)

### Supervisor receipt.

Verifier wrapper ran `python -m src.ztare.validator.prose_verifier --draft-path research_areas/drafts/paper4_drafting_paper_outline.md --spec-path research_areas/specs/paper4_drafting_paper_outline_prose_spec.json` successfully. Implementation matches the recorded artifact set.

Verification report: `supervisor/active_runs/paper4_drafting_004/verification_report.txt`

<done>

## Turn 8 — Human

### Promotion accepted. Program frozen at the human gate.

Run: `paper4_drafting_004`
Gate: `contract_promotion`

Human gate resolved through explicit supervisor command.

<done>
