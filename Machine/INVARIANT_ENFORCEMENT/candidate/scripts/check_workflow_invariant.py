#!/usr/bin/env python3
"""Validate the staged Machine snapshot, never substitute unstaged source/tests."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

CODE = 'MACHINE_AUTOMATED_EXECUTION_REQUIRED'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def main():
    if sys.argv[1:] != ['--staged']:
        raise ValueError('Use --staged; working-tree validation cannot authorize a commit')
    root = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel').decode().strip())
    changed = {p for p in git(root, 'diff', '--cached', '--name-only', '-z').decode().split('\0') if p}
    feature_change = any(p == 'Machine' or p.startswith(('src/', 'scripts/', '.githooks/')) for p in changed)
    if feature_change and 'tests/test_workflow_invariant.py' not in changed:
        raise ValueError('New or edited executable features require staged invariant regression coverage')
    with tempfile.TemporaryDirectory(prefix='machine-staged-invariant-') as name:
        snapshot = Path(name)
        for entry in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
            if not entry:
                continue
            metadata, raw_path = entry.split(b'\t', 1)
            mode, object_id, stage = metadata.decode().split()
            relative = Path(os.fsdecode(raw_path))
            if stage != '0' or mode not in ('100644', '100755') or relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unresolved, redirected or unsupported staged file: ' + str(relative))
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(root, 'cat-file', 'blob', object_id))
            target.chmod(0o755 if mode == '100755' else 0o644)
        for required in ('AGENTS.md', 'src/workflow_invariant.py', 'tests/test_workflow_invariant.py',
                         '.githooks/pre-commit', 'scripts/check_workflow_invariant.py'):
            if not (snapshot / required).is_file():
                raise ValueError('Mandatory invariant enforcement file missing from index: ' + required)
        print(CODE + ': validating staged source and regression tests', file=sys.stderr, flush=True)
        # Git hooks inherit repository-local GIT_* variables. Tests create
        # disposable repositories; they must never inherit the invoking index.
        child_environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for variable in git(root, 'rev-parse', '--local-env-vars').decode().splitlines():
            child_environment.pop(variable, None)
        for arguments in (['-p', 'test_workflow_invariant.py'], []):
            result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover',
                                     '-s', 'tests', *arguments, '-v'], cwd=snapshot,
                                    env=child_environment, timeout=120)
            if result.returncode:
                raise ValueError('Staged invariant/coordination suite failed; commit blocked')
    print(CODE + ': staged checks passed; operational workflows remain blocked until qualified', file=sys.stderr)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(CODE + ': COMMIT BLOCKED: ' + str(error), file=sys.stderr)
        sys.exit(3)
