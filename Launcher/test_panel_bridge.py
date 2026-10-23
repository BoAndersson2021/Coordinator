"""Bounded Valhall/PANEL front-door regressions; never create a model thread."""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import select
import subprocess
import tempfile
import time
import tomllib
import unittest

ROOT = Path(__file__).resolve().parent
WORKSPACE = Path('/Users/boandersson/Desktop/CodeExp2')
spec = importlib.util.spec_from_file_location("launcher_build", ROOT / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class NativeClient:
    def __init__(self, executable):
        self.process = subprocess.Popen([str(executable), "--panel-agent"], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.buffer = b""
        self.number = 0
        self.receipt = self.read()

    def read(self):
        deadline = time.monotonic() + 20
        while b"\n" not in self.buffer:
            if time.monotonic() >= deadline:
                raise TimeoutError("native bridge reply")
            if select.select([self.process.stdout], [], [], 0.25)[0]:
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("native bridge closed")
                self.buffer += chunk
        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line)

    def call(self, method, params):
        self.number += 1
        self.process.stdin.write(json.dumps({"id": self.number, "method": method, "params": params}).encode() + b"\n")
        self.process.stdin.flush()
        while True:
            reply = self.read()
            if reply.get("id") == self.number and "method" not in reply:
                if "error" in reply:
                    raise RuntimeError(reply["error"])
                return reply["result"]

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)
            raise AssertionError("owned native server did not stop after stdin EOF")
        finally:
            self.process.stdout.close()


class PanelBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="valhall-panel-test-")
        cls.app = Path(cls.temporary.name) / "CodeExp2.app"
        cls.resources = cls.app / "Contents/Resources"
        cls.resources.mkdir(parents=True)
        cls.executable = cls.app / "Contents/MacOS/CodeExp2"
        cls.executable.parent.mkdir()
        cls.profile = (ROOT / "valhalla.config.toml").read_bytes()
        (cls.resources / "valhalla.config.toml").write_bytes(cls.profile)
        cls.projection = build.panel_profile(cls.profile)
        (cls.resources / "valhall-panel-profile.json").write_text(json.dumps(cls.projection))
        (cls.app / "Contents/Info.plist").write_bytes(plistlib.dumps({
            "CFBundleExecutable": "CodeExp2", "CFBundleIdentifier": "local.codeexp2.panel-test",
            "CFBundlePackageType": "APPL"}))
        subprocess.run(["xcrun", "swiftc", "-module-cache-path", str(Path(cls.temporary.name) / "cache"),
                        "-O", "-framework", "AppKit", str(ROOT / "CodeExp2.swift"), "-o", str(cls.executable)],
                       check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_projection_round_trips_exact_canonical_profile(self):
        projection = build.panel_profile(self.profile)
        self.assertEqual(projection["source_sha256"], hashlib.sha256(self.profile).hexdigest())
        assignments = projection["arguments"][1::2]
        self.assertEqual(tomllib.loads("\n".join(assignments)), tomllib.loads(self.profile.decode()))
        special = {'plugins': {'name.with.dots@host': {'enabled': True}}, 'note': 'a\\b\n"c'}
        self.assertEqual(tomllib.loads('value=' + build.toml_value(special))['value'], special)
        with self.assertRaises(ValueError):
            build.toml_value(float('nan'))

    def test_native_profile_identity_and_shared_claim_release(self):
        clients = []
        try:
            for _ in range(2):
                client = NativeClient(self.executable)
                clients.append(client)
                self.assertEqual(client.receipt["method"], "valhall/launch")
                receipt = client.receipt["params"]
                self.assertEqual(receipt["format"], "valhall-panel-launch/1")
                self.assertEqual(receipt["pid"], client.process.pid)
                self.assertEqual(receipt["workspace"], str(WORKSPACE))
                self.assertIn('Launcher-assigned instance alias: ' + receipt['alias'], receipt['onboard_prompt'])
                self.assertTrue(receipt['onboard_prompt'].startswith('onboard\n'))
                client.call("initialize", {"clientInfo": {"name": "valhall_panel_bridge_test", "version": "1"},
                                           "capabilities": {"experimentalApi": True}})
                actual = client.call("config/read", {"cwd": str(WORKSPACE), "includeLayers": False})['config']
                def compare(a, expected):
                    if isinstance(expected, dict):
                        for k, v in expected.items():
                            self.assertIn(k, a)
                            compare(a[k], v)
                    else:
                        self.assertEqual(a, expected)
                compare(actual, tomllib.loads(self.profile.decode()))
                self.assertEqual(actual['sandbox_mode'], 'danger-full-access')
            aliases = [c.receipt['params']['alias'] for c in clients]
            self.assertNotEqual(*aliases)
            names = ['Odin', 'Thor', 'Freya', 'Loki', 'Tyr', 'Heimdall', 'Balder', 'Frigg', 'Njord', 'Freyr', 'Skadi', 'Idunn']
            alias = aliases[0].split('-')
            slot = names.index(alias[0]) + (int(alias[1]) - 1) * 12 if len(alias) == 2 else names.index(alias[0])
            claim = WORKSPACE / 'Launcher/build/instance-claims' / f'{slot}.lock'
            with claim.open('r+') as lock:
                with self.assertRaises(BlockingIOError):
                    fcntl.lockf(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                clients[0].close()
                clients.pop(0)
                fcntl.lockf(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.lockf(lock, fcntl.LOCK_UN)
        finally:
            for client in clients:
                client.close()

    def test_stale_projection_and_terminal_boundaries_fail_before_launch(self):
        path = self.resources / 'valhall-panel-profile.json'
        try:
            stale = dict(self.projection, source_sha256='0' * 64)
            path.write_text(json.dumps(stale))
            result = subprocess.run([str(self.executable), '--panel-agent'], input=b'', capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b'')
            self.assertIn(b'projection', result.stderr)
        finally:
            path.write_text(json.dumps(self.projection))
        for arguments in (['--terminal'], ['--panel-agent', 'unrelated-path']):
            result = subprocess.run([str(self.executable)] + arguments, input=b'', capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(b'valhall/launch', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
