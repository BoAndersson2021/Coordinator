"""Actual disposable commits through the installed trusted checker, never bypassed."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import time

BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'candidate-v2'
INSTALLED = Path('/Users/boandersson/Desktop/Machine')
cases = []
started = time.monotonic()


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True,
                          timeout=180, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))


def checked(root, *args):
    result = run(root, *args)
    assert not result.returncode, result.stdout + result.stderr
    return result.stdout.strip()


with tempfile.TemporaryDirectory(prefix='machine-work-view-gate-', dir='/private/tmp') as temporary:
    root = Path(temporary) / 'repository'
    shutil.copytree(SOURCE, root)
    checked(root, 'init', '-q')
    hooks = root / '.git/machine-invariant-hooks'
    shutil.copytree(INSTALLED / '.git/machine-invariant-hooks', hooks)
    checked(root, 'config', 'core.hooksPath', str(hooks))
    checked(root, 'add', '-A')

    def commit(name, expected):
        before = run(root, 'rev-parse', 'HEAD').stdout.strip()
        result = run(root, '-c', 'user.name=Work View Fixture', '-c',
                     'user.email=work-view-fixture@example.invalid', 'commit', '-m', name)
        after = run(root, 'rev-parse', 'HEAD').stdout.strip()
        passed = result.returncode == 0 if expected else result.returncode != 0 and before == after
        (BASE / ('HOOK_' + name + '.log')).write_text(result.stdout + result.stderr)
        cases.append({'case': name, 'expected_commit': expected, 'exit_code': result.returncode,
                      'head_changed': before != after, 'passed': passed})
        print(json.dumps(cases[-1]), flush=True)
        assert passed, result.stdout + result.stderr

    commit('valid_shared_work_view', True)
    original_bridge = (root / 'src/native_bridge.py').read_text()
    original_core = (root / 'src/machine.py').read_text()
    original_test = (root / 'tests/test_workflow_invariant.py').read_text()

    (root / 'src/native_bridge.py').write_text(original_bridge + '\n# Fixture executable edit\n')
    checked(root, 'add', 'src/native_bridge.py')
    commit('missing_staged_invariant_coverage', False)
    checked(root, 'restore', '--source=HEAD', '--staged', '--worktree', '.')

    prefix, work_method = original_bridge.split('    def work_view(self):\n', 1)
    bridge = prefix + '    def work_view(self):\n' + work_method.replace(
        "        return result\n", "        result['tasks'][0]['execution_status'] = 'running'\n        return result\n", 1)
    assert bridge != original_bridge
    (root / 'src/native_bridge.py').write_text(bridge)
    (root / 'tests/test_workflow_invariant.py').write_text(original_test + '\n# Fixture: CLI cannot invent running execution.\n')
    checked(root, 'add', 'src/native_bridge.py', 'tests/test_workflow_invariant.py')
    commit('cli_dashboard_disagreement', False)
    checked(root, 'restore', '--source=HEAD', '--staged', '--worktree', '.')

    core = original_core.replace('Workflow execution is blocked; live executor readiness has not been established.',
                                 'Use bridge-collect explicitly to refresh delivered work')
    assert core != original_core
    (root / 'src/machine.py').write_text(core)
    (root / 'tests/test_workflow_invariant.py').write_text(original_test + '\n# Fixture: no manual workflow next step.\n')
    checked(root, 'add', 'src/machine.py', 'tests/test_workflow_invariant.py')
    commit('manual_next_step_regression', False)

(BASE / 'HOOK_VERIFICATION.json').write_text(json.dumps({
    'status': 'PASS', 'cases': cases, 'elapsed_seconds': round(time.monotonic() - started, 3),
    'scope': 'Real disposable commits using a copy of the unchanged installed trusted checker; no production commit.'}, indent=2) + '\n')
