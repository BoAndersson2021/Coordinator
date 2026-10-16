import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
spec = importlib.util.spec_from_file_location('machine', ROOT / 'src/machine.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def operation():
    return str(uuid.uuid4())


def tree(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        # These are isolated ledger-algorithm tests. Real production barriers are
        # exercised without mocks by test_workflow_invariant and CLI subprocesses.
        self.invariant_patch = patch('workflow_invariant.require_automated_workflow')
        self.invariant_patch.start()
        self.addCleanup(self.invariant_patch.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / 'studio'
        self.root.mkdir()
        for name in ('Design', 'docs'):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copy2(ROOT / 'machine.json', self.root / 'machine.json')
        self.project = self.base / 'external'
        self.project.mkdir()
        (self.project / 'README.md').write_text('# External workspace\nInspection fixture.\n')
        (self.project / 'AGENTS.md').write_text('# Instructions\nInspect only for this fixture.\n')
        for command in (['git', 'init', '-b', 'main'], ['git', 'add', 'README.md', 'AGENTS.md'],
                        ['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                         'commit', '-m', 'Inspection fixture']):
            subprocess.run(command, cwd=self.project, check=True, capture_output=True)
        self.ledger = m.Ledger(self.root)
        self.thread = operation()

    def tearDown(self):
        self.invariant_patch.stop()
        self.temporary.cleanup()

    def file(self, name, data):
        path = self.base / name
        path.write_text(json.dumps(data))
        return str(path)

    def initialize(self):
        self.ledger.initialize('fixture-owner')
        m.register_project(self.ledger, 'external', str(self.project), 'fixture-owner', operation())
        self.observe()

    def observe(self, **overrides):
        data = {'schema_version': 1, 'thread_id': self.thread, 'server_id': 'fixture-server',
                'cwd': str(self.project), 'status': 'idle', 'observed_at': m.now(),
                'source': 'codex_tui.list_threads', **overrides}
        return m.bind_agent(self.ledger, 'inspector', 'external', self.file('observation.json', data), operation())

    def prepare(self):
        self.initialize()
        return m.prepare_task(self.ledger, 'inspect', 'external', 'inspector',
                              'Summarize scope and supported entry points.', 'fixture-owner',
                              'Fixture read-only assignment', operation())

    def action(self, version, action, op=None, **parameters):
        return m.task_action(self.ledger, 'inspect', version, action, op or operation(), **parameters)

    def receipt(self, attempt, outcome='delivered', source='codex_tui.send_message_to_thread', **overrides):
        return self.file('receipt.json', {'schema_version': 1, 'task_id': 'inspect',
                         'attempt_id': attempt, 'thread_id': self.thread,
                         'server_id': 'fixture-server', 'outcome': outcome,
                         'source': source, 'detail': 'Queued message fixture-queued-message for thread ' + self.thread + '.', **overrides})

    def delivered(self, native=False):
        self.prepare()
        if native:
            self.observe(source='codex_local.read_thread')
        attempt = operation()
        self.action(1, 'dispatch', attempt)
        self.action(2, 'acknowledge', attempt_id=attempt,
                    evidence=self.receipt(attempt, source='codex.queue' if native else 'codex_tui.send_message_to_thread'))

    def reported(self):
        self.delivered()
        self.action(3, 'report', evidence=self.report())

    def report(self, **overrides):
        task = self.ledger.status()['tasks'][0]
        return self.file('report.json', {'schema_version': 1, 'task_id': 'inspect',
                         'attempt_id': task['attempts'][-1]['attempt_id'],
                         'thread_id': self.thread, 'server_id': 'fixture-server',
                         'turn_id': operation(), 'turn_status': 'completed',
                         'source': 'codex_tui.read_thread',
                         'body': 'Fixture report: external workspace supports inspection.', **overrides})

    def review(self, **overrides):
        task = self.ledger.status()['tasks'][0]
        checks = [{'file': name, 'sha256': sha, 'observation': 'Independently inspected fixture source.'}
                  for name, sha in task['inspected_inputs'].items()]
        return self.file('review.json', {'schema_version': 1, 'task_id': 'inspect',
                         'report_digest': task['report_digest'], 'revision': task['revision'],
                         'reviewer': 'fixture-independent-reviewer', 'checks': checks,
                         'verdict': 'pass', **overrides})

    def test_startup_is_read_only_without_state(self):
        before = tree(self.root)
        self.assertEqual(self.ledger.status()['status'], 'uninitialized')
        self.assertEqual(len(m.sources(self.root)['files']), 39)
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'src/machine.py'),
                                 '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(tree(self.root), before)
        self.assertFalse(self.ledger.directory.exists())

    def test_status_after_initialize_changes_no_bytes(self):
        self.initialize()
        before = tree(self.root)
        self.ledger.status()
        m.sources(self.root)
        self.assertEqual(tree(self.root), before)

    def test_full_inspection_cycle_and_replace_coordinator(self):
        self.reported()
        self.ledger = m.Ledger(self.root)
        self.action(4, 'verify', evidence=self.review())
        result = self.action(5, 'close')
        self.assertEqual(result['state'], 'closed')
        task = m.Ledger(self.root).status()['tasks'][0]
        self.assertEqual(task['verdict'], 'verified')
        self.assertEqual(task['version'], 6)
        self.assertEqual(task['operation'], 'inspect_repository')

    def test_unknown_schema_rejected_without_mutation(self):
        self.initialize()
        with sqlite3.connect(self.ledger.path) as connection:
            connection.execute('PRAGMA user_version=99')
        before = tree(self.root)
        with self.assertRaisesRegex(m.Rejected, 'schema'):
            self.ledger.status()
        self.assertEqual(tree(self.root), before)

    def test_do_not_initialize_over_existing_state(self):
        self.ledger.initialize('owner')
        before = tree(self.root)
        with self.assertRaisesRegex(m.Rejected, 'already exists'):
            self.ledger.initialize('other-owner')
        self.assertEqual(tree(self.root), before)

    def test_machine_manifest_required_before_initialize(self):
        (self.root / 'machine.json').unlink()
        with self.assertRaises(m.Rejected):
            self.ledger.initialize('owner')
        self.assertFalse(self.ledger.directory.exists())

    def test_source_drift_blocks_initialize(self):
        (self.root / 'Design/agentic-game-studio-v0.2-handoff/corpus/architecture-v1.2.txt').write_text('changed')
        with self.assertRaisesRegex(m.Rejected, 'digest mismatch'):
            self.ledger.initialize('owner')
        self.assertFalse(self.ledger.directory.exists())

    def test_machine_and_ancestor_project_paths_rejected(self):
        for path in (self.root, self.root / 'Design', self.root.parent):
            with self.subTest(path=path), self.assertRaisesRegex(m.Rejected, 'separate'):
                m.project_identity(path, self.root)

    def test_nested_git_project_path_rejected(self):
        child = self.project / 'subdirectory'
        child.mkdir()
        with self.assertRaisesRegex(m.Rejected, 'exact Git'):
            m.project_identity(child, self.root)

    def test_wrong_workspace_observation_is_atomic(self):
        self.initialize()
        before = tree(self.root)
        with self.assertRaisesRegex(m.Rejected, 'workspace'):
            self.observe(cwd=str(self.root))
        self.assertEqual(tree(self.root), before)

    def test_stale_and_future_observations_rejected(self):
        self.initialize()
        for seconds in (-301, 60):
            with self.subTest(seconds=seconds), self.assertRaisesRegex(m.Rejected, 'stale|future'):
                self.observe(observed_at=(datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat())

    def test_silent_agent_rebind_rejected(self):
        self.initialize()
        with self.assertRaisesRegex(m.Rejected, 'rebound'):
            self.observe(thread_id=operation())

    def test_stale_precondition_preserves_task(self):
        self.prepare()
        before = tree(self.root)
        with self.assertRaisesRegex(m.Rejected, 'Stale'):
            self.action(0, 'dispatch')
        self.assertEqual(tree(self.root), before)

    def test_dispatch_replay_cannot_authorize_resend(self):
        self.prepare()
        op = operation()
        first = self.action(1, 'dispatch', op)
        replay = self.action(1, 'dispatch', op)
        self.assertTrue(first['dispatchable'])
        self.assertTrue(replay['replayed'])
        self.assertFalse(replay['dispatchable'])
        self.assertEqual(self.ledger.status()['tasks'][0]['version'], 2)

    def test_operation_identity_cannot_change_input(self):
        self.prepare()
        op = operation()
        self.action(1, 'dispatch', op)
        with self.assertRaisesRegex(m.Rejected, 'changed input'):
            self.action(2, 'dispatch', op)

    def test_pending_delivery_survives_restart_and_blocks_retry(self):
        self.prepare()
        self.action(1, 'dispatch')
        self.ledger = m.Ledger(self.root)
        self.assertEqual(self.ledger.status()['recovery_required'], ['inspect'])
        with self.assertRaisesRegex(m.Rejected, 'reconcile'):
            self.action(2, 'dispatch')

    def test_uncertain_delivery_reconciliation_and_explicit_retry(self):
        self.prepare()
        attempt = operation()
        self.action(1, 'dispatch', attempt)
        self.action(2, 'uncertain', attempt_id=attempt, reason='Acknowledgement lost')
        with self.assertRaises(m.Rejected):
            self.action(3, 'dispatch')
        evidence = self.receipt(attempt, 'not_delivered', 'codex_tui.read_thread')
        self.action(3, 'reconcile', attempt_id=attempt, outcome='not_delivered', evidence=evidence)
        self.assertEqual(self.action(4, 'dispatch')['state'], 'delivery_pending')

    def test_failed_send_does_not_prove_no_delivery(self):
        self.prepare()
        attempt = operation()
        self.action(1, 'dispatch', attempt)
        with self.assertRaisesRegex(m.Rejected, 'failed send'):
            self.action(2, 'reconcile', attempt_id=attempt, outcome='not_delivered',
                        evidence=self.receipt(attempt, 'not_delivered'))

    def test_wrong_delivery_receipt_rejected_atomically(self):
        self.prepare()
        attempt = operation()
        self.action(1, 'dispatch', attempt)
        before = tree(self.root)
        with self.assertRaisesRegex(m.Rejected, 'mismatch'):
            self.action(2, 'acknowledge', attempt_id=attempt,
                        evidence=self.receipt(attempt, thread_id=operation()))
        self.assertEqual(tree(self.root), before)

    def test_report_and_close_cannot_bypass_delivery_or_review(self):
        self.prepare()
        with self.assertRaises(m.Rejected):
            self.action(1, 'report', evidence=self.file('report.json', {'claim': 'done'}))
        with self.assertRaises(m.Rejected):
            self.action(1, 'close')

    def test_executor_self_review_rejected(self):
        self.reported()
        with self.assertRaisesRegex(m.Rejected, 'own independent'):
            self.action(4, 'verify', evidence=self.review(reviewer=self.thread))

    def test_review_must_bind_report_and_all_inputs(self):
        self.reported()
        with self.assertRaisesRegex(m.Rejected, 'retained report'):
            self.action(4, 'verify', evidence=self.review(report_digest='0' * 64))
        review = json.loads(Path(self.review()).read_text())
        review['checks'] = review['checks'][:1]
        with self.assertRaisesRegex(m.Rejected, 'every pinned'):
            self.action(4, 'verify', evidence=self.file('review-short.json', review))

    def test_changed_source_blocks_dispatch_and_verification(self):
        self.prepare()
        original = (self.project / 'README.md').read_text()
        (self.project / 'README.md').write_text('Changed working tree')
        with self.assertRaisesRegex(m.Rejected, 'input drift'):
            self.action(1, 'dispatch')
        (self.project / 'README.md').write_text(original)
        attempt = operation()
        self.action(1, 'dispatch', attempt)
        self.action(2, 'acknowledge', attempt_id=attempt, evidence=self.receipt(attempt))
        self.action(3, 'report', evidence=self.report())
        review = self.review()
        (self.project / 'README.md').write_text('Changed after report')
        with self.assertRaisesRegex(m.Rejected, 'digest changed'):
            self.action(4, 'verify', evidence=review)

    def test_record_and_operation_tampering_detected(self):
        self.prepare()
        with sqlite3.connect(self.ledger.path) as connection:
            connection.execute("UPDATE tasks SET state='closed'")
        with self.assertRaisesRegex(m.Rejected, 'state index'):
            self.ledger.status()
        with sqlite3.connect(self.ledger.path) as connection:
            connection.execute("UPDATE tasks SET state='prepared'")
            connection.execute("UPDATE operations SET response='{}'")
        with self.assertRaisesRegex(m.Rejected, 'Operation/event'):
            self.ledger.status()

    def test_missing_or_changed_retained_evidence_detected(self):
        self.initialize()
        with sqlite3.connect(self.ledger.path) as connection:
            connection.execute('DELETE FROM evidence')
        with self.assertRaisesRegex(m.Rejected, 'Missing retained'):
            self.ledger.status()

    def test_crash_before_commit_preserves_last_committed_transition(self):
        self.prepare()
        attempt = operation()
        self.action(1, 'dispatch', attempt)
        code = '''import importlib.util, os, pathlib
spec=importlib.util.spec_from_file_location('machine', {!r})
import sys
sys.path.insert(0, str(pathlib.Path(spec.origin).parent))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ledger=m.Ledger({!r})
with ledger.connect(write=True) as connection:
    task=ledger.get(connection,'tasks','inspect')
    task['state']='closed';task['version']=99
    ledger.put(connection,'tasks',task)
    os._exit(93)
'''.format(str(ROOT / 'src/machine.py'), str(self.root))
        result = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True)
        self.assertEqual(result.returncode, 93)
        task = m.Ledger(self.root).status()['tasks'][0]
        self.assertEqual(task['state'], 'delivery_pending')
        self.assertEqual(task['version'], 2)

    def test_incomplete_or_wrong_thread_report_rejected(self):
        self.delivered()
        for overrides in ({'turn_status': 'inProgress'}, {'thread_id': operation()}):
            with self.subTest(overrides=overrides), self.assertRaisesRegex(m.Rejected, 'mismatch'):
                self.action(3, 'report', evidence=self.report(**overrides))

    def test_transport_limit_rejection_leaves_no_pending_attempt(self):
        self.initialize()
        m.prepare_task(self.ledger, 'inspect', 'external', 'inspector', 'x' * 1000,
                       'owner', 'read-only fixture', operation())
        with self.assertRaisesRegex(m.Rejected, 'transport limit'):
            self.action(1, 'dispatch')
        self.assertEqual(self.ledger.status()['tasks'][0]['state'], 'prepared')

    def test_two_cli_coordinators_are_blocked_before_dispatch(self):
        self.prepare()
        command = [sys.executable, '-B', str(ROOT / 'src/machine.py'), '--root', str(self.root),
                   'task-dispatch', '--id', 'inspect', '--expected-version', '1', '--operation-id']
        processes = [subprocess.Popen(command + [operation()], stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for _ in range(2)]
        results = [process.communicate(timeout=10) for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [3, 3], results)
        task = self.ledger.status()['tasks'][0]
        self.assertEqual(len(task['attempts']), 0)
        self.assertEqual(task['version'], 1)

    def test_notloaded_requires_native_queue_observation(self):
        self.prepare()
        self.observe(status='notLoaded')
        with self.assertRaisesRegex(m.Rejected, 'native queue'):
            self.action(1, 'dispatch')
        self.observe(status='notLoaded', source='codex_local.read_thread')
        result = self.action(1, 'dispatch')
        self.assertEqual(result['envelope']['transport'], 'codex_queue')

    def test_boolean_schema_rejected(self):
        self.initialize()
        with self.assertRaisesRegex(m.Rejected, 'observation'):
            self.observe(schema_version=True)
        manifest = self.root / 'machine.json'
        value = json.loads(manifest.read_text())
        value['schema_version'] = True
        manifest.write_text(json.dumps(value))
        with self.assertRaisesRegex(m.Rejected, 'manifest'):
            m.sources(self.root)

    def test_external_project_cannot_be_machine_worktree(self):
        subprocess.run(['git', 'init', '-b', 'main'], cwd=self.root, check=True, capture_output=True)
        subprocess.run(['git', 'add', 'machine.json'], cwd=self.root, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-m', 'Studio fixture'], cwd=self.root, check=True, capture_output=True)
        linked = self.base / 'studio-other-worktree'
        subprocess.run(['git', 'worktree', 'add', '-b', 'candidate', str(linked)],
                       cwd=self.root, check=True, capture_output=True)
        with self.assertRaisesRegex(m.Rejected, 'share Machine Git history'):
            m.project_identity(linked, self.root)

    def replacement_begin(self, **overrides):
        self.delivered(native=True)
        self.replacement_thread = operation()
        observation = {'schema_version': 1, 'thread_id': self.replacement_thread,
                       'server_id': 'fixture-server', 'cwd': str(self.project), 'status': 'notLoaded',
                       'observed_at': m.now(), 'source': 'codex_local.read_thread'}
        m.bind_agent(self.ledger, 'replacement', 'external', self.file('replacement-agent.json', observation), operation())
        task = self.ledger.status()['tasks'][0]
        attempt = task['attempts'][-1]['attempt_id']
        with self.ledger.connect() as connection:
            response = json.loads(connection.execute('SELECT response FROM operations WHERE id=?', (attempt,)).fetchone()[0])
        observed = {'schema_version': 1, 'task_id': 'inspect', 'attempt_id': attempt,
                    'thread_id': self.thread, 'server_id': 'fixture-server',
                    'queued_submission_id': 'fixture-queued-message',
                    'prompt_sha256': m.digest(response['envelope']['prompt'].encode()),
                    'source': 'codex_local.thread/queue/list', **overrides}
        self.removal_operation = operation()
        return self.action(3, 'replacement-begin', self.removal_operation, new_agent='replacement',
                           evidence=self.file('queue-observation.json', observed))

    def removal_receipt(self, **overrides):
        task = self.ledger.status()['tasks'][0]
        return self.file('queue-removal.json', {'schema_version': 1, 'task_id': 'inspect',
                         'attempt_id': task['attempts'][-1]['attempt_id'], 'thread_id': self.thread,
                         'server_id': 'fixture-server', 'queued_submission_id': 'fixture-queued-message',
                         'replacement_operation_id': self.removal_operation,
                         'source': 'codex_local.thread/queue/delete', 'response': {'deleted': True}, **overrides})

    def test_replacement_preserves_task_and_original_attempt(self):
        self.replacement_begin()
        self.action(4, 'replacement-finish', replacement_operation_id=self.removal_operation,
                    evidence=self.removal_receipt())
        task = self.ledger.status()['tasks'][0]
        self.assertEqual(task['id'], 'inspect')
        self.assertEqual(task['state'], 'prepared')
        self.assertEqual(task['thread_id'], self.replacement_thread)
        self.assertEqual(task['attempts'][0]['state'], 'queue_removed')
        self.assertEqual(task['replacements'][0]['old_thread_id'], self.thread)
        self.assertTrue(self.action(5, 'dispatch')['dispatchable'])

    def test_replacement_pending_survives_restart_and_blocks_dispatch(self):
        self.replacement_begin()
        self.ledger = m.Ledger(self.root)
        self.assertEqual(self.ledger.status()['recovery_required'], ['inspect'])
        with self.assertRaises(m.Rejected):
            self.action(4, 'dispatch')

    def test_replacement_requires_exact_original_queued_message(self):
        for override in ({'queued_submission_id': 'foreign-message'}, {'prompt_sha256': '0' * 64}):
            with self.subTest(override=override):
                # Each rejected observation must leave the accepted task intact.
                if hasattr(self, 'removal_operation'):
                    self.tearDown()
                    self.setUp()
                with self.assertRaises(m.Rejected):
                    self.replacement_begin(**override)
                self.assertEqual(self.ledger.status()['tasks'][0]['state'], 'delivered')

    def test_replacement_removal_failure_cannot_enable_dispatch(self):
        self.replacement_begin()
        for override in ({'response': {'deleted': False}}, {'thread_id': operation()},
                         {'response': {'deleted': 1}}):
            with self.subTest(override=override), self.assertRaises(m.Rejected):
                self.action(4, 'replacement-finish', replacement_operation_id=self.removal_operation,
                            evidence=self.removal_receipt(**override))
        self.assertEqual(self.ledger.status()['tasks'][0]['state'], 'replacement_pending')

    def test_replacement_cannot_follow_a_received_report(self):
        self.reported()
        with self.assertRaisesRegex(m.Rejected, 'unreported'):
            self.action(4, 'replacement-begin', new_agent='replacement',
                        evidence=self.file('unused.json', {}))


if __name__ == '__main__':
    unittest.main()
