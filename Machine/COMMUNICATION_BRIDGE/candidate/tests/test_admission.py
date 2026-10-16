"""Disposable local-operator admission tests; environment identities are fixture assertions."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import admission as a
spec = importlib.util.spec_from_file_location('admission_test_machine', ROOT / 'src/machine.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def uid():
    return str(uuid.uuid4())


def tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir='/private/tmp')
        self.base = Path(self.temp.name).resolve()
        self.root, self.scratch = self.base / 'machine', self.base / 'scratch'
        for dest in (self.root, self.scratch):
            dest.mkdir()
            for name in ('Design', 'docs', 'src'):
                shutil.copytree(ROOT / name, dest / name)
            for name in ('machine.json', 'Machine', 'AGENTS.md'):
                shutil.copy2(ROOT / name, dest / name)
        self.ledger = m.Ledger(self.root)
        self.ledger.initialize('fixture-owner')
        self.time = datetime.now(timezone.utc)
        self.coordinator, self.target = uid(), uid()
        self.env = patch.dict(os.environ, {'CODEX_THREAD_ID': self.coordinator,
                                          'CODEX_SESSION_ID': self.coordinator})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.temp.cleanup)
        self.service = a.Admission(self.ledger, m.sources, lambda: self.time)
        self.obs = {'schema_version': 1, 'thread_id': self.target, 'server_id': 'fixture-server',
                    'cwd': str(self.root), 'status': 'idle', 'observed_at': self.time.isoformat(),
                    'source': 'codex_tui.read_thread'}
        self.decision = {'schema_version': 1, 'kind': 'scratch_init_admission',
                         'owner': 'fixture-owner', 'owner_quote': 'Fixture explicit bounded approval',
                         'machine_root': str(self.root), 'coordinator_thread_id': self.coordinator,
                         'target_thread_id': self.target, 'scratch_root': str(self.scratch),
                         'init_owner': 'BehaviorTest', 'issued_at': self.time.isoformat(),
                         'expires_at': (self.time + timedelta(minutes=15)).isoformat()}
        self.obsfile, self.decisionfile = self.base / 'obs.json', self.base / 'decision.json'
        self.admission, self.permit = uid(), uid()

    def inputs(self):
        self.obsfile.write_text(json.dumps(self.obs))
        self.decisionfile.write_text(json.dumps(self.decision))

    def admit(self):
        self.inputs()
        return self.service.admit(self.obsfile, self.decisionfile, self.admission)

    def issue(self):
        self.admit()
        return self.service.issue(self.admission, self.permit)

    def target_actor(self):
        os.environ['CODEX_THREAD_ID'] = os.environ['CODEX_SESSION_ID'] = self.target

    @property
    def request(self):
        return self.service.home / (self.permit + '.request.json')

    def test_inspection_startup_does_not_create_store(self):
        before = tree(self.root)
        with self.assertRaisesRegex(a.AdmissionRejected, 'Unknown permit'):
            self.service.inspect(self.permit)
        self.ledger.status()
        self.assertEqual(tree(self.root), before)
        self.assertFalse(self.service.home.exists())

    def test_single_execution_and_replay_rejected_without_legacy_mutation(self):
        legacy = self.ledger.path.read_bytes()
        self.issue()
        self.target_actor()
        before = tree(self.root)
        self.assertTrue(self.service.inspect(self.permit)['eligible'])
        self.assertEqual(tree(self.root), before)
        result = self.service.execute(self.permit, self.request)
        self.assertEqual(result['status'], 'succeeded')
        with m.Ledger(self.scratch).connect() as db:
            self.assertEqual(json.loads(db.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]),
                             'BehaviorTest')
        after = tree(self.scratch)
        with self.assertRaisesRegex(a.AdmissionRejected, 'consumed'):
            self.service.execute(self.permit, self.request)
        self.assertEqual(tree(self.scratch), after)
        self.assertEqual(self.ledger.path.read_bytes(), legacy)
        self.assertFalse(self.service.inspect(self.permit)['eligible'])

    def test_invalid_observations_owner_and_lifetime(self):
        variants = [('obs', 'thread_id', uid()), ('obs', 'cwd', str(self.scratch)),
                    ('obs', 'source', 'guessed'), ('obs', 'status', 'running'),
                    ('obs', 'observed_at', (self.time - timedelta(seconds=301)).isoformat()),
                    ('decision', 'owner', 'different'), ('decision', 'coordinator_thread_id', uid()),
                    ('decision', 'expires_at', (self.time + timedelta(seconds=901)).isoformat()),
                    ('decision', 'issued_at', (self.time + timedelta(seconds=1)).isoformat())]
        for record, key, value in variants:
            obj = self.obs if record == 'obs' else self.decision
            original = obj[key]
            with self.subTest(record=record, key=key):
                obj[key] = value
                with self.assertRaises(a.AdmissionRejected):
                    self.admit()
                self.assertFalse((self.scratch / '.machine').exists())
                obj[key] = original
        self.assertFalse(self.service.state.exists())

    def test_wrong_actor_missing_identity_and_session_mismatch(self):
        self.issue()
        for thread, session in ((self.coordinator, self.coordinator), (self.target, uid()), ('', '')):
            with self.subTest(thread=thread):
                os.environ['CODEX_THREAD_ID'], os.environ['CODEX_SESSION_ID'] = thread, session
                with self.assertRaises(a.AdmissionRejected):
                    self.service.execute(self.permit, self.request)
                self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'issued')
                self.assertFalse((self.scratch / '.machine').exists())

    def test_changed_request_arguments_and_bytes(self):
        self.issue()
        self.target_actor()
        original = self.request.read_bytes()
        for content in (json.dumps({**json.loads(original), 'init_owner': 'different'}).encode(),
                        original + b' '):
            with self.subTest(content=content):
                self.request.write_bytes(content)
                with self.assertRaises(a.AdmissionRejected):
                    self.service.execute(self.permit, self.request)
                self.assertFalse((self.scratch / '.machine').exists())
        self.request.write_bytes(original)
        self.assertTrue(self.service.inspect(self.permit)['eligible'])

    def test_expired_or_profile_drift_rejects_before_consumption(self):
        self.issue()
        self.target_actor()
        self.time += timedelta(minutes=15)
        with self.assertRaisesRegex(a.AdmissionRejected, 'expired'):
            self.service.execute(self.permit, self.request)
        self.time -= timedelta(minutes=15)
        (self.root / 'AGENTS.md').write_text('Changed policy')
        with self.assertRaisesRegex(a.AdmissionRejected, 'profile changed'):
            self.service.execute(self.permit, self.request)
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'issued')
        self.assertFalse((self.scratch / '.machine').exists())

    def test_scratch_replacement_symlink_and_existing_state(self):
        self.issue()
        self.target_actor()
        old = self.base / 'old'
        self.scratch.rename(old)
        shutil.copytree(old, self.scratch)
        with self.assertRaisesRegex(a.AdmissionRejected, 'identity changed'):
            self.service.execute(self.permit, self.request)
        shutil.rmtree(self.scratch)
        self.scratch.symlink_to(old, target_is_directory=True)
        with self.assertRaises(a.AdmissionRejected):
            self.service.execute(self.permit, self.request)
        self.scratch.unlink()
        old.rename(self.scratch)
        (self.scratch / '.machine').mkdir()
        with self.assertRaisesRegex(a.AdmissionRejected, 'already exists'):
            self.service.execute(self.permit, self.request)

    def test_changed_source_context_rejects(self):
        self.issue()
        self.target_actor()
        (self.scratch / 'machine.json').write_text('{}')
        with self.assertRaises((a.AdmissionRejected, m.Rejected)):
            self.service.execute(self.permit, self.request)
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'issued')

    def test_operation_replay_changed_input_and_one_permit_limit(self):
        self.admit()
        self.assertTrue(self.admit()['replayed'])
        self.decision['owner_quote'] += ' changed'
        with self.assertRaisesRegex(a.AdmissionRejected, 'changed input'):
            self.admit()
        self.decision['owner_quote'] = 'Fixture explicit bounded approval'
        self.inputs()
        with self.assertRaisesRegex(a.AdmissionRejected, 'already admitted'):
            self.service.admit(self.obsfile, self.decisionfile, uid())
        first = self.service.issue(self.admission, self.permit)
        self.assertTrue(self.service.issue(self.admission, self.permit)['replayed'])
        self.assertEqual(first['status'], 'issued')
        with self.assertRaisesRegex(a.AdmissionRejected, 'one permit'):
            self.service.issue(self.admission, uid())

    def test_interrupted_issuance_is_reserved_and_never_republished(self):
        self.admit()
        original = a.write_once
        def interrupted(filename, value):
            if filename == self.request:
                raise OSError('Fixture publication failure')
            return original(filename, value)
        with patch.object(a, 'write_once', interrupted):
            with self.assertRaises(OSError):
                self.service.issue(self.admission, self.permit)
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'issuing')
        self.assertEqual(self.service.issue(self.admission, self.permit)['status'], 'issuance_pending')
        self.assertFalse(self.request.exists())
        with self.assertRaises(a.AdmissionRejected):
            self.service.issue(self.admission, uid())

    def test_initializer_error_or_process_interruption_consumes(self):
        self.issue()
        self.target_actor()
        with patch.object(m.Ledger, 'initialize', side_effect=OSError('Fixture init failure')):
            with self.assertRaisesRegex(a.AdmissionRejected, 'outcome_unknown'):
                self.service.execute(self.permit, self.request)
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'outcome_unknown')
        with self.assertRaises(a.AdmissionRejected):
            self.service.execute(self.permit, self.request)

    def test_process_cut_after_durable_consumption_blocks_retry(self):
        self.issue()
        self.target_actor()
        with patch.object(m.Ledger, 'initialize', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.service.execute(self.permit, self.request)
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'executing')
        with self.assertRaises(a.AdmissionRejected):
            self.service.execute(self.permit, self.request)
        self.assertFalse((self.scratch / '.machine').exists())

    def test_cut_after_init_before_result_save_does_not_repeat_effect(self):
        self.issue()
        self.target_actor()
        original = self.service.save
        calls = []
        def interrupted(body):
            calls.append(body['permits'][self.permit]['state'])
            if len(calls) == 2:
                raise OSError('Fixture result persistence failure')
            return original(body)
        with patch.object(self.service, 'save', interrupted):
            with self.assertRaises(OSError):
                self.service.execute(self.permit, self.request)
        self.assertTrue((self.scratch / '.machine/state.sqlite3').exists())
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'executing')
        after = tree(self.scratch)
        with self.assertRaises(a.AdmissionRejected):
            self.service.execute(self.permit, self.request)
        self.assertEqual(tree(self.scratch), after)

    def test_two_cli_executors_only_one_succeeds(self):
        self.issue()
        self.target_actor()
        command = [sys.executable, '-B', str(ROOT / 'src/machine.py'), '--root', str(self.root),
                   'permit-execute', '--permit-id', self.permit, '--request', str(self.request)]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for _ in range(2)]
        outputs = [proc.communicate(timeout=20) for proc in processes]
        self.assertEqual(sorted(proc.returncode for proc in processes), [0, 2], outputs)
        self.assertEqual(self.service.read()['permits'][self.permit]['state'], 'succeeded')
        with m.Ledger(self.scratch).connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM events').fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
