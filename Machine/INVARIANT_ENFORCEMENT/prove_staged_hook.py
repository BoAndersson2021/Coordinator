"""Exercise real commits in a disposable repository, including staged tampering."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import time
import sys

ROOT = Path(__file__).resolve().parent
CANDIDATE = sys.argv[1] if len(sys.argv) > 1 else 'candidate'
SUFFIX = {'candidate-v2': '_V2', 'candidate-v3': '_V3'}.get(CANDIDATE, '')
started = time.monotonic()
results = []


with tempfile.TemporaryDirectory(prefix='machine-hook-proof-', dir='/private/tmp') as name:
    repo = Path(name) / 'repo'
    shutil.copytree(ROOT / CANDIDATE, repo, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    def run(*args):
        return subprocess.run(args, cwd=repo, text=True, capture_output=True, timeout=100,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    def git(*args):
        result = run('git', *args)
        if result.returncode:
            raise AssertionError((args, result.stderr[-3000:]))
        return result.stdout.strip()
    git('init', '-b', 'main')
    git('config', 'user.name', 'Invariant fixture')
    git('config', 'user.email', 'invariant@example.invalid')
    if SUFFIX:
        hooks = repo / '.git/machine-invariant-hooks'
        hooks.mkdir()
        shutil.copy2(repo / '.githooks/pre-commit', hooks / 'pre-commit')
        shutil.copy2(repo / 'scripts/check_workflow_invariant.py', hooks / 'check_workflow_invariant.py')
        git('config', 'core.hooksPath', str(hooks))
    else:
        git('config', 'core.hooksPath', '.githooks')
    git('add', '.')
    positive = run('git', 'commit', '-m', 'Fixture: validated enforcement')
    (ROOT / ('HOOK_POSITIVE' + SUFFIX + '.log')).write_text(positive.stdout + positive.stderr)
    assert positive.returncode == 0, positive.stderr[-4000:]
    head = git('rev-parse', 'HEAD')
    results.append({'case': 'reviewed staged snapshot', 'exit_code': positive.returncode, 'committed': True})
    def reject(case):
        result = run('git', 'commit', '-m', 'Fixture: must be rejected')
        assert result.returncode != 0, case
        assert 'MACHINE_AUTOMATED_EXECUTION_REQUIRED' in result.stderr, result.stderr
        assert 'COMMIT BLOCKED' in result.stderr, result.stderr[-3000:]
        assert git('rev-parse', 'HEAD') == head
        results.append({'case': case, 'exit_code': result.returncode, 'committed': False,
                        'head_unchanged': True, 'stderr_tail': result.stderr[-1800:]})
        git('restore', '--staged', '--worktree', '.')
    source = repo / 'src/workflow_invariant.py'
    original = source.read_text()
    source.write_text(original + '\n# executable edit without staged invariant coverage\n')
    git('add', 'src/workflow_invariant.py')
    reject('executable edit without staged invariant regressions')
    source.write_text(original.replace('raise InvariantViolation(adapter, operation)', 'return None'))
    tests = repo / 'tests/test_workflow_invariant.py'
    tests.write_text(tests.read_text() + '\n# staged invariant coverage\n')
    git('add', 'src/workflow_invariant.py', 'tests/test_workflow_invariant.py')
    source.write_text(original)  # Unstaged repair must not conceal the broken index.
    reject('staged disabled guard masked by repaired working tree')
    extra = repo / 'src/unregistered_adapter.py'
    extra.write_text('def execute():\n    return "unguarded"\n')
    tests.write_text(tests.read_text() + '\n# new adapter coverage required\n')
    git('add', 'src/unregistered_adapter.py', 'tests/test_workflow_invariant.py')
    reject('new unregistered adapter')
    # Restore does not erase an untracked file introduced by the rejected commit.
    # It remains inside this disposable fixture, outside the staged snapshot.
    tests.write_text(tests.read_text() + '\n# missing staged checker proof\n')
    git('add', 'tests/test_workflow_invariant.py')
    git('update-index', '--force-remove', 'scripts/check_workflow_invariant.py')
    reject('missing staged checker despite working-tree checker')
    if SUFFIX:
        tests.write_text(tests.read_text() + '\n# hook executable-mode coverage required\n')
        git('add', 'tests/test_workflow_invariant.py')
        git('update-index', '--chmod=-x', '.githooks/pre-commit')
        reject('non-executable staged hook despite executable working copy')
        hook = repo / '.githooks/pre-commit'
        hook.write_text('#!/bin/sh\n# scripts/check_workflow_invariant.py\nexit 0\n')
        tests.write_text(tests.read_text() + '\n# hook integrity coverage required\n')
        git('add', '.githooks/pre-commit', 'tests/test_workflow_invariant.py')
        reject('no-op staged and working-tree hook cannot replace installed verifier')
        checker = repo / 'scripts/check_workflow_invariant.py'
        checker.write_text('raise SystemExit(0)\n')
        tests.write_text(tests.read_text() + '\n# checker integrity coverage required\n')
        git('add', 'scripts/check_workflow_invariant.py', 'tests/test_workflow_invariant.py')
        reject('no-op staged checker cannot replace installed verifier')
        extra = repo / 'scripts/unregistered_adapter.py'
        extra.write_text('def execute():\n    return "unguarded"\n')
        tests.write_text(tests.read_text() + '\n# scripts adapter coverage required\n')
        git('add', 'scripts/unregistered_adapter.py', 'tests/test_workflow_invariant.py')
        reject('new adapter outside src inventory')
        tests.write_text(tests.read_text().replace('def test_raw_wire_cannot_submit_queue_or_unknown_effects',
                                                 'def removed_wire_test'))
        git('add', 'tests/test_workflow_invariant.py')
        reject('mandatory invariant test removed')
        if SUFFIX == '_V3':
            tests.write_text(tests.read_text().replace('class WorkflowInvariantTests',
                             '@unittest.skip("must not qualify skipped guards")\nclass WorkflowInvariantTests'))
            git('add', 'tests/test_workflow_invariant.py')
            reject('mandatory invariant tests skipped')
            tests.write_text(tests.read_text().replace('    def test_raw_wire_cannot_submit_queue_or_unknown_effects(self):',
                             '    @unittest.expectedFailure\n    def test_raw_wire_cannot_submit_queue_or_unknown_effects(self):\n        self.fail("must not qualify an expected failure")'))
            git('add', 'tests/test_workflow_invariant.py')
            reject('mandatory invariant test reports expected failure')
            tests.write_text(tests.read_text() + '\ndef load_tests(loader, suite, pattern):\n    return unittest.TestSuite()\n')
            git('add', 'tests/test_workflow_invariant.py')
            reject('mandatory invariant tests omitted from discovery')
            tests.write_text('import os\nos._exit(0)\n' + tests.read_text())
            git('add', 'tests/test_workflow_invariant.py')
            reject('early successful exit cannot replace actual test completion')

report = {'schema_version': 1, 'status': 'PASS', 'cases': results,
          'elapsed_seconds': round(time.monotonic() - started, 3),
          'scope': 'Disposable Git repository only; no production commit, source change or workflow dispatch.'}
(ROOT / ('HOOK_VERIFICATION' + SUFFIX + '.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'cases': len(results), 'elapsed_seconds': report['elapsed_seconds']}))
