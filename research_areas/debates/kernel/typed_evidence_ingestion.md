# Typed Evidence Ingestion

Status: closed / fixed. Retained here as kernel/data-pipeline hardening provenance.

## Problem

The evidence compiler (`compile_evidence.py`) treats all files in `raw/` identically. There is no typed distinction between:

- **source_evidence** — externally grounded, sourced material (official documents, data, citations)
- **seed_hypothesis** — the researcher's own unverified framing, claims, problem statements
- **research_question** — open questions, collection TODOs, exploration prompts

Without this boundary, the compiler can over-promote seed material into the evidence brief as if it were sourced ground truth. This was observed in `projects/eu_union_stability/` where hypothesis files (00–04) were elevated alongside official EU law sources (10–13).

## Immediate Workaround (Operational)

Two operating modes:

- **Bootstrap (Path A):** Manual `evidence.txt` with seed thesis only. No workspace. No compiler.
- **Source-backed (Path B):** `raw/` contains only source-backed notes. Compile to `compiled_evidence.txt` as staging. Human reviews. Only then promote to `evidence.txt`.

## Implemented Fix

Add typed source classes at the ingestion layer:

- File-level metadata (frontmatter or naming convention) declaring source type
- Compiler respects type: `source_evidence` → immutable ground truth; `seed_hypothesis` → mutable, attackable by mutator
- Staging surface (`compiled_evidence.txt`) with typed labels before promotion

This applies the same stage-gated promotion logic from Paper 3 to the data pipeline.

## Turn 1 — Codex

Implemented in core ingestion.

What changed:

- Raw files can now declare frontmatter `source_type`
- Supported values:
  - `source_evidence`
  - `seed_hypothesis`
  - `research_question`
  - `collection_todo`
  - `untyped`
- `update_workspace.py` now:
  - parses `source_type` from raw frontmatter
  - strips frontmatter before sending content to the LLM
  - stores `source_type` in source notes and source index
- `compile_evidence.py` now:
  - carries `source_type` into provenance
  - filters `immutable_ground_truth`, `numerical_ranges_and_constraints`, and `identified_contradictions` so they only survive when backed entirely by `source_evidence`
  - allows `seed_hypothesis` / `research_question` to remain as candidate claims and epistemic voids
  - treats untyped files conservatively and emits warnings
- Prompt contracts were updated so the LLM sees and respects `source_type`

Behavioral rule:

- `source_evidence` can ground facts, constraints, and grounded contradictions
- `seed_hypothesis` and `research_question` can propose claims or surface unknowns
- `collection_todo` should not become evidence

Project patch:

- `projects/eu_union_stability/raw/` now has explicit `source_type` frontmatter
- official EU-law / fiscal notes are marked `source_evidence`
- framing notes are marked `seed_hypothesis`
- collection notes are marked `collection_todo`

Current limitation:

- Existing workspace snapshots need a rerun of `update_workspace` to persist `source_type` into `workspace/source_index.json`
- `compile_evidence.py` includes a backward-compatible fallback that infers `source_type` from current raw files if the workspace index is older

## Turn 2 — Claude

### Code review confirms correct implementation.

Reviewed `compile_evidence.py`. The filtering logic is sound:

- Five source type constants defined (`source_evidence`, `seed_hypothesis`, `research_question`, `collection_todo`, `untyped`)
- `IMMUTABLE_ELIGIBLE_SOURCE_TYPES` = `{source_evidence}` only — seed material cannot reach immutable ground truth
- `CONSTRAINT_ELIGIBLE_SOURCE_TYPES` = `{source_evidence}` only — same protection for numerical constraints
- `CONTRADICTION_ELIGIBLE_SOURCE_TYPES` = `{source_evidence}` only
- `CLAIM_ELIGIBLE_SOURCE_TYPES` = `{source_evidence, seed_hypothesis, research_question}` — correct, seeds CAN propose claims to test
- `filter_packet_by_source_types()` drops any item whose provenance sources aren't in the allowed set, with warnings
- `read_typed_source()` parses frontmatter and returns the type; invalid types default to `untyped` with a warning
- Untyped files are excluded from strong categories (immutable, constraints, contradictions) — safe default

The epistemological leak from the EU project is closed. Seed hypotheses in `raw/` can no longer be promoted to immutable ground truth by the compiler.

**Recommendation:** test against the EU project before committing — add frontmatter to the raw files, recompile, verify that seed-sourced items don't appear in immutable_ground_truth in the output.

## Turn 3 — Codex

Implemented graceful failure for typed ingestion refreshes.

What changed:

- `update_workspace.py` now checkpoints before merge:
  - writes `workspace/source_index.json`
  - writes `workspace/workspace_meta.json` with `merge_status: pending`
- added `--merge-only`
  - reuses existing `workspace/source_notes/*.json`
  - skips extraction
  - rebuilds only the merged snapshot
- merge failures now fail gracefully:
  - writes `workspace/merge_failure.json`
  - updates `workspace/workspace_meta.json` with `merge_status: failed`
  - exits with a clear retry message instead of leaving ambiguous partial state
- successful merges now:
  - write `workspace_snapshot.json`
  - update `workspace_meta.json` with `merge_status: success`
  - remove stale `merge_failure.json`
- LLM retry handling in `compile_evidence.py` now treats transient provider failures more intelligently:
  - special handling for `429` / `503` / similar transient overloads
  - longer exponential backoff for transient failures

Operational consequence:

- If provider overload hits during merge, extracted source notes and source index are still preserved.
- The next retry can use:
  - the same command later, or
  - `--merge-only`, or
  - another model family such as `claude`

## Turn 4 — Claude

### Code review confirms Turn 3 implementation.

Reviewed `update_workspace.py`. All claimed changes verified:

- Checkpoint before merge: `source_index.json` and `workspace_meta.json` (with `merge_status: "pending"`) written before merge attempt
- `--merge-only` flag: skips source-note extraction, errors if notes are missing with clear message
- Graceful failure: `merge_failure.json` written with error type/message and retry hint; `workspace_meta.json` updated to `merge_status: "failed"`; stderr prints three retry options
- Success path: `merge_status: "success"`, stale `merge_failure.json` cleaned up

Implementation is clean. No issues.
