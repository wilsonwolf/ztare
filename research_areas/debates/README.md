# Debate Records

This folder stores the canonical, curated debate records that explain why major research and architecture decisions changed.

## Layout And Naming

Debates are grouped by family:

- `papers/`
- `kernel/`
- `supervisor/`
- `product/`

Naming convention:

- short, stable, lowercase file names
- group by the thing being hardened, not by model/vendor
- use the debate folder to express relationship, not a long filename

## What belongs here

- long-lived debate files that capture design decisions
- paper-level argument trails
- stage-level decision logs that are still relevant after implementation

Examples:
- `papers/paper1.md`
- `papers/paper2.md`
- `papers/paper3.md`
- `kernel/v4_core.md`
- `kernel/v4_bridge_hardening.md`
- `kernel/runner_hardening.md`
- `supervisor/supervisor_loop.md`

## What does not belong here

- generated per-run debate logs
- benchmark scratch debates
- temporary back-and-forth artifacts created during loop execution

Those belong under project-local generated artifacts and are ignored from git:
- `projects/*/debate_log_iter_*.md`
- `projects/*/debate_queue/`
- `projects/*/debate_reports/`

## Rule of thumb

If a file explains a decision you would want to read six months later, keep it here.

If a file only records one run's local attack/response trace, keep it out of git.
