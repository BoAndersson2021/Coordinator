"""Bridge contract regressions: no TUI or onboarding prompt is started here."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest

from websockets.sync.client import connect


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
CODEX = "/Users/boandersson/.npm-global/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex"
SELECTED_MODEL = tomllib.loads((ROOT / "valhalla.config.toml").read_text())["model"]
spec = importlib.util.spec_from_file_location("desktop_bridge", ROOT / "desktop_bridge.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class DesktopBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.children = []

    def tearDown(self):
        for child in self.children:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=3)
        self.temp.cleanup()

    def child(self, *arguments):
        process = subprocess.Popen(arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.children.append(process)
        return process

    def wait_for_exit(self, process):
        deadline = time.monotonic() + 5
        while process.poll() is None and time.monotonic() < deadline:
            time.sleep(.05)
        self.assertIsNotNone(process.poll(), "process did not retire")

    def test_runtime_manifest_is_exact_and_tampering_fails(self):
        manifest = self.root / "runtime.json"
        identity = bridge.runtime_identity()
        manifest.write_text(json.dumps(identity))
        bridge.verify_runtime(manifest)
        manifest.write_text(json.dumps({**identity, "files_sha256": "0" * 64}))
        with self.assertRaisesRegex(RuntimeError, "transport bytes"):
            bridge.verify_runtime(manifest)

    def test_projection_requires_one_selected_model(self):
        projection = self.root / "projection.json"
        projection.write_text(json.dumps({"format": "valhall-panel-profile/1", "arguments": ["--config", "model=" + json.dumps(SELECTED_MODEL)]}))
        self.assertEqual(bridge.projection(projection)[1], SELECTED_MODEL)
        projection.write_text(json.dumps({"format": "valhall-panel-profile/1", "arguments": ["--config", "approval_policy=\"never\""]}))
        with self.assertRaisesRegex(RuntimeError, "selected model"):
            bridge.projection(projection)

    def test_model_admission_rejects_absent_or_malformed_catalog(self):
        rpc = object.__new__(bridge.Rpc)
        rpc.call = lambda *_: {"data": [{"model": "other", "id": "other"}], "nextCursor": None}
        with self.assertRaisesRegex(RuntimeError, "selected model is unavailable"):
            rpc.ensure_model(SELECTED_MODEL)
        rpc.call = lambda *_: {"data": "not-an-array", "nextCursor": None}
        with self.assertRaisesRegex(RuntimeError, "invalid data"):
            rpc.ensure_model(SELECTED_MODEL)

    def test_supervisor_retires_exact_children_after_host_death(self):
        host = self.child("/bin/sleep", "60")
        server = self.child("/bin/sleep", "60")
        tui = self.child("/bin/sleep", "60")
        bridge_dir = self.root / "bridge"
        bridge_dir.mkdir(mode=0o700)
        watcher = self.child(sys.executable, str(ROOT / "desktop_bridge.py"), "--supervise",
                             "--host", json.dumps(bridge.process_identity(host.pid)),
                             "--server", json.dumps(bridge.process_identity(server.pid)),
                             "--tui", json.dumps(bridge.process_identity(tui.pid)), "--bridge", str(bridge_dir))
        host.kill()
        self.wait_for_exit(host)
        self.wait_for_exit(server)
        self.wait_for_exit(tui)
        self.wait_for_exit(watcher)
        retirement = json.loads((bridge_dir / "retired.json").read_text())
        self.assertEqual(retirement["reason"], "host_lifetime_ended")

    def test_loopback_capability_rejects_anonymous_rpc_and_admits_live_model(self):
        token = os.urandom(32).hex()
        token_path = self.root / "capability.token"
        token_path.write_text(token + "\n")
        os.chmod(token_path, 0o600)
        endpoint = bridge.endpoint_url()
        profile = json.loads((WORKSPACE / "Launcher/build/CodeExp2.app/Contents/Resources/valhall-panel-profile.json").read_text())["arguments"]
        server = self.child(CODEX, "app-server", "--listen", endpoint, "--ws-auth", "capability-token",
                            "--ws-token-file", str(token_path), *profile)
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if server.poll() is not None:
                self.fail("capability server exited before accepting connections")
            try:
                authenticated = connect(endpoint + "/", legacy=True, open_timeout=.2,
                                        additional_headers={"Authorization": "Bearer " + token})
            except Exception:
                time.sleep(.05)
                continue
            else:
                authenticated.close()
                break
        else:
            self.fail("capability server never accepted connections")
        with self.assertRaises(Exception):
            connect(endpoint + "/", legacy=True, open_timeout=2)
        rpc = bridge.Rpc(endpoint, token)
        try:
            rpc.ensure_model(SELECTED_MODEL)
        finally:
            rpc.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
