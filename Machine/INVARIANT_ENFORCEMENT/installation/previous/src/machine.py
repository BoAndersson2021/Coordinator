#!/usr/bin/env python3
"""Mammuth Machine inspection coordinator. Standard library, no model calls."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import uuid

# Bridge modules share the entry module's exception and function identities.
if __name__ == '__main__':
    sys.modules['machine'] = sys.modules[__name__]

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 1
MAX_EVIDENCE = 1024 * 1024
MAX_OBSERVATION_AGE = 300


class Rejected(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def identifier(value):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}', value):
        raise Rejected('Invalid identifier')
    return value


def uuid_value(value):
    try:
        if str(uuid.UUID(value)) != value:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise Rejected('Expected a canonical UUID')
    return value


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise Rejected('Expected nonempty bounded text')
    return value


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError()
    except (ValueError, AttributeError):
        raise Rejected('Expected a timestamp with timezone')
    age = (datetime.now(timezone.utc) - parsed).total_seconds()
    if age < -30 or age > MAX_OBSERVATION_AGE:
        raise Rejected('Agent observation is stale or in the future; recollect it')
    return value


def safe_regular(path):
    path = Path(path).absolute()
    for part in (path,) + tuple(path.parents):
        if part.is_symlink():
            raise Rejected('Symlink paths are not accepted: ' + str(path))
    if not path.is_file():
        raise Rejected('Missing regular file: ' + str(path))
    return path


def evidence_bytes(path):
    path = safe_regular(path)
    if path.stat().st_size > MAX_EVIDENCE:
        raise Rejected('Evidence exceeds 1 MiB bound')
    content = path.read_bytes()
    if len(content) > MAX_EVIDENCE:
        raise Rejected('Evidence changed beyond size bound')
    return content


def git(repo, *args):
    try:
        result = subprocess.run(['git', '-C', str(repo), *args], check=True,
                                text=True, capture_output=True, timeout=10,
                                env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    except (OSError, subprocess.SubprocessError):
        raise Rejected('Cannot inspect Git repository: ' + str(repo))
    return result.stdout.strip()


def project_identity(repo, machine_root):
    repo = Path(repo).resolve(strict=True)
    machine_root = Path(machine_root).resolve()
    if repo == machine_root or machine_root in repo.parents or repo in machine_root.parents:
        raise Rejected('External project must be separate from Machine and its ancestors')
    if Path(git(repo, 'rev-parse', '--show-toplevel')).resolve() != repo:
        raise Rejected('Project path must be the exact Git worktree root')
    common = Path(git(repo, 'rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = repo / common
    if (machine_root / '.git').exists():
        studio_common = Path(git(machine_root, 'rev-parse', '--git-common-dir'))
        if not studio_common.is_absolute():
            studio_common = machine_root / studio_common
        if common.resolve() == studio_common.resolve():
            raise Rejected('External project cannot share Machine Git history')
    return {'repo': str(repo), 'git_common_dir': str(common.resolve()),
            'revision': git(repo, 'rev-parse', 'HEAD')}


def sources(root):
    """Pin normative context and portable communication snapshots; no YAML parser."""
    root = Path(root)
    manifest = json.loads(safe_regular(root / 'machine.json').read_text())
    if type(manifest.get('schema_version')) is not int or manifest != {'schema_version': SCHEMA, 'kind': 'MammuthMachine', 'mode': 'inspect_only'}:
        raise Rejected('Unsupported Machine implementation manifest')
    baseline = root / 'Design/agentic-game-studio-v0.2-handoff'
    inventory = json.loads(safe_regular(baseline / 'evidence/inventory.json').read_text())
    required = ['corpus/architecture-v1.2.txt', 'corpus/agentic-structure.txt',
                'corpus/unified-operating-model.txt', 'corpus/system-position.txt',
                'agentic-studio.install.yaml']
    identities = {}
    for name in required:
        actual = digest(safe_regular(baseline / name).read_bytes())
        if inventory['files'].get(name) != actual:
            raise Rejected('Baseline digest mismatch: ' + name)
        identities[str((baseline / name).relative_to(root))] = actual
    extension = root / 'Design/studio-capability-system-v0.1'
    expected = json.loads(safe_regular(extension / 'handoff/inventory.json').read_text())['files']
    for name, expected_digest in expected.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise Rejected('Unsafe inventory path')
        actual = digest(safe_regular(extension / name).read_bytes())
        if actual != expected_digest:
            raise Rejected('Capability digest mismatch: ' + name)
        identities[str((extension / name).relative_to(root))] = actual
    communication = root / 'docs/communications'
    provenance = json.loads(safe_regular(communication / 'provenance.json').read_text())
    if provenance.get('schema_version') != SCHEMA:
        raise Rejected('Unsupported communication provenance schema')
    expected_names = {'universal-multi-agent-build-protocol.md',
                      'how-to-communicate-with-other-codex-agents.md',
                      'app-terminal-codex-launch-pattern.md'}
    if set(provenance['files']) != expected_names:
        raise Rejected('Incomplete communication source set')
    for name in sorted(expected_names):
        actual = digest(safe_regular(communication / name).read_bytes())
        if actual != provenance['files'][name]['sha256']:
            raise Rejected('Communication digest mismatch: ' + name)
        identities[str((communication / name).relative_to(root))] = actual
    for name in ('Intent.txt', 'THE-MAMMUTH-MACHINE.txt', 'Benefit-of-System-v0.2.txt'):
        identities['Design/' + name] = digest(safe_regular(root / 'Design' / name).read_bytes())
    return {'files': identities, 'context_digest': digest(canonical(identities).encode())}


SQL = '''
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE projects (id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE agents (id TEXT PRIMARY KEY, record TEXT NOT NULL);
CREATE TABLE tasks (id TEXT PRIMARY KEY, version INTEGER NOT NULL, state TEXT NOT NULL, record TEXT NOT NULL);
CREATE TABLE evidence (sha256 TEXT PRIMARY KEY, content BLOB NOT NULL);
CREATE TABLE operations (id TEXT PRIMARY KEY, request_digest TEXT NOT NULL, response TEXT NOT NULL);
CREATE TABLE events (seq INTEGER PRIMARY KEY, previous TEXT NOT NULL, digest TEXT NOT NULL, record TEXT NOT NULL);
'''


class Ledger:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.directory = self.root / '.machine'
        self.path = self.directory / 'state.sqlite3'

    def initialize(self, owner):
        text(owner)
        sources(self.root)
        if self.directory.exists() or self.directory.is_symlink():
            raise Rejected('State directory already exists; no overwrite or implicit migration')
        self.directory.mkdir(mode=0o700)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            with sqlite3.connect(self.path) as connection:
                connection.execute('PRAGMA synchronous=FULL')
                connection.execute('PRAGMA fullfsync=ON')
                connection.executescript(SQL)
                connection.execute('PRAGMA user_version=1')
                for key, value in {'schema_version': SCHEMA, 'owner': owner,
                                   'machine_root': str(self.root), 'created_at': now(),
                                   'authority_model': 'local_operator_assertion'}.items():
                    connection.execute('INSERT INTO meta VALUES (?,?)', (key, canonical(value)))
                self.event(connection, {'kind': 'initialize', 'owner': owner, 'at': now()})
            self.sync_directory()
        except Exception:
            # Preserve an incomplete initialization for inspection, never silently repair.
            raise
        return {'status': 'initialized', 'schema_version': SCHEMA,
                'owner': owner, 'authority_model': 'local_operator_assertion'}

    def sync_directory(self):
        fd = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @contextmanager
    def connect(self, write=False):
        safe_regular(self.path)
        connection = sqlite3.connect(self.path.as_uri() + ('?mode=rw' if write else '?mode=ro'),
                                     uri=True, timeout=2)
        connection.row_factory = sqlite3.Row
        try:
            if not write:
                connection.execute('PRAGMA query_only=ON')
            connection.execute('PRAGMA synchronous=FULL')
            connection.execute('PRAGMA fullfsync=ON')
            if connection.execute('PRAGMA user_version').fetchone()[0] != SCHEMA:
                raise Rejected('Unsupported state schema; no implicit migration')
            meta = {row['key']: json.loads(row['value']) for row in connection.execute('SELECT * FROM meta')}
            if meta.get('schema_version') != SCHEMA or meta.get('machine_root') != str(self.root):
                raise Rejected('State identity/schema mismatch; do not transplant state')
            if write:
                connection.execute('BEGIN IMMEDIATE')
            self.integrity(connection)
            yield connection
            if write:
                connection.commit()
                self.sync_directory()
        except Exception:
            if write:
                connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def event(connection, record):
        last = connection.execute('SELECT digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        previous = last[0] if last else '0' * 64
        serialized = canonical(record)
        identity = digest((previous + '\n' + serialized).encode())
        connection.execute('INSERT INTO events(previous,digest,record) VALUES (?,?,?)',
                           (previous, identity, serialized))

    @staticmethod
    def integrity(connection):
        if connection.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise Rejected('SQLite integrity failure')
        previous = '0' * 64
        for row in connection.execute('SELECT * FROM events ORDER BY seq'):
            if row['previous'] != previous or digest((previous + '\n' + row['record']).encode()) != row['digest']:
                raise Rejected('Event integrity failure')
            previous = row['digest']
        for row in connection.execute('SELECT * FROM evidence'):
            if digest(bytes(row['content'])) != row['sha256']:
                raise Rejected('Evidence integrity failure')
        # Table records must match the last recorded event, not just parse as JSON.
        expected = {'projects': {}, 'agents': {}, 'tasks': {}}
        for row in connection.execute('SELECT record FROM events ORDER BY seq'):
            event = json.loads(row['record'])
            if event.get('table') in expected:
                expected[event['table']][event['record']['id']] = event['record']
        for table, records in expected.items():
            actual = {row['id']: json.loads(row['record']) for row in connection.execute('SELECT * FROM ' + table)}
            if actual != records:
                raise Rejected('Record/event mismatch: ' + table)
        for row in connection.execute('SELECT * FROM tasks'):
            record = json.loads(row['record'])
            if record['version'] != row['version'] or record['state'] != row['state']:
                raise Rejected('Task state index mismatch')
        recorded_operations = {}
        for row in connection.execute('SELECT record FROM events ORDER BY seq'):
            event = json.loads(row[0])
            if event['kind'] == 'operation':
                recorded_operations[event['operation_id']] = (event['request_digest'], event['response'])
        operations = {row['id']: (row['request_digest'], json.loads(row['response']))
                      for row in connection.execute('SELECT * FROM operations')}
        if operations != recorded_operations:
            raise Rejected('Operation/event mismatch')
        for table in ('projects', 'agents', 'tasks'):
            for row in connection.execute('SELECT record FROM ' + table):
                record = json.loads(row[0])
                if record.get('schema_version') != SCHEMA:
                    raise Rejected('Unsupported record schema')
                references = [record[key] for key in ('observation_digest', 'report_digest', 'review_digest') if key in record]
                references += [attempt[key] for attempt in record.get('attempts', [])
                               for key in ('receipt_digest', 'reconciliation_digest') if key in attempt]
                references += [replacement[key] for replacement in record.get('replacements', [])
                               for key in ('observation_digest', 'removal_digest') if key in replacement]
                for reference in references:
                    if not connection.execute('SELECT 1 FROM evidence WHERE sha256=?', (reference,)).fetchone():
                        raise Rejected('Missing retained evidence')

    def mutate(self, operation_id, request, function):
        uuid_value(operation_id)
        request_digest = digest(canonical(request).encode())
        with self.connect(write=True) as connection:
            previous = connection.execute('SELECT * FROM operations WHERE id=?', (operation_id,)).fetchone()
            if previous:
                if previous['request_digest'] != request_digest:
                    raise Rejected('Operation identity reused with changed input')
                response = json.loads(previous['response'])
                response['replayed'] = True
                if 'dispatchable' in response:
                    response['dispatchable'] = False
                return response
            result = function(connection)
            result['replayed'] = False
            connection.execute('INSERT INTO operations VALUES (?,?,?)',
                               (operation_id, request_digest, canonical(result)))
            self.event(connection, {'kind': 'operation', 'operation_id': operation_id,
                                    'request_digest': request_digest, 'response': result, 'at': now()})
            return result

    def get(self, connection, table, identity):
        if table not in ('projects', 'agents', 'tasks'):
            raise Rejected('Unknown record owner')
        row = connection.execute('SELECT record FROM ' + table + ' WHERE id=?', (identity,)).fetchone()
        if not row:
            raise Rejected('Unknown ' + table + ' record: ' + identity)
        return json.loads(row['record'])

    def put(self, connection, table, record):
        if table == 'tasks':
            connection.execute('INSERT OR REPLACE INTO tasks VALUES (?,?,?,?)',
                               (record['id'], record['version'], record['state'], canonical(record)))
        elif table in ('projects', 'agents'):
            connection.execute('INSERT OR REPLACE INTO ' + table + ' VALUES (?,?)',
                               (record['id'], canonical(record)))
        else:
            raise Rejected('Unknown record owner')
        self.event(connection, {'kind': 'record', 'table': table, 'record': record, 'at': now()})

    def evidence(self, connection, filename):
        content = evidence_bytes(filename)
        sha = digest(content)
        connection.execute('INSERT OR IGNORE INTO evidence VALUES (?,?)', (sha, content))
        return sha

    def status(self):
        if not self.directory.exists() and not self.directory.is_symlink():
            return {'schema_version': SCHEMA, 'status': 'uninitialized', 'root': str(self.root),
                    'projects': [], 'agents': [], 'tasks': [], 'recovery_required': [],
                    'operational_qualification': 'unverified'}
        with self.connect() as connection:
            records = {table: [json.loads(row['record']) for row in connection.execute('SELECT record FROM ' + table + ' ORDER BY id')]
                       for table in ('projects', 'agents', 'tasks')}
            recovery = [task['id'] for task in records['tasks']
                        if task['state'] in ('delivery_pending', 'recovery_required', 'replacement_pending')]
            return {'schema_version': SCHEMA, 'status': 'inspection_coordinator',
                    'root': str(self.root), **records, 'recovery_required': recovery,
                    'authority_model': 'local_operator_assertion',
                    'operational_qualification': 'unverified'}


def register_project(ledger, identity, repo, owner, operation_id):
    identifier(identity)
    text(owner)
    binding = project_identity(repo, ledger.root)
    request = {'command': 'project-register', 'id': identity, 'owner': owner, **binding}
    def apply(connection):
        if connection.execute('SELECT 1 FROM projects WHERE id=?', (identity,)).fetchone():
            raise Rejected('Project already registered; no implicit rebind')
        record = {'schema_version': SCHEMA, 'id': identity, 'owner': owner, **binding,
                  'allowed_operations': ['inspect_repository'], 'registered_at': now()}
        ledger.put(connection, 'projects', record)
        return {'project': record}
    return ledger.mutate(operation_id, request, apply)


def bind_agent(ledger, identity, project, observation_file, operation_id):
    identifier(identity)
    observation = json.loads(evidence_bytes(observation_file))
    required = {'schema_version', 'thread_id', 'server_id', 'cwd', 'status', 'observed_at', 'source'}
    if set(observation) != required or type(observation['schema_version']) is not int or observation['schema_version'] != SCHEMA:
        raise Rejected('Unsupported/incomplete agent observation')
    uuid_value(observation['thread_id'])
    text(observation['server_id'])
    if observation['source'] not in ('codex_tui.list_threads', 'agent_identity_handshake', 'codex_local.read_thread'):
        raise Rejected('Unsupported observation source')
    if observation['status'] not in ('idle', 'active', 'notLoaded'):
        raise Rejected('Agent unavailable or awaiting input/approval')
    timestamp(observation['observed_at'])
    request = {'command': 'agent-bind', 'id': identity, 'project_id': project, 'observation': observation}
    def apply(connection):
        target = ledger.get(connection, 'projects', project)
        if str(Path(observation['cwd']).resolve(strict=True)) != target['repo']:
            raise Rejected('Agent workspace does not match the registered project root')
        old = connection.execute('SELECT record FROM agents WHERE id=?', (identity,)).fetchone()
        if old:
            old = json.loads(old[0])
            if any(old[key] != value for key, value in
                   (('project_id', project), ('thread_id', observation['thread_id']),
                    ('server_id', observation['server_id']), ('cwd', observation['cwd']))):
                raise Rejected('Agent identity cannot be silently rebound')
        receipt = ledger.evidence(connection, observation_file)
        retained = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (receipt,)).fetchone()[0])
        if retained != observation:
            raise Rejected('Agent observation changed during binding')
        record = {'schema_version': SCHEMA, 'id': identity, 'project_id': project,
                  **{key: value for key, value in observation.items() if key != 'schema_version'},
                  'observation_digest': receipt}
        ledger.put(connection, 'agents', record)
        return {'agent': record}
    return ledger.mutate(operation_id, request, apply)


def prepare_task(ledger, identity, project, agent, brief, requested_by, authorization, operation_id):
    identifier(identity)
    for value in (brief, requested_by, authorization):
        text(value)
    if '\x00' in brief:
        raise Rejected('Invalid brief')
    context = sources(ledger.root)
    request = {'command': 'task-prepare', 'id': identity, 'project_id': project, 'agent_id': agent,
               'brief': brief, 'requested_by': requested_by, 'authorization': authorization,
               'context_digest': context['context_digest']}
    def apply(connection):
        if connection.execute('SELECT 1 FROM tasks WHERE id=?', (identity,)).fetchone():
            raise Rejected('Task already exists')
        project_record = ledger.get(connection, 'projects', project)
        agent_record = ledger.get(connection, 'agents', agent)
        if agent_record['project_id'] != project:
            raise Rejected('Agent belongs to another project')
        current = project_identity(project_record['repo'], ledger.root)
        if current['git_common_dir'] != project_record['git_common_dir']:
            raise Rejected('Project repository identity changed')
        inspected_inputs = {name: digest(safe_regular(Path(current['repo']) / name).read_bytes())
                            for name in ('AGENTS.md', 'README.md')}
        record = {'schema_version': SCHEMA, 'id': identity, 'version': 1, 'state': 'prepared',
                  'project_id': project, 'agent_id': agent, 'brief': brief,
                  'requested_by': requested_by, 'authorization': authorization,
                  'authority_model': 'local_operator_assertion', 'operation': 'inspect_repository',
                  'revision': current['revision'], 'context': context,
                  'inspected_inputs': inspected_inputs,
                  'repo': current['repo'], 'thread_id': agent_record['thread_id'],
                  'server_id': agent_record['server_id'], 'created_at': now(), 'attempts': []}
        ledger.put(connection, 'tasks', record)
        return {'task': record}
    return ledger.mutate(operation_id, request, apply)


def task_action(ledger, identity, expected_version, action, operation_id, **parameters):
    request = {'command': 'task-' + action, 'id': identity,
               'expected_version': expected_version, **parameters}
    # Pin evidence bytes in the operation input, so a changed receipt cannot reuse an identity.
    if parameters.get('evidence'):
        request['evidence_digest'] = digest(evidence_bytes(parameters['evidence']))
    def apply(connection):
        task = ledger.get(connection, 'tasks', identity)
        if task['version'] != expected_version:
            raise Rejected('Stale task version; inspect state before changing it')
        state = task['state']
        result = {}
        evidence_sha = None
        if parameters.get('evidence'):
            evidence_sha = ledger.evidence(connection, parameters['evidence'])
            if evidence_sha != request['evidence_digest']:
                raise Rejected('Evidence changed during transition')
        if action == 'dispatch':
            if state != 'prepared':
                raise Rejected('Dispatch forbidden from ' + state + '; reconcile uncertain delivery first')
            agent = ledger.get(connection, 'agents', task['agent_id'])
            timestamp(agent['observed_at'])
            if agent['status'] == 'notLoaded' and agent['source'] != 'codex_local.read_thread':
                raise Rejected('Dormant app-server task cannot be resumed implicitly; verify the native queue route')
            if any(task[key] != agent[key] for key in ('thread_id', 'server_id')) or agent['cwd'] != task['repo']:
                raise Rejected('Agent target drift')
            project = ledger.get(connection, 'projects', task['project_id'])
            current = project_identity(task['repo'], ledger.root)
            if current['revision'] != task['revision'] or current['git_common_dir'] != project['git_common_dir']:
                raise Rejected('Project revision or repository drift; create a new assignment')
            if sources(ledger.root)['context_digest'] != task['context']['context_digest']:
                raise Rejected('Context drift; create a new assignment')
            for name, sha in task['inspected_inputs'].items():
                if digest(safe_regular(Path(task['repo']) / name).read_bytes()) != sha:
                    raise Rejected('Inspection input drift; create a new assignment')
            prompt = ('Machine inspection ' + task['id'] + ' / attempt ' + operation_id + '.\n'
                      'Repo: ' + task['repo'] + '\nPinned HEAD: ' + task['revision'] + '\n'
                      'Authorization: read-only repository inspection. Read applicable AGENTS.md. '
                      'Do not edit, initialize, claim, repair, run setup, start Blender, commit, or send messages. '
                      'If your cwd or HEAD differs, report mismatch and stop.\n'
                      'Inspect only AGENTS.md and README.md; do not follow links for this assignment. '
                      + task['brief'] + '\nReport cwd, HEAD, cited file paths, observations, limits, and any blocker. '
                      'This request grants no mutation or acceptance authority.')
            if len(prompt.encode()) > 1000:
                raise Rejected('Prompt exceeds transport limit of 1,000 UTF-8 bytes; shorten brief')
            task['attempts'].append({'attempt_id': operation_id, 'state': 'delivery_pending', 'at': now()})
            task['state'] = 'delivery_pending'
            result = {'dispatchable': True, 'envelope': {'schema_version': SCHEMA,
                      'task_id': identity, 'attempt_id': operation_id, 'thread_id': task['thread_id'],
                      'server_id': task['server_id'], 'prompt': prompt,
                      'transport': 'codex_queue' if agent['source'] == 'codex_local.read_thread' else 'codex_tui'}}
            task['attempts'][-1]['envelope'] = result['envelope']
            if parameters.get('bridge_profile'):
                task['attempts'][-1]['bridge_profile'] = parameters['bridge_profile']
                task['attempts'][-1]['history_anchor'] = parameters.get('history_anchor')
        elif action == 'replacement-begin':
            if state != 'delivered' or not task['attempts']:
                raise Rejected('Replacement requires an accepted, unreported queued assignment')
            agent = ledger.get(connection, 'agents', parameters['new_agent'])
            timestamp(agent['observed_at'])
            if (agent['project_id'] != task['project_id'] or agent['cwd'] != task['repo']
                    or agent['server_id'] != task['server_id'] or agent['source'] != 'codex_local.read_thread'
                    or agent['thread_id'] == task['thread_id']):
                raise Rejected('Replacement agent must be a different verified native thread for the same project/server')
            observed = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (evidence_sha,)).fetchone()[0])
            required = {'schema_version', 'task_id', 'attempt_id', 'thread_id', 'server_id',
                        'queued_submission_id', 'prompt_sha256', 'source'}
            if (set(observed) != required or type(observed['schema_version']) is not int
                    or observed['schema_version'] != SCHEMA or observed['source'] != 'codex_local.thread/queue/list'):
                raise Rejected('Unsupported queued-message observation')
            attempt = task['attempts'][-1]
            for key, value in (('task_id', identity), ('attempt_id', attempt['attempt_id']),
                               ('thread_id', task['thread_id']), ('server_id', task['server_id'])):
                if observed[key] != value:
                    raise Rejected('Queued-message observation mismatch: ' + key)
            receipt = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (attempt['receipt_digest'],)).fetchone()[0])
            marker = 'Queued message ' + observed['queued_submission_id'] + ' for thread ' + task['thread_id'] + '.'
            if receipt['source'] != 'codex.queue' or marker not in receipt['detail']:
                raise Rejected('Queue identity does not match the original acknowledgement')
            original = json.loads(connection.execute('SELECT response FROM operations WHERE id=?', (attempt['attempt_id'],)).fetchone()[0])
            if digest(original['envelope']['prompt'].encode()) != observed['prompt_sha256']:
                raise Rejected('Queued prompt does not match the original dispatch')
            replacement = {'operation_id': operation_id, 'old_agent_id': task['agent_id'],
                           'old_thread_id': task['thread_id'], 'new_agent_id': agent['id'],
                           'new_thread_id': agent['thread_id'], 'server_id': task['server_id'],
                           'queued_submission_id': observed['queued_submission_id'],
                           'attempt_id': attempt['attempt_id'], 'observation_digest': evidence_sha,
                           'state': 'removal_pending', 'at': now()}
            task.setdefault('replacements', []).append(replacement)
            task['state'] = 'replacement_pending'
            result['removal_operation_id'] = operation_id
        elif action == 'replacement-finish':
            if state != 'replacement_pending':
                raise Rejected('No journaled replacement to finish')
            replacement = task['replacements'][-1]
            if replacement['operation_id'] != parameters['replacement_operation_id']:
                raise Rejected('Replacement operation mismatch')
            removed = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (evidence_sha,)).fetchone()[0])
            required = {'schema_version', 'task_id', 'attempt_id', 'thread_id', 'server_id',
                        'queued_submission_id', 'replacement_operation_id', 'source', 'response'}
            if (set(removed) != required or type(removed['schema_version']) is not int
                    or removed['schema_version'] != SCHEMA or removed['source'] != 'codex_local.thread/queue/delete'
                    or removed['response'] != {'deleted': True} or type(removed['response'].get('deleted')) is not bool):
                raise Rejected('Exact pending queue removal is not confirmed; do not send to replacement')
            for key, value in (('task_id', identity), ('attempt_id', replacement['attempt_id']),
                               ('thread_id', replacement['old_thread_id']), ('server_id', task['server_id']),
                               ('queued_submission_id', replacement['queued_submission_id']),
                               ('replacement_operation_id', replacement['operation_id'])):
                if removed[key] != value:
                    raise Rejected('Queue removal receipt mismatch: ' + key)
            agent = ledger.get(connection, 'agents', replacement['new_agent_id'])
            timestamp(agent['observed_at'])
            if (agent['thread_id'] != replacement['new_thread_id'] or agent['cwd'] != task['repo']
                    or agent['project_id'] != task['project_id'] or agent['server_id'] != task['server_id']):
                raise Rejected('Replacement target drift')
            replacement['state'] = 'queue_removed'
            replacement['removal_digest'] = evidence_sha
            replacement['completed_at'] = now()
            task['attempts'][-1]['state'] = 'queue_removed'
            task['attempts'][-1]['reconciliation_digest'] = evidence_sha
            task['agent_id'] = agent['id']
            task['thread_id'] = agent['thread_id']
            task['state'] = 'prepared'
        elif action in ('acknowledge', 'uncertain', 'reconcile'):
            if state not in ('delivery_pending', 'recovery_required'):
                raise Rejected('No unresolved delivery to reconcile')
            attempt = task['attempts'][-1]
            if parameters['attempt_id'] != attempt['attempt_id']:
                raise Rejected('Attempt identity mismatch')
            if action == 'uncertain':
                task['state'] = 'recovery_required'
                attempt['state'] = 'uncertain'
                attempt['reason'] = text(parameters['reason'])
            else:
                evidence = evidence_sha
                receipt = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (evidence,)).fetchone()[0])
                outcome = 'delivered' if action == 'acknowledge' else parameters['outcome']
                required = {'schema_version', 'task_id', 'attempt_id', 'thread_id', 'server_id', 'outcome', 'source', 'detail'}
                if set(receipt) != required or type(receipt['schema_version']) is not int or receipt['schema_version'] != SCHEMA:
                    raise Rejected('Unsupported delivery receipt')
                for key, value in (('task_id', identity), ('attempt_id', attempt['attempt_id']),
                                   ('thread_id', task['thread_id']), ('server_id', task['server_id']),
                                   ('outcome', outcome)):
                    if receipt[key] != value:
                        raise Rejected('Delivery receipt mismatch: ' + key)
                if receipt['source'] not in ('codex_tui.send_message_to_thread', 'codex_tui.read_thread',
                                              'codex.queue', 'codex_local.read_thread', 'codex_local.thread/queue/add'):
                    raise Rejected('Receipt needs transport or thread reconciliation provenance')
                if outcome == 'not_delivered' and receipt['source'] not in ('codex_tui.read_thread', 'codex_local.read_thread'):
                    raise Rejected('A failed send alone does not prove no delivery')
                text(receipt['detail'])
                task['state'] = 'delivered' if outcome == 'delivered' else 'prepared'
                attempt['state'] = outcome
                attempt['receipt_digest'] = evidence
        elif action == 'report':
            if state != 'delivered':
                raise Rejected('Report requires confirmed delivery')
            report = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (evidence_sha,)).fetchone()[0])
            required = {'schema_version', 'task_id', 'attempt_id', 'thread_id', 'server_id',
                        'turn_id', 'turn_status', 'source', 'body'}
            if set(report) != required or type(report['schema_version']) is not int or report['schema_version'] != SCHEMA:
                raise Rejected('Unsupported report record')
            for key, value in (('task_id', identity), ('attempt_id', task['attempts'][-1]['attempt_id']),
                               ('thread_id', task['thread_id']), ('server_id', task['server_id']),
                               ('turn_status', 'completed')):
                if report[key] != value:
                    raise Rejected('Report identity/status mismatch: ' + key)
            if report['source'] not in ('codex_tui.read_thread', 'codex_local.read_thread'):
                raise Rejected('Unsupported report provenance')
            uuid_value(report['turn_id'])
            if not isinstance(report['body'], str) or not report['body'].strip() or len(report['body']) > 64000:
                raise Rejected('Missing or oversized completed report body')
            task['report_digest'] = evidence_sha
            task['state'] = 'reported'
        elif action == 'verify':
            if state != 'reported':
                raise Rejected('Verification requires a retained report')
            sha = evidence_sha
            review = json.loads(connection.execute('SELECT content FROM evidence WHERE sha256=?', (sha,)).fetchone()[0])
            required = {'schema_version', 'task_id', 'report_digest', 'revision', 'reviewer', 'checks', 'verdict'}
            if set(review) != required or type(review['schema_version']) is not int or review['schema_version'] != SCHEMA or review['task_id'] != identity:
                raise Rejected('Unsupported verification record')
            if review['report_digest'] != task['report_digest'] or review['revision'] != task['revision']:
                raise Rejected('Review does not bind the retained report and pinned revision')
            text(review['reviewer'])
            if review['reviewer'] in (task['agent_id'], task['thread_id']):
                raise Rejected('Executor cannot provide its own independent inspection review')
            if not isinstance(review['checks'], list) or not review['checks']:
                raise Rejected('Independent inspection checks are required')
            for check in review['checks']:
                if not isinstance(check, dict) or set(check) != {'file', 'sha256', 'observation'}:
                    raise Rejected('Invalid inspection check')
                relative = Path(check['file'])
                if relative.is_absolute() or '..' in relative.parts:
                    raise Rejected('Check must name a file within the project')
                file = safe_regular(Path(task['repo']) / relative)
                if digest(file.read_bytes()) != check['sha256']:
                    raise Rejected('Verification file digest changed')
                if task['inspected_inputs'].get(check['file']) != check['sha256']:
                    raise Rejected('Check is not bound to a pinned inspection input')
                text(check['observation'])
            if {check['file'] for check in review['checks']} != set(task['inspected_inputs']):
                raise Rejected('Review must cover every pinned inspection input')
            if git(task['repo'], 'rev-parse', 'HEAD') != task['revision']:
                raise Rejected('Project revision changed during inspection')
            if sources(ledger.root)['context_digest'] != task['context']['context_digest']:
                raise Rejected('Context changed during inspection')
            if review['verdict'] not in ('pass', 'fail'):
                raise Rejected('Invalid review verdict')
            task['review_digest'] = sha
            task['state'] = 'verified' if review['verdict'] == 'pass' else 'rejected'
        elif action == 'close':
            if state not in ('verified', 'rejected'):
                raise Rejected('Cannot close unverified inspection')
            task['verdict'] = state
            task['state'] = 'closed'
        else:
            raise Rejected('Unsupported task operation')
        task['version'] += 1
        task['updated_at'] = now()
        ledger.put(connection, 'tasks', task)
        return {'task_id': identity, 'state': task['state'], 'version': task['version'], **result}
    return ledger.mutate(operation_id, request, apply)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT, help='Machine root; external game repositories are separate')
    commands = p.add_subparsers(dest='command')
    for name in ('status', 'doctor'):
        command = commands.add_parser(name, help='Read-only ' + name)
        command.add_argument('--json', action='store_true')
    show = commands.add_parser('task-show', help='Read one complete assignment record')
    show.add_argument('--id', required=True)
    evidence = commands.add_parser('evidence-show', help='Read retained evidence by digest')
    evidence.add_argument('--sha256', required=True)
    init = commands.add_parser('init', help='Explicitly create local coordination state')
    init.add_argument('--owner', required=True)
    project = commands.add_parser('project-register', help='Bind an external Git worktree; inspection only')
    project.add_argument('--id', required=True)
    project.add_argument('--repo', required=True)
    project.add_argument('--owner', required=True)
    project.add_argument('--operation-id', required=True)
    agent = commands.add_parser('agent-bind', help='Record a fresh, explicitly supplied thread observation')
    agent.add_argument('--id', required=True)
    agent.add_argument('--project', required=True)
    agent.add_argument('--observation', required=True)
    agent.add_argument('--operation-id', required=True)
    prepare = commands.add_parser('task-prepare', help='Record an authorized read-only inspection assignment')
    for name in ('id', 'project', 'agent', 'brief', 'requested-by', 'authorization', 'operation-id'):
        prepare.add_argument('--' + name, required=True)
    configure = commands.add_parser('bridge-configure', help='Explicitly bind an existing native project route')
    for name in ('project', 'endpoint', 'registry', 'role', 'route-manifest', 'operation-id'):
        configure.add_argument('--' + name, required=True)
    observe = commands.add_parser('bridge-observe', help='Read and refresh an existing native agent binding')
    observe.add_argument('--agent', required=True)
    observe.add_argument('--operation-id', required=True)
    send = commands.add_parser('bridge-send', help='Deliver a prepared inspection once through its native route')
    send.add_argument('--id', required=True)
    send.add_argument('--expected-version', type=int, required=True)
    send.add_argument('--operation-id', required=True)
    collect = commands.add_parser('bridge-collect', help='Collect or reconcile a matching reply; never sends')
    collect.add_argument('--id', required=True)
    commands.add_parser('work-view', help='Read current tasks and retained replies without contacting agents')
    for action in ('dispatch', 'acknowledge', 'uncertain', 'reconcile', 'report', 'verify', 'close',
                   'replacement-begin', 'replacement-finish'):
        command = commands.add_parser('task-' + action)
        command.add_argument('--id', required=True)
        command.add_argument('--expected-version', type=int, required=True)
        command.add_argument('--operation-id', required=True)
        if action in ('acknowledge', 'uncertain', 'reconcile'):
            command.add_argument('--attempt-id', required=True)
        if action in ('acknowledge', 'reconcile', 'report', 'verify', 'replacement-begin', 'replacement-finish'):
            command.add_argument('--evidence', required=True)
        if action == 'uncertain':
            command.add_argument('--reason', required=True)
        if action == 'reconcile':
            command.add_argument('--outcome', choices=('delivered', 'not_delivered'), required=True)
        if action == 'replacement-begin':
            command.add_argument('--new-agent', required=True)
        if action == 'replacement-finish':
            command.add_argument('--replacement-operation-id', required=True)
    admit = commands.add_parser('session-admit', help='Explicit operator admission for one scratch-init test')
    for field in ('observation', 'owner-decision', 'operation-id'):
        admit.add_argument('--' + field, required=True)
    issue = commands.add_parser('permit-issue', help='Issue the admission single-use scratch permit')
    issue.add_argument('--admission-id', required=True)
    issue.add_argument('--operation-id', required=True)
    inspect = commands.add_parser('permit-inspect', help='Read permit scope/eligibility without mutation')
    inspect.add_argument('--permit-id', required=True)
    execute = commands.add_parser('permit-execute', help='Consume permit and initialize its exact scratch root')
    execute.add_argument('--permit-id', required=True)
    execute.add_argument('--request', required=True)
    return p


def main(argv=None):
    a = parser().parse_args(argv)
    ledger = Ledger(a.root)
    from admission import Admission, AdmissionRejected
    try:
        if a.command in (None, 'status'):
            result = ledger.status()
            result['tasks'] = [{key: task[key] for key in
                               ('id', 'version', 'state', 'project_id', 'agent_id', 'revision')}
                               for task in result['tasks']]
        elif a.command == 'doctor':
            result = {'status': 'source_integrity_pass', **sources(a.root),
                      'ledger': ledger.status()['status'], 'operational_qualification': 'unverified'}
        elif a.command == 'task-show':
            with ledger.connect() as connection:
                result = ledger.get(connection, 'tasks', a.id)
        elif a.command == 'evidence-show':
            with ledger.connect() as connection:
                row = connection.execute('SELECT content FROM evidence WHERE sha256=?', (a.sha256,)).fetchone()
                if not row:
                    raise Rejected('Unknown evidence digest')
                result = json.loads(row[0])
        elif a.command in ('session-admit', 'permit-issue', 'permit-inspect', 'permit-execute'):
            admission = Admission(ledger, sources)
            if a.command == 'session-admit':
                result = admission.admit(a.observation, a.owner_decision, a.operation_id)
            elif a.command == 'permit-issue':
                result = admission.issue(a.admission_id, a.operation_id)
            elif a.command == 'permit-inspect':
                result = admission.inspect(a.permit_id)
            else:
                result = admission.execute(a.permit_id, a.request)
        elif a.command == 'init':
            result = ledger.initialize(a.owner)
        elif a.command == 'project-register':
            result = register_project(ledger, a.id, a.repo, a.owner, a.operation_id)
        elif a.command == 'agent-bind':
            result = bind_agent(ledger, a.id, a.project, a.observation, a.operation_id)
        elif a.command == 'task-prepare':
            result = prepare_task(ledger, a.id, a.project, a.agent, a.brief,
                                  a.requested_by, a.authorization, a.operation_id)
        elif a.command in ('bridge-configure', 'bridge-observe', 'bridge-send', 'bridge-collect', 'work-view'):
            from native_bridge import Bridge
            bridge = Bridge(ledger)
            if a.command == 'bridge-configure':
                result = bridge.configure(a.project, a.endpoint, a.registry, a.role, a.route_manifest, a.operation_id)
            elif a.command == 'bridge-observe':
                result = bridge.observe(a.agent, a.operation_id)
            elif a.command == 'bridge-send':
                result = bridge.send(a.id, a.expected_version, a.operation_id)
            elif a.command == 'bridge-collect':
                result = bridge.collect(a.id)
            else:
                result = bridge.work_view()
        else:
            parameters = {key: getattr(a, key) for key in
                          ('attempt_id', 'evidence', 'reason', 'outcome', 'new_agent', 'replacement_operation_id')
                          if hasattr(a, key)}
            result = task_action(ledger, a.id, a.expected_version, a.command[5:], a.operation_id, **parameters)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (Rejected, AdmissionRejected, OSError, sqlite3.Error, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({'status': 'rejected', 'reason': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
