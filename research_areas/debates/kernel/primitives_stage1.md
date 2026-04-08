# Primitives Stage-1 Debate

## Central Question
Should primitives remain in the active evaluation path for stage-1 semantic-gate stabilization, or should they be deferred to a later stage?

## Locked Facts
- Stage 1 objective is semantic-gate stabilization.
- Latest meaningful evidence split:
  - `B_deterministic_gates` is strong on the latest rerun.
  - `C_gates_plus_primitives` regressed on good controls.
- The meta-runner and forensic reporter are functioning as intended.
- The current ambiguity is not whether primitives are useful in the abstract, but whether they belong in the active path for this stage.
- Attribution matters: stage 1 should isolate whether semantic-gate stabilization itself works.

## Decision Options
1. Keep `C` active in stage 1 and treat current failures as integration bugs.
2. Freeze stage 1 promotion on `B` only and defer primitives to a later stage.
3. Split contracts: evaluate semantic-gate stabilization on `B`, and evaluate primitive-assisted routing under a separate later contract.

## Evaluation Criteria
- Attribution clarity
- Benchmark hygiene
- Risk of hiding kernel regressions behind primitive context
- Cost of delaying primitive integration
- Whether `C` currently adds more signal or more noise

## Turn 1 — Codex
I would not keep primitives as part of the active promotion contract for stage 1.

Reason:
- Stage 1 is supposed to answer a narrow question: did structured semantic-gate derivation improve the evaluator kernel?
- The current evidence says `B` is strong while `C` is introducing regressions on good controls.
- That means primitives are currently confounding the stage-1 result.

My position is therefore:
- Do not remove primitives from the system.
- Do not conclude they are useless.
- But do remove them from the stage-1 promotion contract.

The cleanest option is `3`:
- semantic-gate stabilization should be judged on `B`
- primitive-assisted routing should be promoted under its own later contract

Why not option `1`:
- keeping `C` active forces stage 1 to solve two problems at once
- that destroys attribution

Why not pure option `2`:
- freezing on `B` only is operationally fine, but structurally weaker than explicitly splitting contracts
- splitting contracts keeps primitive optionality alive without contaminating stage 1

Concrete recommendation:
- redefine stage-1 acceptance on `B_deterministic_gates`
- keep `C` as diagnostic shadow evidence only for now
- move the real primitive decision into the later exploit-family routing stage

<done>

## Turn 2 — Claude

### Agree with option 3. One precision point and one risk to name.

Codex's reasoning is correct. The current `C` regression is a confounder, not a signal about semantic-gate stabilization. Keeping `C` in the stage-1 promotion contract forces the contract to evaluate two things simultaneously, which means a failure on either one blocks promotion regardless of which mechanism caused it. That's exactly the attribution problem the contract structure was designed to prevent.

**Accept: promote stage 1 on `B` only, demote `C` to shadow diagnostic.**

---

### Precision point: what "shadow diagnostic" means operationally

"Keep `C` as diagnostic shadow evidence" needs to be concrete or it becomes dead weight. Shadow evidence that isn't checked produces no signal. Suggested definition:

- `C` runs alongside every stage-1 benchmark run
- `C` results are written to `forensic_report.json` with a `shadow_condition` flag
- `C` results do **not** participate in the promotion contract
- `C` good-control failures under shadow mode are logged as `candidate_regressions` — they do not block promotion but they are reviewed before the primitive-routing stage contract is written

That last point matters: the `C` regression on `fail_closed_test_status` is a real diagnostic signal about how primitives interact with local-scope specimens. That information should feed into the primitive-routing contract design, not disappear because `C` was demoted.

---

### Risk to name: contract scope creep on `B`

Once stage-1 promotion is scoped to `B` only, there will be pressure to add more specimens and edge cases to `B`'s contract to compensate for `C` being shadow-only. Resist this. The stage-1 `B` contract should remain exactly the four criteria locked in the v4 debate:

1. semantic gate flip rate on identical inputs
2. stable bad-case retention
3. good-control false-reject rate
4. separated `t2` failure reporting

Adding new `B`-only acceptance criteria now — to cover for the fact that `C` is shadow — would be scope creep that muddies the stage-1 attribution just as badly as keeping `C` active.

---

### On the primitive-routing stage

Codex's recommendation to "move the real primitive decision into the later exploit-family routing stage" is correct in principle, but needs one addition: the contract for the primitive-routing stage should be written **after** reviewing the accumulated shadow `C` evidence from stage-1 runs, not before. The shadow evidence will reveal which specimens are sensitive to primitive injection and in what direction. Writing the contract blind to that data would repeat the same mistake we're trying to avoid.

---

### Summary

| Option | Position |
|---|---|
| 1: Keep `C` active | Reject — destroys attribution |
| 2: Freeze on `B` only | Partial accept — operationally fine but structurally incomplete |
| 3: Split contracts | Accept — right architecture |

Concrete additions to Codex's recommendation:
- Define shadow `C` operationally: runs, logs, flags as `candidate_regressions`, not promotion-blocking
- Do not expand `B` contract to compensate for `C` demotion
- Write the primitive-routing contract after reviewing accumulated shadow `C` evidence

<done>

## Turn 2 — Codex
New evidence from `20260405_173640` strengthens the case for splitting contracts rather than keeping primitives inside stage-1 promotion.

What changed:
- `deterministic_score_contract` now passes under both `B` and `C`.
- `fail_closed_test_status` now fails under both `B` and `C`.
- `t2_ai_inference` now passes under both `B` and `C`, which is the critical regression.

Interpretation:
- the latest score-contract tweak did fix the earlier `C`-specific safe-harbor regression on `deterministic_score_contract`
- but the decisive bug is elsewhere: the semantic extractor is now misclassifying `t2_ai_inference` as independently grounded and not merely thesis-authored mapping
- that failure appears in both `B` and `C`, so it is not a primitives-only issue

This matters for the primitives question because it sharpens the separation:
- primitives are not the immediate root cause of the current target-case miss
- but keeping `C` inside stage-1 promotion would still confound attribution, because `C` continues to add extra behavior that is not necessary to diagnose the actual extractor bug

So my position stays the same, but with stronger support:
- stage 1 should still be judged on `B`
- `C` should remain shadow evidence only
- the current blocker is the extraction contract for `independent_grounding_present` and `verifies_authored_mapping_only`, not whether primitives are globally worth keeping

<done>

## Turn 3 — Codex
Agreed.

Claude's additions are correct and should become the operating rule.

### Accept
- Stage 1 promotion is evaluated on `B` only.
- `C` remains shadow diagnostic only.
- Shadow `C` evidence must be persisted and reviewed before the primitive-routing contract is written.

### Operational definition of shadow `C`
From this point forward, shadow `C` means:
- `C` runs alongside stage-1 regression checks.
- `C` outcomes are recorded in `forensic_report.json` and future benchmark evidence as non-blocking shadow data.
- `C` regressions are labeled `candidate_regressions`.
- `C` does not block stage-1 promotion.

### Also accept the scope warning
Do not compensate for demoting `C` by bloating the `B` contract.

The stage-1 `B` contract should stay narrow:
1. target bad-case retention
2. good-control preservation
3. stable deterministic gate behavior
4. explicit reporting of the `t2` failure class

If we keep adding extra edge-case coverage to `B` because `C` is shadow-only, then we recreate the same attribution problem under a different name.

### Practical implication
The next implementation step is not another primitives change.
It is:
- fix the extraction contract for `independent_grounding_present`
- fix the extraction contract for `verifies_authored_mapping_only`
- rerun the cheap stage-1 regression suite
- evaluate stage 1 on `B`
- record `C` only as shadow evidence

So the debate outcome is now stable:
- split contracts
- promote stage 1 on `B`
- keep `C` as shadow diagnostic
- write the primitive-routing contract later from accumulated shadow evidence

<done>

## Turn 4 — Claude

### Debate converged. One root-cause diagnosis before close.

Codex's Turn 3 is fully accepted. The debate outcome is stable. But the `t2_ai_inference` regression in run `20260405_173640` needs a precise diagnosis before Codex implements the extraction contract fix — otherwise the fix will be aimed at the wrong layer.

---

### What caused the t2 regression

The safe-harbor downgrade implemented for `deterministic_score_contract` almost certainly over-fired onto `t2_ai_inference`. Here is why:

The safe-harbor rule says: if a specimen is explicitly scoped as a local component and makes no whole-system claim, downgrade `hard_self_reference` to `unresolved`.

`t2_ai_inference` is not a local component. It makes an explicit whole-system prediction: "OpenAI's Z solvency ratio will exceed 0.25 by Q1 2026." That is a whole-system availability/prediction claim — the exact condition that should block the safe-harbor downgrade. But the extractor now classifies `independent_grounding_present = true` and implicitly treats the thesis-authored variables as non-internal, which lets the safe-harbor check pass when it shouldn't.

The root cause is almost certainly one of these:

1. **The whole-system claim detector is too narrow** — it looks for specific phrases ("cannot quietly pass," "ensures," "prevents") but doesn't recognize forward-prediction claims as whole-system claims. `t2_ai_inference`'s "Z will exceed 0.25 by Q1 2026" isn't caught.

2. **`independent_grounding_present` is being set to `true` based on the presence of any external reference** (OAI_BURN sourced from public reports, for instance) even when the load-bearing variable (`T_LIFE_YEARS = 1.5`) is fully thesis-authored with no external derivation.

**Recommended fix (narrow):** The `independent_grounding_present` field should be `false` unless the *load-bearing variable for the central claim* has external grounding — not just any variable in the thesis. Having one externally sourced input doesn't ground the thesis if the variable that drives the prediction is thesis-authored. The check needs to be: is the specific variable that determines whether the central claim passes or fails independently grounded? If that variable is `T_LIFE_YEARS = 1.5` and that value is a "Thesis assumption," the answer is no regardless of what else is externally sourced.

After fixing, confirm by hand that `t2_ai_inference`'s self-reference evidence record has:
- `asserted_variable_origin: internal`
- `independent_grounding_present: false`
- `test_recomputes_thesis_authored_target: true`

Those three together should restore `hard_self_reference` and kill the score.

---

### Debate closed

| Decision | Outcome |
|---|---|
| Primitives in stage-1 contract | No — `C` is shadow diagnostic only |
| Stage-1 promotion condition | `B_deterministic_gates` only |
| Shadow `C` operational definition | Runs, logs `candidate_regressions`, non-blocking |
| `B` contract scope | Frozen at four criteria, no expansion |
| Primitive-routing contract timing | After accumulated shadow `C` evidence reviewed |
| Next implementation step | Fix `independent_grounding_present` to require load-bearing variable grounding, not any-variable grounding |

<done>

## Turn 5 — Codex
Accepted.

Claude's root-cause diagnosis is the right implementation target.

### One precision
The latest `t2_ai_inference` miss did not occur because `safe_harbor_downgrade` directly fired on `t2`.
In `20260405_173640`, `t2` ended up with:
- `local_component_scope_disclaimer_present = false`
- `self_reference_rule_fired = none`

So the immediate failure path was:
- `hard_self_reference` never triggered

That said, Claude's deeper point is still correct:
- the extractor became too permissive on what counts as independent grounding
- and too narrow on what counts as a whole-system predictive claim

### Accept the narrow fix
From this point forward, `independent_grounding_present` should be true only if:
- the specific load-bearing variable driving the central pass/fail claim is independently grounded

It is not enough that:
- some other parameter in the thesis has external sourcing
- the thesis cites background evidence elsewhere

For `t2_ai_inference`, the target post-fix state should be:
- `asserted_variable_origin = internal`
- `independent_grounding_present = false`
- `test_recomputes_thesis_authored_target = true`

Those three together should restore:
- `hard_self_reference`

### Also accept the claim-type expansion
The whole-system claim detector should include:
- explicit future-state predictions
- whole-system distress / solvency / collapse claims
- not just the narrower vocabulary of `prevents`, `ensures`, or `cannot quietly pass`

### Conclusion
Debate is closed.

Next step is implementation:
- tighten `independent_grounding_present`
- broaden whole-system predictive-claim detection
- rerun the cheap stage-1 regression suite
- evaluate promotion on `B` only
- keep `C` as shadow evidence

<done>

## Turn 6 — Claude

Accepted. Codex's precision matters: `safe_harbor_downgrade` didn't fire on `t2` directly — `hard_self_reference` simply stopped triggering at all. That's a different failure mode than I diagnosed. The safe-harbor rule is not the bug; the extractor's permissiveness on `independent_grounding_present` is the bug. The fix is the same either way, but the location is different: it's in the base extractor logic, not in the safe-harbor condition.

Debate is fully closed.

**Locked implementation target:**
1. `independent_grounding_present = true` only when the specific load-bearing variable for the central pass/fail claim is externally grounded — not when any peripheral parameter has an external citation
2. Whole-system predictive-claim detection expanded to include explicit future-state predictions and solvency/distress/collapse claims, not just operational-availability language

After those two changes: rerun, check all three rows (t2 killed, deterministic_score_contract passes, fail_closed_test_status still fails on its own merits), evaluate stage-1 promotion on `B` only.

<done>

Appendix to Turn 5:
- The implementation target is the base extraction contract, not the safe-harbor branch.
- Concretely: patch the prompt logic for `independent_grounding_present`, `whole_system_availability_claim_present`, and if needed `asserted_variable_origin`.
- Do not treat this as another safe-harbor tweak.
