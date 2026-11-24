"""Certify completed execution separately from semantic coverage; never turn an interrupted run into PASS."""
import argparse
import hashlib
import json
from pathlib import Path


def summarize(result, case, exit_code):
    report = json.loads((result / 'pair_report.json').read_text())
    expected = case['stable_output_sha256']
    rows = report.get('rows', [])
    executed = (exit_code in (0, 2) and report.get('error') is None and
                report.get('stable_output_status') == 'PASS' and
                report.get('selected_event_status') in ('PASS', 'INCOMPLETE') and
                [r.get('variant') for r in rows] == ['original', 'v81'] and
                all(r.get('native_exit') == 0 and r.get('integrity') == 'PASS' and
                    r.get('stable_sha256') == expected for r in rows))
    inventory = []
    for path in sorted(result.iterdir()):
        if path.is_file() and path.name not in ('execution-summary.json', 'artifact-manifest.json'):
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            inventory.append({'file': path.name, 'bytes': path.stat().st_size, 'sha256': digest})
    (result / 'artifact-manifest.json').write_text(json.dumps(inventory, indent=2) + '\n')
    status = {'bars': case['records'], 'input_sha256': case['raw_sha256'], 'runner_exit': exit_code,
              'complete_pair_execution': 'PASS' if executed else 'FAIL_OR_INCOMPLETE',
              'stable_output_status': report.get('stable_output_status', 'NOT RUN'),
              'selected_event_status': report.get('selected_event_status', 'NOT RUN'),
              'full_semantic_state_status': 'INCOMPLETE', 'rows': rows,
              'meaning': 'CI success certifies completed pair execution and scoped audit only; not V9 release readiness.'}
    (result / 'execution-summary.json').write_text(json.dumps(status, indent=2) + '\n')
    return status, executed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--exit-code', type=int, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    a = parser.parse_args()
    s, executed = summarize(a.result, json.loads(a.case.read_text()), a.exit_code)
    with a.summary.open('a', encoding='utf-8') as f:
        f.write(f"## {s['bars']} synthetic candles\n\n"
                f"- Full pair execution: **{s['complete_pair_execution']}**\n"
                f"- Golden output: **{s['stable_output_status']}**\n"
                f"- Selected-event status: **{s['selected_event_status']}**\n"
                "- Full semantic state: **INCOMPLETE**. Not a V9 release PASS.\n")
    print(json.dumps(s, indent=2))
    raise SystemExit(0 if executed else 1)


if __name__ == '__main__':
    main()
