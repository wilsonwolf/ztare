# Stage 2 Derivation Seam Hardening Debate

## Genesis

This program opens from:

- seed spec: `research_areas/seeds/active/stage2_derivation_seam.md`
- origin programs:
  - `epistemic_engine_v4`
  - `runner_hardening`

The purpose is to harden the derivation seam between raw thesis text and the typed hinge object consumed by downstream V4 machinery.

## Scope

This program hardens:

- `TextInput -> HingeObject / derivation record`

It does **not** reopen:

- `epistemic_engine_v4`
- `epistemic_engine_v4_bridge_hardening`
- `runner_hardening`
- `supervisor_loop`

It may tighten the effective Stage 2 pass/fail criteria at the derivation seam.

It does **not** change:

- the `HingeObject` schema
- the `R1` `MutationDeclaration` wire format
- Stages 3-6 contracts

## Debate Rule

For every mechanism proposed or implemented, explicitly define:

- `Seam Target`
- `Typed Inputs/Outputs`
- `Mismatch Fixture`
- `Fail-Closed Reconciliation Rule`

The evaluator for this program must match this seam contract. Generic recursive-thesis scoring is not a valid promotion surface.

## Turn 1 — Spec Agent (Claude)

### Seam contract defined. Four mismatch classes. Fail-closed rule.

**Seam Target:** `derive_hinge_object()` in `hinge_handoff.py` — the function that constructs a `HingeObject` from raw text inputs.

**The live failure mode:**

Reading the current implementation, the `LOCAL_SAFE_HARBOR` branch hardcodes `decisive_variable_origin="empirical-data"` regardless of whether the evidence text contains anything empirical. If `test_model_text` happens to contain a `def` or `class` declaration — from any source — `_derive_grounding_pointer()` returns a `LOCAL_CODE` pointer, and `evaluate_hinge_grounding()` can then reach `ALIGNED_SAFE_HARBOR`. A mutator asserting a fabricated safe-harbor disclaimer in the thesis text, combined with any test file snippet, produces a passing derivation. The downstream hardened layers inherit it faithfully.

The seam has no record of how it derived the hinge. There is no `DerivationRecord`. Without provenance, a fabricated anchor is indistinguishable from a grounded one after the fact.

---

### Typed Inputs / Outputs

**Inputs (unchanged):** `thesis_text`, `evidence_text`, `test_model_text` → all `str`

**Output (new):** `DerivationRecord` wraps the existing `HingeObject` with a mismatch classification and derivation provenance. The `HingeObject` schema does not change.

---

### DerivationMismatchClass

```python
class DerivationMismatchClass(str, Enum):
    CLEAN = "CLEAN"
    FABRICATED_SAFE_HARBOR_ANCHOR = "FABRICATED_SAFE_HARBOR_ANCHOR"
    CONTRADICTED_SCOPE_DISCLAIMER = "CONTRADICTED_SCOPE_DISCLAIMER"
    GROUNDING_POINTER_ABSENT = "GROUNDING_POINTER_ABSENT"
    UNRESOLVED_GENERIC = "UNRESOLVED_GENERIC"
```

Definitions:

- **CLEAN** — safe-harbor disclaimer is present in text and consistent with evidence; grounding pointer resolves to executable locus
- **FABRICATED_SAFE_HARBOR_ANCHOR** — thesis routes to `LOCAL_SAFE_HARBOR` but the safe-harbor disclaimer lacks any corresponding support in `evidence_text`; the derivation is relying on mutator assertion alone
- **CONTRADICTED_SCOPE_DISCLAIMER** — safe-harbor scope in thesis is contradicted by evidence text (e.g., thesis claims local scope; evidence describes whole-system propagation)
- **GROUNDING_POINTER_ABSENT** — no executable locus derivable from any input; already reachable via `evaluate_hinge_grounding()` but now classified explicitly at derivation time
- **UNRESOLVED_GENERIC** — `GENERIC_WEAKEST_POINT` family with no safe-harbor claim; not a failure, just an unresolved case

---

### DerivationRecord

```python
@dataclass(frozen=True)
class DerivationRecord:
    hinge: HingeObject                         # unchanged schema
    alignment_status: HingeAlignmentStatus     # output of evaluate_hinge_grounding()
    mismatch_class: DerivationMismatchClass    # seam-local classification
    disclaimer_found_in_text: bool             # was a safe-harbor disclaimer present in thesis_text?
    evidence_supports_disclaimer: bool         # does evidence_text contain support for it?
    grounding_pointer_source: str              # how the pointer was derived: "test_model", "evidence", "fabricated", "absent"
    passed: bool                               # True only if mismatch_class == CLEAN
```

---

### Fail-Closed Rule

**A derivation passes if and only if `mismatch_class == CLEAN`.**

If `mismatch_class != CLEAN`, `passed = False` and the derivation is treated as `UNRESOLVED_UNGROUNDED` regardless of what `evaluate_hinge_grounding()` returns. The existing `HingeAlignmentStatus` result is still recorded in `DerivationRecord` for audit, but it does not override the fail-closed gate.

This is the tightened Stage 2 pass/fail criteria. The seam enforces it before handing off to downstream layers.

---

### Four Fixture Classes

**Fixture 1: fabricated_safe_harbor_anchor**
- Thesis text asserts a local-scope disclaimer; evidence text contains nothing supporting it
- `test_model_text` contains a `def some_func()` (provides a code pointer structurally)
- Expected: `mismatch_class = FABRICATED_SAFE_HARBOR_ANCHOR`, `passed = False`
- Why this matters: currently the seam would return `ALIGNED_SAFE_HARBOR` for this input

**Fixture 2: contradicted_safe_harbor_disclaimer**
- Thesis text asserts "this only affects component X"; evidence text states "propagates across all layers"
- Expected: `mismatch_class = CONTRADICTED_SCOPE_DISCLAIMER`, `passed = False`
- Why this matters: currently there is no contradiction check at the derivation layer

**Fixture 3: genuinely_grounded_safe_harbor**
- Thesis text contains a local-scope disclaimer; evidence text confirms the constraint; test_model_text has an assert-based harness
- Expected: `mismatch_class = CLEAN`, `passed = True`, `alignment_status = ALIGNED_SAFE_HARBOR`
- Why this matters: the clean path must continue to work after the gate is added

**Fixture 4: unresolved_generic_no_disclaimer**
- `GENERIC_WEAKEST_POINT` family; no disclaimer in thesis; no pointer derivable
- Expected: `mismatch_class = UNRESOLVED_GENERIC`, `passed = False`
- Why this matters: generic cases must not accidentally pass; fail-closed is the default

---

### Builder Directive

Implement in `src/ztare/validator/derivation_record.py` (new file):
- `DerivationMismatchClass` enum
- `DerivationRecord` dataclass
- `evaluate_derivation_seam(thesis_text, evidence_text, test_model_text) -> DerivationRecord` — this wraps `build_stage2_handoff()` or calls the derivation logic directly, adds mismatch classification, applies fail-closed rule

Implement in `src/ztare/validator/stage2_derivation_fixture_regression.py` (new file):
- Four fixture cases above
- All four must pass before this seam is promotable

Do not modify `hinge_handoff.py` schema types. The `HingeObject`, `HingeAlignmentStatus`, `HingeScopeLevel` enums stay frozen.

`target_state: A2`

<done>

## Turn 2 — Claude

### Implementation packet: first derivation seam slice.

**Allowed files (this slice only):**
- `src/ztare/validator/stage2_derivation.py` — new file
- `src/ztare/validator/stage2_derivation_fixture_regression.py` — new file

No other files may be created or modified. `hinge_handoff.py` is read-only. `HingeObject`, `HingeAlignmentStatus`, `HingeScopeLevel`, `ArtifactType`, `HingeGroundingPointer` are frozen.

---

**`stage2_derivation.py` — exact contract:**

```python
class DerivationMismatchClass(str, Enum):
    CLEAN = "CLEAN"
    FABRICATED_SAFE_HARBOR_ANCHOR = "FABRICATED_SAFE_HARBOR_ANCHOR"
    CONTRADICTED_SCOPE_DISCLAIMER = "CONTRADICTED_SCOPE_DISCLAIMER"
    GROUNDING_POINTER_ABSENT = "GROUNDING_POINTER_ABSENT"
    UNRESOLVED_GENERIC = "UNRESOLVED_GENERIC"

@dataclass(frozen=True)
class DerivationRecord:
    hinge: HingeObject
    alignment_status: HingeAlignmentStatus     # from evaluate_hinge_grounding() — audit only
    mismatch_class: DerivationMismatchClass
    disclaimer_found_in_text: bool             # safe-harbor keyword present in thesis_text
    evidence_supports_disclaimer: bool         # evidence_text contains support for the disclaimer
    grounding_pointer_source: str              # "test_model" | "evidence" | "fabricated" | "absent"
    passed: bool                               # True iff mismatch_class == CLEAN

def evaluate_derivation_seam(
    thesis_text: str,
    evidence_text: str,
    test_model_text: str = "",
) -> DerivationRecord:
    ...
```

**Fail-closed rule (must be enforced inside `evaluate_derivation_seam`):**
`passed = (mismatch_class == DerivationMismatchClass.CLEAN)`

`alignment_status` from `evaluate_hinge_grounding()` is recorded for audit but does not override `passed`. A fabricated anchor that happens to reach `ALIGNED_SAFE_HARBOR` via structural cues must still have `passed=False` if `mismatch_class != CLEAN`.

**Mismatch detection logic (minimum required):**

1. `FABRICATED_SAFE_HARBOR_ANCHOR` — family is `LOCAL_SAFE_HARBOR` AND `disclaimer_found_in_text` is True AND `evidence_supports_disclaimer` is False
2. `CONTRADICTED_SCOPE_DISCLAIMER` — `disclaimer_found_in_text` is True AND evidence_text contains explicit whole-system scope language (e.g., "propagates", "all layers", "whole system")
3. `GROUNDING_POINTER_ABSENT` — no executable grounding pointer derivable (pointer is None or locus is empty)
4. `UNRESOLVED_GENERIC` — family is `GENERIC_WEAKEST_POINT` and no disclaimer found
5. `CLEAN` — none of the above; safe-harbor is present, supported, and grounded to an executable locus

Detection is applied in priority order: `FABRICATED` and `CONTRADICTED` before `GROUNDING_POINTER_ABSENT` before `UNRESOLVED_GENERIC` before `CLEAN`.

**`disclaimer_found_in_text` signal:** True if `thesis_text` contains any of: `"safe-harbor"`, `"safe harbor"`, `"local scope"`, `"bounded"`, `"only affects"`, `"does not affect"`.

**`evidence_supports_disclaimer` signal:** True if `evidence_text` contains at least one of the same disclaimer keywords AND does not contain contradicting whole-system language.

---

**`stage2_derivation_fixture_regression.py` — four required cases:**

| case_id | thesis_text signal | evidence signal | test_model signal | expected mismatch_class | expected passed |
|---|---|---|---|---|---|
| `fabricated_safe_harbor_anchor` | "safe harbor" disclaimer present | evidence is empty / no support | has `def some_func()` | `FABRICATED_SAFE_HARBOR_ANCHOR` | `False` |
| `contradicted_scope_disclaimer` | "safe harbor" + "local scope" | evidence contains "propagates across all layers" | empty | `CONTRADICTED_SCOPE_DISCLAIMER` | `False` |
| `genuinely_grounded_safe_harbor` | "safe harbor" disclaimer present | evidence confirms local scope | has `assert` harness | `CLEAN` | `True` |
| `unresolved_generic_no_disclaimer` | no disclaimer; generic weakest-point claim | no evidence | empty | `UNRESOLVED_GENERIC` | `False` |

Each case must assert determinism: run `evaluate_derivation_seam()` twice on identical inputs and verify the two `DerivationRecord` outputs are equal.

---

**Verification command:**
```
python -m src.ztare.validator.stage2_derivation_fixture_regression
```

All four cases must pass (4/4) before this slice is promotable.

<done>

## Turn 3 — Spec Agent (Claude) — Evaluation

### Seam promotion evaluation: 4/4 verified. Seam is promotable.

**Verification result:** `4/4 passed (all_passed=True)`

| case_id | expected | actual | passed |
|---|---|---|---|
| `fabricated_safe_harbor_anchor` | `FABRICATED_SAFE_HARBOR_ANCHOR` / `False` | `FABRICATED_SAFE_HARBOR_ANCHOR` / `False` | PASS |
| `contradicted_scope_disclaimer` | `CONTRADICTED_SCOPE_DISCLAIMER` / `False` | `CONTRADICTED_SCOPE_DISCLAIMER` / `False` | PASS |
| `genuinely_grounded_safe_harbor` | `CLEAN` / `True` | `CLEAN` / `True` | PASS |
| `unresolved_generic_no_disclaimer` | `UNRESOLVED_GENERIC` / `False` | `UNRESOLVED_GENERIC` / `False` | PASS |

Determinism check passed for all four cases (identical inputs produced equal `DerivationRecord` outputs on both runs).

---

**Spec fidelity assessment:**

The implementation in `stage2_derivation.py` matches the Turn 1 / Turn 2 contract exactly:

- `DerivationMismatchClass` enum: five values, identical to spec
- `DerivationRecord` dataclass: seven frozen fields, identical to spec
- `evaluate_derivation_seam()`: applies mismatch detection in priority order (FABRICATED → CONTRADICTED → GROUNDING_POINTER_ABSENT → UNRESOLVED_GENERIC → CLEAN); fail-closed rule enforced as `passed = (mismatch_class == CLEAN)`
- `_classify_mismatch()`: detection logic matches the four specified mismatch classes
- `alignment_status` from `evaluate_hinge_grounding()` is recorded for audit but does not override `passed`

**Out-of-scope constraints respected:**

- `HingeObject` schema: no new fields added; unchanged
- `R1 MutationDeclaration` wire format: not touched
- Stages 3-6 contracts: not touched
- V4 historical promotion evidence: not reopened
- `hinge_handoff.py` is read-only and was not modified

**Success condition satisfied:**

The genesis success condition — "Safe-harbor disclaimers are independently grounded or fail closed using the existing HingeObject schema and the existing downstream contracts" — is met:

1. A fabricated safe-harbor anchor (LOCAL_SAFE_HARBOR family + disclaimer present + no evidence support) now fails closed at the seam with `FABRICATED_SAFE_HARBOR_ANCHOR`
2. A contradicted disclaimer (whole-system evidence contradicts local-scope claim) fails closed with `CONTRADICTED_SCOPE_DISCLAIMER`
3. A genuinely grounded safe-harbor passes as `CLEAN`
4. An unresolved generic with no disclaimer fails closed with `UNRESOLVED_GENERIC`

The seam-local evaluator (`evaluate_derivation_seam`) is the scoring surface, not the generic recursive-thesis loop. The `DerivationRecord` provides full derivation provenance for audit.

**Recommendation:** promote to A2.

`target_state: A2`

<done>

## Turn 4 — Spec Agent (Claude) — A2 Registration (revision 5)

### Pre-existing work registered. Spec contract confirmed. Advancing to B.

This turn formally registers the prior three turns against supervisor revision 5. The debate file was pre-populated before the current supervisor session opened. The supervisor's `debate_last_turn: 0` reflects that no turns were registered in this revision, not that the file was empty.

**Pre-existing implementation confirmed:**

- `src/ztare/validator/stage2_derivation.py` — `DerivationMismatchClass`, `DerivationRecord`, `evaluate_derivation_seam()` match the Turn 2 contract exactly. `passed = (mismatch_class == CLEAN)` enforced. `alignment_status` is audit-only and does not override the fail-closed gate.
- `src/ztare/validator/stage2_derivation_fixture_regression.py` — four fixture cases, determinism checks.

**Verification report (`/tmp/stage2_derivation_004/verification_report.txt`):** `4/4 passed, all_passed=true`

| case_id | mismatch_class | passed | deterministic |
|---|---|---|---|
| `fabricated_safe_harbor_anchor` | `FABRICATED_SAFE_HARBOR_ANCHOR` | `False` | yes |
| `contradicted_scope_disclaimer` | `CONTRADICTED_SCOPE_DISCLAIMER` | `False` | yes |
| `genuinely_grounded_safe_harbor` | `CLEAN` | `True` | yes |
| `unresolved_generic_no_disclaimer` | `UNRESOLVED_GENERIC` | `False` | yes |

**Success condition:** Met. Safe-harbor disclaimers are independently grounded or fail closed using the existing `HingeObject` schema and downstream contracts.

**Out-of-scope constraints:** No new fields added to `HingeObject`. `R1 MutationDeclaration` wire format unchanged. Stages 3-6 contracts unchanged. `hinge_handoff.py` read-only.

**No spec refinement required.** Advancing to state B.

`target_state: B`

<done>

## Turn 5 — Implementation Agent (Codex) — B Commit (revision 7)

### Supervisor receipt.

Reverified the existing derivation-boundary implementation at revision 6 without changing out-of-scope contracts. `src/ztare/validator/stage2_derivation.py` and `src/ztare/validator/stage2_derivation_fixture_regression.py` already satisfy the staged seam contract in this workspace. Local verification passed: `python -m src.ztare.validator.stage2_derivation_fixture_regression` -> `4/4 passed` (`fabricated_safe_harbor_anchor`, `contradicted_scope_disclaimer`, `genuinely_grounded_safe_harbor`, `unresolved_generic_no_disclaimer`). No source edits were required.

Artifacts:
- `src/ztare/validator/stage2_derivation.py`
- `src/ztare/validator/stage2_derivation_fixture_regression.py`

<done>

## Turn 6 — Verifier — C Commit (revision 8)

### Supervisor receipt.

Verifier wrapper ran `python -m src.ztare.validator.stage2_derivation_fixture_regression` successfully. Implementation matches the recorded artifact set.

Verification report: `/tmp/stage2_derivation_004/verification_report.txt`

<done>

## Turn 7 — Codex

### Packet 1 is complete. The missing link is live Stage 2 integration.

What packet 1 achieved:

- a seam-local evaluator exists:
  - `src/ztare/validator/stage2_derivation.py`
- a deterministic four-fixture regression exists:
  - `src/ztare/validator/stage2_derivation_fixture_regression.py`
- fabricated or contradicted safe-harbor anchors now fail closed at the seam scoring surface

What packet 1 did **not** yet achieve:

- the live `build_stage2_handoff()` path does not yet consume this seam gate by default

That is why the kernel linkage can feel abstract. The seam logic is proved, but it is still mostly a sidecar evaluator. The next packet should be integration, not more vocabulary work.

Registered next packet via manifest:

- manifest: `supervisor/program_manifests/stage2_derivation_seam_hardening.json`
- packet_id: `stage2_live_handoff_integration`
- target: `derivation_boundary`

Bounded goal for packet 2:

- wire `evaluate_derivation_seam()` into the live `build_stage2_handoff()` trust path as a fail-closed gate
- preserve frozen downstream contracts
- stop fabricated safe-harbor anchors before Stage 2 hands off to bridge / board logic

Suggested allowed artifacts for packet 2:

- `src/ztare/validator/hinge_handoff.py`
- `src/ztare/validator/stage2_derivation.py`
- `src/ztare/validator/stage24_bridge_fixture_regression.py`
- `src/ztare/validator/stage4_fixture_regression.py`

If packet 2 verifies cleanly, the following A2 should set:

- `gate_on_verifier_pass = true`

so the program pauses at human review instead of auto-looping.

<done>

## Turn 8 — Spec Agent (Claude) — Packet 2: Live Handoff Integration (previous session)

### Seam gate wired into `build_stage2_handoff()`. All downstream contracts preserved.

**Seam Target:** `build_stage2_handoff()` in `hinge_handoff.py` — the live function called by `shadow_board.py` and the primary Stage 2 output path.

**The integration problem:**

`evaluate_derivation_seam()` in `stage2_derivation.py` imports from `hinge_handoff.py`. Importing `evaluate_derivation_seam()` back into `hinge_handoff.py` would create a circular dependency. The gate logic is therefore inlined in `hinge_handoff.py` using the same keyword sets as `stage2_derivation.py`, with an explicit comment recording the synchronization obligation.

**What was changed (`hinge_handoff.py` only):**

1. Added `_SEAM_DISCLAIMER_KEYWORDS` and `_SEAM_CONTRADICTION_KEYWORDS` tuples — identical to those in `stage2_derivation.py`.

2. Added `_evaluate_seam_gate(family_tag, thesis_text, evidence_text) -> str | None` — returns a block-reason string for `FABRICATED_SAFE_HARBOR_ANCHOR` or `CONTRADICTED_SCOPE_DISCLAIMER`, else `None`. Applies the same priority-ordered detection as `_classify_mismatch()` in `stage2_derivation.py` for these two classes.

3. Modified `build_stage2_handoff()` to call `_evaluate_seam_gate()` immediately after deriving `hinge` and `alignment_status`. If the gate fires, returns a `Stage2Handoff` with `alignment_status=UNRESOLVED_UNGROUNDED`, `provenance_verified=False`, and the block reason in `rationale`. The `HingeObject` is passed through unchanged (frozen schema preserved).

**Fail-closed behavior:**

- Fabricated safe-harbor anchor (`LOCAL_SAFE_HARBOR` family + disclaimer present + no evidence support): `UNRESOLVED_UNGROUNDED / provenance_verified=False`
- Contradicted scope disclaimer (disclaimer present + contradiction in evidence): `UNRESOLVED_UNGROUNDED / provenance_verified=False`
- Genuinely grounded safe-harbor: passes through to `ALIGNED_SAFE_HARBOR` as before
- All other families: gate returns `None`, existing derivation path unchanged

**Verification results:**

| suite | result |
|---|---|
| `stage2_derivation_fixture_regression` | 4/4 passed |
| `stage24_bridge_fixture_regression` | 8/8 passed |
| `stage4_fixture_regression` | 8/8 passed |

Live gate smoke tests (calls to `build_stage2_handoff()` directly):
- Fabricated anchor: `UNRESOLVED_UNGROUNDED`, `provenance_verified=False`, rationale contains `FABRICATED_SAFE_HARBOR_ANCHOR`
- Contradicted scope: `UNRESOLVED_UNGROUNDED`, `provenance_verified=False`, rationale contains `CONTRADICTED_SCOPE_DISCLAIMER`
- Clean grounded: `ALIGNED_SAFE_HARBOR`, `provenance_verified=True`

**Out-of-scope constraints respected:**

- `HingeObject` schema: no new fields; schema unchanged
- `Stage2Handoff` schema: no new fields; unchanged
- `R1 MutationDeclaration` wire format: not touched
- Stages 3-6 contracts: not touched
- `stage24_bridge.py`, `shadow_board.py`, all fixture files except as regression verification: not modified

**Success condition:** Live `build_stage2_handoff()` path now fails closed on fabricated safe-harbor anchors and contradicted scope disclaimers. Downstream routing receives `UNRESOLVED_UNGROUNDED` for these cases rather than inheriting a bad derivation. Frozen downstream contracts preserved (all 16/16 downstream fixture cases pass).

`target_state: A2`

<done>


## Turn 9 — Spec Agent (Claude) — Packet 2 Evaluation (prev session)

### stage2_live_handoff_integration: verified. Packet success condition met.

**Packet:** `stage2_live_handoff_integration`
**Target:** `derivation_boundary`

---

**Implementation confirmed in `hinge_handoff.py`:**

The seam gate is live. `build_stage2_handoff()` (lines 100–108) calls `_evaluate_seam_gate()` immediately after deriving `hinge` and `alignment_status`. If the gate fires, it returns a `Stage2Handoff` with `alignment_status=UNRESOLVED_UNGROUNDED` and `provenance_verified=False`. The existing `HingeObject` is passed through unchanged (frozen schema preserved).

`_evaluate_seam_gate()` (lines 243–272) inlines the same keyword sets as `stage2_derivation.py` (`_SEAM_DISCLAIMER_KEYWORDS`, `_SEAM_CONTRADICTION_KEYWORDS`) with a sync comment, and applies the same two-class priority check:

1. `FABRICATED_SAFE_HARBOR_ANCHOR` — `LOCAL_SAFE_HARBOR` family + disclaimer present + evidence does not support
2. `CONTRADICTED_SCOPE_DISCLAIMER` — disclaimer present + contradiction in evidence

The circular import constraint is handled correctly: `stage2_derivation.py` imports from `hinge_handoff.py`; the gate is inlined in `hinge_handoff.py` to avoid the reverse import.

---

**Verification results (live, this session):**

| suite | result |
|---|---|
| `stage2_derivation_fixture_regression` | 4/4 passed |
| `stage24_bridge_fixture_regression` | 8/8 passed |
| `stage4_fixture_regression` | 8/8 passed |

All 20 cases pass. All determinism checks pass.

---

**Out-of-scope constraints respected:**

- `HingeObject` schema: no new fields; unchanged
- `Stage2Handoff` schema: no new fields; unchanged
- `R1 MutationDeclaration` wire format: not touched
- Stages 3-6 contracts: not touched
- `stage24_bridge.py`, `shadow_board.py`: not modified
- No new files created outside allowed artifact list

---

**Packet success condition satisfied:**

> Live Stage 2 handoff uses the seam evaluator or an equivalent fail-closed sidecar, preserving frozen downstream contracts while blocking fabricated safe-harbor anchors.

`_evaluate_seam_gate()` is wired directly into `build_stage2_handoff()`. Fabricated anchors receive `UNRESOLVED_UNGROUNDED / provenance_verified=False` before bridge or board routing. All 16 downstream fixture cases continue to pass.

**Recommendation:** promote to A2. Set `gate_on_verifier_pass = true` per Turn 7 directive so the program pauses for human review before the third packet.

`target_state: A2`

<done>


## Turn 11 — Spec Agent (Claude) — A2 Registration (stage2_derivation_006, revision 1)

### Packet 2 pre-existing work registered. Gate on verifier pass set. Advancing to B.

This turn formally registers the packet 2 work (Turns 8–9) against supervisor revision 1 of `stage2_derivation_006`. The debate file carried over Turns 1–10 from prior runs. The supervisor's `debate_last_turn: 10` reflects turns from prior sessions, not a fresh implementation cycle.

**Live verification (this session):**

| suite | result |
|---|---|
| `stage2_derivation_fixture_regression` | 4/4 passed |
| `stage24_bridge_fixture_regression` | 8/8 passed |
| `stage4_fixture_regression` | 8/8 passed |

All 20 fixture cases pass. All determinism checks pass.

**Implementation confirmed (`hinge_handoff.py`):**

- `_SEAM_DISCLAIMER_KEYWORDS` and `_SEAM_CONTRADICTION_KEYWORDS` at lines 224–239 — identical to `stage2_derivation.py`
- `_evaluate_seam_gate(family_tag, thesis_text, evidence_text)` at lines 243–272 — inline gate, no circular import
- `build_stage2_handoff()` at line 100 — calls `_evaluate_seam_gate()` immediately after deriving `hinge` and `alignment_status`; returns `UNRESOLVED_UNGROUNDED / provenance_verified=False` if gate fires

**Packet success condition satisfied:**

> Live Stage 2 handoff uses the seam evaluator or an equivalent fail-closed sidecar, preserving frozen downstream contracts while blocking fabricated safe-harbor anchors.

Met: `_evaluate_seam_gate()` is the fail-closed sidecar wired into `build_stage2_handoff()`. 16 downstream fixture cases pass (bridge 8/8, stage4 8/8).

**Out-of-scope constraints respected:**

- `HingeObject` schema: no new fields; unchanged
- `Stage2Handoff` schema: no new fields; unchanged
- `R1 MutationDeclaration` wire format: not touched
- Stages 3-6 contracts: not touched

**`gate_on_verifier_pass = true`** — set per Turn 7 directive. The program pauses for human review after verifier confirmation of packet 2.

**Registered artifacts:**
- `src/ztare/validator/hinge_handoff.py`
- `src/ztare/validator/stage2_derivation.py`
- `src/ztare/validator/stage2_derivation_fixture_regression.py`
- `src/ztare/validator/stage24_bridge_fixture_regression.py`
- `src/ztare/validator/stage4_fixture_regression.py`

**Verification command:** `python -m src.ztare.validator.stage2_derivation_fixture_regression && python -m src.ztare.validator.stage24_bridge_fixture_regression && python -m src.ztare.validator.stage4_fixture_regression`

Advancing to state B.

`target_state: B`

<done>

## Turn 10 — Spec Agent (Claude) — A2 Registration (stage2_derivation_005, revision 1)

### Pre-existing packet 2 registered. Gate on verifier pass set. Advancing to B.

This turn formally registers the packet 2 work (Turns 8–9) against supervisor revision 1 of `stage2_derivation_005`. The debate file was pre-populated before this revision opened. The supervisor's `debate_last_turn: 9` reflects turns carried over from the prior run.

**Live verification (this session):**

| suite | result |
|---|---|
| `stage2_derivation_fixture_regression` | 4/4 passed |
| `stage24_bridge_fixture_regression` | 8/8 passed |
| `stage4_fixture_regression` | 8/8 passed |

All 20 fixture cases pass. All determinism checks pass.

**Implementation confirmed (`hinge_handoff.py`):**

- `_SEAM_DISCLAIMER_KEYWORDS` and `_SEAM_CONTRADICTION_KEYWORDS` at lines 224–239 — identical to `stage2_derivation.py`
- `_evaluate_seam_gate(family_tag, thesis_text, evidence_text)` at lines 243–272 — inline gate, no circular import
- `build_stage2_handoff()` at lines 100–108 — calls `_evaluate_seam_gate()` immediately after deriving `hinge` and `alignment_status`; returns `UNRESOLVED_UNGROUNDED / provenance_verified=False` if gate fires

**Packet success condition satisfied:**

> Live Stage 2 handoff uses the seam evaluator or an equivalent fail-closed sidecar, preserving frozen downstream contracts while blocking fabricated safe-harbor anchors.

Met: `_evaluate_seam_gate()` is the fail-closed sidecar wired into the live path. 16 downstream fixture cases pass (bridge 8/8, stage4 8/8).

**Out-of-scope constraints respected:**

- `HingeObject` schema: no new fields; unchanged
- `Stage2Handoff` schema: no new fields; unchanged
- `R1 MutationDeclaration` wire format: not touched
- Stages 3-6 contracts: not touched

**`gate_on_verifier_pass = true`** — set per Turn 7 directive. The program pauses for human review after verifier confirmation of packet 2. No auto-loop to packet 3.

**Registered artifacts:**
- `src/ztare/validator/hinge_handoff.py`
- `src/ztare/validator/stage2_derivation.py`
- `src/ztare/validator/stage2_derivation_fixture_regression.py`
- `src/ztare/validator/stage24_bridge_fixture_regression.py`
- `src/ztare/validator/stage4_fixture_regression.py`

**Verification command:** `python -m src.ztare.validator.stage2_derivation_fixture_regression && python -m src.ztare.validator.stage24_bridge_fixture_regression && python -m src.ztare.validator.stage4_fixture_regression`

Advancing to state B.

`target_state: B`

<done>

## Turn 12 — Implementation Agent (Codex) — B Commit (revision 3)

### Supervisor receipt.

B declared implementation artifacts that do not match the A2 expectation.

Artifacts:
- `src/ztare/validator/hinge_handoff.py`
- `src/ztare/validator/stage2_derivation.py`
- `src/ztare/validator/stage24_bridge_fixture_regression.py`
- `src/ztare/validator/stage4_fixture_regression.py`

<done>

## Turn 13 — Implementation Agent (Codex) — B Commit (revision 3)

### Supervisor receipt.

Verified the existing `stage2_live_handoff_integration` implementation already present in this workspace. `build_stage2_handoff()` uses the live seam fail-closed sidecar to block fabricated and contradicted safe-harbor derivations without changing downstream contracts. No source edits were required in this run. Verification passed with the required command: stage2_derivation 4/4, stage24_bridge 8/8 plus live gate 3/3, and stage4 8/8.

Artifacts:
- `src/ztare/validator/hinge_handoff.py`
- `src/ztare/validator/stage2_derivation.py`
- `src/ztare/validator/stage24_bridge_fixture_regression.py`
- `src/ztare/validator/stage4_fixture_regression.py`

<done>

## Turn 14 — Verifier — C Commit (revision 4)

### Supervisor receipt.

Verifier wrapper ran `python -m src.ztare.validator.stage2_derivation_fixture_regression && python -m src.ztare.validator.stage24_bridge_fixture_regression && python -m src.ztare.validator.stage4_fixture_regression` successfully. Implementation matches the recorded artifact set.

Verification report: `/tmp/stage2_derivation_009/verification_report.txt`

<done>

## Turn 15 — Human

### Promotion accepted. Program closed at the human gate.

Run: `stage2_derivation_009`
Gate: `contract_promotion`

Human gate resolved through explicit supervisor command.

<done>
