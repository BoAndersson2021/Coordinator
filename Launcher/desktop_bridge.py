#!/usr/bin/env python3
"""Create and supervise one capability-bound Desktop TUI bridge."""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import time
import tomllib
import uuid

from websockets.sync.client import connect


RUNTIME_FORMAT = "codeexp2-desktop-bridge-runtime/1"
RECEIPT_FORMAT = "codeexp2-desktop-session-receipt/2"
BRIDGE_BINDING_FORMAT = "codeexp2-desktop-session-bridge/2"
TOKEN_ENVIRONMENT = "CODEXP2_DESKTOP_BRIDGE_CAPABILITY"


def fail(message):
    raise RuntimeError(message)


def private_directory(path, existing=False):
    path.mkdir(mode=0o700, parents=True, exist_ok=existing)
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        fail("Desktop bridge directory is not private")
    return path.resolve()


def private_file(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())


def write_private(path, value):
    private_file(path, json.dumps(value, sort_keys=True) + "\n")


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def runtime_identity():
    import websockets
    from websockets.sync import client as sync_client
    distribution = importlib.metadata.distribution("websockets")
    package = Path(websockets.__file__).resolve().parent
    if distribution.version != "17.2" or websockets.__version__ != distribution.version:
        fail("Desktop bridge transport version differs from reviewed pin")
    if package != Path(distribution.locate_file("websockets")).resolve() or Path(sync_client.__file__).resolve() != package / "sync/client.py":
        fail("Desktop bridge transport is shadowed")
    files = {str(path.relative_to(package)): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(package.rglob("*")) if path.is_file() and path.suffix in {".py", ".so", ".dylib"}}
    if "sync/client.py" not in files:
        fail("Desktop bridge transport is incomplete")
    return {"format": RUNTIME_FORMAT, "distribution": "websockets", "version": distribution.version,
            "files_sha256": sha256_text(json.dumps(files, sort_keys=True, separators=(",", ":")))}


def verify_runtime(manifest_path):
    try:
        manifest = json.loads(Path(manifest_path).read_text())
    except (OSError, ValueError) as error:
        raise RuntimeError("Desktop bridge runtime manifest is unavailable") from error
    if manifest != runtime_identity():
        fail("Desktop bridge interpreter or transport bytes differ from the bundled reviewed runtime")


def process_identity(pid):
    result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "pid=", "-o", "lstart="], text=True,
                            capture_output=True, timeout=3)
    fields = result.stdout.split()
    if result.returncode != 0 or len(fields) != 6 or not fields[0].isdigit() or int(fields[0]) != pid:
        fail("Desktop bridge process lifetime cannot be observed")
    return {"pid": pid, "started_at": " ".join(fields[1:])}


def process_is_live(identity):
    try:
        return process_identity(identity["pid"]) == identity
    except (KeyError, RuntimeError, ValueError):
        return False


def reserve_loopback_port():
    reservation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        reservation.bind(("127.0.0.1", 0))
        return reservation.getsockname()[1]
    finally:
        reservation.close()


def endpoint_url():
    # A possible port race fails closed: the server still requires the capability
    # token before it accepts an RPC, and the bridge verifies the real endpoint.
    return "ws://127.0.0.1:" + str(reserve_loopback_port())


class Rpc:
    def __init__(self, endpoint, capability):
        self.connection = connect(endpoint + "/", legacy=True, open_timeout=2, close_timeout=2,
                                  max_size=1024 * 1024, max_queue=16,
                                  additional_headers={"Authorization": "Bearer " + capability})
        self.sequence = 0
        self.call("initialize", {"clientInfo": {"name": "codeexp2_desktop_bridge", "version": "2"},
                                  "capabilities": {"experimentalApi": True}})
        self.connection.send(json.dumps({"method": "initialized", "params": {}}))

    def call(self, method, params):
        self.sequence += 1
        request_id = str(self.sequence)
        self.connection.send(json.dumps({"id": request_id, "method": method, "params": params}))
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            message = json.loads(self.connection.recv(timeout=max(.01, deadline - time.monotonic())))
            if message.get("id") != request_id:
                continue
            if "error" in message:
                fail(json.dumps(message["error"], sort_keys=True))
            return message["result"]
        fail("Desktop bridge RPC timed out: " + method)

    def close(self):
        self.connection.close()

    def ensure_model(self, selected):
        cursor = None
        for _ in range(8):
            page = self.call("model/list", {"cursor": cursor, "limit": 100, "includeHidden": True})
            models = page.get("data")
            if not isinstance(models, list):
                fail("Desktop bridge model admission returned invalid data")
            if any(isinstance(model, dict) and selected in {model.get("model"), model.get("id")} for model in models):
                return
            cursor = page.get("nextCursor")
            if cursor is None:
                break
            if not isinstance(cursor, str) or not cursor:
                fail("Desktop bridge model admission returned invalid pagination")
        fail("Desktop bridge selected model is unavailable: " + selected)

    def start_receiver(self, workspace, selected_model):
        result = self.call("thread/start", {"cwd": str(workspace), "model": selected_model,
                                             "sandbox": "danger-full-access", "approvalPolicy": "never",
                                             "approvalsReviewer": "user", "ephemeral": False})
        thread = result.get("thread") if isinstance(result, dict) else None
        if not isinstance(thread, dict) or not isinstance(thread.get("id"), str) or not thread["id"] or thread.get("cwd") != str(workspace):
            fail("Desktop bridge did not create its exact receiver")
        return thread["id"]

    def start_onboarding(self, receiver, prompt):
        self.call("turn/start", {"threadId": receiver, "input": [{"type": "text", "text": prompt}]})


def projection(path):
    try:
        result = json.loads(Path(path).read_text())
        arguments = result.get("arguments")
        if result.get("format") != "valhall-panel-profile/1" or not isinstance(arguments, list) or not arguments:
            fail("Desktop bridge profile projection is missing or stale")
        if len(arguments) % 2 or any(arguments[index] != "--config" or not isinstance(arguments[index + 1], str)
                                   for index in range(0, len(arguments), 2)):
            fail("Desktop bridge profile projection is invalid")
        config = tomllib.loads("\n".join(arguments[1::2]))
        model = config.get("model")
        if not isinstance(model, str) or not model:
            fail("Desktop bridge profile has no selected model")
        return arguments, model
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        raise RuntimeError("Desktop bridge profile projection is invalid") from error


def live(process):
    return process is not None and process.poll() is None


def terminate(process):
    if not live(process):
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def supervise(host, server, tui, bridge):
    # This process remains alive when the host is SIGKILLed. It only retires the
    # exact processes named in the receipt after the recorded host lifetime ends.
    while process_is_live(host):
        time.sleep(.15)
    for identity in (tui, server):
        if process_is_live(identity):
            try:
                os.kill(identity["pid"], signal.SIGTERM)
            except ProcessLookupError:
                pass
    capability = bridge / "capability.token"
    if capability.is_file() and not capability.is_symlink():
        capability.unlink()
    retired = bridge / "retired.json"
    try:
        write_private(retired, {"format": "codeexp2-desktop-session-retirement/1", "reason": "host_lifetime_ended",
                                "host": host, "server": server, "tui": tui,
                                "retired_at_utc": datetime.now(timezone.utc).isoformat()})
    except (OSError, RuntimeError):
        pass


def start_supervisor(host, server, tui, bridge):
    return subprocess.Popen([sys.executable, __file__, "--supervise", "--host", json.dumps(host),
                             "--server", json.dumps(server), "--tui", json.dumps(tui), "--bridge", str(bridge)],
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            close_fds=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace")
    parser.add_argument("--codex")
    parser.add_argument("--profile-projection")
    parser.add_argument("--runtime-manifest")
    parser.add_argument("--alias")
    parser.add_argument("--color")
    parser.add_argument("--claim-fd", type=int)
    parser.add_argument("--prompt")
    parser.add_argument("--supervise", action="store_true")
    parser.add_argument("--host")
    parser.add_argument("--server")
    parser.add_argument("--tui")
    parser.add_argument("--bridge")
    parser.add_argument("--verify-runtime", action="store_true")
    args = parser.parse_args()
    if args.verify_runtime:
        if not args.runtime_manifest:
            fail("Desktop bridge runtime manifest is required")
        verify_runtime(args.runtime_manifest)
        return
    if args.supervise:
        if not all((args.host, args.server, args.tui, args.bridge)):
            fail("Desktop bridge supervisor inputs are incomplete")
        supervise(json.loads(args.host), json.loads(args.server), json.loads(args.tui), Path(args.bridge))
        return
    if not all((args.workspace, args.codex, args.profile_projection, args.runtime_manifest, args.alias, args.color,
                args.claim_fd, args.prompt)):
        fail("Desktop bridge launch inputs are incomplete")
    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir() or not Path(args.codex).is_file() or not Path(args.profile_projection).is_file():
        fail("Desktop bridge launch inputs are unavailable")
    if args.claim_fd <= 2 or fcntl.fcntl(args.claim_fd, fcntl.F_GETFD) < 0:
        fail("Desktop bridge did not inherit the instance claim")
    verify_runtime(args.runtime_manifest)
    arguments, selected_model = projection(args.profile_projection)
    root = private_directory(workspace / "Launcher/build/desktop-bridges", existing=True)
    bridge = private_directory(root / (args.alias + "-" + uuid.uuid4().hex))
    capability = os.urandom(32).hex()
    capability_path = bridge / "capability.token"
    private_file(capability_path, capability + "\n")
    endpoint = endpoint_url()
    server_log = open(bridge / "app-server.log", "x", encoding="utf-8")
    os.chmod(server_log.name, 0o600)
    host = process_identity(os.getpid())
    server = subprocess.Popen([args.codex, "app-server", "--listen", endpoint, "--ws-auth", "capability-token",
                               "--ws-token-file", str(capability_path), *arguments], cwd=workspace, stdin=subprocess.DEVNULL,
                              stdout=server_log, stderr=subprocess.STDOUT, close_fds=True)
    rpc = None
    tui = None
    supervisor = None
    try:
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if not live(server):
                fail("Desktop bridge app server exited before becoming available")
            try:
                rpc = Rpc(endpoint, capability)
                break
            except Exception:
                time.sleep(.05)
        if rpc is None:
            fail("Desktop bridge app server did not become available")
        # Admission precedes receiver creation. The bridge owns the exact
        # receiver before the TUI starts, instead of inferring its first event.
        rpc.ensure_model(selected_model)
        receiver = rpc.start_receiver(workspace, selected_model)
        environment = dict(os.environ)
        environment[TOKEN_ENVIRONMENT] = capability
        tui = subprocess.Popen([args.codex, "resume", "--remote", endpoint, "--remote-auth-token-env", TOKEN_ENVIRONMENT,
                                "--no-alt-screen", receiver], cwd=workspace, pass_fds=(args.claim_fd,),
                               close_fds=True, env=environment)
        server_identity = process_identity(server.pid)
        tui_identity = process_identity(tui.pid)
        issued = datetime.now(timezone.utc)
        receipt = {"format": RECEIPT_FORMAT, "bridge_id": uuid.uuid4().hex, "alias": args.alias, "color": args.color,
                   "workspace": str(workspace), "endpoint": {"kind": "loopback-websocket-capability", "url": endpoint,
                   "capability_token_path": str(capability_path), "capability_token_sha256": sha256_text(capability)},
                   "receiver_id": receiver, "processes": {"host": host, "server": server_identity, "tui": tui_identity},
                   "issued_at_utc": issued.isoformat(), "expires_at_utc": (issued + timedelta(hours=8)).isoformat(),
                   "pre_receipt_phase": "none"}
        supervisor = start_supervisor(host, server_identity, tui_identity, bridge)
        write_private(bridge / "receipt.json", receipt)
        print(json.dumps({"method": "codeexp2/desktopSessionBridge", "params": receipt}, sort_keys=True), flush=True)
        # Receipt publication precedes the only onboarding turn. No arbitrary
        # turn can be sent by this bridge before that boundary.
        rpc.start_onboarding(receiver, args.prompt)
        rpc.close()
        rpc = None
        raise SystemExit(tui.wait())
    except BaseException:
        if rpc is not None:
            rpc.close()
        terminate(tui)
        terminate(server)
        server_log.close()
        raise
    finally:
        # The supervisor observes the host exit and performs idempotent stale
        # retirement. Keep it out of the session's claim/process tree.
        if supervisor is not None and live(supervisor):
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("CodeExp2 desktop bridge: " + str(error), file=sys.stderr)
        raise SystemExit(1)
