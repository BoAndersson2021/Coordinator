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
from unittest import mock

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
        projection.write_text(json.dumps({"format": "valhall-panel-profile/1", "arguments": ["--config", "model=" + json.dumps(SELECTED_MODEL), "--config", "default_permissions=\":workspace-write\"", "--config", "approval_policy=\"on-request\""]}))
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

    def test_panel_frames_are_confined_to_the_exact_receipt_receiver(self):
        receiver = "receiver-a"
        allowed = {"id": 1, "method": "turn/start", "params": {"threadId": receiver, "input": []}}
        self.assertEqual(bridge.receiver_bound_panel_frame(json.dumps(allowed), receiver), allowed)
        for frame in (
            {"id": 1, "method": "turn/start", "params": {"threadId": "receiver-b", "input": []}},
            {"id": 1, "method": "config/read", "params": {"threadId": receiver}},
            {"id": 1, "method": "thread/read", "params": {}},
        ):
            with self.subTest(frame=frame), self.assertRaisesRegex(RuntimeError, "RECEIVER_VIOLATION"):
                bridge.receiver_bound_panel_frame(json.dumps(frame), receiver)

    def test_factory_publishes_receipt_before_onboarding(self):
        workspace = self.root / "workspace"
        (workspace / "Launcher/build/desktop-bridges").mkdir(parents=True)
        os.chmod(workspace / "Launcher/build/desktop-bridges", 0o700)
        projection = self.root / "projection.json"
        projection.write_text(json.dumps({"format": "valhall-panel-profile/1", "arguments": [
            "--config", "model=" + json.dumps(SELECTED_MODEL), "--config", 'default_permissions=":workspace-write"',
            "--config", 'approval_policy="on-request"']}))
        calls = []
        case = self

        class Process:
            def __init__(self, pid): self.pid = pid
            def poll(self): return None
            def terminate(self): pass
            def wait(self, timeout=None): return 0

        class Rpc:
            def __init__(self, *_): pass
            def ensure_model(self, model): self.model = model
            def effective_policy(self): return {"model": SELECTED_MODEL, "sandbox_mode": "workspace-write", "approval_policy": "on-request"}
            def start_receiver(self, actual_workspace, model, policy): return "receipt-receiver"
            def start_onboarding(self, receiver, prompt):
                calls.append((receiver, prompt))
                case.assertTrue(list((workspace / "Launcher/build/desktop-bridges").glob("*/receipt.json")))
            def close(self): pass

        request = bridge.BridgeRequest(workspace, "codex", projection, self.root / "runtime.json", "thor", "#4c211b", 9, "onboard", "terminal_tui")
        identities = iter(({"pid": 100, "started_at": "host"}, {"pid": 101, "started_at": "server"}, {"pid": 102, "started_at": "client"}))
        with (mock.patch.object(bridge, "Rpc", Rpc), mock.patch.object(bridge.subprocess, "Popen", side_effect=[Process(101), Process(102)]),
              mock.patch.object(bridge, "process_identity", side_effect=lambda pid: next(identities) if pid in {os.getpid(), 101, 102} else {"pid": pid, "started_at": "unknown"}),
              mock.patch.object(bridge, "start_supervisor", return_value=Process(103)), mock.patch.object(bridge, "endpoint_url", return_value="ws://127.0.0.1:4444"),
              mock.patch.object(bridge, "live", return_value=True), mock.patch.object(bridge, "private_file", wraps=bridge.private_file)):
            with self.assertRaises(SystemExit) as exit:
                bridge.BridgeFactory.create(request)
        self.assertEqual(exit.exception.code, 0)
        self.assertEqual(calls, [("receipt-receiver", "onboard")])
        receipt = json.loads(next((workspace / "Launcher/build/desktop-bridges").glob("*/receipt.json")).read_text())
        self.assertEqual(set(receipt["endpoint"]), {"kind", "url", "capability_token_path", "capability_token_sha256"})
        self.assertEqual(Path(receipt["endpoint"]["capability_token_path"]).parent, next((workspace / "Launcher/build/desktop-bridges").glob("*")).resolve())

    def test_terminal_launch_uses_remote_exact_receiver_resume_form(self):
        workspace = self.root / "terminal-command-workspace"
        (workspace / "Launcher/build/desktop-bridges").mkdir(parents=True)
        os.chmod(workspace / "Launcher/build/desktop-bridges", 0o700)
        projection = self.root / "terminal-command-projection.json"
        projection.write_text(json.dumps({"format": "valhall-panel-profile/1", "arguments": [
            "--config", "model=" + json.dumps(SELECTED_MODEL), "--config", 'default_permissions=":workspace-write"',
            "--config", 'approval_policy="on-request"']}))

        class Process:
            def __init__(self, pid): self.pid = pid
            def poll(self): return None
            def terminate(self): pass
            def wait(self, timeout=None): return 0

        class Rpc:
            def __init__(self, *_): pass
            def ensure_model(self, _): pass
            def effective_policy(self): return {"model": SELECTED_MODEL, "sandbox_mode": "workspace-write", "approval_policy": "on-request"}
            def start_receiver(self, *_): return "fresh-receiver"
            def start_onboarding(self, *_): pass
            def close(self): pass

        request = bridge.BridgeRequest(workspace, "codex", projection, self.root / "runtime.json", "thor", "#4c211b", 9, "onboard", "terminal_tui")
        identities = iter(({"pid": 300, "started_at": "host"}, {"pid": 301, "started_at": "server"}, {"pid": 302, "started_at": "client"}))
        with (mock.patch.object(bridge, "Rpc", Rpc), mock.patch.object(bridge.subprocess, "Popen", side_effect=[Process(301), Process(302)]) as launch,
              mock.patch.object(bridge, "process_identity", side_effect=lambda pid: next(identities) if pid in {os.getpid(), 301, 302} else {"pid": pid, "started_at": "unknown"}),
              mock.patch.object(bridge, "start_supervisor", return_value=Process(303)), mock.patch.object(bridge, "endpoint_url", return_value="ws://127.0.0.1:4446"),
              mock.patch.object(bridge, "live", return_value=True)):
            with self.assertRaises(SystemExit):
                bridge.BridgeFactory.create(request)
        command = launch.call_args_list[1].args[0]
        self.assertEqual(command[:2], ["codex", "--remote"])
        self.assertEqual(command[-2:], ["resume", "fresh-receiver"])

    def test_factory_panel_launch_proves_the_exact_receipt_receiver(self):
        workspace = self.root / "panel-workspace"
        (workspace / "Launcher/build/desktop-bridges").mkdir(parents=True)
        os.chmod(workspace / "Launcher/build/desktop-bridges", 0o700)
        projection = self.root / "panel-projection.json"
        projection.write_text(json.dumps({"format": "valhall-panel-profile/1", "arguments": [
            "--config", "model=" + json.dumps(SELECTED_MODEL), "--config", 'default_permissions=":workspace-write"',
            "--config", 'approval_policy="on-request"']}))
        calls = []

        class Process:
            def __init__(self, pid): self.pid = pid
            def poll(self): return None
            def terminate(self): pass
            def wait(self, timeout=None): return 0

        class Rpc:
            def __init__(self, *_): pass
            def ensure_model(self, _): pass
            def effective_policy(self): return {"model": SELECTED_MODEL, "sandbox_mode": "workspace-write", "approval_policy": "on-request"}
            def start_receiver(self, *_): return "panel-receiver"
            def start_onboarding(self, receiver, _): calls.append(receiver)
            def close(self): pass

        request = bridge.BridgeRequest(workspace, "codex", projection, self.root / "runtime.json", "thor", "#4c211b", 9, "onboard", "panel_client")
        identities = iter(({"pid": 200, "started_at": "host"}, {"pid": 201, "started_at": "server"}, {"pid": 202, "started_at": "panel"}))
        with (mock.patch.object(bridge, "Rpc", Rpc), mock.patch.object(bridge.subprocess, "Popen", return_value=Process(201)),
              mock.patch.object(bridge.BridgeFactory, "_panel_client", return_value=Process(202)) as launch,
              mock.patch.object(bridge.BridgeFactory, "_wait_for_panel_client", return_value={"pid": 202, "started_at": "panel"}) as prove,
              mock.patch.object(bridge, "process_identity", side_effect=lambda pid: next(identities) if pid in {os.getpid(), 201, 202} else {"pid": pid, "started_at": "unknown"}),
              mock.patch.object(bridge, "start_supervisor", return_value=Process(203)), mock.patch.object(bridge, "endpoint_url", return_value="ws://127.0.0.1:4445"),
              mock.patch.object(bridge, "live", return_value=True)):
            with self.assertRaises(SystemExit) as exit:
                bridge.BridgeFactory.create(request)
        self.assertEqual(exit.exception.code, 0)
        self.assertEqual(calls, ["panel-receiver"])
        self.assertEqual(launch.call_args.args[-1], "panel-receiver")
        self.assertEqual(prove.call_args.args[-1], "panel-receiver")

    def test_supervisor_retires_exact_children_after_host_death(self):
        host = self.child("/bin/sleep", "60")
        server = self.child("/bin/sleep", "60")
        tui = self.child("/bin/sleep", "60")
        bridge_dir = self.root / "bridge"
        bridge_dir.mkdir(mode=0o700)
        bridge.private_file(bridge_dir / "capability.token", "private\n")
        watcher = self.child(sys.executable, str(ROOT / "desktop_bridge.py"), "--supervise",
                             "--host", json.dumps(bridge.process_identity(host.pid)),
                             "--server", json.dumps(bridge.process_identity(server.pid)),
                             "--client", json.dumps(bridge.process_identity(tui.pid)), "--bridge", str(bridge_dir))
        host.kill()
        self.wait_for_exit(host)
        self.wait_for_exit(server)
        self.wait_for_exit(tui)
        self.wait_for_exit(watcher)
        retirement = json.loads((bridge_dir / "retired.json").read_text())
        self.assertEqual(retirement["reason"], "host_lifetime_ended")
        self.assertFalse((bridge_dir / "capability.token").exists())

    def test_host_retirement_invalidates_token_after_client_exit(self):
        bridge_dir = self.root / "retired-bridge"
        bridge_dir.mkdir(mode=0o700)
        token = bridge_dir / "capability.token"
        bridge.private_file(token, "private\n")
        host = {"pid": 999991, "started_at": "never"}
        server = {"pid": 999992, "started_at": "never"}
        client = {"pid": 999993, "started_at": "never"}
        bridge.retire(host, server, client, bridge_dir, reason="bridge_host_exited")
        bridge.retire(host, server, client, bridge_dir, reason="bridge_host_exited")
        self.assertFalse(token.exists())
        self.assertEqual(json.loads((bridge_dir / "retired.json").read_text())["reason"], "bridge_host_exited")

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
