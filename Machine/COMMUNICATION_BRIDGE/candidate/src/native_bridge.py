"""Operate one existing native inspection route; never launch/resume an agent."""
from contextlib import contextmanager
import ast
import json
import os
from pathlib import Path
import tempfile
import uuid

from machine import (Rejected, canonical, digest, evidence_bytes, now, safe_regular,
                     bind_agent, task_action, uuid_value)
from native_socket import NativeSocket


def new_id():
    return str(uuid.uuid4())


@contextmanager
def evidence_file(value):
    # Internal records are formed from actual RPC results, never caller-supplied JSON.
    fd, filename = tempfile.mkstemp(prefix='machine-bridge-', dir=Path(tempfile.gettempdir()).resolve())
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(canonical(value))
        yield filename
    finally:
        os.unlink(filename)


def input_text(items):
    if not isinstance(items, list):
        raise Rejected('Malformed native input')
    if any(not isinstance(item, dict) or item.get('type') != 'text'
           or not isinstance(item.get('text'), str) for item in items):
        return None
    return ''.join(item.get('text', '') for item in items)


class Bridge:
    def __init__(self, ledger, client_factory=NativeSocket):
        self.ledger = ledger
        self.client_factory = client_factory

    def record(self, table, identity):
        with self.ledger.connect() as connection:
            return self.ledger.get(connection, table, identity)

    def configure(self, project, endpoint, registry, role, route_manifest, operation_id):
        target = self.record('projects', project)
        # NativeSocket validates socket ownership on connection, without starting a daemon.
        NativeSocket(endpoint)
        if role not in ('brainstorm', 'modeling'):
            raise Rejected('Initial native bridge supports existing Blender project roles only')
        root = Path(target['repo'])
        registry = safe_regular(registry)
        manifest = safe_regular(route_manifest)
        if registry != root / '.runtime/session.json' or manifest.parent.parent != root / 'Routes/releases':
            raise Rejected('Use the project-owned native registry and route release')
        profile = {'schema_version': 1, 'endpoint': endpoint, 'registry': str(registry),
                   'role': role, 'route_manifest': str(manifest),
                   'manifest_sha256': digest(evidence_bytes(manifest)),
                   'route_verifier_sha256': digest(evidence_bytes(root / 'scripts/route_contract.py'))}
        self.validate_profile(target, profile)
        request = {'command': 'bridge-configure', 'project': project, 'profile': profile}
        def apply(connection):
            current = self.ledger.get(connection, 'projects', project)
            existing = current.get('native_bridge')
            if existing is not None and existing != profile:
                raise Rejected('Native route is already bound; no implicit route replacement')
            current['native_bridge'] = profile
            self.ledger.put(connection, 'projects', current)
            return {'project': project, 'native_bridge': profile}
        return self.ledger.mutate(operation_id, request, apply)

    def validate_profile(self, project, profile):
        if type(profile.get('schema_version')) is not int or profile['schema_version'] != 1:
            raise Rejected('Unsupported native bridge profile')
        root = Path(project['repo'])
        manifest_path = safe_regular(profile['route_manifest'])
        if digest(evidence_bytes(manifest_path)) != profile['manifest_sha256']:
            raise Rejected('Native route manifest changed')
        manifest = json.loads(evidence_bytes(manifest_path))
        pointer = json.loads(evidence_bytes(root / 'Routes/ACTIVE.json'))
        if (pointer.get('release_id') != manifest.get('release_id')
                or pointer.get('manifest_sha256') != profile['manifest_sha256']):
            raise Rejected('Native route is no longer active')
        policy = manifest.get('policy', {})
        if (policy.get('execution') != 'attended_embedded_codex'
                or policy.get('authentication') != 'existing_codex_account'
                or policy.get('delivery') != 'codex_queue_to_exact_registered_thread'
                or policy.get('control') != 'existing_local_codex_control_socket'
                or policy.get('model_api_fallback') is not False):
            raise Rejected('Unsupported native execution route')
        if safe_regular(manifest_path.parent / 'MANIFEST.sha256').read_text().strip() != profile['manifest_sha256']:
            raise Rejected('Native route checksum sidecar changed')
        if digest(evidence_bytes(root / 'scripts/route_contract.py')) != profile['route_verifier_sha256']:
            raise Rejected('Native route verifier changed')
        sources = manifest.get('sources')
        if not isinstance(sources, dict) or not sources:
            raise Rejected('Missing native route sources')
        tree = ast.parse(evidence_bytes(root / 'scripts/route_contract.py'))
        constants = {node.targets[0].id: ast.literal_eval(node.value)
                     for node in tree.body if isinstance(node, ast.Assign)
                     and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                     and node.targets[0].id in ('CORE_FILES', 'POLICY')}
        if set(sources) != set(constants.get('CORE_FILES', ())) or policy != constants.get('POLICY'):
            raise Rejected('Native route source inventory or policy differs from its verifier')
        for name, sha in sources.items():
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                raise Rejected('Invalid native route source')
            if digest(evidence_bytes(root / relative)) != sha:
                raise Rejected('Native routing source changed: ' + name)
        # Reproduce the project's literal adapter recipe without importing project code.
        tree = ast.parse(evidence_bytes(root / 'scripts/modeling_operations.py'))
        try:
            function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                            and node.name == 'source_digest')
            names = next(ast.literal_eval(node.value) for node in function.body
                         if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                         and target.id == 'names' for target in node.targets))
            version = next(ast.literal_eval(node.value) for node in tree.body
                           if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                           and target.id == 'VERSION' for target in node.targets))
        except (StopIteration, ValueError, TypeError):
            raise Rejected('Unsupported native adapter digest recipe')
        import hashlib
        adapter = hashlib.sha256()
        for name in names:
            if not isinstance(name, str) or Path(name).name != name:
                raise Rejected('Invalid native adapter recipe file')
            adapter.update(name.encode())
            adapter.update(evidence_bytes(root / 'scripts' / name))
        if manifest.get('adapter_identity') != {'version': version, 'source_digest': adapter.hexdigest()}:
            raise Rejected('Native adapter source changed')
        registry = json.loads(evidence_bytes(profile['registry']))
        thread = registry.get(profile['role'])
        uuid_value(thread)
        return thread

    def profile(self, agent):
        project = self.record('projects', agent['project_id'])
        profile = project.get('native_bridge')
        if profile is None:
            raise Rejected('Configure this project native route explicitly first')
        if self.validate_profile(project, profile) != agent['thread_id']:
            raise Rejected('Project role moved to another thread; inspect replacement explicitly')
        if agent['server_id'] != profile['endpoint']:
            raise Rejected('Native endpoint differs from the agent binding')
        return profile

    def read_thread(self, client, agent):
        thread = client.request('thread/read', {'threadId': agent['thread_id'], 'includeTurns': False})['thread']
        if thread.get('id') != agent['thread_id'] or thread.get('cwd') != agent['cwd']:
            raise Rejected('Actual native thread/workspace differs from binding')
        if thread.get('status', {}).get('type') not in ('idle', 'active', 'notLoaded'):
            raise Rejected('Native thread unavailable or waiting for input/approval')
        return thread

    def refresh(self, client, agent):
        thread = self.read_thread(client, agent)
        observation = {'schema_version': 1, 'thread_id': thread['id'],
                       'cwd': thread['cwd'], 'server_id': agent['server_id'],
                       'status': thread['status']['type'], 'observed_at': now(),
                       'source': 'codex_local.read_thread'}
        with evidence_file(observation) as filename:
            return bind_agent(self.ledger, agent['id'], agent['project_id'], filename, new_id())

    def observe(self, agent_id, operation_id):
        uuid_value(operation_id)
        agent = self.record('agents', agent_id)
        profile = self.profile(agent)
        with self.client_factory(profile['endpoint']) as client:
            thread = self.read_thread(client, agent)
        observation = {'schema_version': 1, 'thread_id': thread['id'], 'cwd': thread['cwd'],
                       'server_id': agent['server_id'], 'status': thread['status']['type'],
                       'observed_at': now(), 'source': 'codex_local.read_thread'}
        with evidence_file(observation) as filename:
            return bind_agent(self.ledger, agent_id, agent['project_id'], filename, operation_id)

    def transition(self, task, action, evidence=None, **parameters):
        if evidence is None:
            return task_action(self.ledger, task['id'], task['version'], action, new_id(), **parameters)
        with evidence_file(evidence) as filename:
            return task_action(self.ledger, task['id'], task['version'], action, new_id(),
                               evidence=filename, **parameters)

    def receipt(self, task, source, detail):
        return {'schema_version': 1, 'task_id': task['id'],
                'attempt_id': task['attempts'][-1]['attempt_id'],
                'thread_id': task['thread_id'], 'server_id': task['server_id'],
                'outcome': 'delivered', 'source': source, 'detail': detail}

    def send(self, identity, expected_version, operation_id):
        uuid_value(operation_id)
        task = self.record('tasks', identity)
        # Inspect operation identity before any connection or source refresh.
        with self.ledger.connect() as connection:
            prior = connection.execute('SELECT request_digest FROM operations WHERE id=?', (operation_id,)).fetchone()
        if prior is not None:
            raise Rejected('Send operation already recorded; collect existing delivery, never resend')
        if task['state'] != 'prepared' or task['version'] != expected_version:
            raise Rejected('Send requires the current prepared task')
        agent = self.record('agents', task['agent_id'])
        profile = self.profile(agent)
        with self.client_factory(profile['endpoint']) as client:
            self.refresh(client, agent)
            history = client.request('thread/turns/list', {'threadId': task['thread_id'],
                                     'limit': 1, 'itemsView': 'notLoaded', 'sortDirection': 'desc'})
            if not isinstance(history.get('data'), list):
                raise Rejected('Missing native history baseline')
            anchor = history['data'][0]['id'] if history['data'] else None
            if anchor is not None:
                uuid_value(anchor)
            result = task_action(self.ledger, identity, expected_version, 'dispatch', operation_id,
                                 bridge_profile=profile, history_anchor=anchor)
            if result.get('replayed') or not result.get('dispatchable'):
                raise Rejected('Dispatch was already recorded; never resend')
            envelope = result['envelope']
            task = self.record('tasks', identity)
            try:
                queued = client.request('thread/queue/add', {'threadId': task['thread_id'],
                                        'clientUserMessageId': operation_id,
                                        'input': [{'type': 'text', 'text': envelope['prompt']}]})['queuedSubmission']
                uuid_value(queued['id'])
                if (queued.get('clientUserMessageId') != operation_id
                        or input_text(queued.get('input')) != envelope['prompt']):
                    raise Rejected('Queue acknowledgement does not match the submitted input')
                receipt = self.receipt(task, 'codex_local.thread/queue/add',
                                      'Queued message ' + queued['id'] + ' for thread ' + task['thread_id'] + '.')
                return self.transition(task, 'acknowledge', receipt, attempt_id=operation_id)
            except Exception:
                current = self.record('tasks', identity)
                if current['state'] == 'delivery_pending':
                    self.transition(current, 'uncertain', attempt_id=operation_id,
                                    reason='Native send or receipt persistence uncertain; collect, never resend')
                raise

    def pages(self, client, method, params):
        seen = set()
        for _ in range(20):
            page = client.request(method, params)
            data = page.get('data')
            if not isinstance(data, list):
                raise Rejected('Malformed native history page')
            yield from data
            cursor = page.get('nextCursor')
            if cursor is None:
                return
            if not isinstance(cursor, str) or not cursor or cursor in seen:
                raise Rejected('Native history cursor is invalid or repeated')
            seen.add(cursor)
            params = {**params, 'cursor': cursor}
        raise Rejected('Native history page bound reached; delivery remains unresolved')

    def collect(self, identity):
        task = self.record('tasks', identity)
        if task['state'] in ('reported', 'verified', 'rejected', 'closed'):
            return self.view(task)
        if task['state'] not in ('delivery_pending', 'recovery_required', 'delivered'):
            raise Rejected('No delivery to collect')
        attempt = task['attempts'][-1]
        envelope = attempt.get('envelope')
        profile = attempt.get('bridge_profile')
        if not envelope or not profile:
            raise Rejected('Historical manual delivery requires its existing inspection/reconciliation route')
        agent = self.record('agents', task['agent_id'])
        if profile != self.profile(agent):
            raise Rejected('Recorded delivery native route changed')
        with self.client_factory(profile['endpoint']) as client:
            thread = self.read_thread(client, agent)
            matches = []
            for turn in self.pages(client, 'thread/turns/list',
                                   {'threadId': task['thread_id'], 'limit': 5,
                                    'itemsView': 'full', 'sortDirection': 'desc'}):
                if turn.get('id') == attempt.get('history_anchor'):
                    break
                if turn.get('itemsView') != 'full':
                    raise Rejected('Native turn history is incomplete')
                items = turn.get('items', [])
                if any(item.get('type') == 'userMessage' and input_text(item.get('content')) == envelope['prompt']
                       for item in items):
                    matches.append(turn)
            if len(matches) > 1:
                raise Rejected('Multiple matching turns; inspect duplicate execution before acceptance')
            if matches:
                turn = matches[0]
                uuid_value(turn['id'])
                if task['state'] != 'delivered':
                    self.transition(task, 'reconcile', self.receipt(task, 'codex_local.read_thread',
                                    'Exact submitted input observed in native turn ' + turn['id']),
                                    attempt_id=attempt['attempt_id'], outcome='delivered')
                    task = self.record('tasks', identity)
                if turn.get('status') == 'completed':
                    finals = [item['text'] for item in turn['items'] if item.get('type') == 'agentMessage'
                              and item.get('phase') == 'final_answer' and item.get('text', '').strip()]
                    if not finals:
                        raise Rejected('Completed turn has no explicit final answer; retain for inspection')
                    report = {'schema_version': 1, 'task_id': identity, 'attempt_id': attempt['attempt_id'],
                              'thread_id': task['thread_id'], 'server_id': task['server_id'],
                              'turn_id': turn['id'], 'turn_status': 'completed',
                              'source': 'codex_local.read_thread', 'body': '\n\n'.join(finals)}
                    self.transition(task, 'report', report)
                    return self.view(self.record('tasks', identity))
                return {**self.view(task), 'execution_status': turn.get('status'),
                        'thread_status': thread['status'], 'turn_id': turn['id']}
            queued = [entry for entry in self.pages(client, 'thread/queue/list',
                      {'threadId': task['thread_id']})
                      if entry.get('clientUserMessageId') == attempt['attempt_id']]
            if len(queued) > 1 or any(input_text(entry.get('input')) != envelope['prompt'] for entry in queued):
                raise Rejected('Native queue input identity is ambiguous or changed')
            if queued and task['state'] != 'delivered':
                self.transition(task, 'reconcile', self.receipt(task, 'codex_local.read_thread',
                                'Exact submitted input remains queued as ' + queued[0]['id']),
                                attempt_id=attempt['attempt_id'], outcome='delivered')
                task = self.record('tasks', identity)
            return {**self.view(task), 'execution_status': 'queued' if queued else 'not_observed',
                    'thread_status': thread['status'],
                    'note': 'No resend. Absence from bounded history is not proof of non-delivery.'}

    def view(self, task):
        result = {key: task[key] for key in ('id', 'state', 'version', 'project_id', 'agent_id')}
        if task.get('report_digest'):
            with self.ledger.connect() as connection:
                result['report'] = json.loads(connection.execute(
                    'SELECT content FROM evidence WHERE sha256=?', (task['report_digest'],)).fetchone()[0])
        return result

    def work_view(self):
        return {'tasks': [self.view(task) for task in self.ledger.status()['tasks']],
                'network_observation': False, 'next': 'Use bridge-collect explicitly to refresh delivered work'}
