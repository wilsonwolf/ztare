#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
HYPOTHESES_DIR = PROJECT_DIR / "hypotheses"
WORKSPACE_DIR = PROJECT_DIR / "workspace"

STATUS_FILES = (
    "latest_information_yield.json",
    "underidentification_verdict.json",
    "latest_candidate_selection.json",
    "latest_mutation_declaration.json",
    "latest_mutation_validation.json",
)


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _archive_status_files() -> list[str]:
    archived: list[str] = []
    archive_dir = WORKSPACE_DIR / "promotion_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    for name in STATUS_FILES:
        target = WORKSPACE_DIR / name
        if not target.exists():
            continue
        archived_target = archive_dir / name
        if archived_target.exists():
            archived_target.unlink()
        shutil.move(str(target), str(archived_target))
        archived.append(name)
    return archived


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote a hypothesis bundle into the active project root."
    )
    parser.add_argument("name", help="Hypothesis bundle directory name under hypotheses/")
    parser.add_argument(
        "--clear-status",
        action="store_true",
        help="Archive stale workspace status files for operator clarity.",
    )
    args = parser.parse_args()

    bundle_dir = HYPOTHESES_DIR / args.name
    thesis_src = bundle_dir / "thesis.md"
    test_model_src = bundle_dir / "test_model.py"

    if not bundle_dir.is_dir():
        raise SystemExit(f"Missing hypothesis bundle: {bundle_dir}")
    if not thesis_src.exists():
        raise SystemExit(f"Bundle is missing thesis.md: {thesis_src}")

    _copy(thesis_src, PROJECT_DIR / "thesis.md")

    active_test_model = PROJECT_DIR / "test_model.py"
    if test_model_src.exists():
        _copy(test_model_src, active_test_model)
        test_model_action = f"copied {test_model_src.name}"
    else:
        if active_test_model.exists():
            active_test_model.unlink()
            test_model_action = "deleted stale project-root test_model.py"
        else:
            test_model_action = "no test_model.py present; runner will fail closed"

    archived: list[str] = []
    if args.clear_status:
        archived = _archive_status_files()

    print(f"Promoted hypothesis bundle: {args.name}")
    print(f"- thesis.md <- {thesis_src}")
    print(f"- test_model.py: {test_model_action}")
    if args.clear_status:
        if archived:
            print(f"- archived workspace status files: {', '.join(archived)}")
        else:
            print("- no workspace status files needed archiving")
    print("")
    print("Next step:")
    print(
        "python -m src.ztare.validator.autoresearch_loop "
        "--project eu_union_stability "
        "--rubric eu_union_integration "
        "--iters 3 "
        "--mutator_model claude "
        "--judge_model claude "
        "--deterministic_score_gates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
