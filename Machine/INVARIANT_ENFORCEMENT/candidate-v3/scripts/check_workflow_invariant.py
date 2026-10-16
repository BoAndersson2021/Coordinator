#!/usr/bin/env python3
"""Validate the staged Machine snapshot, never substitute unstaged source/tests."""
import os
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import json

CODE = 'MACHINE_AUTOMATED_EXECUTION_REQUIRED'

RUNNER = r'''
import json, pathlib, sys, unittest
expected = {'test_workflow_invariant.WorkflowInvariantTests.' + name
            for name in json.loads(sys.argv[1])}
report_path, pattern = pathlib.Path(sys.argv[2]), sys.argv[3]
class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
    def addSuccess(self, test):
        self.successes.append(test.id())
        super().addSuccess(test)
suite = unittest.defaultTestLoader.discover('tests', pattern=pattern)
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
missing = sorted(expected - set(result.successes))
report = {'tests_run': result.testsRun, 'successes': result.successes,
          'skipped': len(result.skipped), 'expected_failures': len(result.expectedFailures),
          'missing_successes': missing,
          'passed': result.wasSuccessful() and not missing}
report_path.write_text(json.dumps(report))
if missing:
    print('MACHINE_AUTOMATED_EXECUTION_REQUIRED: mandatory tests did not complete successfully: '
          + ', '.join(missing), file=sys.stderr)
sys.exit(0 if report['passed'] else 3)
'''


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
            if str(relative) == '.githooks/pre-commit' and mode != '100755':
                raise ValueError('Staged pre-commit hook must be executable (100755)')
            target = snapshot / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(root, 'cat-file', 'blob', object_id))
            target.chmod(0o755 if mode == '100755' else 0o644)
        for required in ('AGENTS.md', 'src/workflow_invariant.py', 'tests/test_workflow_invariant.py',
                         '.githooks/pre-commit', 'scripts/check_workflow_invariant.py'):
            if not (snapshot / required).is_file():
                raise ValueError('Mandatory invariant enforcement file missing from index: ' + required)
        mandatory_tests = {
            'test_all_known_and_unknown_adapters_fail_without_a_provider',
            'test_environment_cannot_enable_manual_fallback',
            'test_unknown_and_workflow_commands_deny_by_default',
            'test_every_cli_command_has_an_explicit_scope',
            'test_every_runtime_module_is_in_the_closed_inventory',
            'test_launcher_cannot_bypass_guarded_cli',
            'test_native_send_denies_before_ledger_or_connection',
            'test_manual_dispatch_handover_and_acceptance_deny_before_ledger',
            'test_scratch_denies_before_permit_consumption_or_initialization',
            'test_socket_public_and_private_queue_paths_deny_before_writes',
            'test_raw_wire_cannot_submit_queue_or_unknown_effects',
            'test_health_commands_fail_loudly_with_observation_separate_from_readiness',
            'test_workflow_cli_denies_before_state_creation',
            'test_governance_requires_future_features_and_hook',
            'test_hook_bootstrap_propagates_installed_verifier_failure',
            'test_checker_cannot_succeed_without_staged_repository',
            'test_missing_or_broken_runtime_modules_fail_with_structured_invariant',
        }
        test_tree = ast.parse((snapshot / 'tests/test_workflow_invariant.py').read_text())
        classes = [node for node in test_tree.body if isinstance(node, ast.ClassDef)
                   and node.name == 'WorkflowInvariantTests']
        tests = ({node.name for node in classes[0].body if isinstance(node, ast.FunctionDef)}
                 if len(classes) == 1 else set())
        if not mandatory_tests <= tests:
            raise ValueError('Mandatory invariant regressions removed: ' + ', '.join(sorted(mandatory_tests - tests)))
        print(CODE + ': validating staged source and regression tests', file=sys.stderr, flush=True)
        # Git hooks inherit repository-local GIT_* variables. Tests create
        # disposable repositories; they must never inherit the invoking index.
        child_environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for variable in git(root, 'rev-parse', '--local-env-vars').decode().splitlines():
            child_environment.pop(variable, None)
        for pattern in ('test_workflow_invariant.py', 'test*.py'):
            report_path = snapshot / '.invariant-test-result.json'
            if report_path.exists():
                report_path.unlink()
            result = subprocess.run([sys.executable, '-B', '-c', RUNNER,
                                     json.dumps(sorted(mandatory_tests)), str(report_path), pattern], cwd=snapshot,
                                    env=child_environment, timeout=120)
            if result.returncode or not report_path.is_file():
                raise ValueError('Staged invariant/coordination suite failed; commit blocked')
            report = json.loads(report_path.read_text())
            expected = {'test_workflow_invariant.WorkflowInvariantTests.' + name for name in mandatory_tests}
            if not report.get('passed') or not expected <= set(report.get('successes', [])):
                raise ValueError('Mandatory invariant tests were skipped, undiscovered or unsuccessful')
    print(CODE + ': staged checks passed; operational workflows remain blocked until qualified', file=sys.stderr)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, SyntaxError, OSError, subprocess.SubprocessError) as error:
        print(CODE + ': COMMIT BLOCKED: ' + str(error), file=sys.stderr)
        sys.exit(3)
