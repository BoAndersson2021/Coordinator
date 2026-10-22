"""PANEL-owned coordinator client; uses the mission's tested Unix WebSocket route.

Only the saved PANEL receiver is writable. This is not the shared CodeExp2 CLI.
"""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import shlex
import socket
import sys
import time
import uuid

CONTROL_SOURCE_ROOT = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('PANEL_CONTROL_ROOT', str(CONTROL_SOURCE_ROOT))).resolve()
ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
os.chmod(ROOT, 0o700)
if ROOT.is_symlink() or ROOT.stat().st_uid != os.getuid() or (ROOT.stat().st_mode & 0o777) != 0o700:
    raise RuntimeError('PANEL control root must be a private owner directory')
TARGET = Path('/Users/boandersson/Desktop/PANEL')
CODEEXP2 = CONTROL_SOURCE_ROOT.parents[2]
sys.path.insert(0, str(CODEEXP2 / 'scripts'))
from human_session import Session as HumanSession, exclusive_lock
HUMAN_SESSION = ROOT / 'human-session'
SOURCE = TARGET / 'Evidence/Protocol/panel-protocol-350bb55681d1/socket-probe-final.py'
spec = importlib.util.spec_from_file_location('panel_transport', SOURCE)
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)
STATE = ROOT / 'receiver.json'

def save(path, value):
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as handle:
        handle.write(json.dumps(value, indent=2) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)

parser = argparse.ArgumentParser()
parser.add_argument('operation', choices=['admit', 'inspect', 'start', 'turn', 'collect', 'status', 'interrupt', 'close'])
parser.add_argument('--prompt')
parser.add_argument('--name', default='operation')
parser.add_argument('--outcome', help='Human-requested outcome for one admitted task session')
parser.add_argument('--scope', help='Authorized scope for one admitted task session')
parser.add_argument('--done', help='Human closure: concrete completed result')
parser.add_argument('--remains', help='Human closure: remaining work or none')
parser.add_argument('--next-action', help='Human closure: next concrete action; omit only for complete scope')
parser.add_argument('--next-authority', choices=['authorized', 'owner_decision', 'external_dependency', 'none'])
parser.add_argument('--model', help='Explicit currently advertised native model for this turn only')
parser.add_argument('--reviewer', default='auto_review', choices=['user', 'auto_review'])
parser.add_argument('--decision', choices=['accept', 'decline', 'cancel', 'reconnect-cancel'])
parser.add_argument('--marker')
args = parser.parse_args()
logpath = ROOT / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '-' + args.name + '.jsonl')
log = logpath.open('x')
os.chmod(logpath, 0o600)

def record(direction, data):
    log.write(json.dumps({'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'direction': direction, 'data': data}) + '\n')
    log.flush()

class Client(transport.Client):
    allowed_methods = {'initialize', 'initialized', 'thread/list', 'thread/read', 'thread/start', 'thread/resume', 'thread/turns/list', 'turn/start', 'turn/interrupt'}
    def receive(self):
        result = super().receive()
        record('received', result)
        return result
    def send(self, method, params=None, notify=False):
        if method == 'thread/list':
            assert params['cwd'] == str(TARGET) and params['useStateDbOnly'] is True
        elif method == 'thread/start':
            assert not STATE.exists() and params['cwd'] == str(TARGET)
        elif method.startswith(('thread/', 'turn/')):
            assert params['threadId'] == json.loads(STATE.read_text())['id']
        record('sent', {'method': method, 'params': params})
        return super().send(method, params, notify)

def connect():
    c = Client()
    c.send('initialize', {'clientInfo': {'name': 'panel_coordinator_thor', 'title': 'PANEL Coordinator Thor', 'version': '0.1'}, 'capabilities': {'experimentalApi': True}})
    c.send('initialized', {}, notify=True)
    return c

c = None
state = None
human = HumanSession(HUMAN_SESSION, CODEEXP2)
control_lock = None
try:
    if args.operation == 'admit':
        print(json.dumps(human.admit(args.outcome, args.scope)), flush=True)
        raise SystemExit(0)
    if args.operation == 'close':
        print(json.dumps(human.close(args.outcome, args.done, args.remains, args.next_action, args.next_authority)), flush=True)
        raise SystemExit(0)
    if args.operation in {'start', 'turn', 'collect', 'interrupt'}:
        human.begin_work()
        control_lock = exclusive_lock(ROOT / '.control.lock')
        control_lock.__enter__()
    state = json.loads(STATE.read_text()) if STATE.exists() else None
    c = connect()
    if args.operation == 'inspect':
        result = c.send('thread/list', {'cwd': str(TARGET), 'limit': 100, 'useStateDbOnly': True})
        save(ROOT / 'target-threads.json', result)
        print(json.dumps({'threads': [{k:t.get(k) for k in ('id','cwd','status','name','preview')} for t in result['data']], 'nextCursor': result.get('nextCursor')}), flush=True)
    elif args.operation == 'start':
        result = c.send('thread/start', {'cwd': str(TARGET), 'ephemeral': False, 'sandbox': 'workspace-write', 'approvalPolicy': 'on-request', 'approvalsReviewer': 'auto_review', 'developerInstructions': 'You are the PANEL repository builder receiving authorized bounded tasks from Coordinator Thor. The Coordinator actual session identity is unavailable; do not invent it. Follow native repository instructions and the fresh assignment. Initial phase is read-only onboarding/setup only. No product work until a later explicit assignment after setup verification. Do not launch other agents or modify other repositories. Preserve all existing work. Agent recipient replies use builder-communication/1 JSON; actual session identity is required. No staging, commits, pushes, global config changes, or Terminal injection.'})
        assert result['cwd'] == str(TARGET) and result['approvalPolicy'] == 'on-request' and result['approvalsReviewer'] == 'auto_review'
        state = {'id': result['thread']['id'], 'settings': result, 'active_turn': None, 'coordinator_session_id': os.environ.get('CODEX_THREAD_ID')}
        save(STATE, state)
        print(json.dumps({'id': state['id'], 'settings': {k:result.get(k) for k in ('cwd','approvalPolicy','approvalsReviewer','sandbox','model','instructionSources')}}), flush=True)
    elif args.operation == 'status':
        result = c.send('thread/read', {'threadId': state['id'], 'includeTurns': False})
        print(json.dumps(result), flush=True)
    elif args.operation == 'interrupt':
        assert state['active_turn']
        print(c.send('turn/interrupt', {'threadId': state['id'], 'turnId': state['active_turn']}), flush=True)
    else:
        if args.operation == 'turn':
            assert args.prompt and not state['active_turn'], 'Reconcile active turn before another send'
        else:
            assert state['active_turn'], 'No active turn to collect'
        pending = None
        resolution = False
        final = None
        texts = []
        def handler(event):
            global c, pending
            p = event['params']
            meta = p.get('_meta', {})
            if event['method'] == 'mcpServer/elicitation/request':
                assert p['threadId'] == state['id'] and p['turnId'] == state['active_turn']
                assert p.get('serverName') == 'cua_repl' and p.get('mode') == 'form'
                assert meta.get('connector_id') == 'computer-use'
                assert meta.get('tool_params', {}).get('app') in {'studio.panel.to-bo', 'studio.panel.activity-preview', 'studio.panel.coordinator-preview', 'studio.panel.agents-preview'}
                assert meta.get('tool_name') in {'get_app_state', 'get_app_screenshot', 'get_app_state_and_screenshot', 'click', 'type_text', 'paste', 'press_key', 'set_value', 'select_text', 'scroll', 'drag', 'perform_secondary_action'}
                decision = {'id': event['id'], 'result': {'action': 'accept', 'content': {}}}
                record('scoped_panel_app_inspection_consent', decision)
                c.frame(json.dumps(decision).encode())
                return
            assert event['method'] == 'item/commandExecution/requestApproval' and args.decision
            assert p['threadId'] == state['id'] and p['turnId'] == state['active_turn']
            parsed = shlex.split(p['command'])
            if len(parsed) == 3 and parsed[1] in ('-c', '-lc'):
                parsed = shlex.split(parsed[2])
            assert parsed == ['/usr/bin/touch', args.marker], 'Unexpected approval; no decision sent'
            if pending == event['id'] and args.decision == 'reconnect-cancel':
                record('replayed_pending_request', event)
                return
            pending = event['id']
            if args.decision == 'reconnect-cancel':
                c.close()
                c = connect()
                c.request_handler = handler
                resumed = c.send('thread/resume', {'threadId': state['id'], 'cwd': str(TARGET), 'excludeTurns': True, 'approvalPolicy': 'on-request', 'approvalsReviewer': 'user', 'sandbox': 'workspace-write'})
                record('reconnect', resumed)
                c.send('turn/interrupt', {'threadId': state['id'], 'turnId': state['active_turn']})
            elif args.decision == 'cancel':
                c.send('turn/interrupt', {'threadId': state['id'], 'turnId': state['active_turn']})
            else:
                decision = {'id': event['id'], 'result': {'decision': args.decision}}
                record('decision', decision)
                c.frame(json.dumps(decision).encode())
        c.request_handler = handler
        if args.operation == 'turn' and state['active_turn'] is None:
            # A just-created, idle receiver is already the exact live client.
            # Resume is only for recovery of an existing receiver; forcing it
            # here makes the app-server reject an otherwise direct-input-ready
            # session before its first turn is allowed to begin.
            observed = c.send('thread/read', {'threadId': state['id'], 'includeTurns': False})['thread']
            assert observed['id'] == state['id']
            assert observed['cwd'] == str(TARGET)
            assert observed.get('status', {}).get('type') == 'idle'
            assert observed.get('canAcceptDirectInput') is True
            record('direct_input_ready', {k: observed.get(k) for k in ('id', 'cwd', 'status', 'canAcceptDirectInput', 'model', 'modelProvider')})
            effective = state['settings']
        else:
            effective = c.send('thread/resume', {'threadId':state['id'],'cwd':str(TARGET),'excludeTurns':True})
        record('effective_settings', {k:effective.get(k) for k in ('approvalPolicy','approvalsReviewer','sandbox','cwd','instructionSources')})
        if args.operation == 'turn':
            prompt = Path(args.prompt).read_text()
            turn_params = {'threadId': state['id'], 'input': [{'type':'text','text':prompt}], 'approvalPolicy':'on-request','approvalsReviewer':args.reviewer}
            if args.model:
                turn_params['model'] = args.model
            result = c.send('turn/start', turn_params)
            state['active_turn'] = result['turn']['id']
            save(STATE,state)
        else:
            history = c.send('thread/turns/list', {'threadId':state['id'],'limit':1,'itemsView':'full'})
            for turn in history['data']:
                if turn['id'] == state['active_turn'] and turn['status'] != 'inProgress':
                    final=turn
                    texts=[item['text'] for item in turn.get('items',[]) if item.get('type') == 'agentMessage']
                    for t in texts:
                        print(t[:1600],flush=True)
        print(json.dumps({'thread':state['id'],'turn':state['active_turn'],'log':str(logpath)}),flush=True)
        deadline = time.monotonic() + 1800
        while time.monotonic() < deadline and (final is None or (pending is not None and not resolution)):
            try:
                event = c.events.pop(0) if c.events else c.receive()
            except socket.timeout:
                continue
            p = event.get('params',{})
            if 'method' in event and 'id' in event:
                handler(event)
                continue
            if p.get('threadId') not in (None,state['id']):
                continue
            method = event.get('method')
            if method == 'item/completed':
                item=p.get('item',{})
                if item.get('type') == 'agentMessage':
                    texts.append(item['text'])
                    print(item['text'][:1600],flush=True)
            if method == 'serverRequest/resolved' and p.get('requestId') == pending:
                resolution = True
            if method == 'turn/completed' and p.get('turn',{}).get('id') == state['active_turn']:
                final=p['turn']
            if final is not None and (pending is None or resolution):
                break
        if final is None:
            raise TimeoutError('Turn not complete; saved active ID must be reconciled')
        result={'thread':state['id'],'turn':final,'texts':texts,'pending_request':pending,'request_resolved':resolution,'marker_exists':Path(args.marker).exists() if args.marker else None,'log':str(logpath)}
        result_path = ROOT/(args.name+'-result.json')
        save(result_path,result)
        state['active_turn']=None
        save(STATE,state)
        source_state_path = ROOT/(args.name+'-source-state.json')
        save(source_state_path, {'workspace': str(CODEEXP2), 'receiver_id': state['id'], 'turn_id': final['id']})
        terminal = {'completed': 'completed', 'failed': 'failed', 'interrupted': 'stopped'}.get(final.get('status'), 'stopped')
        human.terminal(terminal, 'PANEL managed receiver ' + state['id'] + ' turn ' + final['id'])
        human.reconcile([human.evidence('result', result_path), human.evidence('log', logpath), human.evidence('receiver_state', STATE), human.evidence('source_state', source_state_path)], receiver_id=state['id'], turn_id=final['id'])
        print(json.dumps({'final':final.get('status'),'result':str(ROOT/(args.name+'-result.json')),'approval_seen':pending is not None,'resolved':resolution}),flush=True)
finally:
    if c:
        c.close()
    if control_lock:
        control_lock.__exit__(None, None, None)
    log.close()
