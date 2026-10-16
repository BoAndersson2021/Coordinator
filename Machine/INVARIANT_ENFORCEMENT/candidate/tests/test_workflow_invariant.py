"""Unmocked production barrier tests: denial must precede every new effect."""
import argparse
import ast
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import machine
import admission
import native_bridge
import native_socket
import workflow_invariant as invariant


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


if __name__ == '__main__':
    unittest.main()
