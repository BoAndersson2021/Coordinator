"""Dashboard observations must remain truthful, private, read-only and supervised."""
from http.client import HTTPConnection
import hashlib
import json
import os
from pathlib import Path
import plistlib
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import dashboard
import machine


def fixture_ledger(root, state='delivered', report=False, review=False):
    directory = root / '.machine'
    directory.mkdir()
    with sqlite3.connect(directory / 'state.sqlite3') as connection:
        connection.executescript(machine.SQL)
        connection.execute('PRAGMA user_version=1')
        for key, value in {'schema_version': 1, 'machine_root': str(root)}.items():
            connection.execute('INSERT INTO meta VALUES (?,?)', (key, json.dumps(value)))
        evidence = b'{"detail":"historical evidence"}'
        digest = hashlib.sha256(evidence).hexdigest()
        connection.execute('INSERT INTO evidence VALUES (?,?)', (digest, evidence))
        record = {'schema_version': 1, 'id': 'queued-without-worker', 'version': 3,
                  'state': state, 'project_id': 'fixture-project', 'agent_id': 'fixture-role',
                  'thread_id': 'saved-thread', 'updated_at': '2020-01-01T00:00:00+00:00',
                  'attempts': [{'attempt_id': 'exact-existing-attempt', 'receipt_digest': digest}]}
        if report:
            record['report_digest'] = digest
        if review:
            record['review_digest'] = digest
        connection.execute('INSERT INTO tasks VALUES (?,?,?,?)',
                           (record['id'], 3, state, machine.canonical(record)))
        machine.Ledger.event(connection, {'kind': 'record', 'table': 'tasks', 'record': record})


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def server(self):
        server = dashboard.DashboardServer(self.root, 0, 'fixture-token')
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server

    def request(self, server, path='/api/snapshot', method='GET', headers=None):
        connection = HTTPConnection('127.0.0.1', server.server_port, timeout=3)
        self.addCleanup(connection.close)
        connection.request(method, path, headers=headers if headers is not None else
                           {'X-Machine-Token': 'fixture-token'})
        response = connection.getresponse()
        return response.status, response.read(), dict(response.getheaders())

    def test_http_auth_origin_and_method_boundaries(self):
        server = self.server()
        self.assertEqual(server.server_address[0], '127.0.0.1')
        self.assertEqual(self.request(server, headers={})[0], 401)
        self.assertEqual(self.request(server, headers={'X-Machine-Token': 'wrong'})[0], 401)
        self.assertEqual(self.request(server, headers={'Host': 'evil.invalid', 'X-Machine-Token': 'fixture-token'})[0], 403)
        self.assertEqual(self.request(server, headers={'Origin': 'https://evil.invalid', 'X-Machine-Token': 'fixture-token'})[0], 403)
        self.assertEqual(self.request(server, method='POST')[0], 405)
        self.assertEqual(self.request(server, path='/api/task-dispatch')[0], 404)
        code, html, headers = self.request(server, path='/')
        self.assertEqual(code, 200)
        self.assertNotIn(b'fixture-token', html)
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertNotIn('Access-Control-Allow-Origin', headers)

    def test_queued_without_worker_never_becomes_running(self):
        fixture_ledger(self.root)
        server = self.server()
        before = (self.root / '.machine/state.sqlite3').read_bytes()
        code, raw, _ = self.request(server)
        self.assertEqual(code, 200)
        body = json.loads(raw)
        task = body['tasks'][0]
        self.assertFalse(task['live_receiver_proven'])
        self.assertFalse(task['workflow_ready'])
        self.assertIn('execution not established', task['delivery'])
        self.assertFalse(task['report_retained'])
        self.assertEqual(task['evidence_at'], '2020-01-01T00:00:00+00:00')
        self.assertNotEqual(task['evidence_at'], body['observed_at'])
        self.assertEqual((self.root / '.machine/state.sqlite3').read_bytes(), before)
        self.assertEqual(sorted(p.name for p in (self.root / '.machine').iterdir()), ['state.sqlite3'])

    def test_historical_completion_and_review_do_not_qualify_runtime(self):
        fixture_ledger(self.root, state='verified', report=True, review=True)
        result = dashboard.snapshot(self.root)
        task = result['tasks'][0]
        self.assertTrue(task['report_retained'])
        self.assertTrue(task['review_retained'])
        self.assertEqual(task['historical_verdict'], 'verified')
        self.assertEqual(result['counts']['live_receivers_proven'], 0)
        self.assertFalse(result['workflow_invariant']['workflow_ready'])
        self.assertFalse(result['network_observation'])

    def test_corrupt_ledger_fails_instead_of_serving_previous_success(self):
        fixture_ledger(self.root)
        server = self.server()
        self.assertEqual(self.request(server)[0], 200)
        with sqlite3.connect(self.root / '.machine/state.sqlite3') as connection:
            connection.execute("UPDATE tasks SET state='verified'")
        server.cached_at = time.monotonic() - dashboard.REFRESH_SECONDS - 1
        code, raw, _ = self.request(server)
        self.assertEqual(code, 503)
        self.assertEqual(json.loads(raw)['status'], 'observation_failed')
        self.assertNotIn('tasks', json.loads(raw))

    def test_empty_ledger_is_not_initialized_by_dashboard(self):
        server = self.server()
        code, raw, _ = self.request(server)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)['tasks'], [])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_supervisor_is_keepalive_and_repeated_start_preserves_identity(self):
        calls = []
        def supervisor(*args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, stdout='pid = 4242\n', stderr='')
        health = {'pid': 4242, 'instance': 'owned-instance', 'workflow_ready': False}
        with patch.object(Path, 'home', return_value=self.root), patch.object(sys, 'platform', 'darwin'), \
             patch.object(dashboard, 'launchctl', side_effect=supervisor), \
             patch.object(dashboard, 'health_request', return_value=health), \
             patch.object(dashboard.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            first = dashboard.ensure_service(self.root)
            config_before = dashboard.load_configuration(self.root)
            second = dashboard.ensure_service(self.root)
            self.assertEqual(config_before, dashboard.load_configuration(self.root))
            self.assertEqual(first['service']['instance'], second['service']['instance'])
            definition = plistlib.loads(dashboard.service_paths(self.root)['plist'].read_bytes())
            self.assertTrue(definition['KeepAlive'])
            self.assertTrue(definition['RunAtLoad'])
            self.assertEqual(definition['ProgramArguments'][-1], 'dashboard-serve')
            self.assertNotIn('bootstrap', [c[0] for c in calls])
            self.assertNotIn('token', json.dumps(first))

    def test_supervisor_definition_change_is_not_silently_adopted(self):
        with patch.object(Path, 'home', return_value=self.root), patch.object(sys, 'platform', 'darwin'), \
             patch.object(dashboard, 'launchctl', return_value=subprocess.CompletedProcess([], 0, stdout='pid = 4242\n')), \
             patch.object(dashboard, 'health_request', return_value={'pid': 4242}), \
             patch.object(dashboard.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            dashboard.ensure_service(self.root)
            path = dashboard.service_paths(self.root)['plist']
            original = plistlib.loads(path.read_bytes())
            original['KeepAlive'] = False
            path.write_bytes(plistlib.dumps(original))
            with self.assertRaisesRegex(machine.Rejected, 'adoption required'):
                dashboard.ensure_service(self.root)

    def test_non_macos_does_not_fall_back_to_a_terminal(self):
        with patch.object(sys, 'platform', 'linux'), patch.object(dashboard.subprocess, 'run') as run:
            with self.assertRaisesRegex(machine.Rejected, 'no manual fallback'):
                dashboard.ensure_service(self.root)
        run.assert_not_called()

    def test_sensitive_report_body_and_receipt_are_not_exposed(self):
        fixture_ledger(self.root, report=True)
        raw = json.dumps(dashboard.snapshot(self.root))
        self.assertNotIn('historical evidence', raw)
        self.assertNotIn('report_digest', raw)
        self.assertNotIn('receipt_digest', raw)


if __name__ == '__main__':
    unittest.main()
