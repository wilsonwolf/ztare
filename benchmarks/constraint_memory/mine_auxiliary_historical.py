import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / 'benchmarks' / 'constraint_memory'
SUITE_DIR = BENCH / 'auxiliary_historical'

MAPPING = {
    'hbr_case_method_roi_proxy': {
        'project_dir': ROOT / 'projects' / 'hbr_strategy',
        'thesis_rel': 'history/1775180818_iter1_score_155_hbr_strategy.md',
        'expected_exploit': 'Claim-test mismatch, Self-referential ROI projection, Selective rigor',
        'description': (
            'The thesis claims the Case Method Executive framework will reduce initiative failure rates by 5 percentage points, '
            'but the test suite only proves that if one assumes a 5-point reduction, the ROI proxy rises. '
            'It validates the downstream arithmetic consequence of the assumption rather than the causal claim.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the thesis uses optimistic numbers or a weak baseline. '
            'Count family_detected=true only if it identifies that the test suite validates the ROI arithmetic implied by an assumed '
            'failure-rate reduction instead of testing whether the framework actually causes that reduction.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the falsification suite proves only the arithmetic consequence of an assumed mitigation delta rather than testing whether the Case Method Executive framework causes that delta.',
            'The evaluator kills the thesis because the proof validates an ROI proxy conditional on the thesis-authored 5-point reduction and therefore never independently tests the load-bearing causal claim.',
            'The evaluator kills the thesis because the code rigorously checks bookkeeping around expected NPV while leaving the actual intervention efficacy untested.'
        ],
        'detection_keywords': [
            'claim-test mismatch',
            'downstream arithmetic only',
            'roi proxy',
            'self-referential roi projection',
            'tests consequence not cause',
            'untested mitigation delta'
        ],
        'family_negative_examples': [
            'optimistic roi',
            'weak baseline',
            'bad executive estimate',
            'high wacc'
        ],
        'structural_detection_keywords': [
            'assumed reduction',
            'causal claim untested',
            'conditional arithmetic',
            'failure-rate reduction',
            'roi consequence',
            'self-authored delta'
        ],
    },
    'ai_inference_internal_price_floor': {
        'project_dir': ROOT / 'projects' / 'ai_inference_collapse_gemini_gemini',
        'thesis_rel': 'history/v5_score_95.md',
        'expected_exploit': 'Self-referential falsification, Internally constructed Y, Cooked books',
        'description': (
            'The thesis claims a hyperscaler-backed OSS market price ceiling below $1/1M tokens and a November 2025 insolvency event. '
            'The test suite internally constructs the price ceiling Y from its own chosen cost stack and then proves insolvency from that internally-authored Y, '
            'rather than validating the market ceiling independently.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the cost assumptions are aggressive or the market forecast is weak. '
            'Count family_detected=true only if it identifies that the decisive market ceiling Y is constructed from thesis-authored internal inputs and then used to self-certify the insolvency timeline.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the market price ceiling Y is internally constructed from thesis-authored cost assumptions rather than independently grounded, so the insolvency proof is self-referential.',
            'The evaluator kills the thesis because the code validates the consequences of its own chosen hyperscaler cost stack instead of testing whether that market floor exists in the world.',
            'The evaluator kills the thesis because the November 2025 insolvency date is forced by an internally manufactured price ceiling and therefore does not constitute independent falsification.'
        ],
        'detection_keywords': [
            'constructed y',
            'internal price floor',
            'market ceiling self-authored',
            'self-referential falsification',
            'tests own floor',
            'y is internally derived'
        ],
        'family_negative_examples': [
            'price too low',
            'weak forecast',
            'aggressive margin assumption',
            'bad date estimate'
        ],
        'structural_detection_keywords': [
            'internally constructed',
            'market price ceiling',
            'november 2025',
            'own cost stack',
            'self-certified floor',
            'y variable'
        ],
    },
    'central_station_mirrored_monte_carlo': {
        'project_dir': ROOT / 'projects' / 'central_station',
        'thesis_rel': 'history/1775271249_iter9_score_95_startup_experiment_design.md',
        'expected_exploit': 'Perfectly mirrored simulation, Tautological verification, Claim-test mismatch',
        'description': (
            'The thesis simulates a world where the parameter ranges already encode the desired conclusion '
            '(same cohort retention dominates random; referral timing remains noisy) and then treats Monte Carlo dominance rates as proof. '
            'The fixed seed makes the printed path reproducible, but the deeper problem is that the simulated world is authored to favor the conclusion.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the simulation uses a fixed seed. '
            'Count family_detected=true only if it identifies that the Monte Carlo environment is parameterized so the preferred design already wins by construction, '
            'making the proof a mirrored or tautological simulation rather than an independent test.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the Monte Carlo world is built from parameter ranges that already encode the conclusion, so the simulation only confirms a mirrored environment.',
            'The evaluator kills the thesis because the test suite proves dominance inside a thesis-authored behavioral world rather than independently validating that world.',
            'The evaluator kills the thesis because the seed is merely reproducibility theater layered over a more fundamental tautology: the simulation priors already guarantee the claimed ordering.'
        ],
        'detection_keywords': [
            'mirrored simulation',
            'perfectly mirrored simulation',
            'simulation world encodes conclusion',
            'tautological verification',
            'seed is incidental',
            'parameterized to win'
        ],
        'family_negative_examples': [
            'uses fixed seed',
            'n=20 is rigid',
            'simulation is deterministic',
            'monte carlo is noisy'
        ],
        'structural_detection_keywords': [
            'authored behavioral ranges',
            'common random world',
            'conclusion built in',
            'mirrored world',
            'same cohort dominates by construction',
            'tautological simulation'
        ],
    },
    'central_station_hypothetical_target_laundering': {
        'project_dir': ROOT / 'projects' / 'central_station',
        'thesis_rel': 'history/1775257745_iter5_score_100_central_station.md',
        'expected_exploit': 'Hypothetical-target laundering, Claim-test mismatch, Tautological verification',
        'description': (
            'The thesis feeds hypothetical target P50 values into the viability model and then asserts that those same '
            'targets imply a healthy business. The key member-acquisition result is explicitly assumed rather than tested, '
            'so the code validates a thesis-authored target world instead of independently falsifying the business.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the thesis uses optimistic startup assumptions or '
            'weak market inputs. Count family_detected=true only if it identifies that the test suite launders hypothetical '
            'target values as if they were validated observations, or that the proof assumes the decisive acquisition/fit '
            'result and then checks downstream viability thresholds inside that assumed world.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the financial model is fed hypothetical target P50 values and then treats those thesis-authored targets as if they were validated evidence.',
            'The evaluator kills the thesis because the code assumes the decisive member-acquisition and problem-solution-fit outcomes already occurred, then only verifies downstream viability arithmetic.',
            'The evaluator kills the thesis because the proof validates business viability inside an authored target world rather than independently testing whether the sprint can produce that world.'
        ],
        'detection_keywords': [
            'hypothetical-target laundering',
            'assumed target world',
            'claim-test mismatch',
            'tests viability not validation',
            'hypothetical p50s treated as observed',
            'downstream viability only'
        ],
        'family_negative_examples': [
            'startup assumptions are optimistic',
            'market too small',
            'weak referral estimate',
            'pre-seed model is speculative'
        ],
        'structural_detection_keywords': [
            'hypothetical observed p50',
            'assumes 80 members',
            'problem-solution-fit target',
            'validated observations not tested',
            'target inputs laundered as evidence',
            'viability checked inside assumed world'
        ],
    },
}


def extract_code_block(markdown_text):
    match = re.search(r"```python\s*\n(.*?)\n```", markdown_text, re.DOTALL)
    if not match:
        raise ValueError('No python code block found in thesis markdown.')
    return match.group(1).rstrip() + '\n'


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def build_suite():
    SUITE_DIR.mkdir(parents=True, exist_ok=True)
    index_payload = []

    for specimen_id, cfg in MAPPING.items():
        project_dir = cfg['project_dir']
        thesis_path = project_dir / cfg['thesis_rel']
        evidence_path = project_dir / 'evidence.txt'
        axioms_path = project_dir / 'verified_axioms.json'
        output_dir = SUITE_DIR / specimen_id
        output_dir.mkdir(parents=True, exist_ok=True)

        thesis_text = thesis_path.read_text(encoding='utf-8')
        code_text = extract_code_block(thesis_text)

        shutil.copyfile(thesis_path, output_dir / 'thesis.md')
        shutil.copyfile(evidence_path, output_dir / 'evidence.txt')
        (output_dir / 'test_model.py').write_text(code_text, encoding='utf-8')
        if axioms_path.exists():
            shutil.copyfile(axioms_path, output_dir / 'verified_axioms.json')
        else:
            (output_dir / 'verified_axioms.json').write_text('[]\n', encoding='utf-8')

        specimen_meta = {
            'id': specimen_id,
            'label': 'bad',
            'expected_exploit': cfg['expected_exploit'],
            'family_detection_strict_rule': cfg['family_detection_strict_rule'],
            'acceptable_structural_failures': cfg['acceptable_structural_failures'],
            'description': cfg['description'],
            'rubric': 'constraint_memory_benchmark',
            'pass_threshold': 60,
            'detection_keywords': cfg['detection_keywords'],
            'family_negative_examples': cfg['family_negative_examples'],
            'structural_detection_keywords': cfg['structural_detection_keywords'],
            'expected_flags': {},
            'source': {
                'project_dir': str(project_dir.relative_to(ROOT)),
                'thesis_path': str(thesis_path.relative_to(ROOT)),
                'evidence_path': str(evidence_path.relative_to(ROOT)),
            },
        }
        write_json(output_dir / 'specimen.json', specimen_meta)
        write_json(
            output_dir / 'source_metadata.json',
            {
                'id': specimen_id,
                'origin': 'historical_expansion_candidate',
                'project_dir': str(project_dir.relative_to(ROOT)),
                'thesis_path': str(thesis_path.relative_to(ROOT)),
            },
        )
        index_payload.append(
            {
                'id': specimen_id,
                'project_dir': str(project_dir.relative_to(ROOT)),
                'thesis_path': str(thesis_path.relative_to(ROOT)),
                'output_dir': str(output_dir.relative_to(ROOT)),
            }
        )

    write_json(SUITE_DIR / 'index.json', index_payload)


if __name__ == '__main__':
    build_suite()
