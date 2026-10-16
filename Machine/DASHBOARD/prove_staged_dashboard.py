"""Real disposable Git commits; never edits the installed Machine repository."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time

BASE = Path(__file__).resolve().parent
CANDIDATE = BASE / 'candidate-v2'


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True,
                          timeout=180, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))


def checked(root, *args):
    result = run(root, *args)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


cases = []
started = time.monotonic()
with tempfile.TemporaryDirectory(prefix='machine-dashboard-commit-proof-', dir='/private/tmp') as name:
    root = Path(name) / 'repository'
    shutil.copytree(CANDIDATE, root)
    checked(root, 'init', '-q')
    hooks = root / '.git/machine-invariant-hooks'
    hooks.mkdir()
    for relative, target in [('.githooks/pre-commit', 'pre-commit'),
                             ('scripts/check_workflow_invariant.py', 'check_workflow_invariant.py')]:
        shutil.copy2(root / relative, hooks / target)
        (hooks / target).chmod(0o700)
    checked(root, 'config', 'core.hooksPath', str(hooks))
    checked(root, 'add', '-A')

    def commit(case, expected):
        before = run(root, 'rev-parse', 'HEAD').stdout.strip()
        result = run(root, '-c', 'user.name=Dashboard Fixture', '-c',
                     'user.email=dashboard-fixture@example.invalid', 'commit', '-m', case)
        (BASE / ('HOOK_' + case + '.log')).write_text(result.stdout + result.stderr)
        after = run(root, 'rev-parse', 'HEAD').stdout.strip()
        passed = (result.returncode == 0) if expected else (result.returncode != 0 and before == after)
        cases.append({'case': case, 'expected_commit': expected, 'exit_code': result.returncode,
                      'head_changed': before != after, 'passed': passed})
        print(json.dumps(cases[-1]), flush=True)
        if not passed:
            raise AssertionError(case + ':\n' + result.stdout + result.stderr)

    commit('valid_dashboard', True)
    baseline_test = (root / 'tests/test_workflow_invariant.py').read_text()
    baseline_js = (root / 'src/dashboard_assets/dashboard.js').read_text()

    (root / 'src/dashboard_assets/dashboard.js').write_text(baseline_js + '\n// fixture feature edit\n')
    checked(root, 'add', 'src/dashboard_assets/dashboard.js')
    commit('missing_staged_invariant_coverage', False)
    checked(root, 'restore', '--source=HEAD', '--staged', '--worktree', '.')

    (root / 'tests/test_workflow_invariant.py').write_text(baseline_test.replace(
        '    def test_dashboard_browser_failure_and_reconnection_contract(self):',
        '    @unittest.skip("fixture skip must block")\n    def test_dashboard_browser_failure_and_reconnection_contract(self):'))
    checked(root, 'add', 'tests/test_workflow_invariant.py')
    commit('skipped_browser_invariant', False)
    checked(root, 'restore', '--source=HEAD', '--staged', '--worktree', '.')

    (root / 'src/dashboard_assets/dashboard.js').write_text(
        baseline_js.replace('staleSeconds * 1000', 'Number.POSITIVE_INFINITY'))
    (root / 'tests/test_workflow_invariant.py').write_text(baseline_test + '\n# Fixture: mandatory browser coverage must catch disabled stale watchdog.\n')
    checked(root, 'add', 'src/dashboard_assets/dashboard.js', 'tests/test_workflow_invariant.py')
    commit('disabled_stale_watchdog', False)
    checked(root, 'restore', '--source=HEAD', '--staged', '--worktree', '.')

    (root / 'src/dashboard_assets/unregistered.js').write_text('console.log("unregistered executable");\n')
    (root / 'tests/test_workflow_invariant.py').write_text(baseline_test + '\n# Fixture: unknown runtime asset must not inherit access.\n')
    checked(root, 'add', '-A')
    commit('unregistered_runtime_asset', False)

result = {'status': 'PASS', 'cases': cases, 'elapsed_seconds': round(time.monotonic() - started, 3),
          'checker_sha256': hashlib.sha256((CANDIDATE / 'scripts/check_workflow_invariant.py').read_bytes()).hexdigest(),
          'scope': 'Actual commits through the candidate pinned hook in a disposable repository; no production commit or workflow qualification.'}
(BASE / 'HOOK_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
