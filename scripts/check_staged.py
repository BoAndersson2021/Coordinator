"""Verify CodeExp2 index bytes under an independently adopted local policy.

Source development admission is separate from runtime workflow qualification.
The installed bootstrap pins this verifier and its reviewed policy; staged code
cannot replace either trusted input. No installation or runtime dispatch occurs.
"""
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

CODE = 'MACHINE_AUTOMATED_EXECUTION_REQUIRED'
GIT = '/usr/bin/git'
TEST_PATH = 'tests/test_commit_gate.py'

RUNNER = r'''
import json, sys, unittest
expected = set(json.loads(sys.argv[1]))
class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
    def addSuccess(self, test):
        self.successes.append(test.id())
        super().addSuccess(test)
suite = unittest.defaultTestLoader.discover('tests', pattern='test*.py')
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
passed = (result.wasSuccessful() and not result.skipped
          and not result.expectedFailures and expected <= set(result.successes))
payload = {'passed': passed, 'successes': result.successes,
           'tests_run': result.testsRun, 'skipped': len(result.skipped),
           'expected_failures': len(result.expectedFailures)}
with open(int(sys.argv[2]), 'w', closefd=False) as out:
    out.write(json.dumps(payload))
    out.flush()
sys.exit(0 if passed else 3)
'''


def bootstrap(verifier_sha, policy_sha):
    """Render the local hook only after independent review of these digests."""
    return ('''#!/bin/sh
exec /usr/bin/python3 -I -S -B - "$0" <<'PY'
import hashlib, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1]).resolve().parent
try:
    for name, digest in %r.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError('installed trusted input changed: ' + name)
    result = subprocess.run(['/usr/bin/python3', '-I', '-S', '-B',
                             str(root / 'check_staged.py'), '--staged'])
    sys.exit(result.returncode)
except (OSError, ValueError) as error:
    print('MACHINE_AUTOMATED_EXECUTION_REQUIRED: COMMIT BLOCKED: ' + str(error), file=sys.stderr)
    sys.exit(3)
PY
''' % {'check_staged.py': verifier_sha, 'reviewed-policy.json': policy_sha}).encode()


def reject(message):
    raise ValueError(message)


def clean_environment():
    return {key: value for key, value in os.environ.items()
            if not key.startswith('GIT_') and not key.startswith('PYTHON')}


def git(root, *args):
    return subprocess.check_output([GIT, '-C', str(root), *args],
                                   env=clean_environment(), stderr=subprocess.PIPE)


def protected(name):
    parts = tuple(p.casefold() for p in PurePosixPath(name).parts)
    return (parts[-1] in {'agents.md', 'agents.override.md', 'claude.md'}
            or any(p in {'.agents', '.codex', '.githooks'} for p in parts)
            or name.casefold() == 'machine/automated_workflow_requirements.md')


def ordinary(mode, blob, name):
    if mode == '000000':
        return True
    if mode != '100644' or PurePosixPath(name).suffix.lower() not in {'.md', '.txt', '.log'}:
        return False
    try:
        blob.decode('utf-8')
    except UnicodeError:
        return False
    return not blob.startswith(b'#!') and b'\0' not in blob


def mission_document(mode, blob, name):
    """Content-only admission for three agent-interpreted documentation records.

    This is not validation of mission readiness, owner acceptance or permission
    to execute anything described by a record. Operational JSON stays subject
    to the reviewed development inventory, as do all protected instructions.
    """
    if mode == '000000':
        return True
    parts = PurePosixPath(name).parts
    formats = {
        'MISSION.json': 'codeexp2-mission-coordination/1',
        'REPOSITORY-RENAME.json': 'codeexp2-repository-relocation/1',
        'REMOTE-DECOMMISSION.json': 'codeexp2-remote-decommission/1',
    }
    if (mode != '100644' or len(parts) != 3 or parts[0] != 'Missions'
            or parts[1].casefold() in {'packages', 'controlworkflowevidence'}
            or parts[2] not in formats or len(blob) > 1048576):
        return False

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('non-finite JSON number')
        if isinstance(value, dict):
            for item in value.values():
                finite(item)
        elif isinstance(value, list):
            for item in value:
                finite(item)

    try:
        body = json.loads(blob.decode('utf-8'), object_pairs_hook=pairs)
        finite(body)
        if not isinstance(body, dict):
            return False
        consumer = body.get('consumer')
        return (body.get('format') == formats[parts[2]]
                and isinstance(body.get('mission'), str) and bool(body['mission'].strip())
                and isinstance(consumer, dict)
                and consumer.get('kind') == 'agent-interpreted'
                and consumer.get('grants_execution_permission') is False)
    except (UnicodeError, ValueError, RecursionError):
        return False


def check():
    if sys.argv[1:] != ['--staged']:
        reject('use --staged; working-tree checks cannot authorize a commit')
    root = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel').decode().strip())
    gitdir = Path(git(root, 'rev-parse', '--absolute-git-dir').decode().strip())
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY',
                'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_CONFIG', 'GIT_CONFIG_COUNT',
                'GIT_CONFIG_PARAMETERS', 'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_SYSTEM',
                'GIT_NAMESPACE', 'GIT_SHALLOW_FILE', 'GIT_REPLACE_REF_BASE',
                'GIT_NO_REPLACE_OBJECTS'):
        if os.environ.get(key):
            reject('redirected Git input: ' + key)
    index = os.environ.get('GIT_INDEX_FILE')
    if index and Path(index).resolve() != (gitdir / 'index').resolve():
        reject('redirected Git input: GIT_INDEX_FILE')
    policy = json.loads(Path(__file__).with_name('reviewed-policy.json').read_text())
    if policy.get('version') != 1:
        reject('unknown reviewed development policy')
    files = policy['files']
    instructions = policy['instructions']
    mandatory = policy['mandatory_tests']
    if not files or not mandatory or len(set(mandatory)) != len(mandatory):
        reject('missing or duplicate mandatory regressions')
    if any(not name.startswith('test_commit_gate.CommitGateTests.test_') for name in mandatory):
        reject('invalid mandatory regression identity')
    if git(root, 'ls-files', '--unmerged', '-z'):
        reject('unresolved staged entries')
    entries = {}
    for record in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if not record:
            continue
        metadata, raw_name = record.split(b'\t', 1)
        mode, oid, stage = metadata.decode().split()
        name = os.fsdecode(raw_name)
        path = PurePosixPath(name)
        if stage != '0' or path.is_absolute() or '..' in path.parts:
            reject('unresolved or redirected staged entry: ' + name)
        entries[name] = (mode, oid)
    raw = git(root, 'diff', '--cached', '--raw', '-z', '--no-abbrev', '--no-renames',
              '--no-ext-diff', '--no-textconv', '--ignore-submodules=none').split(b'\0')
    if raw[-1] != b'' or (len(raw) - 1) % 2:
        reject('malformed staged changes')
    feature = False
    changed = set()
    for pos in range(0, len(raw) - 1, 2):
        old_mode, new_mode, old_oid, new_oid, status = raw[pos].decode().split()
        old_mode = old_mode.removeprefix(':')
        name = os.fsdecode(raw[pos + 1])
        changed.add(name)
        if status not in {'A', 'M', 'D'}:
            reject('unsupported staged change: ' + name)
        old = b'' if old_mode == '000000' else git(root, 'cat-file', 'blob', old_oid)
        new = b'' if new_mode == '000000' else git(root, 'cat-file', 'blob', new_oid)
        if protected(name):
            reviewed_deletion = (status == 'D' and name in instructions
                                 and instructions[name] is None)
            reviewed_content = (new_mode == '100644'
                                and hashlib.sha256(new).hexdigest() == instructions.get(name))
            if not (reviewed_deletion or reviewed_content):
                reject('instruction/invariant change requires review: ' + name)
        elif not ((ordinary(old_mode, old, name) and ordinary(new_mode, new, name))
                  or (mission_document(old_mode, old, name)
                      and mission_document(new_mode, new, name))):
            if name not in files:
                reject('unreviewed executable/data path: ' + name)
            feature = True
    if not feature:
        print(CODE + ': ordinary/reviewed documentation passed')
        return
    if TEST_PATH not in changed:
        reject('executable development requires staged invariant regressions in ' + TEST_PATH)
    for name, expected in files.items():
        if expected is None:
            if name in entries:
                reject('reviewed deletion still present: ' + name)
            continue
        if name not in entries:
            reject('reviewed development file missing from index: ' + name)
        mode, oid = entries[name]
        blob = git(root, 'cat-file', 'blob', oid)
        if mode != expected['mode'] or hashlib.sha256(blob).hexdigest() != expected['sha256']:
            reject('staged development bytes require review: ' + name)
    with tempfile.TemporaryDirectory(prefix='codeexp2-staged-') as directory:
        snapshot = Path(directory)
        for name, (mode, oid) in entries.items():
            if mode not in {'100644', '100755'}:
                reject('unsupported staged mode: ' + name)
            path = snapshot / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(git(root, 'cat-file', 'blob', oid))
            path.chmod(0o755 if mode == '100755' else 0o644)
        with tempfile.TemporaryFile() as report:
            result = subprocess.run(['/usr/bin/python3', '-I', '-S', '-B', '-c', RUNNER,
                                     json.dumps(mandatory), str(report.fileno())],
                                    cwd=snapshot, env=clean_environment(),
                                    pass_fds=(report.fileno(),), timeout=120)
            report.seek(0)
            body = json.load(report)
        if (result.returncode or not body.get('passed')
                or not set(mandatory) <= set(body.get('successes', []))):
            reject('mandatory staged regressions failed, skipped or did not complete')
    print(CODE + ': reviewed staged development checks passed; runtime authority unchanged')


if __name__ == '__main__':
    try:
        check()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(CODE + ': COMMIT BLOCKED: ' + str(error), file=sys.stderr)
        sys.exit(3)
