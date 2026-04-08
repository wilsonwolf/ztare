# paper4_manuscript Program Plan

- status: `soft-decommissioned`
- canonical_manuscript: `research_areas/drafts/paper4_full_working.md`
- note: supervisor packet work on Paper 4 is archived as an experiment/evidence set; do not open new `paper4_manuscript_*` runs unless explicitly reviving the experiment
- note: packet statuses below record the final supervisor state, not the active writing workflow
- manifest: `/Users/daalami/figs_activist_loop/supervisor/program_manifests/paper4_manuscript.json`
- completion_policy: `manifest_exhausted_to_D`

## Packets

### 1. Opening section against the frozen outline

- packet_id: `manuscript_opening`
- status: `complete`
- target: `manuscript_opening`
- summary: Draft and verify the paper opening without reopening locked claims, title scope, or principal-scalability boundaries.
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript_manuscript_opening.md`
- success_condition: Opening draft passes deterministic prose verification and pauses at human review.

### 2. Theory foundations fragment

- packet_id: `manuscript_theory_foundations`
- status: `complete`
- target: `manuscript_theory_foundations`
- summary: Draft the invariant / T1 / T2 foundations as a bounded fragment without silently reopening the verified opening contract.
- depends_on: `manuscript_opening`
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript/02a_theory_foundations.md`
- success_condition: Theory foundations fragment is drafted and verified against a bounded prose spec.

### 3. Theory mechanism fragment

- packet_id: `manuscript_theory_mechanism`
- status: `complete`
- target: `manuscript_theory_mechanism`
- summary: Draft the T3 / T4 / interface section as a bounded fragment that depends on the foundations fragment.
- depends_on: `manuscript_theory_foundations`
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript/02b_theory_mechanism.md`
- success_condition: Theory mechanism fragment is drafted and verified against a bounded prose spec.

### 4. Empirical evidence fragment

- packet_id: `manuscript_evidence`
- status: `pending`
- target: `manuscript_evidence`
- summary: Draft the empirical evidence section as a bounded fragment with explicit evidence classes and non-claims.
- depends_on: `manuscript_theory_mechanism`
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript/03_evidence.md`
- success_condition: Evidence fragment is drafted and verified against a bounded prose spec.

### 5. Counterarguments and boundaries fragment

- packet_id: `manuscript_counterarguments`
- status: `pending`
- target: `manuscript_counterarguments`
- summary: Draft the counterarguments/boundaries section, including the principal-scalability and prompt-alignment distinctions, as a bounded fragment.
- depends_on: `manuscript_evidence`
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript/04_counterarguments.md`
- success_condition: Counterarguments fragment is drafted and verified against a bounded prose spec.

### 6. Related work and limitations fragment

- packet_id: `manuscript_related_work_limitations`
- status: `pending`
- target: `manuscript_related_work_limitations`
- summary: Draft the related-work and limitations material as a bounded fragment without reclassifying the paper's non-claims.
- depends_on: `manuscript_counterarguments`
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript/05_related_work_limitations.md`
- success_condition: Related-work/limitations fragment is drafted and verified against a bounded prose spec.

### 7. Conclusion fragment

- packet_id: `manuscript_conclusion`
- status: `pending`
- target: `manuscript_conclusion`
- summary: Draft the conclusion as a bounded fragment that closes the paper without introducing new claims.
- depends_on: `manuscript_related_work_limitations`
- allowed_artifacts:
  - `research_areas/drafts/paper4_manuscript/06_conclusion.md`
- success_condition: Conclusion fragment is drafted and verified against a bounded prose spec.
