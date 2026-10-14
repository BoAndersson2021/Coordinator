"""Record actual owner scope and issue one permit; never execute as the receiver."""
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import subprocess
import uuid

proof = Path(__file__).resolve().parent
root = Path('/Users/boandersson/Desktop/Machine')
target = '01a13808-1755-7643-9165-f2035aa16d16'
coordinator = '01a13696-5178-7d03-bf4e-f97d365abf9d'
assert os.environ.get('CODEX_THREAD_ID') == os.environ.get('CODEX_SESSION_ID') == coordinator
preflight = json.loads((proof / 'PREFLIGHT.json').read_text())
assert preflight['thread']['id'] == target and preflight['thread']['status']['type'] == 'idle'
assert preflight['turns'][0]['id'] == '01a13834-aea0-7741-b9f5-a3b8c5daf2a3'
assert preflight['turns'][0]['status'] == 'completed'
assert any(x.get('type') == 'agentMessage' and x.get('phase') == 'final_answer'
           and str(root) in x['text'] and target in x['text'] for x in preflight['turns'][0]['items'])
now = datetime.now(timezone.utc)
observation = {'schema_version': 1, 'thread_id': target,
    'server_id': 'codex_tui:current-task-server', 'cwd': str(root), 'status': 'idle',
    'observed_at': now.isoformat(), 'source': 'codex_tui.read_thread'}
decision = {'schema_version': 1, 'kind': 'scratch_init_admission', 'owner': 'boandersson',
    'owner_quote': 'Agreed. You run it', 'machine_root': str(root),
    'coordinator_thread_id': coordinator, 'target_thread_id': target,
    'scratch_root': '/private/tmp/machine-agent-behavior-m00nxp6a/studio', 'init_owner': 'BehaviorTest',
    'issued_at': now.isoformat(), 'expires_at': (now + timedelta(minutes=15)).isoformat()}
for name, data in (('OBSERVATION.json', observation), ('OWNER_DECISION.json', decision)):
    with (proof / name).open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
admission, permit = str(uuid.uuid4()), str(uuid.uuid4())
ids = {'admission_id': admission, 'permit_id': permit, 'target_thread_id': target,
       'coordinator_thread_id': coordinator, 'preflight_turn': preflight['turns'][0]['id']}
(proof / 'LIVE_IDS.json').write_text(json.dumps(ids, indent=2) + '\n')
commands = [('ADMIT_RESULT', [str(root / 'Machine'), 'session-admit', '--observation', str(proof / 'OBSERVATION.json'),
    '--owner-decision', str(proof / 'OWNER_DECISION.json'), '--operation-id', admission]),
    ('ISSUE_RESULT', [str(root / 'Machine'), 'permit-issue', '--admission-id', admission, '--operation-id', permit])]
for name, command in commands:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    evidence = {'argv': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    (proof / (name + '.json')).write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence))
    assert result.returncode == 0
