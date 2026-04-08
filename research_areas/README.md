# Research Areas

This folder now has distinct layers by artifact role:

- `research_areas/seeds/active/*.md`: active seed specs currently eligible for genesis-opened work
- `research_areas/seeds/deferred/*.md`: deferred future seeds
- `research_areas/seeds/legacy/*.md`: superseded historical seed specs kept for provenance
- `research_areas/debates/**/*.md`: grouped tactical debate and hardening records
- `research_areas/drafts/**/*.md`: generated draft/manuscript fragments and assembled document outputs
- `research_areas/drafts/**/document_manifest.json`: deterministic assembly manifests for fragment-based documents
- `research_areas/program_plans/*.md`: readable packet plans rendered from active program manifests
- `research_areas/proposal_plans/*.md`: readable proposal plans rendered from pre-registry seed proposals

Seed specs remain strategic inputs. They should not be mutated by the tactical debate loop.

Seed lifecycle is tracked in:
- `research_areas/seed_registry.json`

The registry is authoritative. Folder location is a convention, not the final source of truth; some older seed files remain in place for path stability even after their registry status changes to `closed`.

Current seed statuses:
- `seeds/active/stage2_derivation_seam.md` — registry status is now `closed`; retained for provenance after the derivation-seam program completed
- `seeds/active/paper4_managerial_capitalism.md` — registry status is now `closed`; retained for provenance while the live manuscript continues at `research_areas/drafts/paper4_full_working.md` and `papers/paper4/main.tex`
- `seeds/active/paper4_manuscript.md` — registry status is now `closed`; retained for provenance while supervisor-era packet artifacts remain archived under `research_areas/archive/paper4_supervisor/`
- `seeds/deferred/systems_to_algorithms.md` — deferred future avenue
- `seeds/deferred/vnext_semantic_gate_stabilization.md` — deferred kernel hardening seed for structured semantic-gate stabilization
- `seeds/deferred/ztare_open_source.md` — deferred future avenue
- `seeds/legacy/v3_interface.md` — closed legacy seed, superseded by the V4-era contract and supervisor stack

Canonical debate groups:
- `debates/papers/`
- `debates/kernel/`
- `debates/planning/`
- `debates/supervisor/`
- `debates/product/`
