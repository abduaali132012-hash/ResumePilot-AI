import json
from pathlib import Path

root = Path(__file__).resolve().parent
cases_dir = root / 'cases'
errors = []
case_ids = sorted(p.name for p in cases_dir.iterdir() if p.is_dir())
if not case_ids:
    errors.append('No case directories found under evaluation/cases')

for case_id in case_ids:
    case_dir = cases_dir / case_id
    required = ['job_description.txt', 'candidate_resume.txt', 'expected_evidence.json']
    for name in required:
        if not (case_dir / name).exists():
            errors.append(f'{case_id}: missing {name}')
    if (case_dir / 'expected_evidence.json').exists():
        try:
            payload = json.loads((case_dir / 'expected_evidence.json').read_text(encoding='utf-8'))
            if 'requirements' not in payload:
                errors.append(f'{case_id}: expected_evidence.json missing requirements array')
        except Exception as exc:
            errors.append(f'{case_id}: invalid JSON in expected_evidence.json: {exc}')

for result_name in ['baseline_results.json', 'agent_results.json']:
    path = root / result_name
    if not path.exists():
        errors.append(f'Missing {result_name}')
        continue
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if 'cases' not in payload or 'summary' not in payload:
            errors.append(f'{result_name}: missing cases or summary keys')
    except Exception as exc:
        errors.append(f'{result_name}: invalid JSON: {exc}')

if errors:
    for err in errors:
        print(f'ERROR: {err}')
    raise SystemExit(1)

print(f'Validated {len(case_ids)} cases and 2 result files successfully.')
