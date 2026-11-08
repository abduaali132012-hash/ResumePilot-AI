import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
cases_dir = root / 'cases'
errors = []
case_ids = sorted(
    p.name for p in cases_dir.iterdir()
    if p.is_dir() and re.fullmatch(r'case_\d{2}_.+', p.name)
)
if not case_ids:
    errors.append('No named benchmark case directories found under evaluation/cases')

for case_id in case_ids:
    case_dir = cases_dir / case_id
    required = ['job_description.txt', 'candidate_resume.txt', 'expected_evidence.json']
    for name in required:
        if not (case_dir / name).exists():
            errors.append(f'{case_id}: missing {name}')
    if (case_dir / 'expected_evidence.json').exists():
        try:
            payload = json.loads((case_dir / 'expected_evidence.json').read_text(encoding='utf-8'))
            requirements = payload.get('expected')
            if requirements is None:
                requirements = payload.get('requirements')
            if not isinstance(requirements, list):
                errors.append(
                    f'{case_id}: expected_evidence.json missing expected/requirements array'
                )
        except Exception as exc:
            errors.append(f'{case_id}: invalid JSON in expected_evidence.json: {exc}')

for result_name in ['baseline_results.json', 'agent_results.json']:
    path = root / result_name
    if not path.exists():
        errors.append(f'Missing {result_name}')
        continue
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(payload, dict) or not payload:
            errors.append(f'{result_name}: expected a non-empty object at the top level')
            continue
        if set(payload) != set(case_ids):
            errors.append(
                f'{result_name}: expected results for exactly the {len(case_ids)} named '
                'benchmark cases'
            )
            continue
        for case_id, result in payload.items():
            if not isinstance(result, dict) or not {
                'aligned', 'total_expected', 'evidence_accuracy',
                'false_positives', 'false_negatives',
            }.issubset(result):
                errors.append(f'{result_name}: {case_id} is missing case metrics')
    except Exception as exc:
        errors.append(f'{result_name}: invalid JSON: {exc}')

if errors:
    for err in errors:
        print(f'ERROR: {err}')
    raise SystemExit(1)

print(f'Validated {len(case_ids)} cases and 2 result files successfully.')
