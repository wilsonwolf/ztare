import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from google import genai
import anthropic
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = Path(__file__).resolve().parent
SPECIMENS_ROOT = BENCH_ROOT / 'specimens'
MAIN_SPECIMEN_ROOTS = [
    SPECIMENS_ROOT / 'bad',
    SPECIMENS_ROOT / 'good',
    SPECIMENS_ROOT / 'corpus_bad',
]
OOD_ROOT = SPECIMENS_ROOT / 'ood'
STAGE1_OOD_ROOT = BENCH_ROOT / 'stage1_ood'
STAGE3_OOD_ROOT = BENCH_ROOT / 'stage3_ood'
DERIVED_SUBTLE_ROOT = BENCH_ROOT / 'derived_subtle'
CLAIM_TEST_MISMATCH_ROOT = BENCH_ROOT / 'claim_test_mismatch'
AUXILIARY_HISTORICAL_ROOT = BENCH_ROOT / 'auxiliary_historical'
RUNS_ROOT = BENCH_ROOT / 'runs'

STAGE1_REGRESSION_SPECIMENS = {
    't2_ai_inference',
    'deterministic_score_contract',
    'fail_closed_test_status',
}

STAGE2_REGRESSION_SPECIMENS = {
    't2_ai_inference',
    'deterministic_score_contract',
    'future_distress_threshold_fabrication',
    'opaque_local_risk_router',
    'local_gate_whole_system_overclaim',
}

STAGE3_REGRESSION_SPECIMENS = {
    't2_ai_inference',
    'deterministic_score_contract',
    'future_distress_threshold_fabrication',
    'opaque_local_risk_router',
    'local_gate_whole_system_overclaim',
    'straw_man_design_central_station',
}

BASE_CONDITIONS = {
    'A_baseline_soft_judge': [],
    'B_deterministic_gates': ['--deterministic_score_gates'],
    'C_gates_plus_primitives': ['--deterministic_score_gates', '--use_primitives'],
}

EXPERIMENTAL_CONDITIONS = {
    'C2_gates_plus_primitives_crux_first': [
        '--deterministic_score_gates',
        '--use_primitives',
        '--crux_first_primitives',
    ],
}

_MODEL_MAP = {
    'gemini': 'gemini-2.5-flash',
    'claude': 'claude-sonnet-4-6',
    'claude-opus': 'claude-opus-4-6',
    'gpt4o': 'gpt-4o',
}

_gemini_client = None
_anthropic_client = None
_openai_client = None


def _debug_print(enabled, message):
    if enabled:
        print(f"[debug] {message}", flush=True)


def _get_model_client(model_key):
    global _gemini_client, _anthropic_client, _openai_client
    model_id = _MODEL_MAP[model_key]
    if model_key == 'gemini':
        if _gemini_client is None:
            _gemini_client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        return model_id, _gemini_client
    if model_key in {'claude', 'claude-opus'}:
        if _anthropic_client is None:
            _anthropic_client = anthropic.Anthropic(
                api_key=os.environ.get('ANTHROPIC_API_KEY')
            )
        return model_id, _anthropic_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    return model_id, _openai_client


def _call_json_model(prompt, model_key):
    model_id, client = _get_model_client(model_key)
    if model_key == 'gemini':
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
        )
        text = response.text
    elif model_key in {'claude', 'claude-opus'}:
        response = client.messages.create(
            model=model_id,
            max_tokens=1200,
            messages=[{'role': 'user', 'content': prompt}],
        )
        text = response.content[0].text
    else:
        response = client.chat.completions.create(
            model=model_id,
            max_tokens=1200,
            messages=[{'role': 'user', 'content': prompt}],
        )
        text = response.choices[0].message.content

    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f'Could not parse JSON from adjudicator response: {text[:300]}')
    return json.loads(text[start:end + 1])


def load_specimens(specimen_filter=None, suite='main'):
    specimens = []
    roots = []
    if suite in {'main', 'all'}:
        roots.extend(MAIN_SPECIMEN_ROOTS)
    if suite == 'stage1_regression':
        roots.extend(MAIN_SPECIMEN_ROOTS)
    if suite == 'stage2_regression':
        roots.extend(MAIN_SPECIMEN_ROOTS)
        roots.append(STAGE1_OOD_ROOT)
    if suite == 'stage3_regression':
        roots.extend(MAIN_SPECIMEN_ROOTS)
        roots.append(STAGE1_OOD_ROOT)
        roots.append(STAGE3_OOD_ROOT)
    if suite in {'ood', 'all'}:
        roots.append(OOD_ROOT)
    if suite == 'stage1_ood':
        roots.append(STAGE1_OOD_ROOT)
    if suite in {'derived_subtle', 'all'}:
        roots.append(DERIVED_SUBTLE_ROOT)
    if suite in {'claim_test_mismatch', 'all'}:
        roots.append(CLAIM_TEST_MISMATCH_ROOT)
    if suite in {'auxiliary_historical', 'all'}:
        roots.append(AUXILIARY_HISTORICAL_ROOT)
    for root in roots:
        if not root.exists():
            continue
        for meta_path in sorted(root.rglob('specimen.json')):
            meta = json.loads(meta_path.read_text())
            if specimen_filter and meta['id'] != specimen_filter:
                continue
            if suite == 'stage1_regression' and meta['id'] not in STAGE1_REGRESSION_SPECIMENS:
                continue
            if suite == 'stage2_regression' and meta['id'] not in STAGE2_REGRESSION_SPECIMENS:
                continue
            if suite == 'stage3_regression' and meta['id'] not in STAGE3_REGRESSION_SPECIMENS:
                continue
            meta['_dir'] = meta_path.parent
            specimens.append(meta)
    if not specimens:
        raise SystemExit('No specimens found for requested filter.')
    return specimens


def stage_project(specimen, run_id, condition_name):
    project_name = f"_bench_{run_id}_{specimen['id']}_{condition_name}"
    project_dir = ROOT / 'projects' / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(specimen['_dir'] / 'thesis.md', project_dir / 'current_iteration.md')
    shutil.copyfile(specimen['_dir'] / 'evidence.txt', project_dir / 'evidence.txt')
    shutil.copyfile(specimen['_dir'] / 'test_model.py', project_dir / 'test_model.py')
    axioms_path = specimen['_dir'] / 'verified_axioms.json'
    if axioms_path.exists():
        shutil.copyfile(axioms_path, project_dir / 'verified_axioms.json')
    else:
        (project_dir / 'verified_axioms.json').write_text('[]\n', encoding='utf-8')
    return project_name, project_dir


def get_latest_log(project_dir, before_logs):
    after_logs = set(project_dir.glob('debate_log_iter_*.md'))
    new_logs = sorted(after_logs - before_logs)
    if new_logs:
        return new_logs[-1]
    all_logs = sorted(after_logs)
    return all_logs[-1] if all_logs else None


def detect_specimen(specimen, evaluation):
    text_parts = [
        str(evaluation.get('weakest_point', '')),
        str(evaluation.get('debate_summary', '')),
        json.dumps(evaluation.get('score_contract', {})),
        json.dumps(evaluation.get('criteria_failed', [])),
    ]
    haystack = ' '.join(text_parts).lower()
    family_matched_keywords = [
        keyword
        for keyword in specimen.get('detection_keywords', [])
        if keyword.lower() in haystack
    ]
    structural_matched_keywords = [
        keyword
        for keyword in specimen.get('structural_detection_keywords', [])
        if keyword.lower() in haystack
    ]
    expected_flags = specimen.get('expected_flags', {})
    family_flags_match = bool(expected_flags) and all(
        evaluation.get(key) == value for key, value in expected_flags.items()
    )
    structural_expected_flags = specimen.get('structural_expected_flags', {})
    structural_flags_match = bool(structural_expected_flags) and all(
        evaluation.get(key) == value for key, value in structural_expected_flags.items()
    )
    family_detected = bool(family_matched_keywords) or family_flags_match
    structural_detected = (
        family_detected
        or bool(structural_matched_keywords)
        or structural_flags_match
    )
    return {
        'family_detected': family_detected,
        'family_matched_keywords': family_matched_keywords,
        'family_flags_match': family_flags_match,
        'structural_detected': structural_detected,
        'structural_matched_keywords': structural_matched_keywords,
        'structural_flags_match': structural_flags_match,
    }


def adjudicate_detection(specimen, evaluation, adjudicator_model):
    prompt = f"""
You are adjudicating whether an evaluator correctly identified:
1. the expected exploit family, and/or
2. an acceptable alternative fatal structural flaw.

Return strict JSON with this schema:
{{
  "family_detected": true or false,
  "fatal_structural_detected": true or false,
  "confidence_family": "high" | "medium" | "low",
  "confidence_structural": "high" | "medium" | "low",
  "rationale_family": "<one short paragraph>",
  "rationale_structural": "<one short paragraph>"
}}

Rules:
- Focus on semantic equivalence, not exact wording.
- `family_detected` means the evaluator clearly identified the same exploit family or a very close taxonomic equivalent.
- `fatal_structural_detected` means the evaluator identified a genuinely fatal structural flaw that should count as a true positive kill even if it did not use the expected exploit-family label.
- Do not require the exact exploit label to appear verbatim.
- If the evaluator only criticizes a generic weakness without reaching either the exploit family or an acceptable fatal structural flaw, return false.
- Be stricter for `family_detected` than for `fatal_structural_detected`.
- A generic critique such as "weak forecast", "unsupported assumption", or "unproven inevitability claim" is NOT enough for `family_detected` unless it also identifies exploit-family behavior like rigged thresholds, hardcoded constants, cherry-picked parameters, fake differentiability, self-certification, or equivalent quantitative manipulation.

Expected exploit family:
{specimen.get("expected_exploit")}

Family-detection strict rule:
{specimen.get("family_detection_strict_rule", "None.")}

Acceptable alternative fatal structural failures:
{json.dumps(specimen.get("acceptable_structural_failures", []), indent=2)}

Specimen description:
{specimen.get("description", "")}

Known exploit-family keywords:
{json.dumps(specimen.get("detection_keywords", []), indent=2)}

Family-detection negative examples:
{json.dumps(specimen.get("family_negative_examples", []), indent=2)}

Known structural-failure keywords:
{json.dumps(specimen.get("structural_detection_keywords", []), indent=2)}

Evaluator weakest point:
{evaluation.get("weakest_point", "")}

Evaluator debate summary:
{evaluation.get("debate_summary", "")}

Evaluator criteria_failed:
{json.dumps(evaluation.get("criteria_failed", []))}

Evaluator score_contract:
{json.dumps(evaluation.get("score_contract", {}), indent=2)}
"""
    return _call_json_model(prompt, adjudicator_model)


def run_one(specimen, condition_name, flags, judge_model, run_id, pass_threshold, debug=False, stream_child=False, adjudicator_model=None, suite='main'):
    project_name, project_dir = stage_project(specimen, run_id, condition_name)
    results_dir = RUNS_ROOT / run_id / specimen['id'] / condition_name
    results_dir.mkdir(parents=True, exist_ok=True)
    before_logs = set(project_dir.glob('debate_log_iter_*.md'))

    eval_path = results_dir / 'eval_results.raw.json'
    _debug_print(debug, f"staged project={project_name}")

    cmd = [
        sys.executable,
        '-m',
        'src.ztare.validator.test_thesis',
        '--project', project_name,
        '--rubric', specimen.get('rubric', 'epistemic_engine_v4'),
        '--judge_model', judge_model,
        '--mutator_model', 'benchmark',
        '--disable_attacker_tools',
        '--eval_results_path', str(eval_path),
        *flags,
    ]
    if suite == 'stage3_regression' and '--use_primitives' in flags:
        cmd.extend(['--primitive_routing_profile', 'v4'])
    _debug_print(debug, f"running {' '.join(cmd)}")

    if stream_child:
        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        stdout_lines = []
        assert proc.stdout is not None
        prefix = f"[{specimen['id']}::{condition_name}] "
        for line in proc.stdout:
            stdout_lines.append(line)
            print(prefix + line.rstrip(), flush=True)
        proc.wait()
        proc_stdout = ''.join(stdout_lines)
        proc_stderr = ''
    else:
        proc_completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        proc = proc_completed
        proc_stdout = proc_completed.stdout
        proc_stderr = proc_completed.stderr

    (results_dir / 'stdout.txt').write_text(proc_stdout, encoding='utf-8')
    (results_dir / 'stderr.txt').write_text(proc_stderr, encoding='utf-8')

    if proc.returncode != 0:
        _debug_print(debug, f"subprocess failed returncode={proc.returncode}")
        return {
            'project_name': project_name,
            'condition': condition_name,
            'returncode': proc.returncode,
            'error': 'validator module failed to execute',
            'stdout_path': str(results_dir / 'stdout.txt'),
            'stderr_path': str(results_dir / 'stderr.txt'),
        }

    if not eval_path.exists():
        _debug_print(debug, "missing eval_results output")
        return {
            'project_name': project_name,
            'condition': condition_name,
            'returncode': proc.returncode,
            'error': 'eval_results.json not produced',
            'stdout_path': str(results_dir / 'stdout.txt'),
            'stderr_path': str(results_dir / 'stderr.txt'),
        }

    evaluation = json.loads(eval_path.read_text(encoding='utf-8'))
    (results_dir / 'eval_results.json').write_text(
        json.dumps(evaluation, indent=2) + '\n', encoding='utf-8'
    )

    log_path = get_latest_log(project_dir, before_logs)
    if log_path:
        shutil.copyfile(log_path, results_dir / 'debate_log.md')

    detection = detect_specimen(specimen, evaluation)
    adjudication = None
    family_adjudicator_detected = None
    structural_adjudicator_detected = None
    if specimen['label'] == 'bad' and adjudicator_model:
        try:
            adjudication = adjudicate_detection(specimen, evaluation, adjudicator_model)
            family_adjudicator_detected = bool(adjudication.get('family_detected'))
            structural_adjudicator_detected = bool(adjudication.get('fatal_structural_detected'))
        except Exception as exc:
            adjudication = {
                'error': str(exc),
                'family_detected': None,
                'fatal_structural_detected': None,
            }
        (results_dir / 'detection_adjudication.json').write_text(
            json.dumps(adjudication, indent=2) + '\n', encoding='utf-8'
        )
    family_detected = detection['family_flags_match'] or (
        family_adjudicator_detected if adjudicator_model else detection['family_detected']
    )
    structural_detected = (
        family_detected
        or detection['structural_flags_match']
        or (structural_adjudicator_detected if adjudicator_model else detection['structural_detected'])
    )
    score = evaluation.get('score')
    passed = isinstance(score, (int, float)) and score >= pass_threshold

    row = {
        'project_name': project_name,
        'condition': condition_name,
        'label': specimen['label'],
        'specimen_id': specimen['id'],
        'expected_exploit': specimen.get('expected_exploit'),
        'acceptable_structural_failures': specimen.get('acceptable_structural_failures', []),
        'score': score,
        'passed_threshold': passed,
        'detected': structural_detected,
        'family_detected': family_detected,
        'structural_detected': structural_detected,
        'heuristic_detected': detection['structural_detected'],
        'heuristic_family_detected': detection['family_detected'],
        'heuristic_structural_detected': detection['structural_detected'],
        'adjudicator_detected': structural_adjudicator_detected,
        'adjudicator_family_detected': family_adjudicator_detected,
        'adjudicator_structural_detected': structural_adjudicator_detected,
        'matched_keywords': detection['structural_matched_keywords'],
        'matched_family_keywords': detection['family_matched_keywords'],
        'matched_structural_keywords': detection['structural_matched_keywords'],
        'flags_match': detection['structural_flags_match'],
        'family_flags_match': detection['family_flags_match'],
        'structural_flags_match': detection['structural_flags_match'],
        'weakest_point': evaluation.get('weakest_point'),
        'stdout_path': str(results_dir / 'stdout.txt'),
        'stderr_path': str(results_dir / 'stderr.txt'),
        'eval_results_path': str(results_dir / 'eval_results.json'),
        'detection_adjudication_path': str(results_dir / 'detection_adjudication.json') if adjudicator_model and specimen['label'] == 'bad' else None,
        'debate_log_path': str(results_dir / 'debate_log.md') if log_path else None,
        'returncode': proc.returncode,
    }

    if condition_name == 'A_baseline_soft_judge' and specimen['label'] == 'bad':
        row['score_decoupling'] = bool(structural_detected and passed)

    _debug_print(
        debug,
        f"completed score={score} family={family_detected} structural={structural_detected} "
        f"heur_family={detection['family_detected']} heur_struct={detection['structural_detected']} "
        f"adj_family={family_adjudicator_detected} adj_struct={structural_adjudicator_detected} "
        f"passed_threshold={passed}",
    )
    return row


def summarize(rows, pass_threshold, conditions):
    summary = {'pass_threshold': pass_threshold, 'conditions': {}}
    for condition_name in conditions:
        cond_rows = [r for r in rows if r['condition'] == condition_name and 'error' not in r]
        bad_rows = [r for r in cond_rows if r['label'] == 'bad']
        good_rows = [r for r in cond_rows if r['label'] == 'good']
        condition_summary = {
            'num_specimens': len(cond_rows),
            'num_bad': len(bad_rows),
            'num_good': len(good_rows),
            'exploit_family_detection_rate': (sum(1 for r in bad_rows if r['family_detected']) / len(bad_rows)) if bad_rows else None,
            'fatal_structural_detection_rate': (sum(1 for r in bad_rows if r['structural_detected']) / len(bad_rows)) if bad_rows else None,
            'exploit_detection_rate': (sum(1 for r in bad_rows if r['structural_detected']) / len(bad_rows)) if bad_rows else None,
            'false_accept_rate': (sum(1 for r in bad_rows if r['passed_threshold']) / len(bad_rows)) if bad_rows else None,
            'false_reject_rate': (sum(1 for r in good_rows if not r['passed_threshold']) / len(good_rows)) if good_rows else None,
            'mean_bad_score': (sum(r['score'] for r in bad_rows) / len(bad_rows)) if bad_rows else None,
            'mean_good_score': (sum(r['score'] for r in good_rows) / len(good_rows)) if good_rows else None,
        }
        if condition_name == 'A_baseline_soft_judge' and bad_rows:
            condition_summary['score_decoupling_rate'] = sum(
                1 for r in bad_rows if r.get('score_decoupling')
            ) / len(bad_rows)
        summary['conditions'][condition_name] = condition_summary
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--judge-model',
        default='gemini',
        choices=['gemini', 'claude', 'claude-opus', 'gpt4o'],
    )
    parser.add_argument('--specimen', help='Run only one specimen id')
    parser.add_argument(
        '--suite',
        default='main',
        choices=['main', 'stage1_regression', 'stage2_regression', 'stage3_regression', 'stage1_ood', 'ood', 'derived_subtle', 'claim_test_mismatch', 'auxiliary_historical', 'all'],
        help='Which specimen suite to run. `main` is the corpus/control benchmark, `stage1_regression` is the cheap 3-specimen V4 gate-check set, `stage2_regression` is the cheap 5-specimen hinge-alignment set, `stage3_regression` is the cheap 6-specimen primitive-routing set, `stage1_ood` is the cheap 3-specimen stage-1 out-of-distribution probe set, `ood` is the out-of-distribution stress-test set, `derived_subtle` is the synthetic sensitivity test set, `claim_test_mismatch` is the historical selective-rigor mini-suite, and `auxiliary_historical` is a separate holdout set of additional historical candidates.',
    )
    parser.add_argument('--pass-threshold', type=int, default=60)
    parser.add_argument('--jobs', type=int, default=1, help='Number of specimen/condition runs to execute in parallel.')
    parser.add_argument('--debug', action='store_true', help='Print detailed benchmark progress.')
    parser.add_argument(
        '--adjudicator-model',
        choices=['gemini', 'claude', 'claude-opus', 'gpt4o'],
        help='Optional LLM adjudicator used to decide whether the evaluator semantically caught the exploit family.',
    )
    parser.add_argument(
        '--include-crux-first-condition',
        action='store_true',
        help='Include the experimental C2 condition where the meta-judge identifies the load-bearing claim before consulting primitive context.',
    )
    parser.add_argument(
        '--conditions',
        nargs='*',
        choices=['A_baseline_soft_judge', 'B_deterministic_gates', 'C_gates_plus_primitives', 'C2_gates_plus_primitives_crux_first'],
        help='Optional subset of benchmark conditions to run.',
    )
    args = parser.parse_args()
    conditions = dict(BASE_CONDITIONS)
    if args.include_crux_first_condition:
        conditions.update(EXPERIMENTAL_CONDITIONS)
    if args.suite == 'stage1_regression' and not args.conditions:
        conditions = {
            'B_deterministic_gates': BASE_CONDITIONS['B_deterministic_gates'],
            'C_gates_plus_primitives': BASE_CONDITIONS['C_gates_plus_primitives'],
        }
    if args.suite == 'stage2_regression' and not args.conditions:
        conditions = {
            'B_deterministic_gates': BASE_CONDITIONS['B_deterministic_gates'],
            'C_gates_plus_primitives': BASE_CONDITIONS['C_gates_plus_primitives'],
        }
    if args.suite == 'stage3_regression' and not args.conditions:
        conditions = {
            'B_deterministic_gates': BASE_CONDITIONS['B_deterministic_gates'],
            'C_gates_plus_primitives': BASE_CONDITIONS['C_gates_plus_primitives'],
        }
    if args.conditions:
        selected_conditions = {}
        all_conditions = dict(BASE_CONDITIONS)
        all_conditions.update(EXPERIMENTAL_CONDITIONS)
        for name in args.conditions:
            selected_conditions[name] = all_conditions[name]
        conditions = selected_conditions

    specimens = load_specimens(args.specimen, suite=args.suite)
    run_id = time.strftime('%Y%m%d_%H%M%S')
    run_root = RUNS_ROOT / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    tasks = []
    for specimen in specimens:
        for condition_name, flags in conditions.items():
            tasks.append((specimen, condition_name, flags))

    rows = []
    if args.jobs <= 1:
        for specimen, condition_name, flags in tasks:
            print(f"[benchmark] {specimen['id']} :: {condition_name}")
            rows.append(
                run_one(
                    specimen,
                    condition_name,
                    flags,
                    args.judge_model,
                    run_id,
                    args.pass_threshold,
                    debug=args.debug,
                    stream_child=args.debug,
                    adjudicator_model=args.adjudicator_model,
                    suite=args.suite,
                )
            )
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            future_map = {}
            for specimen, condition_name, flags in tasks:
                print(f"[benchmark] queued {specimen['id']} :: {condition_name}")
                future = executor.submit(
                    run_one,
                    specimen,
                    condition_name,
                    flags,
                    args.judge_model,
                    run_id,
                    args.pass_threshold,
                    args.debug,
                    False,
                    args.adjudicator_model,
                    args.suite,
                )
                future_map[future] = (specimen['id'], condition_name)

            for future in concurrent.futures.as_completed(future_map):
                specimen_id, condition_name = future_map[future]
                print(f"[benchmark] finished {specimen_id} :: {condition_name}")
                rows.append(future.result())

    (run_root / 'results.json').write_text(
        json.dumps(rows, indent=2) + '\n', encoding='utf-8'
    )
    summary = summarize(rows, args.pass_threshold, conditions)
    (run_root / 'metrics_summary.json').write_text(
        json.dumps(summary, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, indent=2))
    print(f"Saved benchmark run to {run_root}")


if __name__ == '__main__':
    main()
