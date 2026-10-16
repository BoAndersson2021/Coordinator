import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import machine as m
import native_bridge as b
import test_machine as fixtures
from test_machine import operation


class FakeClient:
    def __init__(self, fixture):
        self.fixture = fixture
        self.calls = []
        self.turns = []
        self.queue = []
        self.status = 'notLoaded'
        self.cwd = str(fixture.project)
        self.thread = fixture.thread
        self.fail_after_queue = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def request(self, method, params):
        self.calls.append((method, copy.deepcopy(params)))
        if method == 'thread/read':
            return {'thread': {'id': self.thread, 'cwd': self.cwd, 'status': {'type': self.status}}}
        if method == 'thread/queue/add':
            queued = {'id': operation(), 'clientUserMessageId': params['clientUserMessageId'],
                      'input': params['input']}
            self.queue.append(queued)
            if self.fail_after_queue:
                raise OSError('lost acknowledgement')
            return {'queuedSubmission': queued}
        if method == 'thread/queue/list':
            return {'data': self.queue, 'nextCursor': None}
        if method == 'thread/turns/list':
            return {'data': self.turns, 'nextCursor': None}
        raise AssertionError(method)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.CoordinatorTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        f = self.fixture
        self.endpoint = 'unix:/private/tmp/machine-native-fixture.sock'
        original_observe = f.observe
        f.observe = lambda **overrides: original_observe(server_id=self.endpoint,
                    source='codex_local.read_thread', **overrides)
        f.prepare()
        # Prepare again with the freshly bound endpoint rather than editing a task.
        m.prepare_task(f.ledger, 'native', 'external', 'inspector', 'Summarize entry points.',
                       'fixture-owner', 'Authorized native inspection fixture', operation())
        self.client = FakeClient(f)
        self.bridge = b.Bridge(f.ledger, lambda endpoint: self.client)
        scripts = f.project / 'scripts'
        scripts.mkdir()
        (scripts / 'route_contract.py').write_text('# fixture routing implementation\n')
        (f.project / '.runtime').mkdir()
        self.registry = f.project / '.runtime/session.json'
        self.registry.write_text(json.dumps({'brainstorm': f.thread}))
        release = f.project / 'Routes/releases/fixture'
        release.mkdir(parents=True)
        self.manifest = release / 'MANIFEST.json'
        manifest = {'schema': 1, 'release_id': 'fixture', 'policy': {
                    'execution': 'attended_embedded_codex', 'authentication': 'existing_codex_account',
                    'delivery': 'codex_queue_to_exact_registered_thread',
                    'control': 'existing_local_codex_control_socket', 'model_api_fallback': False},
                    'sources': {'scripts/route_contract.py': m.digest((scripts / 'route_contract.py').read_bytes())}}
        (scripts / 'route_contract.py').write_text("CORE_FILES = ('scripts/route_contract.py',)\nPOLICY = "
                                                 + repr(manifest['policy']) + '\n')
        (scripts / 'modeling_operations.py').write_text(
            "VERSION = 1\ndef source_digest():\n    names = ['modeling_operations.py']\n")
        adapter_bytes = b'modeling_operations.py' + (scripts / 'modeling_operations.py').read_bytes()
        manifest['adapter_identity'] = {'version': 1, 'source_digest': m.digest(adapter_bytes)}
        manifest['sources']['scripts/route_contract.py'] = m.digest((scripts / 'route_contract.py').read_bytes())
        self.manifest.write_text(json.dumps(manifest))
        sha = m.digest(self.manifest.read_bytes())
        (release / 'MANIFEST.sha256').write_text(sha + '\n')
        (f.project / 'Routes/ACTIVE.json').write_text(json.dumps({'release_id': 'fixture', 'manifest_sha256': sha}))
        self.bridge.configure('external', self.endpoint, str(self.registry), 'brainstorm',
                              str(self.manifest), operation())

    def task(self):
        return self.bridge.record('tasks', 'native')

    def send(self, op=None):
        return self.bridge.send('native', 1, op or operation())

    def completed_turn(self, status='completed', phase='final_answer', prompt=None):
        prompt = prompt or self.task()['attempts'][-1]['envelope']['prompt']
        return {'id': operation(), 'status': status, 'itemsView': 'full', 'items': [
                {'type': 'userMessage', 'content': [{'type': 'text', 'text': prompt}]},
                {'type': 'agentMessage', 'phase': 'commentary', 'text': 'Work in progress'},
                {'type': 'agentMessage', 'phase': phase, 'text': 'Actual final inspection report.'}]}

    def test_round_trip_retains_actual_final_and_requires_review(self):
        self.send()
        self.client.turns = [self.completed_turn()]
        result = self.bridge.collect('native')
        self.assertEqual(result['state'], 'reported')
        self.assertEqual(result['report']['body'], 'Actual final inspection report.')
        with self.assertRaises(m.Rejected):
            m.task_action(self.fixture.ledger, 'native', result['version'], 'close', operation())
        before = len(self.client.calls)
        self.assertEqual(self.bridge.collect('native'), result)
        self.assertEqual(len(self.client.calls), before)

    def test_repeated_send_never_sends_twice(self):
        op = operation()
        self.send(op)
        with self.assertRaises(m.Rejected):
            self.send(op)
        with self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(len(self.client.queue), 1)

    def test_lost_ack_reconciles_queue_without_resend(self):
        self.client.fail_after_queue = True
        with self.assertRaises(OSError):
            self.send()
        self.assertEqual(self.task()['state'], 'recovery_required')
        result = b.Bridge(self.fixture.ledger, lambda _: self.client).collect('native')
        self.assertEqual(result['execution_status'], 'queued')
        self.assertEqual(result['state'], 'delivered')
        self.assertEqual(len(self.client.queue), 1)

    def test_lost_ack_reconciles_completed_execution_after_restart(self):
        self.client.fail_after_queue = True
        with self.assertRaises(OSError):
            self.send()
        self.client.turns = [self.completed_turn()]
        self.client.queue = []
        fresh = b.Bridge(m.Ledger(self.fixture.root), lambda _: self.client)
        self.assertEqual(fresh.collect('native')['state'], 'reported')
        self.assertEqual(sum(method == 'thread/queue/add' for method, _ in self.client.calls), 1)

    def test_cut_after_journal_before_send_leaves_pending_and_collects_without_send(self):
        original = b.task_action
        def cut(*args, **kwargs):
            original(*args, **kwargs)
            raise KeyboardInterrupt('coordinator stopped')
        with patch.object(b, 'task_action', side_effect=cut), self.assertRaises(KeyboardInterrupt):
            self.send()
        self.assertEqual(self.task()['state'], 'delivery_pending')
        self.assertEqual(self.bridge.collect('native')['execution_status'], 'not_observed')
        self.assertEqual(self.task()['state'], 'delivery_pending')
        self.assertEqual(self.client.queue, [])

    def test_wrong_thread_or_workspace_rejects_before_delivery(self):
        for key, value in [('thread', operation()), ('cwd', str(self.fixture.root))]:
            with self.subTest(key=key):
                previous = getattr(self.client, key)
                setattr(self.client, key, value)
                with self.assertRaises(m.Rejected):
                    self.send()
                setattr(self.client, key, previous)
        self.assertEqual(self.task()['state'], 'prepared')
        self.assertEqual(self.client.queue, [])

    def test_role_replacement_or_route_source_change_rejects(self):
        self.registry.write_text(json.dumps({'brainstorm': operation()}))
        with self.assertRaises(m.Rejected):
            self.send()
        self.registry.write_text(json.dumps({'brainstorm': self.fixture.thread}))
        (self.fixture.project / 'scripts/route_contract.py').write_text('# changed\n')
        with self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(self.client.calls, [])

    def test_unrelated_or_quoted_prompt_cannot_become_report(self):
        self.send()
        prompt = self.task()['attempts'][-1]['envelope']['prompt']
        self.client.queue = []
        for unrelated in ['Other assignment', 'Please review this quoted input:\n' + prompt]:
            self.client.turns = [self.completed_turn(prompt=unrelated)]
            self.assertEqual(self.bridge.collect('native')['state'], 'delivered')

    def test_failed_interrupted_and_active_turns_are_not_completed_reports(self):
        self.send()
        for status in ('failed', 'interrupted', 'inProgress'):
            self.client.turns = [self.completed_turn(status=status)]
            result = self.bridge.collect('native')
            self.assertEqual(result['state'], 'delivered')
            self.assertEqual(result['execution_status'], status)
            self.assertNotIn('report', result)

    def test_duplicate_turns_and_missing_final_reject(self):
        self.send()
        self.client.turns = [self.completed_turn(), self.completed_turn()]
        with self.assertRaises(m.Rejected):
            self.bridge.collect('native')
        for phase in ('commentary', None):
            self.client.turns = [self.completed_turn(phase=phase)]
            with self.assertRaises(m.Rejected):
                self.bridge.collect('native')
        self.assertEqual(self.task()['state'], 'delivered')

    def test_history_pagination_and_cursor_loop(self):
        self.send()
        turn = self.completed_turn()
        original = self.client.request
        def paged(method, params):
            if method == 'thread/turns/list':
                return {'data': [turn] if params.get('cursor') else [],
                        'nextCursor': None if params.get('cursor') else 'next'}
            return original(method, params)
        self.client.request = paged
        self.assertEqual(self.bridge.collect('native')['state'], 'reported')

    def test_cursor_loop_is_not_inferred_as_absence(self):
        self.send()
        original = self.client.request
        self.client.request = lambda method, params: (
            {'data': [], 'nextCursor': 'loop'} if method == 'thread/turns/list' else original(method, params))
        with self.assertRaises(m.Rejected):
            self.bridge.collect('native')
        self.assertEqual(self.task()['state'], 'delivered')

    def test_work_view_is_local_and_does_not_collect_or_send(self):
        self.send()
        before = len(self.client.calls)
        result = self.bridge.work_view()
        self.assertFalse(result['network_observation'])
        self.assertEqual(len(self.client.calls), before)

    def test_changed_queue_acknowledgement_preserves_uncertainty(self):
        original = self.client.request
        def changed(method, params):
            value = original(method, params)
            if method == 'thread/queue/add':
                value['queuedSubmission']['input'] = [{'type': 'text', 'text': 'changed'}]
            return value
        self.client.request = changed
        with self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(self.task()['state'], 'recovery_required')
        with self.assertRaises(m.Rejected):
            self.bridge.collect('native')

    def test_adapter_source_drift_rejects_before_contact(self):
        with (self.fixture.project / 'scripts/modeling_operations.py').open('a') as stream:
            stream.write('# changed implementation\n')
        with self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(self.client.calls, [])

    def test_history_anchor_avoids_replaying_entire_old_conversation(self):
        old = {'id': operation(), 'status': 'completed', 'itemsView': 'notLoaded', 'items': []}
        self.client.turns = [old]
        self.send()
        self.client.turns = [self.completed_turn(), old, {'id': operation(), 'itemsView': 'notLoaded'}]
        self.assertEqual(self.bridge.collect('native')['state'], 'reported')

    def test_concurrent_senders_queue_only_once(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier = Barrier(2)
        original = self.client.request
        def simultaneous(method, params):
            if method == 'thread/read':
                barrier.wait(timeout=5)
            return original(method, params)
        self.client.request = simultaneous
        def send_one():
            try:
                self.send()
                return 'sent'
            except m.Rejected:
                return 'rejected'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: send_one(), range(2)))
        self.assertCountEqual(results, ['sent', 'rejected'])
        self.assertEqual(len(self.client.queue), 1)

    def test_cli_bridge_error_is_structured_json(self):
        import os
        import subprocess
        result = subprocess.run([sys.executable, str(Path(b.__file__).parent / 'machine.py'),
                    '--root', str(self.fixture.root), 'bridge-configure', '--project', 'external',
                    '--endpoint', 'ws://remote:4500', '--registry', str(self.registry),
                    '--role', 'brainstorm', '--route-manifest', str(self.manifest),
                    '--operation-id', operation()], capture_output=True, text=True,
                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stderr)['status'], 'rejected')
        self.assertNotIn('Traceback', result.stderr)

    def test_source_drift_during_native_baseline_read_prevents_submission(self):
        original = self.client.request
        def changed(method, params):
            result = original(method, params)
            if method == 'thread/turns/list' and params.get('itemsView') == 'notLoaded':
                with (self.fixture.project / 'scripts/modeling_operations.py').open('a') as stream:
                    stream.write('# changed while observing\n')
            return result
        self.client.request = changed
        with self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(self.task()['state'], 'prepared')
        self.assertEqual(self.client.queue, [])

    def test_role_drift_during_preflight_prevents_submission(self):
        original = self.client.request
        def changed(method, params):
            result = original(method, params)
            if method == 'thread/turns/list' and params.get('itemsView') == 'notLoaded':
                self.registry.write_text(json.dumps({'brainstorm': operation()}))
            return result
        self.client.request = changed
        with self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(self.task()['state'], 'prepared')
        self.assertEqual(self.client.queue, [])

    def test_role_drift_after_dispatch_intent_preserves_uncertainty_without_send(self):
        original = b.task_action
        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            if args[3] == 'dispatch':
                self.registry.write_text(json.dumps({'brainstorm': operation()}))
            return result
        with patch.object(b, 'task_action', side_effect=changed), self.assertRaises(m.Rejected):
            self.send()
        self.assertEqual(self.task()['state'], 'recovery_required')
        self.assertEqual(self.client.queue, [])

    def test_final_before_request_rejects_report_attribution(self):
        self.send()
        turn = self.completed_turn()
        turn['items'] = [turn['items'][-1], turn['items'][0]]
        self.client.turns = [turn]
        with self.assertRaises(m.Rejected):
            self.bridge.collect('native')
        self.assertNotIn('report_digest', self.task())

    def test_multiple_user_inputs_reject_report_attribution(self):
        self.send()
        for index in (0, 1, 3):
            turn = self.completed_turn()
            turn['items'].insert(index, {'type': 'userMessage', 'content': [
                                {'type': 'text', 'text': 'Another request'}]})
            self.client.turns = [turn]
            with self.assertRaises(m.Rejected):
                self.bridge.collect('native')
        self.assertNotIn('report_digest', self.task())

    def test_acknowledgement_save_failure_collects_without_resubmission(self):
        original = self.bridge.transition
        def failed(task, action, *args, **kwargs):
            if action == 'acknowledge':
                raise OSError('receipt write failed')
            return original(task, action, *args, **kwargs)
        with patch.object(self.bridge, 'transition', side_effect=failed), self.assertRaises(OSError):
            self.send()
        self.assertEqual(self.task()['state'], 'recovery_required')
        self.assertEqual(self.bridge.collect('native')['execution_status'], 'queued')
        self.assertEqual(len(self.client.queue), 1)

    def test_cut_after_submission_before_acknowledgement_persistence(self):
        original = self.client.request
        def interrupted(method, params):
            result = original(method, params)
            if method == 'thread/queue/add':
                raise KeyboardInterrupt('process stopped after submission')
            return result
        self.client.request = interrupted
        with self.assertRaises(KeyboardInterrupt):
            self.send()
        self.assertEqual(self.task()['state'], 'delivery_pending')
        self.client.request = original
        fresh = b.Bridge(m.Ledger(self.fixture.root), lambda _: self.client)
        self.assertEqual(fresh.collect('native')['state'], 'delivered')
        self.assertEqual(len(self.client.queue), 1)


if __name__ == '__main__':
    unittest.main()
