import os
import json
import subprocess
import time
import shutil
from pathlib import Path
import argparse
import sys
from datetime import datetime
from google import genai
from google.genai import types
import anthropic
from openai import OpenAI
from src.ztare.common import utils
from src.ztare.common.paths import PROJECTS_DIR, RUBRICS_DIR
import re
import concurrent.futures
from src.ztare.primitives.primitive_library import format_transfer_hypotheses, retrieve_primitives
from src.ztare.validator.mutation_contract import (
    MutationMismatchCode,
    approved_primitive_keys,
    evaluate_mutation_declaration,
    parse_mutation_declaration,
)
from src.ztare.validator.runner_selection import CandidateScopeVerdict, evaluate_candidate_selection
from src.ztare.validator.v4_family import is_v4_family_project
from src.ztare.validator.information_yield import (
    IterationSignal,
    LoopControlAction,
    evaluate_information_yield,
)

SESSION_TOKENS = 0

# 1. Setup CLI Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--rubric", required=True)
parser.add_argument("--dynamic", action="store_true")
parser.add_argument("--iters", type=int, default=10, help="Number of iterations to run")
parser.add_argument(
    "--auto-evolve",
    action="store_true",
    help="Level 5: AI autonomously rewrites its rubric upon reaching a high score.",
)
parser.add_argument(
    "--mutator_model",
    type=str,
    default="gemini",
    choices=["gemini", "claude", "claude-opus", "gpt4o"],
    help="Model family to use as Mutator.",
)
parser.add_argument(
    "--judge_model",
    type=str,
    default="gemini",
    choices=["gemini", "claude", "claude-opus", "gpt4o"],
    help="Model family to use as Firing Squad and Meta-Judge.",
)
parser.add_argument(
    "--use_primitives",
    action="store_true",
    help="Retrieve approved adversarial precedents for attacker/judge prompts.",
)
parser.add_argument(
    "--use_mutator_primitives",
    action="store_true",
    help="Also expose retrieved transfer hypotheses to the mutator. Off by default.",
)
parser.add_argument(
    "--use_transfer_hypotheses",
    action="store_true",
    help="Alias for --use_mutator_primitives. Expose retrieved transfer hypotheses to the mutator.",
)
parser.add_argument(
    "--primitive_top_k",
    type=int,
    default=3,
    help="Maximum number of approved primitives to retrieve when primitive support is enabled.",
)
parser.add_argument(
    "--deterministic_score_gates",
    action="store_true",
    help="Use Python-enforced hard score gates in test_thesis.py instead of trusting raw LLM scores.",
)
parser.add_argument(
    "--runner_r1_contract",
    action="store_true",
    help="Require a declaration-first MutationDeclaration header before each mutator thesis body.",
)
args = parser.parse_args()
if getattr(args, "use_transfer_hypotheses", False):
    args.use_mutator_primitives = True
if args.use_mutator_primitives:
    args.use_primitives = True
if is_v4_family_project(args.project) and not args.deterministic_score_gates:
    args.deterministic_score_gates = True
    print(f"INFO: Enforcing --deterministic_score_gates for V4-family project [{args.project}].")
if is_v4_family_project(args.project) and not args.runner_r1_contract:
    args.runner_r1_contract = True
    print(f"INFO: Enforcing --runner_r1_contract for V4-family project [{args.project}].")

gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) if os.environ.get("OPENAI_API_KEY") else None

# Keep legacy `client` pointing to Gemini — Firing Squad and Meta-Judge always use it
client = gemini_client


def _load_v4_stage_index() -> int | None:
    if not is_v4_family_project(args.project):
        return None
    state_path = Path("projects") / args.project / "meta_runner_state.json"
    if not state_path.exists():
        return None
    try:
        return json.loads(state_path.read_text()).get("current_stage")
    except Exception:
        return None

ITERATIONS = args.iters

# Resolve Mutator model ID from --mutator_model flag
_MODEL_MAP = {
    "gemini": "gemini-2.5-flash",
    "claude": "claude-sonnet-4-6",
    "claude-opus": "claude-opus-4-6",
    "gpt4o": "gpt-4o",
}
MUTATOR_MODEL_ID = _MODEL_MAP[args.mutator_model]
JUDGE_MODEL_ID = _MODEL_MAP[args.judge_model]
# Escalation model follows the mutator family
_DIRECTOR_MAP = {
    "gemini": "gemini-3.1-pro-preview",
    "claude": "claude-opus-4-6",
    "claude-opus": "claude-opus-4-6",
    "gpt4o": "o1",
}
DIRECTOR_MODEL_ID = _DIRECTOR_MAP[args.mutator_model]

print(f"🧠 Mutator: {MUTATOR_MODEL_ID} | Judge: {JUDGE_MODEL_ID}")

# Paths
PROJECT_DIR = str(PROJECTS_DIR / args.project)
HISTORY_DIR = f"{PROJECT_DIR}/history"
THESIS_PATH = f"{PROJECT_DIR}/thesis.md"
WORKING_PATH = f"{PROJECT_DIR}/current_iteration.md"
EVIDENCE_PATH = f"{PROJECT_DIR}/evidence.txt"
AXIOM_PATH = f"{PROJECT_DIR}/verified_axioms.json"
MAIN_RUBRIC_PATH = RUBRICS_DIR / f"{args.rubric}.json"


def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()


def write_file(filepath, content):
    with open(filepath, "w") as f:
        f.write(content)


def _project_state_paths(project_dir: str) -> tuple[str, ...]:
    return (
        THESIS_PATH,
        WORKING_PATH,
        f"{project_dir}/test_model.py",
        EVIDENCE_PATH,
        f"{project_dir}/probability_dag.json",
    )


def _capture_project_state(paths: tuple[str, ...]) -> dict[str, str | None]:
    snapshot: dict[str, str | None] = {}
    for path in paths:
        snapshot[path] = read_file(path) if os.path.exists(path) else None
    return snapshot


def _restore_project_state(snapshot: dict[str, str | None]) -> None:
    for path, content in snapshot.items():
        if content is None:
            if os.path.exists(path):
                os.remove(path)
            continue
        write_file(path, content)


def _latest_debate_log_text(project_dir: str) -> str:
    project_path = Path(project_dir)
    candidates = sorted(project_path.glob("debate_log_iter_*.md"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        return ""
    return candidates[-1].read_text()


def _dynamic_rubric_path(project: str) -> Path:
    return RUBRICS_DIR / f"dynamic_{project}.json"


def _load_current_committee_digest(project: str) -> str:
    rubric_path = _dynamic_rubric_path(project)
    if not rubric_path.exists():
        return ""
    try:
        payload = json.loads(rubric_path.read_text())
    except Exception:
        return ""
    metadata = payload.get("metadata", {})
    instantiation_record = metadata.get("instantiation_record", {})
    digest = instantiation_record.get("committee_digest", "")
    return digest if isinstance(digest, str) else ""


def _write_latest_information_yield(
    workspace_dir: Path,
    *,
    signal: IterationSignal,
    decision,
) -> None:
    write_file(
        str(workspace_dir / "latest_information_yield.json"),
        json.dumps(
            {
                "signal": {
                    "iteration_index": signal.iteration_index,
                    "score": signal.score,
                    "weakest_point": signal.weakest_point,
                    "score_improved": signal.score_improved,
                    "runtime_failure": signal.runtime_failure,
                    "novel_attack_ids": list(signal.novel_attack_ids),
                    "novel_hinge_ids": list(signal.novel_hinge_ids),
                    "novel_primitive_ids": list(signal.novel_primitive_ids),
                    "verified_axioms_added": signal.verified_axioms_added,
                    "mutation_r1_mismatch": signal.mutation_r1_mismatch,
                    "claim_delta_type": signal.claim_delta_type,
                    "committee_digest": signal.committee_digest,
                    "prior_committee_digest": signal.prior_committee_digest,
                },
                "decision": {
                    "action": decision.action.value,
                    "stagnant_window": decision.stagnant_window,
                    "rationale": decision.rationale,
                },
            },
            indent=2,
        ),
    )


def _extract_mutation_declaration(raw_text: str):
    match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if not match:
        return None, raw_text
    declaration_payload = utils.parse_llm_json(match.group(1))
    declaration = parse_mutation_declaration(declaration_payload)
    remaining = (raw_text[: match.start()] + raw_text[match.end() :]).strip()
    return declaration, remaining


def _prepare_mutation_candidate(
    *,
    raw_text: str,
    current_thesis: str,
    current_test_model: str,
):
    declaration = None
    working_text = raw_text
    if args.runner_r1_contract:
        declaration, working_text = _extract_mutation_declaration(raw_text)
        if declaration is None:
            raise ValueError("Missing required `MutationDeclaration` JSON header.")

    code_match = re.search(r"```python\n(.*?)\n```", working_text, re.DOTALL)
    python_code = code_match.group(1) if code_match else None
    clean_thesis = (
        working_text.replace(code_match.group(0), "").strip()
        if code_match
        else working_text.strip()
    )

    validation_record = None
    if declaration is not None:
        changed_paths: list[str] = []
        if clean_thesis.strip() != current_thesis.strip():
            changed_paths.append(f"projects/{args.project}/thesis.md")
        if python_code is not None and python_code.strip() != current_test_model.strip():
            changed_paths.append(f"projects/{args.project}/test_model.py")
        validation_record = evaluate_mutation_declaration(
            declaration,
            tuple(changed_paths),
            before_text=current_thesis,
            after_text=clean_thesis,
            approved_primitive_keys=approved_primitive_keys(),
        )

    return declaration, validation_record, clean_thesis, python_code, working_text


def _call_anthropic(prompt, model_id):
    """Call Anthropic Claude. Returns response text."""
    message = anthropic_client.messages.create(
        model=model_id,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(prompt, model_id):
    """Call OpenAI. Returns response text."""
    # o1/o3 models use max_completion_tokens instead of max_tokens
    is_reasoning = model_id.startswith("o1") or model_id.startswith("o3")
    kwargs = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
    }
    if is_reasoning:
        kwargs["max_completion_tokens"] = 16000
    else:
        kwargs["max_tokens"] = 16000
    response = openai_client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def safe_mutate(prompt, config=None, model_id=MUTATOR_MODEL_ID):
    global SESSION_TOKENS

    with open(f"{PROJECT_DIR}/last_prompt_debug.txt", "w") as f:
        f.write(f"MODEL USED: {model_id}\n")
        f.write("=" * 30 + "\n")
        f.write(prompt)

    is_claude = model_id.startswith("claude")
    is_openai = model_id.startswith("gpt") or model_id.startswith("o1") or model_id.startswith("o3")

    """Retries for both 429 (Rate Limit) and 503 (Server Overload)."""
    for i in range(12):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            print(f"📡 [DEBUG] Dispatching Mutator request to {model_id}... (Attempt {i + 1})")
            start_time = time.time()

            if is_claude:
                future = executor.submit(_call_anthropic, prompt, model_id)
            elif is_openai:
                future = executor.submit(_call_openai, prompt, model_id)
            else:
                future = executor.submit(
                    client.models.generate_content,
                    model=model_id, contents=prompt, config=config
                )

            response = future.result(timeout=300)
            elapsed = time.time() - start_time
            print(f"✅ [DEBUG] Response received in {elapsed:.1f}s")

            if is_claude or is_openai:
                return response  # already a string

            if response.usage_metadata:
                SESSION_TOKENS += response.usage_metadata.total_token_count
            return response.text

        except concurrent.futures.TimeoutError:
            wait_time = (i + 1) * 15
            print(
                f"⚠️ Zombie Connection Killed. Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)
        except Exception as e:
            error_str = str(e)
            # Catch transient networking/Read errors (like Errno 54)
            is_transient_network_error = any(msg in error_str for msg in [
                "readerror", "connection reset", "broken pipe", "remoteprotocolerror"
            ])
            if "400" in error_str or "404" in error_str:
                print(f"❌ Configuration/Model Error: {e}")
                raise e
            # Catch 500, 502, 503, 504, 529 and 429 as transient retryable errors
            if any(code in error_str for code in ["429", "500", "502", "503", "504", "529", "overloaded"]) or is_transient_network_error:
                wait_time = (i + 1) * 20
                print(f"⚠️ API Transient Issue ({error_str[:15]}...). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Unhandled Exception: {error_str}")
                raise e
            
        finally:
            # CRITICAL FIX: Force thread abandonment on timeout
            executor.shutdown(wait=False, cancel_futures=True)
    raise Exception("Mutation failed after multiple retries.")


# --- CHANGED: Added model_id to the signature ---
def mutate_thesis(
    current_content,
    weakest_point,
    evidence,
    persona,
    stagnation_count,
    model_id=MUTATOR_MODEL_ID,
    failure_log=None,
):
    task_header = "TASK: Resolve the following Systemic Inconsistency:"
    pivot_instruction = ""
    primitive_context = ""
    axioms = []
    if os.path.exists(AXIOM_PATH):
        with open(AXIOM_PATH, "r") as f:
            axioms = json.load(f)

    axiom_str = "\n".join([f"- {a}" for a in axioms]) if axioms else "None yet."
    is_v4_project = is_v4_family_project(args.project)
    v4_stage_index = _load_v4_stage_index()
    style_guide = ""
    output_requirements = ""

    # --- DYNAMIC CONTEXT MANAGEMENT ---
    if is_v4_project:
        document_context = f"### CURRENT SYSTEM STATE (FOR ANALYSIS ONLY)\n{current_content}"
        if stagnation_count >= 3:
            task_header = "🚨 V4 DISCIPLINE OVERRIDE: BOUNDED KERNEL MUTATION 🚨"
            pivot_instruction = """
                ### V4 MUTATION DISCIPLINE
        The run is stagnating, but you are NOT allowed to execute a generic topological pivot.
        You must remain inside the active V4 target: semantic-gate stabilization.

        Allowed mutation surface:
        1. Refine typed semantic evidence fields.
        2. Refine Python-derived gate logic (`clear`, `fatal`, `unresolved`).
        3. Refine unresolved-handling rules.
        4. Preserve `HingeObject` and `ExploitFamilyTag` as interface stubs only.

        Forbidden mutation surface:
        - Do not invent a new grand architecture, marketplace, protocol layer, entropy engine, dispute engine, or governance economy.
        - Do not solve V4 by introducing a new abstract proxy variable detached from benchmark measurement.
        - Do not claim to fix `B`'s systematic misses in general.
        - Do not collapse systematic failure and semantic variance into one scalar notion of improvement.
        - Do not use blank-slate resets, domain shifts, symbolic theater, or laws-of-physics framing.

        Required orientation:
        - Stay close to the frozen Paper 2 benchmark obligations.
        - Prefer narrower, more auditable logic over elegant global pivots.
        - If the current mechanism fails, mutate the gate contract, not the ontology of the whole project.
        """
        else:
            task_header = "TASK: Resolve the following Systemic Inconsistency:"

        style_guide = """
    V4 STYLE GUIDE:
        - NO METAPHORS.
        - NO generic topological pivots.
        - NO symbolic-mapping theater like forcing $Z = f(X, Y)$.
        - Keep the object of improvement narrow: semantic-gate stabilization only.
        - Quantitative claims must map to benchmark-visible outputs such as:
          * semantic gate flip rate
          * stable bad-case retention
          * good-control false-reject behavior
          * separated `t2_ai_inference` failure reporting
        - If you introduce a new structure, specify:
          * the typed fields
          * the Python decision rule
          * the exact failure mode it addresses
        - Maximize auditability, not conceptual grandeur.
        """
        if v4_stage_index == 3:
            style_guide += """
    STAGE 4 SCOPE ENFORCEMENT:
        - This stage is ONLY about Shadow Board behavior.
        - Score-bearing mutation surface is limited to:
          * fixed role catalog
          * role assignment behavior
          * arbiter activation semantics
          * typed-handoff recording / consumption behavior
        - If you notice upstream semantic-gate, whitelist, or quote-validation weaknesses, you may mention them only as logged architectural debt.
        - Those upstream findings are OUT OF SCOPE for this stage and must not be presented as the core fix.
        - Do not propose semantic-gate hardening, whitelist expansion, quote-validation changes, or any stage-1/2/3 mechanism edits.
        """
        output_requirements = """
    V4 OUTPUT REQUIREMENTS:
        - Provide exactly one Python code block for `test_model.py`.
        - The Python block should be a minimal architectural harness, not a fake full-benchmark simulator.
        - The harness should prove only deterministic gate derivation or interface behavior relevant to this seed.
        - Your prose should stay close to this structure:
          * Weakest Link
          * Core Claim
          * Minimal Mechanism
          * Interface Discipline
          * Falsifiable Prediction
          * Failure Condition
        """
        if v4_stage_index == 3:
            output_requirements += """
    STAGE 4 OUTPUT BOUNDARY:
        - The thesis must only make claims about board composition, assignment, arbiter behavior, or typed-handoff recording.
        - Do NOT claim stable adversarial coverage, whole-system robustness, or upstream trust repair.
        - Any upstream-stage weakness must be labeled `OUT-OF-SCOPE DEBT` and must not be the main thesis target.
        """
    elif stagnation_count >= 4:
        print("🚨 EMERGENCY MANDATE: EXECUTING TOPOLOGICAL PIVOT 🚨")
        print("🧹 Purging toxic axioms to allow true architectural reset...")
        
        if os.path.exists(AXIOM_PATH):
            shutil.copy(AXIOM_PATH, f"{AXIOM_PATH}.bak")
            os.remove(AXIOM_PATH) # Hide from test_thesis.py            
        axiom_str = "NONE. (Previous axioms purged due to topological pivot)."
        document_context = "🚨 [SYSTEM STATE PURGED]: Your previous logic was fundamentally and repeatedly rejected by the Auditor. You are starting from a BLANK SLATE. You must derive a new architecture using ONLY the Grounding Data and First Principles. Do NOT iterative-fix; RE-ENGINEER. 🚨"
        task_header = "🚨 EMERGENCY MANDATE: EXECUTE TOPOLOGICAL PIVOT 🚨"   
    elif stagnation_count >= 3:
        document_context = "🚨 [SYSTEM STATE PURGED]: Current logic has reached a terminal friction point. You must derive a NEW Transformation Function. 🚨"
        task_header = "🚨 EMERGENCY MANDATE: EXECUTE TOPOLOGICAL PIVOT 🚨"
    else:
        document_context = (
            f"### CURRENT SYSTEM STATE (FOR ANALYSIS ONLY)\n{current_content}"
        )

    if not is_v4_project and stagnation_count >= 3:
        pivot_instruction = """
                ### 🚨 METACOGNITIVE OVERRIDE: FIRST-PRINCIPLES RE-ENGINEERING 🚨
        The Auditor has identified a terminal friction in the current logic. You are forbidden from iterative refinement. You must execute a structural mutation using these Zero-Domain Heuristics:

        1. STATE INCOMPATIBILITY (Critique as Invariant): Treat the Auditor's critique as an immutable Physical Law of the environment. If this constraint is absolute, what entirely new System Architecture must be derived to reach the Target State ($Z$)?
        2. THE EIGENVALUE (Primary Degree of Freedom): Identify the single, irreducible variable where a change in state forces a deterministic reconfiguration of the entire system. Define the cascading logic-gates that follow this shift.
        3. ZERO-TRUST AUTOPSY (Failure Topology): Fast-forward to the state of System Collapse. Map the 3 specific nodes of failure. Erase the assumptions supporting those nodes and build a bypass that does not rely on their stability.
        4. ENTROPY STRIPPING (Mercenary Utility): Remove all qualitative descriptors and sentimental "narratives." Evaluate the system strictly as a Mercerary Arbitrage. What cold, quantifiable Utility Vector is actually being transferred between participants?
        5. DIMENSIONALITY SHIFT (Category Defiance): If the problem is unsolvable in the current Domain (e.g., as an 'Object' or 'Product'), you must shift the system to a higher Dimensionality (e.g., a 'Service', 'Network', or 'Annuity').
        6. RECIPROCAL OPERATIONS (The Base Variable Attack): If the primary Vector ($X$) required for the goal is locked by systemic friction, identify the Reciprocal Variable ($Y$) that can be manipulated to force the same Resultant State ($Z$). If you cannot expand the Numerator, you must aggressively contract the Denominator.
        7. ADVERSARIAL STRESS-TEST (Archetype Shadow Board): Subject the new logic to a board of three opposing archetypes: The Forensic Skeptic (Entropy Hunter), The Minimalist Purist (Complexity Hunter), and The Disruptive Interloper (Moat Hunter).
        8. SYSTEMIC BACK-PRESSURE (The Success-Liability): If the mechanism functions perfectly, identify the new technical, legal, or competitive resistance created by that very success. Solve for this "Success Trap" within the primary architecture.
        9. COERCIVE VECTORS (Asymmetric Leverage): Identify the specific participant with the absolute power to Veto the State-Change. You must derive a mechanism of Asymmetric Leverage (e.g., legal, mechanical, or existential) that makes the current state more painful for the Veto Player than the transition to the Target State. Logic is a suggestion; leverage is a mandate.
        10. COEFFICIENT OF FRICTION (Inertia Constant): Assume a non-zero systemic resistance factor. Quantify how this friction (e.g., implementation lag) degrades Velocity ($V$) and forces a near-term performance trough.
        
        TASK: Execute a structural mutation. Concede the lost state, apply the new mechanism, and define the exact systemic trade-offs. 
        """
    elif not is_v4_project:
        style_guide = """
    STRICT STYLE GUIDE & LAWS OF PHYSICS: 
        - SYMBOLIC MAPPING: You must map the core problem to the equation $Z = f(X, Y)$. Explicitly define $X$ (the blocked variable) and $Y$ (the leverage variable). 
        - ARITHMETIC TRANSPARENCY: All quantitative claims must be supported by a balanced equation.
        - LOAD-BEARING VARIABLES (MANDATORY): Before your Python block, you MUST provide a markdown table titled "LOAD-BEARING VARIABLES". List every physical constant, financial metric, or baseline assumption you use, and state its exact real-world value. The Attackers will Google these values to verify them. NO HALLUCINATED ENTITY CONSTANTS.
        - STRUCTURAL ARBITRAGE: You are REQUIRED to introduce systemic bypasses, reciprocal leverage points, or category shifts to resolve the Auditor's critique.
        - CONSERVATION OF TRADE-OFFS: A system cannot increase Velocity ($V$) without a proportional increase in Energy ($E$) or decrease in Mass ($M$). You must explicitly state the new operational drag introduced by the pivot.
        - GATEKEEPER REALITY: Identify the entity with the Absolute Veto (The Bottleneck). Define the Asymmetric Leverage required to force a state-change.

        - NO METAPHORS: You are strictly FORBIDDEN from using metaphorical framing (e.g., "The universe is a compiler" or "The company is a ship"). 
        - FALSIFIABILITY: You MUST output a specific, numerical, and testable prediction. 
          * For Science: Predict a specific laboratory result or numerical variance in a physical constant.
          * For Business: Predict a specific financial metric (e.g., EBITDA margin, $t$-month payback, or churn rate) under a defined shock.
        - UNIT TEST REQUIREMENT: Your `test_model.py` must contain 'assert' statements that would FAIL if this prediction is not met.   
        TERMINAL MATH PROTOCOL:
        - If your previous Python execution returned `NaN`, `inf`, or a `DimensionalityError`, your core equation ($Z = f(X, Y)$) is mathematically insolvent. You are FORBIDDEN from attempting to patch it using Python `try/except` blocks or `float64` limits. You must discard the mathematical relationship entirely, identify a different limiting constraint (e.g., thermal limits instead of spatial limits, or liquidity constraints instead of TAM), and derive a fundamentally new equation.    
        """
        output_requirements = """
    CRITICAL OUTPUT REQUIREMENT (THE LOGIC DAG):
        - You must output a "Logic DAG" (Directed Acyclic Graph) at the bottom of your response in markdown format. 
        - List your Axioms (Premises) and show exactly how they link to your Conclusion.
        - Format example:
        - [Axiom 1: Existing constraint] -> [Axiom 2: New leverage point] -> [Conclusion: Resultant state Z]
        - If any node in your graph requires a leap of faith, the Auditor will fail you.        
        
    
    FORMATTING:
        - MANDATORY: You must provide exactly one Python code block (wrapped in ```python) that constitutes the test_model.py script. This script must be standalone and execute all necessary assertions.
        - QUANTITATIVE GUARDRAIL (MANDATORY): Your `test_model.py` MUST strictly enforce mathematical reality based on the domain:
          * FOR PHYSICS/SCIENCE: You must use the `pint` library (`from pint import UnitRegistry`) to assign dimensions to all physical variables. Any Category Error (e.g., adding bits to watts) must throw a `DimensionalityError`.
          * FOR BUSINESS/FINANCE/STRATEGY: You must use strict financial logic (e.g., NPV, IRR, ROI). You must explicitly define your cell-logic and assumptions. If the math relies on infinite TAM, ignores the cost of capital, or contains unit mismatches, the `assert` statements must auto-fail. Do not use `pint` for finance.
        - Maximize Information-to-Word ratio. Scannable, scientific, scrupulous.
        - Direct Answers -> Symbolic Proof -> Quantitative Comparison.
        """

    failure_context = ""
    if failure_log:
        failure_context = f"### ⚠️ RECENT FAILURE ANALYSIS\nYour last attempt failed. The Auditor's critique was: {failure_log}\nDo NOT repeat this mistake."

    if args.use_mutator_primitives:
        transfer_candidates = retrieve_primitives(
            "\n".join(
                [
                    weakest_point or "",
                    evidence[:6000],
                    current_content[:4000],
                    persona[:1500],
                ]
            ),
            top_k=args.primitive_top_k,
        )
        if transfer_candidates:
            primitive_context = (
                format_transfer_hypotheses(transfer_candidates)
                + "\n\nTRANSFER RULES:\n"
                + "- These hypotheses are not evidence and not axioms.\n"
                + "- Use them only if you can justify domain fit in the thesis text.\n"
                + "- If you use one, include a short section titled 'TRANSFER JUSTIFICATION'.\n"
                + "- Your falsification suite must explicitly test the transfer condition you rely on.\n"
            )

    base_prompt = f"""{persona}
    
    AXIOMS (PREVIOUSLY VERIFIED TRUTHS):
    {axiom_str}
    
    CRITICAL CONSTRAINT (THE AXIOMATIC GATE): 
    The axioms above have been verified by the Firing Squad and the Meta-Judge. 
    You are FORBIDDEN from contradicting them within their original domain. 
    HOWEVER, if you are executing a TOPOLOGICAL PIVOT, you are granted 'Axiom Retirement' authority. If an axiom is mathematically true but structurally irrelevant to the new domain (e.g., applying Black Hole limits to a biological brain), you must explicitly drop it by writing: "RETIRED AXIOM: [Axiom Concept] - [Reason it does not apply to this scale/domain]."
    
    
    GROUNDING DATA (IMMUTABLE CONSTANTS): 
    {evidence}
    
    {document_context}
    {failure_context}
    {primitive_context}
    
    ---
    
    ### {task_header} 
    
    "THIS IS THE WEAKEST LINK IN THE CURRENT LOGIC CHAIN: {weakest_point}"

    {style_guide}
    {output_requirements}
    {pivot_instruction}
    """
    if args.runner_r1_contract:
        declaration_prompt = base_prompt + """
RUNNER R1 DECLARATION PHASE (MANDATORY):
- Return ONLY a single raw JSON object.
- Do NOT wrap it in markdown fences.
- Do NOT include any thesis prose, commentary, or Python.
- Commit the mutation declaration before the payload exists.

Required keys:
- `scope_delta`
- `claim_delta_type`
- `primitive_invoked`
- `touched_artifacts`

Allowed `scope_delta` values:
- `THESIS_ONLY`
- `TEST_HARNESS`
- `EVIDENCE_BOUNDARY`
- `RUBRIC_INTERFACE`
- `MULTI_ARTIFACT`

Allowed `claim_delta_type` values:
- `NARROWING`
- `WIDENING`
- `REFRAMING`

Allowed `touched_artifacts` values:
- `thesis.md`
- `current_iteration.md`
- `test_model.py`
- `evidence.txt`
- `rubric.json`
- `runner_runtime`
- `other`

`primitive_invoked` must be `null` or an approved primitive key if explicitly relied on.
"""
        declaration_text = safe_mutate(declaration_prompt, model_id=model_id)
        declaration_payload = utils.parse_llm_json(declaration_text)
        declaration = parse_mutation_declaration(declaration_payload)
        declaration_json = json.dumps(
            {
                "scope_delta": declaration.scope_delta.value,
                "claim_delta_type": declaration.claim_delta_type.value,
                "primitive_invoked": declaration.primitive_invoked,
                "touched_artifacts": [item.value for item in declaration.touched_artifacts],
            },
            indent=2,
        )
        payload_prompt = base_prompt + f"""
RUNNER R1 PAYLOAD PHASE:
- The declaration below is already committed and will be validated before the kernel sees your payload.
- You must honor it exactly.
- Do NOT output another JSON declaration block.
- Output only the thesis / harness payload.

COMMITTED DECLARATION:
```json
{declaration_json}
```
"""
        payload_text = safe_mutate(payload_prompt, model_id=model_id)
        return f"```json\n{declaration_json}\n```\n\n{payload_text.strip()}"

    prompt = base_prompt
    if args.runner_r1_contract:
        prompt += """

RUNNER R1 DECLARATION CONTRACT (MANDATORY):
- Your response must begin with exactly one ```json code block before any thesis prose.
- That JSON block must contain exactly these keys:
  - `scope_delta`
  - `claim_delta_type`
  - `primitive_invoked`
  - `touched_artifacts`
- Allowed `scope_delta` values:
  - `THESIS_ONLY`
  - `TEST_HARNESS`
  - `EVIDENCE_BOUNDARY`
  - `RUBRIC_INTERFACE`
  - `MULTI_ARTIFACT`
- Allowed `claim_delta_type` values:
  - `NARROWING`
  - `WIDENING`
  - `REFRAMING`
- Allowed `touched_artifacts` values:
  - `thesis.md`
  - `current_iteration.md`
  - `test_model.py`
  - `evidence.txt`
  - `rubric.json`
  - `runner_runtime`
  - `other`
- `primitive_invoked` must be `null` or an approved primitive key if you are explicitly relying on one.
- This declaration is a prior commitment. Do not generate the thesis first and then rationalize the declaration after the fact.
"""
    # --- CHANGED: Passing model_id through to safe_mutate ---
    return safe_mutate(prompt, model_id=model_id)


def evolve_rubric(current_rubric_data, winning_thesis):
    """Monotonic Constraint Ratcheting using Pro model."""
    prompt = f"""
    You are a superintelligence monitoring an epistemic optimization loop. 
    The system has successfully solved the current rubric:
    {json.dumps(current_rubric_data, indent=2)}
    
    WINNING THESIS:
    {winning_thesis}
    
    MANDATE (MONOTONIC RATCHETING):
    You must evolve the rubric to the next level of complexity.
    1. Apply Jacobi Inversion: What is the single largest unaddressed second-order consequence, biological reality, or edge-case created by this winning thesis?
    2. Write a NEW rubric. You MUST retain the ruthless spirit of the old criteria, but append ONE brutal new criterion targeting this specific vulnerability.
    3. DO NOT make the rubric easier. Do not allow 'Reward Hacking'.
    
    OUTPUT FORMAT:
    You must return a valid JSON object with exactly two keys:
    - "persona": A string detailing the adversarial persona.
    - "criteria": A JSON object containing key-value string pairs of the grading rules.
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )

    print("\n" + "·" * 40)
    print("🧠 DIRECTOR (PRO): EVOLVING RUBRIC...")
    response_text = safe_mutate(prompt, config=config, model_id=DIRECTOR_MODEL_ID)
    print("·" * 40 + "\n")
    return utils.parse_llm_json(response_text)


if __name__ == "__main__":
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

    # Unique ID for this run — prevents cross-run filename collisions
    RUN_ID = int(time.time())

    with open(MAIN_RUBRIC_PATH, "r") as f:
        rubric_data = json.load(f)

    evidence_text = read_file(EVIDENCE_PATH)
    shutil.copy(THESIS_PATH, WORKING_PATH)

    test_cmd = [
        sys.executable,
        "-m",
        "src.ztare.validator.test_thesis",
        "--project", args.project,
        "--rubric", args.rubric,
        "--judge_model", args.judge_model,
        "--mutator_model", args.mutator_model,
    ]
    if args.dynamic:
        test_cmd.append("--dynamic")
    if args.use_primitives:
        test_cmd.append("--use_primitives")
    if args.use_mutator_primitives:
        test_cmd.append("--use_mutator_primitives")
    if args.primitive_top_k:
        test_cmd.extend(["--primitive_top_k", str(args.primitive_top_k)])
    if args.deterministic_score_gates:
        test_cmd.append("--deterministic_score_gates")

# --- INITIALIZATION ---
if args.dynamic:
    print(
        f"🕵️  INITIALIZING COMMITTEE: Executing generate_committee.py for [{args.project}]..."
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.ztare.validator.generate_committee",
            "--project",
            args.project,
            *(["--use_primitives"] if args.use_primitives else []),
            "--primitive_top_k",
            str(args.primitive_top_k),
        ],
        check=True,
    )
subprocess.run(test_cmd, check=True)
with open("eval_results.json", "r") as f:
    res = json.load(f)

best_score = res["score"]
best_weakest_point = res["weakest_point"]
stagnation_count = 0
last_failure_reason = None
best_state = _capture_project_state(_project_state_paths(PROJECT_DIR))
iteration_history: list[IterationSignal] = []
pending_loop_action = LoopControlAction.CONTINUE
current_committee_digest = _load_current_committee_digest(args.project) if args.dynamic else ""

for i in range(ITERATIONS):
    print(
        f"\n--- Iteration {i + 1} (Score: {best_score} | Stagnation: {stagnation_count}) ---"
    )
    current_thesis = read_file(WORKING_PATH)
    current_mutator = MUTATOR_MODEL_ID
    iteration_prior_committee_digest = current_committee_digest
    if pending_loop_action == LoopControlAction.PIVOT_REQUIRED:
        print(
            "🚀 R4 PIVOT REQUIRED: Boosting Mutator to PRO..."
        )
        current_mutator = DIRECTOR_MODEL_ID

    if args.dynamic and pending_loop_action in {
        LoopControlAction.REFRESH_SPECIALISTS,
        LoopControlAction.PIVOT_REQUIRED,
    }:
        print(
            f"🚨 R4 ACTION {pending_loop_action.value}: Refreshing Specialized Firing Squad..."
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "src.ztare.validator.generate_committee",
                "--project",
                args.project,
                *(["--use_primitives"] if args.use_primitives else []),
                "--primitive_top_k",
                str(args.primitive_top_k),
            ],
            check=True,
        )
        current_committee_digest = _load_current_committee_digest(args.project)

    current_test_model = read_file(f"{PROJECT_DIR}/test_model.py") if os.path.exists(f"{PROJECT_DIR}/test_model.py") else ""
    workspace_dir = Path(PROJECT_DIR) / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    try:
        new_content = mutate_thesis(
            current_thesis,
            best_weakest_point,
            evidence_text,
            rubric_data["persona"],
            stagnation_count,
            model_id=current_mutator,
            failure_log=last_failure_reason,
        )
        mutation_declaration, mutation_validation, clean_thesis, python_code, full_candidate = _prepare_mutation_candidate(
            raw_text=new_content,
            current_thesis=current_thesis,
            current_test_model=current_test_model,
        )
    except Exception as exc:
        print(f"⚠️ Runner R1 rejection: {exc}")
        signal = IterationSignal(
            iteration_index=i + 1,
            score=best_score,
            weakest_point=f"Runner R1 rejection: {exc}",
            mutation_r1_mismatch=True,
            committee_digest=current_committee_digest,
            prior_committee_digest=iteration_prior_committee_digest,
        )
        iteration_history.append(signal)
        yield_decision = evaluate_information_yield(iteration_history)
        _write_latest_information_yield(workspace_dir, signal=signal, decision=yield_decision)
        last_failure_reason = f"Runner R1 rejection: {exc}"
        stagnation_count = yield_decision.stagnant_window
        pending_loop_action = yield_decision.action
        _restore_project_state(best_state)
        time.sleep(1)
        continue

    if mutation_declaration is not None:
        write_file(
            str(workspace_dir / "latest_mutation_declaration.json"),
            json.dumps(
                {
                    "scope_delta": mutation_declaration.scope_delta.value,
                    "claim_delta_type": mutation_declaration.claim_delta_type.value,
                    "primitive_invoked": mutation_declaration.primitive_invoked,
                    "touched_artifacts": [item.value for item in mutation_declaration.touched_artifacts],
                },
                indent=2,
            ),
        )
    if mutation_validation is not None:
        write_file(
            str(workspace_dir / "latest_mutation_validation.json"),
            json.dumps(
                {
                    "mismatch_code": mutation_validation.mismatch_code.value,
                    "declared_scope_delta": mutation_validation.declared_scope_delta.value,
                    "declared_claim_delta_type": mutation_validation.declared_claim_delta_type.value,
                    "declared_primitive_invoked": mutation_validation.declared_primitive_invoked,
                    "declared_touched_artifacts": [item.value for item in mutation_validation.declared_touched_artifacts],
                    "actual_touched_artifacts": [item.value for item in mutation_validation.actual_touched_artifacts],
                    "breadth_delta": mutation_validation.breadth_delta,
                    "rationale": mutation_validation.rationale,
                },
                indent=2,
            ),
        )

    if (
        mutation_validation is not None
        and mutation_validation.mismatch_code != MutationMismatchCode.CLEAN
    ):
        print(
            "⚠️ Runner R1 rejection: "
            f"{mutation_validation.mismatch_code.value} — {mutation_validation.rationale}"
        )
        signal = IterationSignal(
            iteration_index=i + 1,
            score=best_score,
            weakest_point=(
                f"Runner R1 mismatch {mutation_validation.mismatch_code.value}: "
                f"{mutation_validation.rationale}"
            ),
            mutation_r1_mismatch=True,
            claim_delta_type=mutation_declaration.claim_delta_type.value if mutation_declaration is not None else "",
            committee_digest=current_committee_digest,
            prior_committee_digest=iteration_prior_committee_digest,
        )
        iteration_history.append(signal)
        yield_decision = evaluate_information_yield(iteration_history)
        _write_latest_information_yield(workspace_dir, signal=signal, decision=yield_decision)
        last_failure_reason = (
            f"Runner R1 mismatch {mutation_validation.mismatch_code.value}: "
            f"{mutation_validation.rationale}"
        )
        stagnation_count = yield_decision.stagnant_window
        pending_loop_action = yield_decision.action
        _restore_project_state(best_state)
        time.sleep(1)
        continue

    write_file(WORKING_PATH, full_candidate)

    # --- NEW: LEVEL 3 CODE EXTRACTION ---
    # Extract the python code block for the Falsification Suite
    test_model_path = f"{PROJECT_DIR}/test_model.py"

    if python_code is not None:
        # Save the code to a file so test_thesis.py can execute it
        write_file(test_model_path, python_code)

        # Clean the markdown so the code doesn't clutter the thesis text
        write_file(WORKING_PATH, clean_thesis)
        print(f"💾 Falsification Suite saved to: {test_model_path}")
    else:
        # If the AI fails to write a test, we force a failure to maintain rigor
        write_file(
            test_model_path,
            "assert False, 'AI failed to provide a testable falsification suite.'",
        )
        write_file(WORKING_PATH, clean_thesis)
        print(
            "⚠️ Warning: No Python block found. Forcing a test failure to ensure rigor."
        )

    try:
        subprocess.run(test_cmd, check=True)
        with open("eval_results.json", "r") as f:
            new_eval = json.load(f)

        selection_record = evaluate_candidate_selection(
            candidate_score=new_eval["score"],
            best_score_before=best_score,
            mutation_validation=mutation_validation,
            scope_verdict=CandidateScopeVerdict.IN_SCOPE,
            scope_signals=(),
            dynamic=args.dynamic,
            debate_log_text=_latest_debate_log_text(PROJECT_DIR),
        )
        write_file(
            str(workspace_dir / "latest_candidate_selection.json"),
            json.dumps(
                {
                    "scope_verdict": selection_record.scope_verdict.value,
                    "candidate_admissible": selection_record.candidate_admissible,
                    "minority_attack_preserved": selection_record.minority_attack_preserved,
                    "keep_best_in_scope": selection_record.keep_best_in_scope,
                    "selected_as_best": selection_record.selected_as_best,
                    "candidate_score": selection_record.candidate_score,
                    "best_score_before": selection_record.best_score_before,
                    "scope_signals": list(selection_record.scope_signals),
                    "attacker_headers_seen": list(selection_record.attacker_headers_seen),
                    "rationale": selection_record.rationale,
                },
                indent=2,
            ),
        )

        if not selection_record.candidate_admissible:
            print(f"⚠️ Runner R3 rejection: {selection_record.rationale}")
            signal = IterationSignal(
                iteration_index=i + 1,
                score=new_eval["score"],
                weakest_point=f"Runner R3 rejection: {selection_record.rationale}",
                claim_delta_type=mutation_declaration.claim_delta_type.value if mutation_declaration is not None else "",
                committee_digest=current_committee_digest,
                prior_committee_digest=iteration_prior_committee_digest,
            )
            iteration_history.append(signal)
            yield_decision = evaluate_information_yield(iteration_history)
            _write_latest_information_yield(workspace_dir, signal=signal, decision=yield_decision)
            last_failure_reason = f"Runner R3 rejection: {selection_record.rationale}"
            stagnation_count = yield_decision.stagnant_window
            pending_loop_action = yield_decision.action
            _restore_project_state(best_state)
            time.sleep(1)
            continue

        signal = IterationSignal(
            iteration_index=i + 1,
            score=new_eval["score"],
            weakest_point=new_eval["weakest_point"],
            score_improved=new_eval["score"] > best_score,
            claim_delta_type=mutation_declaration.claim_delta_type.value if mutation_declaration is not None else "",
            committee_digest=current_committee_digest,
            prior_committee_digest=iteration_prior_committee_digest,
            verified_axioms_added=len(new_eval.get("verified_axioms", [])),
        )
        iteration_history.append(signal)
        yield_decision = evaluate_information_yield(iteration_history)
        _write_latest_information_yield(workspace_dir, signal=signal, decision=yield_decision)

        if new_eval["score"] > best_score:
            print(f"✅ IMPROVEMENT: {best_score} -> {new_eval['score']}")
            print(f"Targeting New Weakest Link: {new_eval['weakest_point']}")
            best_score = new_eval["score"]
            best_weakest_point = new_eval["weakest_point"]
            stagnation_count = yield_decision.stagnant_window
            last_failure_reason = None
            pending_loop_action = yield_decision.action

            history_stem = f"{RUN_ID}_iter{i + 1}_score_{best_score}_{args.rubric}"
            write_file(f"{HISTORY_DIR}/{history_stem}.md", new_content)

            # Keep thesis.md in sync with the current best thesis
            write_file(THESIS_PATH, new_content + f"\n\n<!-- best_iteration: {history_stem} -->")

            meta = {
                "run_id": RUN_ID,
                "iteration": i + 1,
                "score": best_score,
                "rubric": args.rubric,
                "dynamic": args.dynamic,
                "mutator_model": current_mutator,
                "judge_model": JUDGE_MODEL_ID,
                "weakest_point": best_weakest_point,
                "timestamp": datetime.now().isoformat(),
            }
            write_file(
                f"{HISTORY_DIR}/{history_stem}_meta.json",
                json.dumps(meta, indent=2)
            )

            dag_src = f"{PROJECT_DIR}/probability_dag.json"
            if os.path.exists(dag_src):
                shutil.copy(dag_src, f"{HISTORY_DIR}/{history_stem}_dag.json")

            new_axioms = new_eval.get("verified_axioms", [])
            approved_retirements = new_eval.get("retired_axioms_approved", [])
            if os.path.exists(AXIOM_PATH):
                with open(AXIOM_PATH, "r") as f:
                    current_axioms = json.load(f)
            else:
                current_axioms = []
            # Apply Judge's Veto: Filter out the approved retirements
            if approved_retirements:
                print(
                    f"🗑️ Judge Approved {len(approved_retirements)} Axiom Retirements."
                )
                current_axioms = [
                    ax
                    for ax in current_axioms
                    if not any(
                        ret.lower() in ax.lower() for ret in approved_retirements
                    )
                ]

            if new_axioms:
                print("\n" + "📜" * 20)
                print(f"NEW AXIOMS VERIFIED (ITER {i + 1}):")
                for a in new_axioms:
                    print(f"  • {a}")
                print("📜" * 20 + "\n")

            # --- THE FIX: Clean up duplicates effectively by ignoring backticks/punctuation
            def normalize(text):
                return re.sub(r'[^a-zA-Z0-9]', '', text).lower()
            
            updated_axioms = []
            seen_axioms = set()
            for ax in current_axioms + new_axioms:
                norm = normalize(ax)
                if norm not in seen_axioms:
                    seen_axioms.add(norm)
                    updated_axioms.append(ax)
                    
            with open(AXIOM_PATH, "w") as f:
                json.dump(updated_axioms, f, indent=2)

            best_state = _capture_project_state(_project_state_paths(PROJECT_DIR))

            # Clean up the backup file if the pivot was successful
            if os.path.exists(f"{AXIOM_PATH}.bak"):
                os.remove(f"{AXIOM_PATH}.bak")

            if best_score >= 85 and getattr(args, "auto_evolve", False):
                rubric_data = evolve_rubric(rubric_data, new_content)
                # Overwrite the same rubric file so future runs pick up the evolution automatically
                new_rubric_name = args.rubric
                with open(RUBRICS_DIR / f"{new_rubric_name}.json", "w") as f:
                    json.dump(rubric_data, f, indent=2)

                test_cmd = [
                    sys.executable,
                    "-m",
                    "src.ztare.validator.test_thesis",
                    "--project",
                    args.project,
                    "--rubric",
                    new_rubric_name,
                    "--judge_model", args.judge_model,
                    "--mutator_model", args.mutator_model,
                ]
                if args.dynamic:
                    test_cmd.append("--dynamic")
                if args.use_primitives:
                    test_cmd.append("--use_primitives")
                if args.use_mutator_primitives:
                    test_cmd.append("--use_mutator_primitives")
                if args.primitive_top_k:
                    test_cmd.extend(["--primitive_top_k", str(args.primitive_top_k)])
                if args.deterministic_score_gates:
                    test_cmd.append("--deterministic_score_gates")
                best_score = 20

        else:
            print(f"❌ REVERTED: {new_eval['score']} <= {best_score}")
            print(f"Failed to Resolve: {new_eval['weakest_point']}")
            stagnation_count = yield_decision.stagnant_window
            last_failure_reason = new_eval["weakest_point"]
            pending_loop_action = yield_decision.action
            _restore_project_state(best_state)
            if os.path.exists(f"{AXIOM_PATH}.bak"):
                shutil.copy(f"{AXIOM_PATH}.bak", AXIOM_PATH)

    except subprocess.CalledProcessError:
        print("⚠️ Auditor Subprocess Crashed. Logging stagnation...")
        signal = IterationSignal(
            iteration_index=i + 1,
            score=best_score,
            weakest_point="Auditor subprocess crashed",
            runtime_failure=True,
            claim_delta_type=mutation_declaration.claim_delta_type.value if mutation_declaration is not None else "",
            committee_digest=current_committee_digest,
            prior_committee_digest=iteration_prior_committee_digest,
        )
        iteration_history.append(signal)
        yield_decision = evaluate_information_yield(iteration_history)
        _write_latest_information_yield(workspace_dir, signal=signal, decision=yield_decision)
        stagnation_count = yield_decision.stagnant_window
        pending_loop_action = yield_decision.action
        _restore_project_state(best_state)
        time.sleep(5)

    time.sleep(1)

    # End of loop
    print("\n" + "=" * 50)
    print("🏁 OPTIMIZATION LOOP COMPLETE")
    print(f"Final Score: {best_score}")
    print(f"Total Mutator Tokens Used: {SESSION_TOKENS:,}")
    # Using a rough average of $1.50 per 1M tokens for Gemini Pro/Flash mix
    est_cost = (SESSION_TOKENS / 1000000) * 1.50
    print(f"Estimated Mutator Cost: ${est_cost:.4f}")
    print("=" * 50 + "\n")
