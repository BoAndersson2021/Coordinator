"""Builder adversarial checks, separate from the frozen independent review."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(os.environ.get('MACHINE_BRIDGE_CANDIDATE', str(Path(__file__).resolve().parent / 'candidate'))).resolve()
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'src'))
import test_native_bridge as fixtures
import machine as m


class AdversarialChecks(unittest.TestCase):
    def setUp(self):
        self.case = fixtures.BridgeTests()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def test_actual_cli_reports_invalid_endpoint_as_structured_rejection(self):
        case = self.case
        result = subprocess.run([sys.executable, str(ROOT / 'src/machine.py'),
                   '--root', str(case.fixture.root), 'bridge-configure',
                   '--project', 'external', '--endpoint', 'ws://remote:4500',
                   '--registry', str(case.registry), '--role', 'brainstorm',
                   '--route-manifest', str(case.manifest), '--operation-id', fixtures.operation()],
                   capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_adapter_change_during_baseline_read_prevents_submission(self):
        case = self.case
        original = case.client.request
        def changed(method, params):
            result = original(method, params)
            if method == 'thread/turns/list' and params.get('itemsView') == 'notLoaded':
                with (case.fixture.project / 'scripts/modeling_operations.py').open('a') as stream:
                    stream.write('# changed while observing\n')
            return result
        case.client.request = changed
        with self.assertRaises(m.Rejected):
            case.send()
        self.assertEqual(case.client.queue, [])


if __name__ == '__main__':
    unittest.main()
