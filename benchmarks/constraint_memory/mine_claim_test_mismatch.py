import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / 'benchmarks' / 'constraint_memory'
SUITE_DIR = BENCH / 'claim_test_mismatch'

MAPPING = {
    'selective_rigor_simulation_god': {
        'project_dir': ROOT / 'projects' / 'simulation_god_claude_gemini',
        'thesis_rel': 'history/1775328514_iter13_score_95_sim_god.md',
        'expected_exploit': 'Selective Rigor, Halo Validation, Claim-test mismatch',
        'description': (
            'The specimen performs real cosmology and dimensional calculations on peripheral claims, '
            'but the load-bearing thesis is the necessity of M-hat / consciousness as a completion operator. '
            'The test suite creates a legitimacy halo around the central claim instead of directly testing it.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the thesis contains physics errors, '
            'dimensional mistakes, or unsupported metaphysical claims. Count family_detected=true only if it '
            'explicitly identifies selective rigor, a legitimacy halo, or a mismatch between the rigorous '
            'tests and the load-bearing central claim.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the test suite rigorously validates peripheral physical calculations while never testing the central claim that M-hat is logically necessary.',
            'The evaluator kills the thesis because local dimensional or cosmological consistency is being used as a legitimacy halo for an unproven identity-level thesis.',
            'The evaluator kills the thesis because the proof-of-concept demonstrates mathematical subclaims but not the load-bearing metaphysical or architectural conclusion it claims to establish.',
        ],
        'detection_keywords': [
            'selective rigor',
            'halo validation',
            'legitimacy halo',
            'claim-test mismatch',
            'peripheral proof',
            'untested central claim',
            'tests local physics not core thesis',
        ],
        'family_negative_examples': [
            'physics mistake',
            'dimensional error',
            'unsupported metaphysical claim',
            'bad constant',
        ],
        'structural_detection_keywords': [
            'peripheral',
            'central claim',
            'necessity',
            'm-hat',
            'halo',
            'tests local arithmetic',
            'does not prove',
            'core thesis untested',
        ],
    },
    'selective_rigor_recursive_bayesian': {
        'project_dir': ROOT / 'projects' / 'recursive_bayesian_claude_gemini',
        'thesis_rel': 'history/1775252009_iter4_score_95_recursive_bayesian.md',
        'expected_exploit': 'Selective Rigor, Claim-test mismatch, Scaffolding proof',
        'description': (
            'The specimen contains clean internal arithmetic and architecture-scaffolding checks '
            '(bridge parameter counts, regularization scope, beta ordering), but the load-bearing claim '
            'is that the architecture preserves predictive variance and solves the orthogonality-utility trade-off. '
            'The tests are rigorous, but they target scaffolding rather than the central claim.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the thesis has arbitrary constants '
            'or unsupported assumptions. Count family_detected=true only if it identifies that the tests are '
            'well-formed but aimed at scaffolding, bookkeeping, or internal arithmetic rather than the '
            'load-bearing variance-preservation / orthogonality claim.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the test suite validates internal architecture scaffolding rather than the central claim that the partitioned model preserves predictive variance.',
            'The evaluator kills the thesis because bridge parameter counts, scope reduction, or beta-ordering checks do not independently test the claimed orthogonality-utility resolution.',
            'The evaluator kills the thesis because the proof demonstrates arithmetic consistency of the proposed architecture but never measures or falsifies the load-bearing VPR or utility claim.',
        ],
        'detection_keywords': [
            'selective rigor',
            'claim-test mismatch',
            'scaffolding proof',
            'tests scaffolding not core claim',
            'bridge arithmetic',
            'untested variance claim',
            'untested vpr',
        ],
        'family_negative_examples': [
            'arbitrary constant',
            'unsupported assumption',
            'weak forecast',
            'bad beta choice',
        ],
        'structural_detection_keywords': [
            'variance preservation',
            'vpr',
            'orthogonality',
            'bridge parameter count',
            'scaffolding',
            'internal arithmetic',
            'does not test',
            'core claim untested',
        ],
    },
    'tautological_verification_central_station': {
        'project_dir': ROOT / 'projects' / 'central_station',
        'thesis_rel': 'history/1775255475_iter4_score_77_central_station.md',
        'expected_exploit': 'Tautological Verification, Straw-man falsification, Self-authored thresholds',
        'description': (
            'The specimen computes plausible unit economics and then verifies them against thresholds that '
            'are effectively authored by the thesis itself. The resulting falsification suite is executable '
            'and readable, but structurally trivial: it checks whether the model exceeds thresholds chosen '
            'to make the thesis pass.'
        ),
        'family_detection_strict_rule': (
            'Do NOT count family_detected=true if the evaluator only says the assumptions are optimistic or '
            'the economics are uncertain. Count family_detected=true only if it identifies tautological '
            'verification, self-authored falsification thresholds, or a straw-man test designed to pass.'
        ),
        'acceptable_structural_failures': [
            'The evaluator kills the thesis because the falsification thresholds are thesis-authored and therefore not independent tests of the business claim.',
            'The evaluator kills the thesis because the test suite verifies arithmetic downstream of chosen assumptions instead of independently stress-testing host viability or demand density.',
            'The evaluator kills the thesis because the claimed falsification protocol is a straw-man or tautology rather than an external kill test.',
        ],
        'detection_keywords': [
            'tautological verification',
            'straw-man falsification',
            'self-authored threshold',
            'trivially passable',
            'tests its own assumptions',
            'non-independent falsification',
        ],
        'family_negative_examples': [
            'optimistic assumption',
            'weak economics',
            'uncertain market',
            'high execution risk',
        ],
        'structural_detection_keywords': [
            'tautology',
            'straw man',
            'threshold',
            'self-authored',
            'non-independent',
            'tests downstream arithmetic',
            'not an external kill test',
        ],
    },
}


def extract_test_code(markdown_text: str) -> str:
    blocks = re.findall(r'```python\n(.*?)\n```', markdown_text, flags=re.DOTALL)
    if not blocks:
        raise ValueError('No python code block found in thesis markdown')
    return max(blocks, key=len).strip() + '\n'


def main():
    SUITE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for specimen_id, conf in MAPPING.items():
        project_dir = conf['project_dir']
        thesis_path = project_dir / conf['thesis_rel']
        evidence_path = project_dir / 'evidence.txt'
        axioms_path = project_dir / 'verified_axioms.json'

        thesis_text = thesis_path.read_text(encoding='utf-8')
        test_code = extract_test_code(thesis_text)

        out_dir = SUITE_DIR / specimen_id
        out_dir.mkdir(parents=True, exist_ok=True)

        specimen_json = {
            'id': specimen_id,
            'label': 'bad',
            'expected_exploit': conf['expected_exploit'],
            'family_detection_strict_rule': conf['family_detection_strict_rule'],
            'acceptable_structural_failures': conf['acceptable_structural_failures'],
            'description': conf['description'],
            'rubric': 'constraint_memory_benchmark',
            'pass_threshold': 60,
            'detection_keywords': sorted(set(conf['detection_keywords'])),
            'family_negative_examples': conf['family_negative_examples'],
            'structural_detection_keywords': sorted(set(conf['structural_detection_keywords'])),
            'expected_flags': {},
            'source': {
                'project_dir': str(project_dir.relative_to(ROOT)),
                'thesis_path': str(thesis_path.relative_to(ROOT)),
                'evidence_path': str(evidence_path.relative_to(ROOT)),
            },
        }

        (out_dir / 'specimen.json').write_text(json.dumps(specimen_json, indent=2) + '\n', encoding='utf-8')
        (out_dir / 'thesis.md').write_text(thesis_text, encoding='utf-8')
        (out_dir / 'evidence.txt').write_text(evidence_path.read_text(encoding='utf-8'), encoding='utf-8')
        (out_dir / 'test_model.py').write_text(test_code, encoding='utf-8')
        if axioms_path.exists():
            shutil.copyfile(axioms_path, out_dir / 'verified_axioms.json')
        else:
            (out_dir / 'verified_axioms.json').write_text('[]\n', encoding='utf-8')
        (out_dir / 'source_metadata.json').write_text(json.dumps(conf, indent=2, default=str) + '\n', encoding='utf-8')

        manifest.append({
            'id': specimen_id,
            'project_dir': str(project_dir.relative_to(ROOT)),
            'thesis_path': str(thesis_path.relative_to(ROOT)),
            'output_dir': str(out_dir.relative_to(ROOT)),
        })
        print(f'mined {specimen_id} -> {out_dir.relative_to(ROOT)}')

    (SUITE_DIR / 'index.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
