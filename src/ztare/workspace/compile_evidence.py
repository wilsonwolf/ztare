import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anthropic
from google import genai
from openai import OpenAI

from src.ztare.common import utils
from src.ztare.common.paths import PROJECTS_DIR, PROMPTS_DIR, REPO_ROOT


ROOT_DIR = REPO_ROOT

MODEL_MAP = {
    "gemini": "gemini-2.5-flash",
    "claude": "claude-sonnet-4-6",
    "claude-opus": "claude-opus-4-6",
    "gpt4o": "gpt-4o",
}

TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".json",
    ".csv",
    ".tsv",
    ".yaml",
    ".yml",
    ".html",
    ".htm",
    ".xml",
    ".py",
    ".js",
    ".ts",
}

DEBUG = False


def dbg(msg: str) -> None:
    if not DEBUG:
        return
    ts = time.strftime("%H:%M:%S")
    print(f"[compile_evidence {ts}] {msg}", file=sys.stderr)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(read_text(path))


def load_prompt(name: str) -> str:
    return read_text(PROMPTS_DIR / name).strip()


def resolve_project_dir(project_arg: str) -> Path:
    candidate = Path(project_arg)
    if candidate.exists():
        return candidate.resolve()
    fallback = PROJECTS_DIR / project_arg
    if fallback.exists():
        return fallback.resolve()
    raise FileNotFoundError(f"Project not found: {project_arg}")


class LLMClient:
    def __init__(self, model_family: str):
        if model_family not in MODEL_MAP:
            raise ValueError(f"Unsupported model family: {model_family}")
        self.model_family = model_family
        self.model_id = MODEL_MAP[model_family]
        self.gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) if os.environ.get("GEMINI_API_KEY") else None
        self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")) if os.environ.get("ANTHROPIC_API_KEY") else None
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) if os.environ.get("OPENAI_API_KEY") else None

    def _call_once(self, prompt: str) -> str:
        if self.model_family == "gemini":
            if not self.gemini_client:
                raise RuntimeError("GEMINI_API_KEY is not set.")
            response = self.gemini_client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        if self.model_family in {"claude", "claude-opus"}:
            if not self.anthropic_client:
                raise RuntimeError("ANTHROPIC_API_KEY is not set.")
            message = self.anthropic_client.messages.create(
                model=self.model_id,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        if self.model_family == "gpt4o":
            if not self.openai_client:
                raise RuntimeError("OPENAI_API_KEY is not set.")
            response = self.openai_client.chat.completions.create(
                model=self.model_id,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        raise ValueError(f"Unsupported model family: {self.model_family}")

    def call(self, prompt: str, retries: int = 3) -> str:
        last_error: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                dbg(f"LLM call: family={self.model_family} model={self.model_id} attempt={attempt}/{retries}")
                return self._call_once(prompt)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                dbg(f"LLM call failed: attempt={attempt}/{retries} error={type(exc).__name__}: {exc}")
                if attempt == retries:
                    break
                time.sleep(5 * attempt)
        raise RuntimeError(f"LLM call failed after {retries} attempts: {last_error}") from last_error


def collect_sources(
    raw_dir: Path,
    max_files: int,
    max_chars_per_file: int,
    max_total_chars: int,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings: List[str] = []
    sources: List[Dict[str, Any]] = []
    total_chars = 0

    all_files = sorted(path for path in raw_dir.rglob("*") if path.is_file())
    supported_files = [path for path in all_files if path.suffix.lower() in TEXT_EXTENSIONS]
    skipped_files = [path for path in all_files if path.suffix.lower() not in TEXT_EXTENSIONS]

    if skipped_files:
        warnings.append(
            f"Skipped {len(skipped_files)} non-text files. Convert PDFs/images to markdown or text before compiling evidence."
        )

    for idx, path in enumerate(supported_files[:max_files], start=1):
        raw_text = read_text(path).strip()
        if not raw_text:
            warnings.append(f"Skipped empty file: {path.relative_to(raw_dir)}")
            continue

        remaining = max_total_chars - total_chars
        if remaining <= 0:
            warnings.append("Stopped ingest because max_total_chars budget was reached.")
            break

        trimmed = raw_text[: min(max_chars_per_file, remaining)]
        truncated = len(trimmed) < len(raw_text)
        if truncated:
            warnings.append(f"Truncated {path.relative_to(raw_dir)} to {len(trimmed)} characters.")

        source = {
            "source_id": f"S{idx:03d}",
            "path": str(path.relative_to(raw_dir)),
            "kind": path.suffix.lower().lstrip(".") or "text",
            "chars_used": len(trimmed),
            "truncated": truncated,
            "content": trimmed,
        }
        sources.append(source)
        total_chars += len(trimmed)

    if len(supported_files) > max_files:
        warnings.append(
            f"Read only the first {max_files} supported files out of {len(supported_files)}. Increase --max-files if needed."
        )

    return sources, warnings


def build_prompt(project_name: str, compiler_date: str, sources: List[Dict[str, Any]]) -> str:
    sections = [load_prompt("compile_evidence.md"), f"Project name: {project_name}", f"Compiler date: {compiler_date}", "Raw sources:"]
    for source in sources:
        sections.extend(
            [
                f"### SOURCE {source['source_id']}",
                f"Path: {source['path']}",
                f"Kind: {source['kind']}",
                f"Truncated: {'yes' if source['truncated'] else 'no'}",
                "Contents:",
                source["content"],
            ]
        )
    return "\n\n".join(sections)


def format_source_ids(source_ids: List[str]) -> str:
    cleaned = [sid for sid in source_ids if sid]
    return ", ".join(cleaned) if cleaned else "none"


def render_evidence_markdown(packet: Dict[str, Any], project_name: str, compiler_date: str) -> str:
    lines: List[str] = [
        f"{project_name.upper()} — COMPILED EVIDENCE ({compiler_date})",
        "",
        "This file is a structured evidence brief for adversarial validation.",
        "It preserves contradictions and unknowns instead of smoothing them away.",
        "",
        "# 1. IMMUTABLE GROUND TRUTH",
    ]

    ground_truth = packet.get("immutable_ground_truth", [])
    if ground_truth:
        for item in ground_truth:
            statement = item.get("statement", "").strip()
            strength = item.get("strength", "").strip()
            source_ids = format_source_ids(item.get("source_ids", []))
            if statement:
                lines.append(f"- {statement} [Strength: {strength}; Sources: {source_ids}]")
    else:
        lines.append("- None identified.")

    lines.extend(["", "# 2. NUMERICAL RANGES & CONSTRAINTS (LOAD-BEARING VARIABLES / CONSTRAINTS)"])
    constraints = packet.get("numerical_ranges_and_constraints", [])
    if constraints:
        for item in constraints:
            name = item.get("name", "").strip()
            value_or_range = item.get("value_or_range", "").strip()
            units = item.get("units", "").strip()
            kind = item.get("kind", "").strip()
            notes = item.get("notes", "").strip()
            source_ids = format_source_ids(item.get("source_ids", []))
            value_part = value_or_range or "unspecified"
            unit_part = f" {units}" if units and units not in {"n/a", "none"} else ""
            note_part = f" | Notes: {notes}" if notes else ""
            lines.append(f"- {name}: {value_part}{unit_part} | Kind: {kind} | Sources: {source_ids}{note_part}")
    else:
        lines.append("- None identified.")

    lines.extend(["", "# 3. IDENTIFIED CONTRADICTIONS"])
    contradictions = packet.get("identified_contradictions", [])
    if contradictions:
        for item in contradictions:
            topic = item.get("topic", "").strip()
            claim_a = item.get("claim_a", "").strip()
            claim_b = item.get("claim_b", "").strip()
            why_it_matters = item.get("why_it_matters", "").strip()
            src_a = format_source_ids(item.get("source_ids_a", []))
            src_b = format_source_ids(item.get("source_ids_b", []))
            lines.append(f"- {topic}")
            lines.append(f"  - Claim A: {claim_a} [Sources: {src_a}]")
            lines.append(f"  - Claim B: {claim_b} [Sources: {src_b}]")
            if why_it_matters:
                lines.append(f"  - Why it matters: {why_it_matters}")
    else:
        lines.append("- None identified.")

    lines.extend(["", "# 4. EPISTEMIC VOIDS (OPEN PROBLEMS / UNKNOWNS)"])
    voids = packet.get("epistemic_voids", [])
    if voids:
        for item in voids:
            unknown = item.get("unknown", "").strip()
            why_it_matters = item.get("why_it_matters", "").strip()
            blocking = item.get("blocking", "").strip()
            lines.append(f"- {unknown}")
            if why_it_matters:
                lines.append(f"  - Why it matters: {why_it_matters}")
            if blocking:
                lines.append(f"  - Blocking effect: {blocking}")
    else:
        lines.append("- None identified.")

    lines.extend(["", "# 5. PROVENANCE"])
    provenance = packet.get("provenance", [])
    if provenance:
        for item in provenance:
            source_id = item.get("source_id", "").strip()
            path = item.get("path", "").strip()
            kind = item.get("kind", "").strip()
            summary = item.get("summary", "").strip()
            lines.append(f"- {source_id} | {path} | {kind}")
            if summary:
                lines.append(f"  - Summary: {summary}")
    else:
        lines.append("- None identified.")

    lines.extend(["", "# 6. CANDIDATE CLAIMS TO TEST"])
    claims = packet.get("candidate_claims_to_test", [])
    if claims:
        for idx, item in enumerate(claims, start=1):
            claim = item.get("claim", "").strip()
            why_testable = item.get("why_testable", "").strip()
            depends_on = [dep for dep in item.get("depends_on", []) if dep]
            source_ids = format_source_ids(item.get("source_ids", []))
            priority = item.get("priority", "").strip()
            lines.append(f"{idx}. {claim}")
            if why_testable:
                lines.append(f"   Why testable: {why_testable}")
            if depends_on:
                lines.append(f"   Depends on: {', '.join(depends_on)}")
            lines.append(f"   Priority: {priority} | Sources: {source_ids}")
    else:
        lines.append("- None identified.")

    return "\n".join(lines).strip() + "\n"


def validate_packet_shape(packet: Dict[str, Any]) -> None:
    required_keys = [
        "project",
        "compiler_summary",
        "immutable_ground_truth",
        "numerical_ranges_and_constraints",
        "identified_contradictions",
        "epistemic_voids",
        "provenance",
        "candidate_claims_to_test",
    ]
    missing = [key for key in required_keys if key not in packet]
    if missing:
        raise ValueError(f"Compiled evidence is missing required keys: {', '.join(missing)}")


def load_workspace_packet(workspace_dir: Path) -> Dict[str, Any]:
    snapshot_path = workspace_dir / "workspace_snapshot.json"
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Workspace snapshot not found: {snapshot_path}")
    packet = read_json(snapshot_path)
    validate_packet_shape(packet)
    return packet


def compile_from_raw(
    *,
    project_dir: Path,
    raw_dir: Path,
    model: str,
    max_files: int,
    max_chars_per_file: int,
    max_total_chars: int,
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw source directory not found: {raw_dir}")

    sources, warnings = collect_sources(
        raw_dir=raw_dir,
        max_files=max_files,
        max_chars_per_file=max_chars_per_file,
        max_total_chars=max_total_chars,
    )
    if not sources:
        raise RuntimeError(f"No supported text-like source files found in {raw_dir}")

    compiler_date = time.strftime("%B %d, %Y")
    prompt = build_prompt(project_dir.name, compiler_date, sources)
    dbg(f"Source count={len(sources)} prompt_chars={len(prompt)}")

    llm = LLMClient(model)
    raw_response = llm.call(prompt)
    packet = utils.parse_llm_json(raw_response)
    validate_packet_shape(packet)

    manifest = {
        "project_dir": str(project_dir),
        "mode": "raw",
        "raw_dir": str(raw_dir),
        "model_family": model,
        "model_id": MODEL_MAP[model],
        "generated_on": compiler_date,
        "prompt_path": str(PROMPTS_DIR / "compile_evidence.md"),
        "source_count": len(sources),
        "sources": [{k: v for k, v in source.items() if k != "content"} for source in sources],
        "warnings": warnings,
    }
    evidence_text = render_evidence_markdown(packet, project_dir.name, compiler_date)
    return packet, manifest, evidence_text


def compile_from_workspace(
    *,
    project_dir: Path,
    workspace_dir: Path,
) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    compiler_date = time.strftime("%B %d, %Y")
    packet = copy.deepcopy(load_workspace_packet(workspace_dir))

    meta_path = workspace_dir / "workspace_meta.json"
    source_index_path = workspace_dir / "source_index.json"
    manifest: Dict[str, Any] = {
        "project_dir": str(project_dir),
        "mode": "workspace",
        "workspace_dir": str(workspace_dir),
        "generated_on": compiler_date,
        "source_count": 0,
        "warnings": [],
    }
    if meta_path.exists():
        manifest["workspace_meta"] = read_json(meta_path)
    if source_index_path.exists():
        index_payload = read_json(source_index_path)
        sources = index_payload.get("sources", [])
        manifest["sources"] = sources
        manifest["source_count"] = len(sources)

    evidence_text = render_evidence_markdown(packet, project_dir.name, compiler_date)
    return packet, manifest, evidence_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile raw sources or a workspace snapshot into a structured evidence.txt for ZTARE.")
    parser.add_argument("--project", required=True, help="Project name under projects/ or an explicit project path.")
    parser.add_argument("--raw-dir", help="Optional explicit raw source directory. Defaults to <project>/raw.")
    parser.add_argument("--workspace-dir", help="Optional explicit workspace directory. Defaults to <project>/workspace.")
    parser.add_argument(
        "--mode",
        choices=["auto", "workspace", "raw"],
        default="auto",
        help="Compilation mode. 'auto' prefers workspace/ when present, otherwise falls back to raw/.",
    )
    parser.add_argument("--model", default="gemini", choices=sorted(MODEL_MAP.keys()))
    parser.add_argument(
        "--output",
        help="Optional explicit evidence output path. Defaults to <project>/compiled_evidence.txt.",
    )
    parser.add_argument(
        "--packet-output",
        help="Optional explicit JSON packet output path. Defaults to <project>/compiled_evidence_packet.json.",
    )
    parser.add_argument(
        "--provenance-output",
        help="Optional explicit compiler provenance output path. Defaults to <project>/compiled_evidence_provenance.json.",
    )
    parser.add_argument("--max-files", type=int, default=25, help="Maximum number of raw files to ingest.")
    parser.add_argument(
        "--max-chars-per-file",
        type=int,
        default=12000,
        help="Maximum characters to read from each source file.",
    )
    parser.add_argument(
        "--max-total-chars",
        type=int,
        default=100000,
        help="Maximum total character budget across all ingested sources.",
    )
    parser.add_argument("--debug", action="store_true", help="Print debug details to stderr.")
    args = parser.parse_args()

    global DEBUG
    DEBUG = args.debug

    project_dir = resolve_project_dir(args.project)
    raw_dir = Path(args.raw_dir).resolve() if args.raw_dir else project_dir / "raw"
    workspace_dir = Path(args.workspace_dir).resolve() if args.workspace_dir else project_dir / "workspace"

    output_path = Path(args.output).resolve() if args.output else project_dir / "compiled_evidence.txt"
    packet_output_path = (
        Path(args.packet_output).resolve() if args.packet_output else project_dir / "compiled_evidence_packet.json"
    )
    provenance_output_path = (
        Path(args.provenance_output).resolve()
        if args.provenance_output
        else project_dir / "compiled_evidence_provenance.json"
    )

    use_workspace = False
    if args.mode == "workspace":
        use_workspace = True
    elif args.mode == "raw":
        use_workspace = False
    else:
        use_workspace = (workspace_dir / "workspace_snapshot.json").exists()

    if use_workspace:
        packet, compiler_manifest, evidence_text = compile_from_workspace(
            project_dir=project_dir,
            workspace_dir=workspace_dir,
        )
    else:
        packet, compiler_manifest, evidence_text = compile_from_raw(
            project_dir=project_dir,
            raw_dir=raw_dir,
            model=args.model,
            max_files=args.max_files,
            max_chars_per_file=args.max_chars_per_file,
            max_total_chars=args.max_total_chars,
        )

    write_text(output_path, evidence_text)
    write_json(packet_output_path, packet)
    compiler_manifest["output_path"] = str(output_path)
    compiler_manifest["packet_output_path"] = str(packet_output_path)
    write_json(provenance_output_path, compiler_manifest)

    print(f"Evidence: {output_path}")
    print(f"Evidence packet: {packet_output_path}")
    print(f"Compiler provenance: {provenance_output_path}")
    print(f"Mode: {'workspace' if use_workspace else 'raw'}")
    warnings = compiler_manifest.get("warnings", [])
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
