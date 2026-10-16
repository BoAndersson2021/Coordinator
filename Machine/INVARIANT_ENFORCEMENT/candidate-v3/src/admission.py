"""Local-operator admission for one exact scratch initialization; no generic executor."""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid
import workflow_invariant as invariant

MAX_SECONDS = 900
PROFILE = ('Machine', 'src/machine.py', 'src/admission.py', 'src/workflow_invariant.py',
           'AGENTS.md', 'docs/ADMISSION.md')


class AdmissionRejected(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise AdmissionRejected(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def identity(value):
    try:
        require(str(uuid.UUID(value)) == value, 'Expected canonical UUID')
    except (ValueError, TypeError, AttributeError):
        raise AdmissionRejected('Expected canonical UUID')
    return value


def actor():
    thread = identity(os.environ.get('CODEX_THREAD_ID'))
    require(os.environ.get('CODEX_SESSION_ID') == thread, 'Harness session/thread binding differs')
    return thread


def shape(value, fields):
    require(isinstance(value, dict) and set(value) == set(fields), 'Unsupported admission record fields')
    require(type(value.get('schema_version')) is int and value['schema_version'] == 1,
            'Unsupported admission schema')


def date(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(result.tzinfo is not None, 'Timestamp needs timezone')
        return result
    except (ValueError, TypeError, AttributeError):
        raise AdmissionRejected('Invalid admission timestamp')


def path(value, directory=False):
    p = Path(value)
    require(p.is_absolute() and str(p.resolve(strict=True)) == str(p), 'Use exact canonical path')
    require(not any(part.is_symlink() for part in (p,) + tuple(p.parents)), 'Redirected admission path')
    require(p.is_dir() if directory else p.is_file(), 'Wrong admission path type')
    require(p.stat().st_uid == os.getuid(), 'Admission path owner differs')
    return p


def load(filename):
    p = path(filename)
    require(p.stat().st_size <= 1024 * 1024, 'Admission input exceeds bound')
    return json.loads(p.read_text())


def sync_dir(p):
    fd = os.open(p, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_once(p, value):
    with p.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write((canonical(value) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())
    sync_dir(p.parent)


class Admission:
    def __init__(self, ledger, source_reader, clock=None):
        self.ledger = ledger
        self.root = ledger.root
        self.sources = source_reader
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.home = self.root / '.machine/admission'
        self.state = self.home / 'state.json'

    def profile(self):
        return {name: digest(path(self.root / name).read_bytes()) for name in PROFILE}

    def empty(self):
        return {'schema_version': 1, 'machine_root': str(self.root),
                'authority_model': 'local_operator_assertion', 'admissions': {},
                'permits': {}, 'operations': {}, 'decisions': {}}

    def read(self):
        if not self.state.exists():
            require(not self.state.is_symlink(), 'Redirected admission state')
            return self.empty()
        p = path(self.state)
        require(stat.S_IMODE(p.stat().st_mode) == 0o600, 'Admission state must be private')
        frame = load(p)
        require(set(frame) == {'body', 'sha256'} and digest(canonical(frame['body']).encode()) == frame['sha256'],
                'Admission state checksum differs')
        body = frame['body']
        shape(body, self.empty().keys())
        require(body['machine_root'] == str(self.root) and body['authority_model'] == 'local_operator_assertion',
                'Admission root/trust model differs')
        return body

    def save(self, body):
        temporary = self.home / ('.state-' + uuid.uuid4().hex)
        write_once(temporary, {'body': body, 'sha256': digest(canonical(body).encode())})
        os.replace(temporary, self.state)
        sync_dir(self.home)

    @contextmanager
    def locked(self):
        # Creating this private store is an explicit admitted-operator action, never startup.
        self.ledger.status()
        parent = path(self.root / '.machine', directory=True)
        require(stat.S_IMODE(parent.stat().st_mode) == 0o700, 'Machine state directory must be private')
        if not self.home.exists():
            try:
                self.home.mkdir(mode=0o700)
            except FileExistsError:
                pass  # Another explicit writer may have created the same store.
            sync_dir(parent)
        home = path(self.home, directory=True)
        require(stat.S_IMODE(home.stat().st_mode) == 0o700, 'Admission directory must be private')
        lock = home / 'lock'
        fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                    and stat.S_IMODE(info.st_mode) == 0o600, 'Admission lock owner/mode differs')
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield self.read()
        finally:
            os.close(fd)

    def replay(self, body, op, request):
        identity(op)
        previous = body['operations'].get(op)
        if previous is None:
            return None
        require(previous['request_digest'] == digest(canonical(request).encode()),
                'Admission operation reused with changed input')
        return dict(previous['response'], replayed=True)

    def record(self, body, op, request, response):
        body['operations'][op] = {'request_digest': digest(canonical(request).encode()), 'response': response}

    def fresh(self, admission):
        now = self.clock()
        require(date(admission['decision']['issued_at']) <= now < date(admission['decision']['expires_at']),
                'Admission expired or not yet valid')
        require(admission['profile'] == self.profile(), 'Admitted implementation/instruction profile changed')
        require(admission['context_digest'] == self.sources(self.root)['context_digest'], 'Machine context changed')

    def scratch(self, decision, expected=None):
        p = path(decision['scratch_root'], directory=True)
        require(Path('/private/tmp') in p.parents and p != Path('/private/tmp'),
                'Only an exact private/tmp scratch directory is supported')
        require(p != self.root and self.root not in p.parents and p not in self.root.parents,
                'Scratch root overlaps live Machine')
        info = p.stat()
        witness = {'device': info.st_dev, 'inode': info.st_ino}
        require(expected is None or witness == expected, 'Scratch directory identity changed')
        require(not os.path.lexists(p / '.machine'), 'Scratch state already exists; no overwrite')
        require(self.sources(p)['context_digest'] == self.sources(self.root)['context_digest'],
                'Scratch source context differs')
        return witness

    def admit(self, observation_file, decision_file, op):
        coordinator = actor()
        observation, decision = load(observation_file), load(decision_file)
        shape(observation, ('schema_version', 'thread_id', 'server_id', 'cwd', 'status', 'observed_at', 'source'))
        shape(decision, ('schema_version', 'kind', 'owner', 'owner_quote', 'machine_root',
                         'coordinator_thread_id', 'target_thread_id', 'scratch_root', 'init_owner',
                         'issued_at', 'expires_at'))
        require(decision['kind'] == 'scratch_init_admission' and decision['machine_root'] == str(self.root),
                'Unsupported admission operation/root')
        require(identity(decision['coordinator_thread_id']) == coordinator, 'Issuing coordinator differs')
        require(identity(decision['target_thread_id']) == identity(observation['thread_id']), 'Target thread differs')
        require(observation['cwd'] == str(self.root) and observation['status'] == 'idle'
                and observation['source'] == 'codex_tui.read_thread'
                and isinstance(observation['server_id'], str) and observation['server_id'],
                'Target workspace/status/provenance differs')
        age = (self.clock() - date(observation['observed_at'])).total_seconds()
        require(0 <= age <= 300, 'Session observation is stale/future')
        issued, expires = date(decision['issued_at']), date(decision['expires_at'])
        require(0 <= (self.clock() - issued).total_seconds() <= 300
                and 0 < (expires - issued).total_seconds() <= MAX_SECONDS and self.clock() < expires,
                'Admission lifetime exceeds bounded scope')
        for key in ('owner', 'owner_quote', 'init_owner'):
            require(isinstance(decision[key], str) and 0 < len(decision[key].strip()) <= 2000,
                    'Missing bounded owner/scope text')
        with self.ledger.connect() as connection:
            owner = json.loads(connection.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        require(decision['owner'] == owner, 'Owner differs from local operator ledger')
        request = {'decision': decision, 'observation': observation}
        with self.locked() as body:
            previous = self.replay(body, op, request)
            if previous is not None:
                return previous
            decision_digest = digest(canonical(decision).encode())
            require(decision_digest not in body['decisions'], 'Decision already admitted; do not rename/reissue')
            admission = {'admission_id': op, 'decision': decision, 'observation': observation,
                         'profile': self.profile(), 'context_digest': self.sources(self.root)['context_digest'],
                         'scratch_identity': self.scratch(decision), 'permit_id': None}
            body['admissions'][op] = admission
            body['decisions'][decision_digest] = op
            response = {'status': 'admitted', 'admission_id': op, 'target_thread_id': decision['target_thread_id'],
                        'coordinator_thread_id': coordinator, 'authority_model': 'local_operator_assertion',
                        'allowed_operation': 'scratch_init', 'replayed': False}
            self.record(body, op, request, response)
            self.save(body)
            return response

    def issue(self, admission_id, op):
        identity(admission_id)
        coordinator = actor()
        request = {'admission_id': admission_id, 'coordinator_thread_id': coordinator, 'kind': 'permit_issue'}
        with self.locked() as body:
            previous = self.replay(body, op, request)
            if previous is not None:
                return previous
            require(admission_id in body['admissions'], 'Unknown admission')
            admission = body['admissions'][admission_id]
            self.fresh(admission)
            decision = admission['decision']
            require(coordinator == decision['coordinator_thread_id'], 'Issuing coordinator differs')
            require(admission['permit_id'] is None, 'Admission already has its one permit')
            self.scratch(decision, admission['scratch_identity'])
            envelope = {'schema_version': 1, 'permit_id': op, 'operation': 'scratch_init',
                        **{key: decision[key] for key in ('coordinator_thread_id', 'target_thread_id',
                                                        'scratch_root', 'init_owner')}}
            filename = self.home / (op + '.request.json')
            response = {'status': 'issuance_pending', 'permit_id': op, 'request_path': str(filename),
                        'request_sha256': digest((canonical(envelope) + '\n').encode()), 'replayed': False}
            body['permits'][op] = {'admission_id': admission_id, 'state': 'issuing', 'request': envelope,
                                   'request_sha256': response['request_sha256'], 'result': None}
            admission['permit_id'] = op
            self.record(body, op, request, response)
            self.save(body)  # Reserve issuance BEFORE publishing its envelope.
            write_once(filename, envelope)
            body['permits'][op]['state'] = 'issued'
            response['status'] = 'issued'
            response['execute_argv'] = [str(self.root / 'Machine'), 'permit-execute', '--permit-id', op,
                                        '--request', str(filename)]
            self.record(body, op, request, response)
            self.save(body)
            return response

    def validate(self, body, permit_id, request_file):
        identity(permit_id)
        require(permit_id in body['permits'], 'Unknown permit')
        permit = body['permits'][permit_id]
        require(permit['state'] == 'issued', 'Permit consumed or issuance/execution unresolved; no replay')
        admission = body['admissions'][permit['admission_id']]
        require(actor() == admission['decision']['target_thread_id'], 'Receiving harness thread differs')
        self.fresh(admission)
        require(str(path(request_file)) == str(self.home / (permit_id + '.request.json')),
                'Use the recorded permit request path')
        request = load(request_file)
        require(canonical(request) == canonical(permit['request']), 'Requested operation/target/arguments differ')
        require(digest(path(request_file).read_bytes()) == permit['request_sha256'], 'Permit envelope bytes differ')
        self.scratch(admission['decision'], admission['scratch_identity'])
        return permit, admission

    def inspect(self, permit_id):
        identity(permit_id)
        body = self.read()
        require(permit_id in body['permits'], 'Unknown permit')
        permit = body['permits'][permit_id]
        admission = body['admissions'][permit['admission_id']]
        try:
            self.validate(body, permit_id, self.home / (permit_id + '.request.json'))
            invariant.require_automated_workflow('scratch.init', 'permit-execute')
            eligible, blocker = True, None
        except (AdmissionRejected, invariant.InvariantViolation) as error:
            eligible, blocker = False, str(error)
        return {'permit_id': permit_id, 'state': permit['state'], 'eligible': eligible, 'blocker': blocker,
                'authority_model': 'local_operator_assertion', 'decision': admission['decision'],
                'profile': admission['profile'], 'request': permit['request'], 'result': permit['result']}

    def execute(self, permit_id, request_file):
        invariant.require_automated_workflow('scratch.init', 'permit-execute')
        with self.locked() as body:
            permit, admission = self.validate(body, permit_id, request_file)
            permit['state'] = 'executing'
            permit['executor_thread_id'] = actor()
            permit['started_at'] = self.clock().isoformat()
            self.save(body)  # Durable consume BEFORE the one allowed domain function.
            try:
                result = type(self.ledger)(Path(admission['decision']['scratch_root'])).initialize(
                    admission['decision']['init_owner'])
            except Exception as error:
                permit['state'] = 'outcome_unknown'
                permit['result'] = {'error': str(error), 'retry_permitted': False}
                self.save(body)
                raise AdmissionRejected('Scratch init did not complete; consumed permit retains outcome_unknown') from error
            permit['state'] = 'succeeded'
            permit['result'] = result
            permit['finished_at'] = self.clock().isoformat()
            self.save(body)
            return {'status': 'succeeded', 'permit_id': permit_id, 'operation': 'scratch_init',
                    'result': result, 'replay_permitted': False, 'authority_model': 'local_operator_assertion'}
