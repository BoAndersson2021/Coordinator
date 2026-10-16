"""Read-only installed CLI/API checks after observed late automatic source reload."""
from pathlib import Path
from datetime import datetime, timezone
from http.client import HTTPConnection
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = Path('/Users/boandersson/Desktop/Machine')
sys.path.insert(0, str(ROOT / 'src'))
import dashboard

configuration = dashboard.load_configuration(ROOT)
service = dashboard.health_request(configuration)
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
assert not work['network_observation'] and not http['network_observation']
assert work['workflow_invariant']['workflow_ready'] is False
assert 'bridge-collect' not in work['next']
task = next(t for t in work['tasks'] if t['id'] == 'native-inspection-fresh-start-001')
assert task['ledger_state'] == 'delivered' and task['version'] == 3 and task['attempts'] == 1
assert task['execution_status'] == 'not_established'
assert task['completion_status'] == 'no_completed_report'
assert task['verification_status'] == 'not_reviewed'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((BASE / 'BASELINE.json').read_text())
private = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / '.machine').rglob('*') if p.is_file()}
assert private == baseline['private']
manifest = json.loads((BASE / 'REVIEW_MANIFEST_V2.json').read_text())
assert all(sha(ROOT / name) == digest for name, digest in manifest['files'].items())
events = []
for line in dashboard.service_paths(ROOT)['log'].read_text().splitlines():
    try:
        event = json.loads(line)
    except ValueError:
        continue
    if event.get('status') in ('dashboard_source_changed', 'dashboard_listening'):
        events.append(event)
changed = next(event for event in reversed(events) if event['status'] == 'dashboard_source_changed')
listening = next(event for event in reversed(events) if event['status'] == 'dashboard_listening')
assert listening['pid'] == service['pid']
elapsed = (datetime.fromisoformat(listening['started_at']) - datetime.fromisoformat(changed['at'])).total_seconds()
record = {'status': 'PASS_CURRENT_STATE', 'recorded_at': datetime.now(timezone.utc).isoformat(),
          'reviewed_pins_match': len(manifest['files']), 'cli_exit_code': cli.returncode,
          'cli_http_projection_equal': True, 'counts': work['counts'], 'http_tasks': http['tasks'],
          'service': service, 'automatic_source_reload': True, 'manual_lifecycle_commands': 0,
          'initial_reload_probe': {'status': 'FAILED', 'deadline_seconds': 20,
                                   'log': 'ADOPTION_AND_RELOAD_FAILURE.log'},
          'observed_reload_latency_seconds': elapsed,
          'latency_scope': 'Structured service source-change to following listen events; no restart-time guarantee claimed.',
          'private_files_preserved': len(private), 'workflow_execution': 'blocked',
          'runtime_automation_qualified': False}
(BASE / 'INSTALLED_VERIFICATION.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': record['status'], 'cli_http_projection_equal': True,
                  'automatic_reload_seconds': elapsed, 'dashboard_pid': service['pid'],
                  'private_files_preserved': len(private), 'initial_20_second_probe_failed': True}))
