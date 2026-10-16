#!/usr/bin/env python3
"""Install only independently accepted candidate bytes; preserve prior source/state."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HOME = Path(__file__).resolve().parent
TARGET = Path('/Users/boandersson/Desktop/Machine')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    acceptance_path = HOME / 'REVIEW_ACCEPTANCE.json'
    acceptance = json.loads(acceptance_path.read_text())
    manifest_path = HOME / acceptance['manifest']
    manifest = json.loads(manifest_path.read_text())
    if acceptance['verdict'] != 'PASS' or sha(manifest_path) != acceptance['manifest_sha256']:
        raise RuntimeError('Independent acceptance does not match the candidate')
    if sha(HOME / acceptance['report_file']) != acceptance['report_sha256']:
        raise RuntimeError('Retained independent review changed')
    baseline = json.loads((HOME / 'BASELINE.json').read_text())
    preservation = json.loads((HOME / 'PRESERVATION_BASELINE.json').read_text())
    head = subprocess.check_output(['git', '-C', str(TARGET), 'rev-parse', 'HEAD'], text=True).strip()
    if head != preservation['head']:
        raise RuntimeError('Installed HEAD changed; inspect before installation')
    status = subprocess.check_output(['git', '-C', str(TARGET), 'status', '--porcelain'], text=True)
    if status != preservation['git_status']:
        raise RuntimeError('Installed working tree changed; preserve it')
    for name, expected in baseline['files'].items():
        if sha(TARGET / name) != expected:
            raise RuntimeError('Installed source changed: ' + name)
    for name, expected in preservation['private_files'].items():
        if sha(TARGET / name) != expected:
            raise RuntimeError('Private state changed: ' + name)
    candidate = Path(manifest['candidate_root'])
    contents = {}
    for name, expected in manifest['files'].items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise RuntimeError('Invalid candidate path')
        content = (candidate / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected:
            raise RuntimeError('Candidate changed: ' + name)
        contents[name] = content
    installation = HOME / 'installation'
    installation.mkdir(exist_ok=False)
    previous = installation / 'previous'
    previous.mkdir()
    for name in contents:
        path = TARGET / name
        if path.exists():
            retained = previous / name
            retained.parent.mkdir(parents=True, exist_ok=True)
            retained.write_bytes(path.read_bytes())
    # New modules precede the CLI entry that imports them. No live command runs
    # during replacement. A partial installation retains its complete old bytes.
    order = sorted(contents, key=lambda name: name == 'src/machine.py')
    for name in order:
        path = TARGET / name
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='.machine-install-', dir=path.parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(contents[name])
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    for name, expected in manifest['files'].items():
        if sha(TARGET / name) != expected:
            raise RuntimeError('Installed byte check failed: ' + name)
    for name, expected in preservation['private_files'].items():
        if sha(TARGET / name) != expected:
            raise RuntimeError('Private preservation check failed: ' + name)
    result = {'status': 'installed', 'files': manifest['files'],
              'previous_head': head, 'private_state_preserved': True,
              'independent_review': acceptance, 'live_acceptance': 'pending'}
    (installation / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'installed', 'files': len(contents),
                      'private_state_preserved': True, 'live_acceptance': 'pending'}))


if __name__ == '__main__':
    run()
