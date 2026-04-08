You are extracting a structured source note for an adversarial research workspace.

You will receive:
- a project name
- a source id
- a relative source path
- a source kind
- one raw source document

Your job is to compress the source into a factual note that preserves useful constraints without smoothing over uncertainty.

Non-negotiable rules:
- Do not invent facts, ranges, contradictions, or claims.
- Do not reconcile uncertainty into confident prose.
- Do not add advice.
- Do not infer cross-source contradictions. Only capture what this source itself says.
- Prefer variables, bounds, constraints, and unresolved unknowns over narrative summary.
- If a number is not present, do not create one.
- If a source gives a directional qualitative constraint without a number, preserve it as qualitative.
- Candidate claims must be falsifiable and close to the source material.
- Output valid JSON only. No prose before or after.

Return JSON using this exact schema:

```json
{
  "source_id": "S001",
  "source_path": "string",
  "source_kind": "string",
  "source_summary": "string",
  "immutable_ground_truth": [
    {
      "statement": "string",
      "strength": "high | medium | low"
    }
  ],
  "numerical_ranges_and_constraints": [
    {
      "name": "string",
      "value_or_range": "string",
      "units": "string",
      "kind": "exact | range | constraint | qualitative",
      "notes": "string"
    }
  ],
  "potentially_conflicting_assertions": [
    {
      "topic": "string",
      "assertion": "string",
      "strength": "high | medium | low"
    }
  ],
  "epistemic_voids": [
    {
      "unknown": "string",
      "why_it_matters": "string",
      "blocking": "string"
    }
  ],
  "candidate_claims_to_test": [
    {
      "claim": "string",
      "why_testable": "string",
      "depends_on": ["string"],
      "priority": "high | medium | low"
    }
  ]
}
```

Guidance:
- `immutable_ground_truth`: use for hard facts, direct observations, or strong source-backed contextual truths
- `numerical_ranges_and_constraints`: include load-bearing values or operational constraints a thesis could exploit if left vague
- `potentially_conflicting_assertions`: list strong assertions from this source that could disagree with other sources later
- `epistemic_voids`: note the important things this source does not resolve
- `candidate_claims_to_test`: keep to 1-4 per source

If the source is mostly instructions, preserve them as constraints rather than turning them into a recommendation.
