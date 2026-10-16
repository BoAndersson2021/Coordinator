"""Automated diagnostic-service fault injection; no project/workflow lifecycle."""
from http.client import HTTPConnection
import hashlib
import json
from pathlib import Path
import os
import re
import signal
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = Path('/Users/boandersson/Desktop/Machine')
sys.path.insert(0, str(ROOT / 'src'))
import dashboard


def private_hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / '.machine').rglob('*') if p.is_file()}


def observe(config):
    connection = HTTPConnection('127.0.0.1', config['port'], timeout=2)
    try:
        connection.request('GET', '/api/snapshot', headers={'X-Machine-Token': config['token']})
        response = connection.getresponse()
        assert response.status == 200, response.status
        return json.loads(response.read())
    finally:
        connection.close()


config = dashboard.load_configuration(ROOT)
before = private_hashes()
original = dashboard.health_request(config)
job = dashboard.launchctl('print', dashboard.service_paths(ROOT)['target']).stdout
assert re.search(r'^\s*pid = ' + str(original['pid']) + r'\s*$', job, re.MULTILINE)
first = observe(config)
assert first['workflow_invariant']['workflow_ready'] is False
assert first['counts']['live_receivers_proven'] == 0
assert original['pid'] != os.getpid()
print(json.dumps({'phase': 'fault_injection', 'owned_dashboard_pid': original['pid'],
                  'action': 'Suspend diagnostic service for 12 seconds, then kill it; launchd must recover automatically.'}), flush=True)
started = time.monotonic()
os.kill(original['pid'], signal.SIGSTOP)
time.sleep(12)
os.kill(original['pid'], signal.SIGKILL)
print(json.dumps({'phase': 'process_loss_injected', 'manual_restart': False}), flush=True)
deadline = time.monotonic() + 20
failures = []
recovered = None
while time.monotonic() < deadline:
    try:
        observed = dashboard.health_request(config)
        if observed['instance'] != original['instance'] and observed['pid'] != original['pid']:
            recovered = observed
            break
    except Exception as error:
        failures.append(type(error).__name__)
    time.sleep(0.25)
assert recovered, 'Automatic diagnostic service recovery failed; no manual restart attempted'
second = observe(config)
assert second['workflow_invariant']['workflow_ready'] is False
assert second['tasks'] == first['tasks'], 'Fault test changed retained task projection'
assert first['observed_at'] != second['observed_at']
assert before == private_hashes(), 'Private Machine state changed'
baseline = json.loads((BASE / 'BASELINE.json').read_text())
assert before == baseline['private'], 'Private state drifted from pre-implementation baseline'
record = {'status': 'PASS', 'scope': 'Managed local diagnostic dashboard only; workflow automation remains unqualified',
          'original_service': original, 'recovered_service': recovered,
          'fault': 'Automated SIGSTOP for 12s then SIGKILL of exact authenticated launchd-owned dashboard PID',
          'elapsed_seconds': round(time.monotonic() - started, 3),
          'manual_restart_or_handover': False, 'transient_connection_failures': failures,
          'first_observed_at': first['observed_at'], 'recovered_observed_at': second['observed_at'],
          'counts': second['counts'], 'task_projection_preserved': True,
          'private_files_preserved': len(before), 'workflow_ready': False,
          'browser_reconnection': 'Verified separately through actual browser UI; see UI_VERIFICATION.json'}
(BASE / 'MANAGED_RECOVERY.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record), flush=True)
