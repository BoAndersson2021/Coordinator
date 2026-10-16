"""Adopt only the independently reviewed work-view correction; preserve custody."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
from http.client import HTTPConnection
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = Path('/Users/boandersson/Desktop/Machine')
EXPECTED = '9b3e2e82d59b35bf99b376024e3f694ca20c75fe2152c4389c671e9a251ba80d'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest_path = BASE / 'REVIEW_MANIFEST_V2.json'
assert sha(manifest_path) == EXPECTED
manifest = json.loads(manifest_path.read_text())
review = json.loads((BASE / 'INDEPENDENT_REVIEW_V2.json').read_text())
assert review['status'] == 'completed'
assert EXPECTED in '\n'.join(review['final'])
assert 'PASS' in '\n'.join(review['final'])
proof = json.loads((BASE / 'HOOK_VERIFICATION.json').read_text())
assert proof['status'] == 'PASS' and all(case['passed'] for case in proof['cases'])
baseline = json.loads((BASE / 'BASELINE.json').read_text())
private = lambda: {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / '.machine').rglob('*') if p.is_file()}
for relative, digest in baseline['source'].items():
    assert sha(ROOT / relative) == digest, 'Source drift before adoption: ' + relative
assert private() == baseline['private']
candidate = Path(manifest['candidate_root'])
for relative, digest in manifest['files'].items():
    assert sha(candidate / relative) == digest, relative
directory = BASE / 'installation'
directory.mkdir()
sys.path.insert(0, str(ROOT / 'src'))
import dashboard
configuration = dashboard.load_configuration(ROOT)
service_before = dashboard.health_request(configuration)
previous = {}
for relative in manifest['files']:
    target = ROOT / relative
    if target.exists():
        saved = directory / 'previous' / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        previous[relative] = sha(target)
for relative, digest in manifest['files'].items():
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate / relative, target)
    assert sha(target) == digest
assert private() == baseline['private']
assert sha(ROOT / 'scripts/check_workflow_invariant.py') == baseline['source']['scripts/check_workflow_invariant.py']
assert sha(ROOT / '.git/machine-invariant-hooks/check_workflow_invariant.py') == baseline['source']['scripts/check_workflow_invariant.py']
result = {'status': 'PASS', 'recorded_at': datetime.now(timezone.utc).isoformat(),
          'review_manifest_sha256': EXPECTED, 'review_turn_id': review['turn_id'],
          'adopted_files': manifest['files'], 'previous': previous,
          'private_files_preserved': len(baseline['private']), 'checker_and_policy_unchanged': True,
          'manual_dashboard_restart': False, 'workflow_execution': 'blocked',
          'next': 'Verify real CLI/API agreement and automatic source reload; no lifecycle command.'}
(directory / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'adopted_files': len(manifest['files']),
                  'private_files_preserved': len(baseline['private']), 'workflow_execution': 'blocked'}))

# Observe the existing managed source watcher; never start/restart it manually.
deadline = time.monotonic() + 20
while True:
    try:
        service_after = dashboard.health_request(configuration)
        if service_after['instance'] != service_before['instance']:
            break
    except (OSError, ValueError):
        pass
    assert time.monotonic() < deadline, 'Automatic dashboard source reload failed'
    time.sleep(0.25)
cli = subprocess.run([sys.executable, '-B', str(ROOT / 'src/machine.py'), 'work-view'],
                     capture_output=True, text=True, timeout=10)
assert cli.returncode == 3, cli.stderr
work = json.loads(cli.stdout)
connection = HTTPConnection('127.0.0.1', configuration['port'], timeout=3)
try:
    connection.request('GET', '/api/snapshot', headers={'X-Machine-Token': configuration['token']})
    response = connection.getresponse()
    assert response.status == 200
    http = json.loads(response.read())
finally:
    connection.close()
assert work['counts'] == http['counts']
assert len(work['tasks']) == len(http['tasks'])
for cli_task, http_task in zip(work['tasks'], http['tasks']):
    for field, value in http_task.items():
        assert cli_task[field] == value, (cli_task['id'], field)
    assert 'report' not in http_task
assert work['workflow_invariant']['workflow_ready'] is False
assert not work['network_observation'] and not http['network_observation']
assert 'bridge-collect' not in work['next']
task = next(t for t in work['tasks'] if t['id'] == 'native-inspection-fresh-start-001')
assert task['ledger_state'] == 'delivered' and task['version'] == 3 and task['attempts'] == 1
assert task['execution_status'] == 'not_established'
assert task['completion_status'] == 'no_completed_report'
assert task['verification_status'] == 'not_reviewed'
assert private() == baseline['private']
acceptance = {'status': 'PASS', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'service_before': service_before, 'service_after': service_after,
              'automatic_source_reload': True, 'manual_lifecycle_commands': 0,
              'cli_exit_code': cli.returncode, 'cli_http_projection_equal': True,
              'counts': work['counts'], 'http_tasks': http['tasks'],
              'private_files_preserved': len(baseline['private']),
              'workflow_execution': 'blocked', 'runtime_automation_qualified': False}
(BASE / 'INSTALLED_VERIFICATION.json').write_text(json.dumps(acceptance, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'cli_http_projection_equal': True,
                  'automatic_source_reload': True, 'dashboard_pid': service_after['pid'],
                  'private_files_preserved': len(baseline['private'])}))
