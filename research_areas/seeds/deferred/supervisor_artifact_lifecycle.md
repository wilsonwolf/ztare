# Supervisor Artifact Lifecycle And Programmatic Decommission

## Purpose

This seed defines a supervisor-control-plane feature:

- deterministic archival of closed or frozen program artifacts
- no filename guessing
- no reliance on human memory of which files are still live

The motivating failure was Paper 4 decommissioning. We could separate live files from supervisor-era relics, but only by judgment. The system did not know that distinction itself.

## Core Thesis

Program decommissioning should be governed by explicit artifact-lifecycle policy, not by heuristics.

The supervisor already knows:
- program status
- manifests
- staged writes
- committed revisions

It should also know:
- which outputs stay live after decommission
- which outputs archive on decommission
- which records stay in place as provenance

## Problem Statement

Today the missing layer is artifact ownership and lifecycle.

That creates three risks:

1. **Manual memory risk.**
   The principal has to remember which files are canonical and which are relics.

2. **Heuristic archive risk.**
   Any filename-based archive sweep can move a live file by mistake.

3. **Late-added artifact risk.**
   New files created late in a program are easy to miss at decommission time.

## Proposed Mechanism

### 1. Per-program artifact inventory

Add:

```text
supervisor/program_artifacts/<program_id>.json
```

Updated from actual committed writes and assembler outputs.

### 2. Manifest lifecycle policy

Each program manifest should declare:

- `artifact_lifecycle.live_outputs`
- `artifact_lifecycle.archive_on_decommission`
- `artifact_lifecycle.retain_in_place`
- `artifact_lifecycle.archive_root`

### 3. Fail-closed archive command

Add:

```bash
make supervisor-archive-program SUP_PROGRAM=<program_id>
```

The command should:
- require the program to be `closed` or `frozen`
- load manifest lifecycle policy
- load program artifact inventory
- fail closed if any tracked artifact is unclassified
- move only the archive-classified artifacts
- emit an archive receipt

## Success Condition

The feature is complete when:

1. decommissioning a closed program requires no filename guessing
2. late-added tracked artifacts cannot be silently omitted
3. the archive command refuses to run if any artifact lacks lifecycle classification
4. an archive receipt is written with moved and retained paths

## Out Of Scope

- generic repo cleanup
- deleting archived artifacts
- inferring artifact ownership from prefixes like `paper4_*`
- changing active program routing semantics

## Expected Artifacts

- manifest lifecycle schema extension
- `supervisor/program_artifacts/`
- archive receipt schema
- `supervisor-archive-program` command
- regression coverage for unclassified-artifact fail-closed behavior
