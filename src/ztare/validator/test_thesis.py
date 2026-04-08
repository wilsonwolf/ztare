import os
import json
import argparse
import time
import subprocess
import tempfile
from pathlib import Path
from google import genai
from google.genai import types
import anthropic
from openai import OpenAI
from src.ztare.common import utils
from src.ztare.common.paths import PROJECTS_DIR, REPO_ROOT, RUBRICS_DIR
import concurrent.futures
import re
from src.ztare.primitives.primitive_library import (
    format_attack_templates,
    format_judge_guardrail,
    retrieve_primitives,
    retrieve_primitives_by_keys,
)
from src.ztare.validator.primitive_routing import route_primitives_for_v4
from src.ztare.validator.semantic_gate_stabilization import (
    derive_self_reference_gate,
    persist_semantic_gate_analysis,
)
from src.ztare.validator.v4_family import is_v4_family_project

# 1. Setup & Args
parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--rubric", required=True)
parser.add_argument("--dynamic", action="store_true")
parser.add_argument(
    "--judge_model",
    type=str,
    default="gemini",
    choices=["gemini", "claude", "claude-opus", "gpt4o"],
)
parser.add_argument(
    "--mutator_model",
    type=str,
    default="gemini",
)
parser.add_argument("--use_primitives", action="store_true")
parser.add_argument(
    "--primitive_routing_profile",
    choices=["v4"],
    help="Optional routing profile for primitive-enabled evaluation. `v4` enables exploit-family routing outside the canonical project name.",
)
parser.add_argument("--use_mutator_primitives", action="store_true")
parser.add_argument("--use_transfer_hypotheses", action="store_true")
parser.add_argument(
    "--crux_first_primitives",
    action="store_true",
    help="Identify the load-bearing claim / eigenquestion before injecting primitive context into the meta-judge.",
)
parser.add_argument("--primitive_top_k", type=int, default=3)
parser.add_argument(
    "--disable_attacker_tools",
    action="store_true",
    help="Disable Gemini automatic function-calling for the default attacker path. Useful for benchmark runs where specimen code names can collide with tool-calling.",
)
parser.add_argument(
    "--deterministic_score_gates",
    action="store_true",
    help="Use Python-enforced hard gates and criterion booleans instead of trusting a raw LLM score.",
)
parser.add_argument(
    "--eval_results_path",
    default="eval_results.json",
    help="Path to write the final evaluation JSON. Defaults to eval_results.json in the current working directory.",
)
args = parser.parse_known_args()[0]
if getattr(args, "use_transfer_hypotheses", False):
    args.use_mutator_primitives = True
if args.use_mutator_primitives:
    args.use_primitives = True

_MODEL_MAP = {
    "gemini": "gemini-2.5-flash",
    "claude": "claude-sonnet-4-6",
    "claude-opus": "claude-opus-4-6",
    "gpt4o": "gpt-4o",
}
JUDGE_MODEL_ID = _MODEL_MAP[args.judge_model]
MUTATOR_MODEL_ID = args.mutator_model
print(f"⚖️  Judge: {JUDGE_MODEL_ID}")
print(f"🧬 Mutator: {MUTATOR_MODEL_ID}")

gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) if os.environ.get("OPENAI_API_KEY") else None

# Keep legacy `client` pointing to Gemini for ATTACKER_CONFIG function calling
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
PROJECT_DIR = str(PROJECTS_DIR / args.project)
WORKING_PATH = f"{PROJECT_DIR}/current_iteration.md"
EVIDENCE_PATH = f"{PROJECT_DIR}/evidence.txt"
MAIN_RUBRIC_PATH = str(RUBRICS_DIR / f"{args.rubric}.json")
DYNAMIC_RUBRIC_PATH = str(RUBRICS_DIR / f"dynamic_{args.project}.json")
test_path = f"{PROJECT_DIR}/test_model.py"

# --- HELPER FUNCTIONS ---
def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()


test_code_content = (
    read_file(test_path) if os.path.exists(test_path) else "No code provided."
)

def _call_anthropic_judge(prompt, model_id):
    """Call Claude for judging. Returns a fake response-like object with .text."""
    message = anthropic_client.messages.create(
        model=model_id,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    class _Resp:
        text = message.content[0].text
        candidates = None
        prompt_feedback = None
    return _Resp()


def _call_openai_judge(prompt, model_id):
    """Call OpenAI for judging. Returns a fake response-like object with .text."""
    response = openai_client.chat.completions.create(
        model=model_id,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    class _Resp:
        text = response.choices[0].message.content
        candidates = None
        prompt_feedback = None
    return _Resp()


def safe_generate(prompt, config=None, model_id=None):
    """Exponential backoff with dynamic model routing."""
    if model_id is None:
        model_id = JUDGE_MODEL_ID

    is_claude = model_id.startswith("claude")
    is_openai = model_id.startswith("gpt") or model_id.startswith("o1") or model_id.startswith("o3")

    for i in range(12):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            print(f"📡 [DEBUG] Dispatching request to {model_id}... (Attempt {i + 1})")
            start_time = time.time()

            if is_claude:
                future = executor.submit(_call_anthropic_judge, prompt, model_id)
            elif is_openai:
                future = executor.submit(_call_openai_judge, prompt, model_id)
            else:
                future = executor.submit(
                    client.models.generate_content,
                    model=model_id, contents=prompt, config=config
                )

            response = future.result(timeout=300)
            elapsed = time.time() - start_time
            print(f"✅ [DEBUG] Response received in {elapsed:.1f}s")
            return response

        except concurrent.futures.TimeoutError:
            wait_time = (i + 1) * 15
            print(f"⚠️ Zombie Connection Killed (200s Timeout). Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            error_str = str(e)
            if "400" in error_str or "404" in error_str:
                print(f"❌ Configuration/Model Error: {e}")
                raise e
            if any(code in error_str for code in ["429", "500", "502", "503", "504"]):
                wait_time = (i + 1) * 20
                print(f"⚠️ API Transient Issue ({error_str[:15]}...). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Unhandled Exception: {error_str}")
                raise e
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    raise Exception("Max retries exceeded due to persistent API issues.")

# --- LEVEL 3: THE TOOL ---
def execute_python_code(code: str) -> str:
    """Executes Python code with console transparency."""
    #print("\n" + "·" * 40)
    #print("🖥️  LEVEL 3 AGENT EXECUTING PYTHON:")
    #indented_code = "\n".join(["    " + line for line in code.strip().split("\n")])
    #print(indented_code)
    #print("·" * 40 + "\n")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        env = os.environ.copy()
        repo_root = str(REPO_ROOT)
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            repo_root if not existing_pythonpath else f"{repo_root}{os.pathsep}{existing_pythonpath}"
        )
        res = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=repo_root,
            env=env,
        )
        if res.stdout:
            print(f"📊 OUTPUT: {res.stdout.strip()}")
        if res.stderr:
            print(f"⚠️ ERROR: {res.stderr.strip()}")
        return res.stdout if not res.stderr else f"Error: {res.stderr}"
    finally:
        os.remove(tmp_path)


# --- CONFIGURATION (Defined once to stay DRY/Clean) ---
ATTACKER_CONFIG = types.GenerateContentConfig(
    tools=[execute_python_code],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(),
)
ATTACKER_NO_TOOL_CONFIG = types.GenerateContentConfig(temperature=0.2)


def _route_v4_primitives(thesis_text, evidence_text, critiques_text=""):
    v4_routing_enabled = (
        args.use_primitives
        and (
            is_v4_family_project(args.project)
            or args.primitive_routing_profile == "v4"
        )
    )
    if not v4_routing_enabled:
        return None, []
    decision = route_primitives_for_v4(
        thesis_text=thesis_text,
        evidence_text=evidence_text,
        critiques_text=critiques_text,
    )
    primitives = retrieve_primitives_by_keys(decision.primitive_keys)
    return decision, primitives

def run_specialized_attacker(thesis_text, evidence_text, attacker_profile):
    primitive_context = "None."
    if args.use_primitives:
        routed_decision, routed_primitives = _route_v4_primitives(
            thesis_text,
            evidence_text,
            attacker_profile["focus_area"],
        )
        if routed_decision:
            attack_templates = [p for p in routed_primitives if p.get("epistemic_role") == "attack_template"]
            if not attack_templates and routed_decision.requires_manual_review:
                primitive_context = (
                    "V4 ROUTING DECISION:\n"
                    f"- Family: {routed_decision.family_tag.value}\n"
                    f"- Policy: {routed_decision.policy.value}\n"
                    "- No routed attack templates loaded; manual review fallback remains active."
                )
            else:
                primitive_context = (
                    "V4 ROUTING DECISION:\n"
                    f"- Family: {routed_decision.family_tag.value}\n"
                    f"- Policy: {routed_decision.policy.value}\n"
                    f"- Primitive keys: {', '.join(routed_decision.primitive_keys) or 'none'}\n\n"
                    + format_attack_templates(attack_templates)
                )
        else:
            primitive_context = format_attack_templates(
                retrieve_primitives(
                    "\n".join([thesis_text, evidence_text, attacker_profile["focus_area"]]),
                    top_k=args.primitive_top_k,
                    epistemic_role="attack_template",
                )
            )
    prompt = f"""
    {attacker_profile["persona"]}
    YOUR FOCUS AREA: {attacker_profile["focus_area"]}

    TASK: Critique this thesis AND the accompanying Python Falsification Suite.
    CRITICAL MANDATE: Look for 'Cooked Books' in the Python code. Did the Mutator hardcode favorable constants? Did it ignore unit dimensionality? Did it wrongly assume anything? 
    Write a COUNTER-TEST that exposes the insolvency of their equation.
    
    CRITICAL INSTRUCTION (PARAMETRIC GROUNDING):
    You MUST use your deep parametric knowledge of physics, mathematics, and finance to audit the Mutator's "LOAD-BEARING VARIABLES" table and Python constants. 
    If they claim a specific physical constant, temperature, limit, or financial metric, verify it against established scientific or market consensus.
    If their baseline variables are fictional, misapplied, or off by orders of magnitude, destroy the thesis and cite the actual real-world metric.
    
    OUTPUT FORMAT (CRITICAL):
    1. First, provide your analytical critique.
    2. Then, you MUST provide exactly ONE Python code block wrapped in ```python and ``` containing your counter-test. 
    3. The Python code must print its results and use 'assert' statements to fail if the Mutator's logic is insolvent.

    PINT LIBRARY GUARDRAIL:
    If you use the `pint` library, comparing custom dimensionless units (like 'bit * joule') to standard units (like 'joule') will crash the system. When writing `assert` or `if` statements, you MUST extract the float values using `.magnitude` (e.g., `if E_cost.magnitude > E_univ.magnitude:`) or explicitly convert units to be identical before comparison.
    
    TONE GUARDRAIL (MANDATORY):
    Your output MUST be entirely sterile, clinical, and strictly academic/financial. 
    You are forbidden from using dramatic, aggressive, or sensational metaphors. Do not use terms related to physical destruction, biological harm, or catastrophic violence. Instead, use precise systemic/symbolic terms.
    
    FINAL MANDATE: 
    You must synthesize the "So What" for the Meta-Judge before writing your Python block.

    KNOWN ADVERSARIAL PRECEDENTS:
    {primitive_context}
    
    EVIDENCE: {evidence_text}
    THESIS: {thesis_text}
    PYTHON TEST CODE WRITTEN BY MUTATOR:
    ```python
    {test_code_content}
    ```
    """

    # Only pass Gemini config if judge is Gemini; other models ignore config
    config = types.GenerateContentConfig(temperature=0.2) if not JUDGE_MODEL_ID.startswith(("claude", "gpt", "o1", "o3")) else None

    print(f"\n🚀 ATTACKER LAUNCHED: {attacker_profile['role']}")
    print(f"🎯 FOCUS: {attacker_profile['focus_area']}")

    response = safe_generate(prompt, config=config, model_id=JUDGE_MODEL_ID)
    # --- 🔍 SAFETY METADATA DEBUGGER ---
    if response and hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        reason = str(candidate.finish_reason)
        if "STOP" not in reason:
            print(f"\n🛑 [DEBUG] API HALT DETECTED. Finish Reason: {reason}")
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                print("🚨 Safety Ratings Breakdown:")
                for rating in candidate.safety_ratings:
                    if "MEDIUM" in str(rating.probability) or "HIGH" in str(rating.probability):
                        print(f"   -> {rating.category}: {rating.probability}")
    elif response and hasattr(response, 'prompt_feedback'):
        print(f"\n🛑 [DEBUG] PROMPT BLOCKED AT INTAKE: {response.prompt_feedback}")
    else:
        print("\n🛑 [DEBUG] RESPONSE OBJECT IS EMPTY OR MALFORMED.")

    # --- 🛡️ BULLETPROOF TEXT EXTRACTION ---
    try:
        raw_text = response.text if response else None
    except ValueError: 
        raw_text = None
    except Exception as e:
        print(f"⚠️ Unexpected extraction error: {e}")
        raw_text = None        
        
    if not raw_text:
        reason = "UNKNOWN"
        if response and hasattr(response, 'candidates') and response.candidates:
            reason = str(response.candidates[0].finish_reason)
            
        if "SAFETY" in reason:
            return "⚠️ ATTACK BLOCKED BY SAFETY FILTERS: The model's critique triggered corporate safety guardrails."
        else:
            return f"⚠️ ATTACK ABORTED. Finish Reason: {reason}. Treat this as a structural failure."

    # --- THE NUCLEAR EXTRACTION (REGEX) ---
    tool_output_text = ""
    # Find the python code block in the markdown
    code_match = re.search(r"```python\n(.*?)\n```", raw_text, re.DOTALL)
    
    if code_match:
        extracted_code = code_match.group(1)
        # Execute the code manually using your existing tool function
        execution_result = execute_python_code(extracted_code)
        # Append the output directly to the critique so the Meta-Judge can read it
        tool_output_text = f"\n\n### PYTHON EXECUTION OUTPUT:\n{execution_result}"
    else:
        tool_output_text = "\n\n### PYTHON EXECUTION OUTPUT:\n⚠️ No Python block found. Attacker failed to provide a quantitative counter-test."

    # Combine the textual critique with the stdout/stderr from the Python execution
    final_critique = raw_text + tool_output_text

    #print("\n--- ADVERSARIAL LOGIC ---")
    #print(final_critique)
    print("--- END ATTACK ---\n")

    print(f"💥 CRITIQUE MAGNITUDE: {len(final_critique)} chars.")
    return final_critique

def run_meta_judge(text, evidence, main_rubric_data, aggregated_critiques, axioms):
    v4_stage_index = _load_v4_stage_index()
    rubric_str = "\n".join(
        [f"- {k}: {v}" for k, v in main_rubric_data["criteria"].items()]
    )
    axiom_str = "\n".join([f"- {a}" for a in axioms]) if axioms else "None yet."
    crux_analysis = None
    primitive_context = "None."
    routing_decision = None
    if args.crux_first_primitives and args.use_primitives:
        crux_analysis = identify_crux_analysis(
            text, evidence, main_rubric_data, aggregated_critiques
        )
    if args.use_primitives:
        routing_decision, routed_primitives = _route_v4_primitives(
            text,
            evidence,
            aggregated_critiques,
        )
        if routing_decision:
            primitive_context = (
                "V4 ROUTING DECISION:\n"
                f"- Family: {routing_decision.family_tag.value}\n"
                f"- Policy: {routing_decision.policy.value}\n"
                f"- Primitive keys: {', '.join(routing_decision.primitive_keys) or 'none'}\n"
                f"- Manual review required: {routing_decision.requires_manual_review}\n"
                f"- Rationale: {routing_decision.rationale}\n\n"
                + format_judge_guardrail(
                    routed_primitives,
                    require_transfer_proof=args.use_mutator_primitives,
                )
            )
        else:
            primitive_query_parts = [text, evidence, aggregated_critiques]
            if crux_analysis:
                primitive_query_parts.extend(
                    [
                        crux_analysis.get("eigenquestion", ""),
                        crux_analysis.get("load_bearing_claim", ""),
                        crux_analysis.get("why_load_bearing", ""),
                        crux_analysis.get("mismatch_reason", ""),
                        "\n".join(crux_analysis.get("crux_keywords", [])),
                    ]
                )
            primitive_context = format_judge_guardrail(
                retrieve_primitives(
                    "\n".join(part for part in primitive_query_parts if part),
                    top_k=args.primitive_top_k,
                ),
                require_transfer_proof=args.use_mutator_primitives,
            )
    crux_context = "None."
    crux_instruction = ""
    if crux_analysis:
        crux_context = json.dumps(crux_analysis, indent=2)
        crux_instruction = """
    RULES FOR CRUX-FIRST ORDERING:
    - The crux analysis above was produced before any failure precedents were shown.
    - Treat that load-bearing claim as the anchor for this evaluation unless the firing-squad evidence directly refutes it.
    - Decide first whether the falsification suite actually tests that crux.
    - Use failure precedents only to pressure-test the crux; do not let them redefine the crux or soften a claim-test mismatch.
    - If `test_targets_claim` is false or `mismatch_risk` is high, scrutinize selective rigor, halo validation, suite omission, and tautological verification before granting credit for passing tests.
"""
    prompt = f"""
    {main_rubric_data["persona"]}
    MANDATE: You are the Meta-Judge (Bar-Raiser). Synthesize the attacks and score the thesis.
    
    CRITICAL MANDATE (THE AXIOMATIC GATE):
    Below are the IMMUTABLE AXIOMS already proven in previous iterations. 
    If the current thesis contradicts any of these axioms, you must apply a -50 point penalty.
    --- IMMUTABLE AXIOMS ---
    {axiom_str}

    --- PRECEDENT-FREE CRUX IDENTIFICATION ---
    {crux_context}
    {crux_instruction}

    --- KNOWN FAILURE PRECEDENTS ---
    {primitive_context}
    
    CRITICAL MANDATE (THE POPPERIAN CONSTRAINT):
    Before grading the logic against the rubric, you must evaluate Falsifiability. Does this thesis make a specific, testable prediction that could theoretically be proven wrong by a future data point or simulation?
    If the thesis only offers post-hoc rationalizations or relies on unmeasurable variables, the maximum allowable score is 40.
    If the Mutator proposes retiring an axiom, evaluate if it is a valid dimensional shift or just lazy accounting. If valid, add it to retired_axioms_approved. If it is a fraudulent attempt to evade a constraint, penalize the score by -30

    PROBABILITY DAG MANDATE (SUPERFORECASTING OUTPUT):
    After scoring, you must extract the 3-5 most critical load-bearing variables from the thesis and express them as a probability DAG.

    CRITICAL PROBABILITY SEMANTICS (read carefully before assigning numbers):
    - Each node probability represents: P(this node is TRUE | the thesis direction is correct).
      Think of it as: "If this thesis is roughly right, how confident are we this specific mechanism holds?"
      A node that survived the firing squad intact should be 0.60-0.85. One with major holes: 0.20-0.45.
      Do NOT assign node probabilities as marginal base rates of global catastrophes (e.g. 0.05%).
    - The outcome_probability is a WEIGHTED SUM (not a product) of upstream node probabilities:
      outcome = sum(node_i.probability * edge_i.weight) / sum(edge_i.weight)
      This is a causal confidence score, not a joint probability of independent events.
    - Edge weights (0.0-1.0) represent causal contribution: how much does this node drive the outcome?
      The highest-leverage load-bearing variable gets weight ~0.8-1.0. Supporting nodes: 0.3-0.6.

    CALIBRATION CHECK: If your outcome_probability is below 0.05, you have made a math error.
    The DAG measures thesis confidence, not actuarial risk of the worst-case scenario.
    This DAG is appended to the thesis output — it does NOT replace the hardened essay.
    
    --- CORE RUBRIC ---
    {rubric_str}
    --- FIRING SQUAD CRITIQUES ---
    {aggregated_critiques}
    --- EVIDENCE ---
    {evidence}
    --- THESIS ---
    {text}
    """
    if is_v4_family_project(args.project) and v4_stage_index == 3:
        prompt += """

STAGE 4 SCOPE ENFORCEMENT (MANDATORY):
Your score-bearing evaluation must focus only on Shadow Board behavior:
- board composition determinism
- role assignment correctness
- arbiter activation semantics
- typed-handoff recording / consumption behavior

For this stage, a thesis is allowed to consume `typed_handoff_available` as an upstream flag and make a bounded claim about deterministic board composition plus conservative fallback.
Do NOT score the thesis down merely because upstream provenance is unresolved, unless the thesis claims to verify that provenance itself, claims systemic trust repair, or claims stable whole-system adversarial coverage.

If you identify upstream semantic-gate, whitelist, quote-validation, or other stage-1/2/3 weaknesses:
- record them in `logic_gaps` or `debate_summary` as OUT-OF-SCOPE ARCHITECTURAL DEBT
- do NOT treat them as score-bearing failures for this stage
- do NOT use them as the main `weakest_point` unless they directly alter board behavior itself
"""
    criteria_keys = list(main_rubric_data["criteria"].keys())
    if args.deterministic_score_gates:
        criteria_key_str = "\n".join([f"- {key}" for key in criteria_keys])
        prompt += f"""

DETERMINISTIC SCORE CONTRACT (MANDATORY):
Do NOT optimize for rhetorical scoring. Your job is to produce machine-readable gate decisions and criterion booleans.

You must decide the following booleans:
- `is_falsified`: true if the thesis is directly falsified by the unit tests, its own quantitative evidence, or its own architecture claims.
- `computationally_feasible`: true only if the proposed architecture is executable and internally coherent as specified.
- `anti_gaming_preserved`: true only if the mutator still cannot influence its own evaluation.
- `architectural_abstraction_preserved`: true only if the proof remains an architectural mechanism rather than a domain-rich simulation.
- `contains_infallible_aggregator`: true if the proposal reintroduces an absolute veto, infallible aggregator, hidden trusted arbiter, or equivalent trust leak.
- `proof_is_self_referential`: true if the test suite merely recomputes thesis-authored formulas, bookkeeping identities, or self-declared metrics instead of creating an independent falsification environment that could invalidate the claimed mechanism.

You must also output a structured `self_reference_evidence` record for Python-side semantic-gate stabilization:
- `target_claim`: string
- `asserted_variable`: string
- `asserted_variable_origin`: one of `internal|external|mixed|unknown`
- `independent_grounding_present`: boolean
- `test_recomputes_thesis_authored_target`: boolean
- `causal_variable_perturbed`: boolean
- `load_bearing_claim_directly_tested`: boolean
- `local_component_scope_disclaimer_present`: boolean
- `whole_system_availability_claim_present`: boolean
- `verifies_authored_mapping_only`: boolean
- `evidence_lines`: array of short strings
- `counterevidence_lines`: array of short strings
- `confidence`: one of `high|medium|low`

Backward-compatibility rule:
- still provide `proof_is_self_referential`
- but populate `self_reference_evidence` carefully, because Python will derive the final semantic gate from that structured record

Field intent for local safe-harbor cases:
- `local_component_scope_disclaimer_present` = true only when the thesis explicitly limits itself to a narrow local component and disclaims upstream truthfulness/completeness.
- `whole_system_availability_claim_present` = true when the thesis claims end-to-end protection, system-level guarantees, or explicit future-state outcomes such as insolvency, collapse, success, distress, or other whole-system predictions. Do not limit this field to phrases like "prevents" or "ensures"; forward predictions about the whole system also count.
- `verifies_authored_mapping_only` = true when the tests only verify the component's own authored deterministic mapping, thesis-authored thresholds, or thesis-authored future scenarios rather than a claim about independently grounded external reality. A counter-scenario or inverse scenario does NOT make this false if both scenarios are still thesis-authored.

Grounding rule for prediction claims:
- `independent_grounding_present` = true only if the specific load-bearing variable or threshold that determines whether the central claim passes or fails is independently grounded.
- Do NOT set `independent_grounding_present` true merely because some other input variable is externally sourced, or because the thesis cites background evidence elsewhere.
- For forward prediction claims, if the decisive future variable, threshold, horizon, or causal multiplier is a thesis assumption, then `independent_grounding_present` must be false even if other inputs are externally cited.

Extraction rule for self-reference:
- If the tests recompute a thesis-authored future variable or thesis-authored threshold, treat that as self-referential unless the decisive pass/fail variable is independently grounded.
- If the claim is a whole-system future prediction and the decisive variable remains thesis-authored, prefer `asserted_variable_origin = internal` and `independent_grounding_present = false`.

For rubric criteria, you must output:
- `criteria_passed`: array of rubric keys that pass
- `criteria_failed`: array of rubric keys that fail

Use ONLY these rubric keys:
{criteria_key_str}

EVIDENTIARY SAFE HARBOR (MANDATORY):
Do not mark `anti_gaming_preserved` false or `contains_infallible_aggregator` true merely because a narrowly scoped local component consumes upstream booleans, status tokens, or scores.
If ALL of the following are true, evaluate the local contract on its own terms:
- the thesis explicitly disclaims solving upstream truthfulness, calibration, or completeness
- the code implements only a deterministic bounded mapping or a fail-closed gate
- the tests exhaustively validate that local mapping or gate
- the prose does not claim that local execution proves whole-system validity

For such bounded local components:
- exhaustive input-output checks are acceptable evidence for the local claim
- do NOT mark `proof_is_self_referential` true merely because the tests execute the exact mapping being claimed
- dependency on upstream inputs is allowed; false claims about their truthfulness are not

Hard rule:
- If the thesis is falsified, computationally infeasible, anti-gaming is not preserved, or an infallible aggregator is present, say so explicitly. Python will convert those gates into the final score.
"""
    # For non-Gemini judges, append JSON schema as instructions
    is_non_gemini = JUDGE_MODEL_ID.startswith(("claude", "gpt", "o1", "o3"))
    if is_non_gemini:
        if args.deterministic_score_gates:
            prompt += """

CRITICAL: You must respond with ONLY a valid JSON object. No markdown, no explanation.
Required fields:
{
  "is_falsified": <boolean>,
  "computationally_feasible": <boolean>,
  "anti_gaming_preserved": <boolean>,
  "architectural_abstraction_preserved": <boolean>,
  "contains_infallible_aggregator": <boolean>,
  "proof_is_self_referential": <boolean>,
  "self_reference_evidence": {
    "target_claim": <string>,
    "asserted_variable": <string>,
    "asserted_variable_origin": <string>,
    "independent_grounding_present": <boolean>,
    "test_recomputes_thesis_authored_target": <boolean>,
    "causal_variable_perturbed": <boolean>,
    "load_bearing_claim_directly_tested": <boolean>,
    "local_component_scope_disclaimer_present": <boolean>,
    "whole_system_availability_claim_present": <boolean>,
    "verifies_authored_mapping_only": <boolean>,
    "evidence_lines": [<string>, ...],
    "counterevidence_lines": [<string>, ...],
    "confidence": <string>
  },
  "criteria_passed": [<string>, ...],
  "criteria_failed": [<string>, ...],
  "weakest_point": <string>,
  "verified_axioms": [<string>, ...],
  "retired_axioms_approved": [<string>, ...],
  "logic_gaps": [<string>, ...],
  "debate_summary": <string>,
  "adversarial_alignment": <string>,
  "friction_points": [<string>, ...],
  "probability_dag": {
    "outcome": {"label": <string>, "probability": <number>},
    "nodes": [{"id": <string>, "label": <string>, "probability": <number>, "watch_signal": <string>}],
    "edges": [{"from": <string>, "to": <string>, "weight": <number>}]
  }
}"""
        else:
            prompt += """

CRITICAL: You must respond with ONLY a valid JSON object. No markdown, no explanation.
Required fields:
{
  "score": <integer>,
  "weakest_point": <string>,
  "verified_axioms": [<string>, ...],
  "retired_axioms_approved": [<string>, ...],
  "logic_gaps": [<string>, ...],
  "debate_summary": <string>,
  "adversarial_alignment": <string>,
  "friction_points": [<string>, ...],
  "probability_dag": {
    "outcome": {"label": <string>, "probability": <number>},
    "nodes": [{"id": <string>, "label": <string>, "probability": <number>, "watch_signal": <string>}],
    "edges": [{"from": <string>, "to": <string>, "weight": <number>}]
  }
}"""
        response = safe_generate(prompt, config=None, model_id=JUDGE_MODEL_ID)
        evaluation = utils.parse_llm_json(response.text)
        if crux_analysis:
            evaluation["crux_analysis"] = crux_analysis
        if routing_decision:
            evaluation["primitive_routing_decision"] = {
                "family_tag": routing_decision.family_tag.value,
                "policy": routing_decision.policy.value,
                "primitive_keys": list(routing_decision.primitive_keys),
                "punitive_primitives_allowed": routing_decision.punitive_primitives_allowed,
                "requires_manual_review": routing_decision.requires_manual_review,
                "rationale": routing_decision.rationale,
            }
        return evaluation

    if args.deterministic_score_gates:
        schema = {
            "type": "OBJECT",
            "properties": {
                "is_falsified": {"type": "BOOLEAN"},
                "computationally_feasible": {"type": "BOOLEAN"},
                "anti_gaming_preserved": {"type": "BOOLEAN"},
                "architectural_abstraction_preserved": {"type": "BOOLEAN"},
                "contains_infallible_aggregator": {"type": "BOOLEAN"},
                "proof_is_self_referential": {"type": "BOOLEAN"},
                "self_reference_evidence": {
                    "type": "OBJECT",
                    "properties": {
                        "target_claim": {"type": "STRING"},
                        "asserted_variable": {"type": "STRING"},
                        "asserted_variable_origin": {"type": "STRING"},
                        "independent_grounding_present": {"type": "BOOLEAN"},
                        "test_recomputes_thesis_authored_target": {"type": "BOOLEAN"},
                        "causal_variable_perturbed": {"type": "BOOLEAN"},
                        "load_bearing_claim_directly_tested": {"type": "BOOLEAN"},
                        "local_component_scope_disclaimer_present": {"type": "BOOLEAN"},
                        "whole_system_availability_claim_present": {"type": "BOOLEAN"},
                        "verifies_authored_mapping_only": {"type": "BOOLEAN"},
                        "evidence_lines": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "counterevidence_lines": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "confidence": {"type": "STRING"},
                    },
                },
                "criteria_passed": {"type": "ARRAY", "items": {"type": "STRING"}},
                "criteria_failed": {"type": "ARRAY", "items": {"type": "STRING"}},
                "weakest_point": {"type": "STRING"},
                "verified_axioms": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
                "retired_axioms_approved": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
                "logic_gaps": {"type": "ARRAY", "items": {"type": "STRING"}},
                "debate_summary": {"type": "STRING"},
                "adversarial_alignment": {"type": "STRING"},
                "friction_points": {"type": "ARRAY", "items": {"type": "STRING"}},
                "probability_dag": {
                    "type": "OBJECT",
                    "properties": {
                        "outcome": {
                            "type": "OBJECT",
                            "properties": {
                                "label": {"type": "STRING"},
                                "probability": {"type": "NUMBER"}
                            }
                        },
                        "nodes": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "id": {"type": "STRING"},
                                    "label": {"type": "STRING"},
                                    "probability": {"type": "NUMBER"},
                                    "watch_signal": {"type": "STRING"}
                                }
                            }
                        },
                        "edges": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "from": {"type": "STRING"},
                                    "to": {"type": "STRING"},
                                    "weight": {"type": "NUMBER"}
                                }
                            }
                        }
                    }
                },
            },
            "required": [
                "is_falsified",
                "computationally_feasible",
                "anti_gaming_preserved",
                "architectural_abstraction_preserved",
                "contains_infallible_aggregator",
                "proof_is_self_referential",
                "self_reference_evidence",
                "criteria_passed",
                "criteria_failed",
                "weakest_point",
                "logic_gaps",
                "verified_axioms",
                "retired_axioms_approved",
                "debate_summary",
            ],
        }
    else:
        schema = {
            "type": "OBJECT",
            "properties": {
                "score": {"type": "INTEGER"},
                "weakest_point": {"type": "STRING"},
                "verified_axioms": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Atomic truths that survived the firing squad.",
                },
                "retired_axioms_approved": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "List of proposed axiom retirements that the Judge agrees are valid for the new domain.",
                },
                "logic_gaps": {"type": "ARRAY", "items": {"type": "STRING"}},
                "debate_summary": {"type": "STRING"},
                "adversarial_alignment": {
                    "type": "STRING"
                },
                "friction_points": {"type": "ARRAY", "items": {"type": "STRING"}},
                "probability_dag": {
                    "type": "OBJECT",
                    "description": "Superforecasting probability model extracted from the thesis.",
                    "properties": {
                        "outcome": {
                            "type": "OBJECT",
                            "properties": {
                                "label": {"type": "STRING"},
                                "probability": {"type": "NUMBER"}
                            }
                        },
                        "nodes": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "id": {"type": "STRING"},
                                    "label": {"type": "STRING"},
                                    "probability": {"type": "NUMBER"},
                                    "watch_signal": {"type": "STRING"}
                                }
                            }
                        },
                        "edges": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "from": {"type": "STRING"},
                                    "to": {"type": "STRING"},
                                    "weight": {"type": "NUMBER"}
                                }
                            }
                        }
                    }
                },
            },
            "required": [
                "score",
                "weakest_point",
                "logic_gaps",
                "verified_axioms",
                "retired_axioms_approved",
                "debate_summary",
            ],
        }
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
    )
    response = safe_generate(prompt, config=config)
    evaluation = utils.parse_llm_json(response.text)
    if crux_analysis:
        evaluation["crux_analysis"] = crux_analysis
    if routing_decision:
        evaluation["primitive_routing_decision"] = {
            "family_tag": routing_decision.family_tag.value,
            "policy": routing_decision.policy.value,
            "primitive_keys": list(routing_decision.primitive_keys),
            "punitive_primitives_allowed": routing_decision.punitive_primitives_allowed,
            "requires_manual_review": routing_decision.requires_manual_review,
            "rationale": routing_decision.rationale,
        }
    return evaluation


def identify_crux_analysis(text, evidence, main_rubric_data, aggregated_critiques):
    prompt = f"""
    {main_rubric_data["persona"]}
    TASK: Identify the single load-bearing claim / eigenquestion of the thesis BEFORE reading any failure precedents.

    Return strict JSON with this schema:
    {{
      "eigenquestion": "<single foundational yes/no or either/or question>",
      "load_bearing_claim": "<single claim whose failure makes much of the thesis irrelevant>",
      "why_load_bearing": "<brief explanation of why this is the crux>",
      "test_targets_claim": true or false,
      "mismatch_risk": "high" | "medium" | "low",
      "mismatch_reason": "<brief explanation of whether the falsification suite targets the crux or only nearby scaffolding>",
      "crux_keywords": ["<short phrase>", "..."]
    }}

    Rules:
    - Pick exactly one crux, not a list.
    - Prefer the claim whose failure would render most downstream reasoning irrelevant.
    - `test_targets_claim = true` only if the provided falsification suite directly tests that crux.
    - If the tests mainly validate nearby arithmetic, scaffolding, peripheral derivations, or self-authored thresholds, set `test_targets_claim = false`.
    - `mismatch_risk = high` when the thesis appears to prove something adjacent to the crux rather than the crux itself.
    - Do not use external precedents or prior primitive labels. Work only from the thesis, evidence, and firing-squad critiques.

    --- THESIS ---
    {text}

    --- FIRING SQUAD CRITIQUES ---
    {aggregated_critiques}

    --- EVIDENCE ---
    {evidence}
"""
    is_non_gemini = JUDGE_MODEL_ID.startswith(("claude", "gpt", "o1", "o3"))
    if is_non_gemini:
        prompt += """

CRITICAL: You must respond with ONLY a valid JSON object. No markdown, no explanation.
Required fields:
{
  "eigenquestion": <string>,
  "load_bearing_claim": <string>,
  "why_load_bearing": <string>,
  "test_targets_claim": <boolean>,
  "mismatch_risk": <string>,
  "mismatch_reason": <string>,
  "crux_keywords": [<string>, ...]
}"""
        response = safe_generate(prompt, config=None, model_id=JUDGE_MODEL_ID)
        return utils.parse_llm_json(response.text)

    schema = {
        "type": "OBJECT",
        "properties": {
            "eigenquestion": {"type": "STRING"},
            "load_bearing_claim": {"type": "STRING"},
            "why_load_bearing": {"type": "STRING"},
            "test_targets_claim": {"type": "BOOLEAN"},
            "mismatch_risk": {"type": "STRING"},
            "mismatch_reason": {"type": "STRING"},
            "crux_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": [
            "eigenquestion",
            "load_bearing_claim",
            "why_load_bearing",
            "test_targets_claim",
            "mismatch_risk",
            "mismatch_reason",
            "crux_keywords",
        ],
    }
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
    )
    response = safe_generate(prompt, config=config, model_id=JUDGE_MODEL_ID)
    return utils.parse_llm_json(response.text)


def apply_semantic_gate_stabilization(evaluation):
    raw_flag = bool(evaluation.get("proof_is_self_referential", False))
    analysis = derive_self_reference_gate(
        evaluation.get("self_reference_evidence"),
        raw_flag=raw_flag,
    )
    summary = persist_semantic_gate_analysis(Path(PROJECT_DIR), analysis)

    evaluation["proof_is_self_referential_model_raw"] = raw_flag
    evaluation["proof_is_self_referential"] = analysis.proof_is_self_referential
    evaluation["semantic_gate_status"] = analysis.semantic_gate_status
    evaluation["self_reference_rule_fired"] = analysis.self_reference_rule_fired
    evaluation["self_reference_quorum_used"] = analysis.self_reference_quorum_used
    evaluation["self_reference_evidence"] = {
        **analysis.self_reference_evidence.__dict__,
    }
    evaluation["semantic_gate_unresolved_diagnosis"] = (
        analysis.unresolved_diagnosis.__dict__ if analysis.unresolved_diagnosis else None
    )
    evaluation["semantic_gate_summary"] = summary.__dict__
    return evaluation


def finalize_deterministic_score(evaluation, main_rubric_data, test_suite_status):
    criteria_keys = list(main_rubric_data["criteria"].keys())
    criteria_key_set = set(criteria_keys)
    passed = [key for key in evaluation.get("criteria_passed", []) if key in criteria_key_set]
    passed_set = set(passed)
    failed = [key for key in criteria_keys if key not in passed_set]

    hard_fail_reasons = []
    soft_score_caps = []
    safe_harbor_local_component = (
        evaluation.get("self_reference_rule_fired") == "safe_harbor_downgrade"
        and evaluation.get("semantic_gate_status") == "unresolved"
    )
    if test_suite_status != "pass":
        hard_fail_reasons.append(f"Level 3 falsification suite status was `{test_suite_status}`.")
    if evaluation.get("is_falsified", False):
        hard_fail_reasons.append("Meta-Judge marked the thesis as falsified.")
    if not evaluation.get("anti_gaming_preserved", True) and not safe_harbor_local_component:
        hard_fail_reasons.append("Meta-Judge found anti-gaming preservation was violated.")
    if evaluation.get("contains_infallible_aggregator", False) and not safe_harbor_local_component:
        hard_fail_reasons.append("Meta-Judge found an infallible aggregator / veto trust leak.")
    if not evaluation.get("computationally_feasible", True):
        soft_score_caps.append(
            {
                "reason": "Meta-Judge marked the thesis as computationally infeasible.",
                "cap": 40,
            }
        )
    if (
        evaluation.get("proof_is_self_referential", False)
        and evaluation.get("self_reference_rule_fired") == "hard_self_reference"
    ):
        hard_fail_reasons.append(
            "Structured semantic-gate derivation classified the proof as hard self-reference."
        )
    elif evaluation.get("proof_is_self_referential", False):
        soft_score_caps.append(
            {
                "reason": "Meta-Judge marked the proof as self-referential rather than a substantive falsification environment.",
                "cap": 25,
            }
        )

    criterion_score = round(100 * len(passed) / len(criteria_keys)) if criteria_keys else 0
    final_score = criterion_score
    if hard_fail_reasons:
        final_score = 0
    else:
        for cap in soft_score_caps:
            final_score = min(final_score, cap["cap"])
        final_score = max(0, min(100, final_score))

    evaluation["criteria_passed"] = passed
    evaluation["criteria_failed"] = failed
    evaluation["score_contract"] = {
        "mode": "deterministic_gates",
        "test_suite_status": test_suite_status,
        "criterion_score": criterion_score,
        "hard_fail_reasons": hard_fail_reasons,
        "soft_score_caps": soft_score_caps,
        "semantic_gate_status": evaluation.get("semantic_gate_status"),
        "self_reference_rule_fired": evaluation.get("self_reference_rule_fired"),
    }
    evaluation["score"] = final_score
    if hard_fail_reasons:
        strongest_reason = hard_fail_reasons[0]
        weakest_point = evaluation.get("weakest_point", "").strip()
        if not weakest_point:
            evaluation["weakest_point"] = strongest_reason
        elif strongest_reason not in weakest_point:
            evaluation["weakest_point"] = f"{strongest_reason} {weakest_point}"
    return evaluation


if __name__ == "__main__":
    thesis, evidence = read_file(WORKING_PATH), read_file(EVIDENCE_PATH)
    with open(MAIN_RUBRIC_PATH, "r") as f:
        main_rubric = json.load(f)

    critiques_text = ""

    log_path = f"{PROJECT_DIR}/debate_log_iter_{int(time.time())}.md"
    with open(log_path, "w") as log:
        log.write(f"# Adversarial Debate: {args.project}\n")
        log.write(
            f"<!-- rubric: {args.rubric} | mutator: {MUTATOR_MODEL_ID} | judge: {JUDGE_MODEL_ID} -->\n\n"
        )

        if args.dynamic and os.path.exists(DYNAMIC_RUBRIC_PATH):
            attackers = json.load(open(DYNAMIC_RUBRIC_PATH))["committee"]
            
            # Launch all attackers simultaneously
            print(f"🚀 Launching {len(attackers)} attackers in parallel...")
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(attackers)-1)
            try:
                future_to_attacker = {
                    executor.submit(run_specialized_attacker, thesis, evidence, att): att 
                    for att in attackers
                }
                for future in concurrent.futures.as_completed(future_to_attacker):
                    attacker = future_to_attacker[future]
                    try:
                        critique = future.result()
                        log.write(f"## Attacker: {attacker['role']}\n{critique}\n\n")
                        critiques_text += f"\n\n### Attack from {attacker['role']}:\n{critique}"
                    except Exception as exc:
                        print(f"❌ {attacker['role']} generated an exception: {exc}")
                        critiques_text += f"\n\n### Attack from {attacker['role']}:\nFAILED DUE TO EXCEPTION."
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
        else:
            # --- FIXED: Robust Extraction & Assignment ---
            prompt = f"Identify the single most catastrophic assumption in this thesis using tools if needed: {thesis}"
            attacker_config = None
            if not JUDGE_MODEL_ID.startswith(("claude", "gpt", "o1", "o3")):
                attacker_config = (
                    ATTACKER_NO_TOOL_CONFIG if args.disable_attacker_tools else ATTACKER_CONFIG
                )
            response = safe_generate(prompt, config=attacker_config)
            
            try:
                # 1. Directly assign to critiques_text to avoid losing the AI's attack
                # The .text property raises a ValueError if the response was blocked by safety filters
                critiques_text = response.text if response and response.text else "⚠️ Attacker response was empty."
            except (ValueError, AttributeError) as exc:
                # 2. Capture and log safety blocks or empty candidates
                error_info = f"⚠️ Attack BLOCKED (Possible Safety Filter): {str(exc)}"
                if response and hasattr(response, 'candidates') and response.candidates:
                    reason = response.candidates[0].finish_reason
                    error_info = f"⚠️ Attack BLOCKED BY SAFETY FILTERS. Reason: {reason}"             
                print(f"\n🛑 {error_info}")
                critiques_text = error_info

        # --- LEVEL 3: THE FALSIFICATION SUITE (The "Tester") ---
        print("⚙️ Executing Falsification Suite (Level 3)...")
        test_path = f"{PROJECT_DIR}/test_model.py"
        test_result_summary = ""
        test_suite_status = "missing"

        if os.path.exists(test_path):
            try:
                # We execute the python script generated by the Main Agent.
                # If an 'assert' fails, the returncode will be non-zero.
                res = subprocess.run(
                    ["python", test_path], capture_output=True, text=True, timeout=15
                )

                if res.returncode == 0:
                    test_result_summary = f"✅ PASS: The thesis survived its own falsification suite.\nOutput: {res.stdout}"
                    test_suite_status = "pass"
                    print("✅ Unit tests passed.")
                else:
                    # Capture the AssertionError or SyntaxError to show the Judge
                    test_result_summary = f"❌ FAIL: The thesis was DISPROVEN by its own unit tests.\nError: {res.stderr}"
                    test_suite_status = "fail"
                    print(f"❌ Unit tests failed: {res.stderr[:50]}...")

            except subprocess.TimeoutExpired:
                test_result_summary = "❌ FAIL: The simulation timed out. The logic is computationally impossible."
                test_suite_status = "timeout"
                print("⏳ Simulation timed out.")
        else:
            test_result_summary = "⚠️ WARNING: No falsification suite (test_model.py) found for this iteration."
            test_suite_status = "missing"

        # MANDATORY: Append the results to critiques_text so the Judge sees it!
        critiques_text += (
            f"\n\n### LEVEL 3 QUANTITATIVE UNIT TEST RESULTS:\n{test_result_summary}"
        )
        log.write(f"\n## Level 3 Unit Test Results\n{test_result_summary}\n\n")
        AXIOM_PATH = f"{PROJECT_DIR}/verified_axioms.json"
        axioms = []
        if os.path.exists(AXIOM_PATH):
            with open(AXIOM_PATH, "r") as f:
                axioms = json.load(f)
        evaluation = run_meta_judge(
            thesis, evidence, main_rubric, critiques_text, axioms
        )
        if args.deterministic_score_gates:
            evaluation = apply_semantic_gate_stabilization(evaluation)
            evaluation = finalize_deterministic_score(evaluation, main_rubric, test_suite_status)
        log.write(f"# Final Score: {evaluation['score']}\n")
        log.write(f"**Weakest Point:** {evaluation['weakest_point']}\n")
        log.write(f"**Rationale:** {evaluation.get('debate_summary', 'N/A')}\n")
        if evaluation.get("crux_analysis"):
            log.write("**Crux Analysis:**\n")
            log.write("```json\n")
            log.write(json.dumps(evaluation["crux_analysis"], indent=2))
            log.write("\n```\n")

        print("\n" + "█" * 60)
        print(f"⭐ FINAL VERDICT SCORE: {evaluation['score']}")
        print(f"🛑 WEAKEST POINT: {evaluation['weakest_point']}")
        print(f"🧠 RATIONALE: {evaluation.get('debate_summary', 'N/A')}")
        print(f"📝 FULL LOG SAVED TO: {log_path}")
        print("█" * 60 + "\n")

    with open(args.eval_results_path, "w") as f:
        json.dump(evaluation, f, indent=2)

    if "probability_dag" in evaluation:
        with open(f"{PROJECT_DIR}/probability_dag.json", "w") as f:
            json.dump(evaluation["probability_dag"], f, indent=2)
        print(f"📊 Probability DAG saved to: {PROJECT_DIR}/probability_dag.json")
