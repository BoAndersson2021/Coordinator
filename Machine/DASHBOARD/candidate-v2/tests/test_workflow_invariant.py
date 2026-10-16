"""Unmocked production barrier tests: denial must precede every new effect."""
import argparse
import ast
import contextlib
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import machine
import admission
import native_bridge
import native_socket
import workflow_invariant as invariant
import dashboard


class WorkflowInvariantTests(unittest.TestCase):
    def setUp(self):
        self.assertNotIsInstance(invariant.require_automated_workflow, Mock,
                                 "A fixture leaked a mock over the production guard")

    def assert_blocked(self, call):
        with self.assertRaises(invariant.InvariantViolation) as captured:
            call()
        self.assertEqual(captured.exception.record['code'], invariant.INVARIANT)
        self.assertFalse(captured.exception.record['workflow_ready'])
        self.assertFalse(captured.exception.record['manual_fallback_permitted'])

    def test_all_known_and_unknown_adapters_fail_without_a_provider(self):
        for adapter in (*invariant.ADAPTERS, 'future.adapter', '', None):
            with self.subTest(adapter=adapter):
                self.assert_blocked(lambda: invariant.require_automated_workflow(adapter, 'execute'))

    def test_environment_cannot_enable_manual_fallback(self):
        with patch.dict(os.environ, {'MACHINE_AUTOMATION_READY': '1',
                                    'MACHINE_ALLOW_MANUAL': '1', 'MACHINE_SKIP_INVARIANT': '1'}):
            self.assert_blocked(lambda: invariant.guard_command('bridge-send'))

    def test_unknown_and_workflow_commands_deny_by_default(self):
        for command in (*invariant.WORKFLOW_COMMANDS, 'future-launch', 'adapter-execute'):
            with self.subTest(command=command):
                self.assert_blocked(lambda: invariant.guard_command(command))

    def test_every_cli_command_has_an_explicit_scope(self):
        actions = [a for a in machine.parser()._actions if isinstance(a, argparse._SubParsersAction)]
        self.assertEqual(len(actions), 1)
        declared = (invariant.ADMIN_COMMANDS | invariant.EVIDENCE_COMMANDS |
                    invariant.HEALTH_COMMANDS | invariant.WORKFLOW_COMMANDS)
        self.assertEqual(set(actions[0].choices), declared,
                         'New/removed CLI commands require invariant classification and tests')
        for command in declared:
            invariant.command_kind(command)

    def test_every_runtime_module_is_in_the_closed_inventory(self):
        actual = {str(p.relative_to(ROOT / 'src')) for p in (ROOT / 'src').rglob('*.py')}
        self.assertEqual(actual, set(invariant.SOURCE_MODULES),
                         'New adapters/modules require invariant integration and acceptance coverage')
        self.assertEqual(invariant.runtime_files(ROOT), set(invariant.RUNTIME_FILES),
                         'All executable files, scripts and adapters require invariant integration')

    def test_launcher_cannot_bypass_guarded_cli(self):
        self.assertEqual((ROOT / 'Machine').read_text(), '''#!/bin/sh
set -eu
MACHINE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHONDONTWRITEBYTECODE=1 exec python3 "$MACHINE_ROOT/src/machine.py" "$@"
''')

    def test_native_send_denies_before_ledger_or_connection(self):
        ledger = Mock()
        client = Mock()
        self.assert_blocked(lambda: native_bridge.Bridge(ledger, client).send('task', 1, 'id'))
        self.assertEqual(ledger.mock_calls, [])
        client.assert_not_called()

    def test_manual_dispatch_handover_and_acceptance_deny_before_ledger(self):
        for action in ('dispatch', 'replacement-begin', 'replacement-finish', 'verify', 'close', 'new-effect'):
            ledger = Mock()
            with self.subTest(action=action):
                self.assert_blocked(lambda: machine.task_action(ledger, 'task', 1, action, 'id'))
                self.assertEqual(ledger.mock_calls, [])

    def test_scratch_denies_before_permit_consumption_or_initialization(self):
        ledger = Mock(root=ROOT)
        service = admission.Admission(ledger, Mock())
        with patch.object(service, 'locked') as lock:
            self.assert_blocked(lambda: service.execute('permit', 'request'))
        lock.assert_not_called()
        self.assertEqual(ledger.mock_calls, [])

    def test_socket_public_and_private_queue_paths_deny_before_writes(self):
        native = native_socket.NativeSocket('unix:/private/tmp/not-opened.sock')
        native.socket = Mock()
        with patch.object(native, '_send') as send:
            for call in (native.request, native._request):
                self.assert_blocked(lambda: call('thread/queue/add', {'threadId': 'saved-thread'}))
            with self.assertRaises(machine.Rejected):
                native._request('turn/start', {})
        send.assert_not_called()
        self.assertEqual(native.sequence, 0)

    def test_raw_wire_cannot_submit_queue_or_unknown_effects(self):
        native = native_socket.NativeSocket('unix:/private/tmp/not-opened.sock')
        native.socket = Mock()
        for method in ('thread/queue/add', 'turn/start', 'thread/resume', 'command/exec', None):
            with self.subTest(method=method):
                self.assert_blocked(lambda: native._send(json.dumps({'method': method}).encode()))
        self.assert_blocked(lambda: native._send(b'payload', opcode=2))
        native.socket.sendall.assert_not_called()

    def test_health_commands_fail_loudly_with_observation_separate_from_readiness(self):
        for args in ([], ['status', '--json'], ['doctor', '--json'], ['invariant-check'], ['work-view']):
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'src/machine.py'), *args],
                                    capture_output=True, text=True, timeout=10)
            with self.subTest(args=args):
                self.assertEqual(result.returncode, invariant.EXIT_CODE, result.stderr)
                body = json.loads(result.stdout)
                self.assertEqual(body['status'], 'workflow_invariant_failed')
                self.assertFalse(body['workflow_invariant']['workflow_ready'])
                self.assertEqual(json.loads(result.stderr)['code'], invariant.INVARIANT)

    def test_workflow_cli_denies_before_state_creation(self):
        commands = (['bridge-send', '--id', 'task', '--expected-version', '1', '--operation-id', 'id'],
                    ['task-dispatch', '--id', 'task', '--expected-version', '1', '--operation-id', 'id'],
                    ['permit-execute', '--permit-id', 'permit', '--request', 'missing'])
        for args in commands:
            with self.subTest(args=args):
                with patch.object(machine.Ledger, 'connect', side_effect=AssertionError('ledger touched')):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        self.assertEqual(machine.main(args), invariant.EXIT_CODE)
                    self.assertEqual(json.loads(stderr.getvalue())['code'], invariant.INVARIANT)

    def test_governance_requires_future_features_and_hook(self):
        instructions = (ROOT / 'AGENTS.md').read_text()
        for required in (invariant.INVARIANT, 'new or edited', 'adapter', 'pre-commit',
                         'scripts/check_workflow_invariant.py'):
            self.assertIn(required, instructions)
        self.assertIn('scripts/check_workflow_invariant.py', (ROOT / '.githooks/pre-commit').read_text())
        self.assertTrue((ROOT / '.githooks/pre-commit').stat().st_mode & 0o111,
                        'A non-executable hook must not pass staged validation')

    def test_missing_or_broken_runtime_modules_fail_with_structured_invariant(self):
        for name, broken, command in (('workflow_invariant.py', False, 'invariant-check'),
                                      ('workflow_invariant.py', True, 'invariant-check'),
                                      ('admission.py', False, 'invariant-check'),
                                      ('admission.py', True, 'invariant-check'),
                                      ('native_bridge.py', False, 'work-view'),
                                      ('native_socket.py', True, 'work-view')):
            with self.subTest(name=name, broken=broken):
                with tempfile.TemporaryDirectory() as folder:
                    source = Path(folder) / 'src'
                    shutil.copytree(ROOT / 'src', source, ignore=shutil.ignore_patterns('__pycache__'))
                    if broken:
                        (source / name).write_text('invalid python syntax !\n')
                    else:
                        (source / name).unlink()
                    result = subprocess.run([sys.executable, '-B', str(source / 'machine.py'), command],
                                            capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 3, result.stderr)
                    self.assertEqual(json.loads(result.stderr)['code'], invariant.INVARIANT)
                    self.assertEqual(result.stdout, '')

    def test_hook_bootstrap_propagates_installed_verifier_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
            hooks = root / '.git/machine-invariant-hooks'
            hooks.mkdir()
            (hooks / 'check_workflow_invariant.py').write_text(
                'import sys\nprint("MACHINE_AUTOMATED_EXECUTION_REQUIRED: COMMIT BLOCKED", file=sys.stderr)\nsys.exit(3)\n')
            result = subprocess.run(['sh', str(ROOT / '.githooks/pre-commit')], cwd=root,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn('COMMIT BLOCKED', result.stderr)

    def test_checker_cannot_succeed_without_staged_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/check_workflow_invariant.py'),
                                     '--staged'], cwd=folder, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn('COMMIT BLOCKED', result.stderr)

    def test_dashboard_is_read_only_and_never_enables_execution(self):
        from http.client import HTTPConnection
        import threading
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(machine.Ledger, 'mutate', side_effect=AssertionError('mutation')), \
                 patch.object(native_bridge.Bridge, 'send', side_effect=AssertionError('dispatch')):
                server = dashboard.DashboardServer(root, 0, 'test-token')
                worker = threading.Thread(target=server.serve_forever, daemon=True)
                worker.start()
                try:
                    connection = HTTPConnection('127.0.0.1', server.server_port, timeout=3)
                    try:
                        connection.request('GET', '/api/snapshot', headers={'X-Machine-Token': 'test-token'})
                        response = connection.getresponse()
                        body = json.loads(response.read())
                        self.assertEqual(response.status, 200)
                    finally:
                        connection.close()
                    self.assertFalse(body['workflow_invariant']['workflow_ready'])
                    self.assertFalse(body['network_observation'])
                    self.assertEqual(list(root.iterdir()), [])
                    self.assert_blocked(lambda: invariant.require_automated_workflow('dashboard', 'dispatch'))
                finally:
                    server.shutdown()
                    server.server_close()

    def test_dashboard_supervision_failure_has_no_manual_fallback(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(Path, 'home', return_value=Path(folder)), \
             patch.object(sys, 'platform', 'darwin'), \
             patch.object(dashboard, 'launchctl', side_effect=machine.Rejected('supervisor unavailable')), \
             patch.object(dashboard.subprocess, 'Popen', side_effect=AssertionError('manual fallback')):
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(machine.main(['dashboard']), invariant.EXIT_CODE)
            body = json.loads(stderr.getvalue())
            self.assertEqual(body['status'], 'dashboard_unavailable')
            self.assertIn('supervisor unavailable', body['reason'])
            self.assertFalse(body['workflow_invariant']['workflow_ready'])

    def test_dashboard_browser_failure_and_reconnection_contract(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required to verify the actual dashboard JavaScript; no skipped coverage')
        result = subprocess.run([node, str(ROOT / 'tests/dashboard_browser_contract.cjs')],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)


if __name__ == '__main__':
    unittest.main()
