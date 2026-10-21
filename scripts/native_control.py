"""Bounded CodeExp2 native control. Effects are limited to owned diagnostics."""
import argparse
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import time
from urllib.parse import urlparse
import uuid

from native_evidence import BUDGETS, evaluate, require, strict_json, safe_read

ROOT = Path(__file__).resolve().parents[1]
READ = {"initialize", "thread/read", "thread/turns/list", "thread/backgroundTerminals/list"}
EFFECT = {"thread/start", "thread/resume", "thread/archive", "thread/unsubscribe", "turn/start", "turn/interrupt", "command/exec"}
FINAL = {"completed", "failed", "interrupted"}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def private_dir(path, new=False):
    path = Path(path).absolute()
    if new:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.mkdir(mode=0o700)
    require(path.is_dir() and not path.is_symlink(), "Expected owned private directory")
    s = path.stat()
    require(s.st_uid == os.getuid() and stat.S_IMODE(s.st_mode) == 0o700, "Run directory must be owner-only")
    return path.resolve()


def atomic(path, value):
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as file:
            file.write(json.dumps(value, indent=2, allow_nan=False) + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temp.exists():
            temp.unlink()


def load(path):
    return strict_json(Path(path).read_text())


def load_binding(path):
    value = load(path)
    if value.get("format") == "codeexp2-owned-diagnostic-binding/2":
        expected = {"format", "repository", "socket_path", "authority_reference", "receiver_id"}
        require(set(value) == expected, "Invalid owned-diagnostic binding fields/version")
        for key in expected - {"receiver_id"}:
            require(isinstance(value[key], str) and bool(value[key].strip()), "Missing binding " + key)
        require(Path(value["repository"]).is_absolute() and Path(value["repository"]).resolve() == ROOT, "Binding must name this canonical CodeExp2 workspace")
        require(Path(value["socket_path"]).is_absolute(), "Socket path must be absolute")
        require(value["receiver_id"] is None or isinstance(value["receiver_id"], str), "Invalid receiver")
        return value
    if value.get("format") == "codeexp2-desktop-session-bridge/2":
        expected = {"format", "receipt_path", "authority_reference"}
        require(set(value) == expected and all(isinstance(value[key], str) and value[key].strip() for key in expected - {"format"}), "DESKTOP_BRIDGE_BINDING_INVALID: invalid desktop bridge binding")
        receipt_path = Path(value["receipt_path"])
        require(receipt_path.is_absolute() and receipt_path.is_file() and not receipt_path.is_symlink(), "DESKTOP_BRIDGE_RECEIPT_MISSING: receipt is missing or redirected")
        info = receipt_path.stat()
        require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o600, "DESKTOP_BRIDGE_CUSTODY_INVALID: receipt is not private")
        bridge_root = ROOT / "Launcher/build/desktop-bridges"
        require(receipt_path.parent.parent == bridge_root and receipt_path.parent.is_dir() and not receipt_path.parent.is_symlink(), "DESKTOP_BRIDGE_CUSTODY_INVALID: receipt escaped its host directory")
        bridge_info = receipt_path.parent.stat()
        require(bridge_info.st_uid == os.getuid() and stat.S_IMODE(bridge_info.st_mode) == 0o700, "DESKTOP_BRIDGE_CUSTODY_INVALID: bridge directory is not private")
        receipt = load(receipt_path)
        receipt_fields = {"format", "bridge_id", "alias", "color", "workspace", "endpoint", "receiver_id", "processes", "issued_at_utc", "expires_at_utc", "pre_receipt_phase"}
        require(set(receipt) == receipt_fields and receipt["format"] == "codeexp2-desktop-session-receipt/2", "DESKTOP_BRIDGE_RECEIPT_INVALID: invalid receipt")
        for key in receipt_fields - {"format", "endpoint", "processes"}:
            require(isinstance(receipt[key], str) and receipt[key].strip(), "DESKTOP_BRIDGE_RECEIPT_INVALID: missing receipt " + key)
        require(receipt["pre_receipt_phase"] == "none", "DESKTOP_BRIDGE_ORDER_INVALID: work preceded receipt publication")
        endpoint = receipt["endpoint"]
        endpoint_fields = {"kind", "url", "capability_token_path", "capability_token_sha256"}
        require(isinstance(endpoint, dict) and set(endpoint) == endpoint_fields and endpoint["kind"] == "loopback-websocket-capability", "DESKTOP_BRIDGE_ENDPOINT_INVALID: invalid endpoint")
        require(all(isinstance(endpoint[key], str) and endpoint[key] for key in endpoint_fields - {"kind"}), "DESKTOP_BRIDGE_ENDPOINT_INVALID: invalid endpoint fields")
        parsed = urlparse(endpoint["url"])
        require(parsed.scheme == "ws" and parsed.hostname == "127.0.0.1" and parsed.port and not parsed.params and not parsed.query and not parsed.fragment and parsed.path in {"", "/"}, "DESKTOP_BRIDGE_ENDPOINT_INVALID: endpoint is not a loopback WebSocket")
        token_path = Path(endpoint["capability_token_path"])
        require(token_path.parent == receipt_path.parent and token_path.is_file() and not token_path.is_symlink(), "DESKTOP_BRIDGE_CAPABILITY_INVALID: capability is missing or redirected")
        token_info = token_path.stat()
        require(token_info.st_uid == os.getuid() and stat.S_IMODE(token_info.st_mode) == 0o600 and token_info.st_size <= 1024, "DESKTOP_BRIDGE_CAPABILITY_INVALID: capability is not private")
        capability = token_path.read_text()
        require(capability.endswith("\n") and len(capability.strip()) >= 32 and hashlib.sha256(capability.strip().encode()).hexdigest() == endpoint["capability_token_sha256"], "DESKTOP_BRIDGE_CAPABILITY_INVALID: capability differs from receipt")
        processes = receipt["processes"]
        require(isinstance(processes, dict) and set(processes) == {"host", "server", "tui"}, "DESKTOP_BRIDGE_PROCESS_INVALID: invalid process set")
        for name, identity in processes.items():
            require(isinstance(identity, dict) and set(identity) == {"pid", "started_at"} and isinstance(identity["pid"], int) and identity["pid"] > 1 and isinstance(identity["started_at"], str) and identity["started_at"], "DESKTOP_BRIDGE_PROCESS_INVALID: invalid receipt process " + name)
        try:
            issued = datetime.fromisoformat(receipt["issued_at_utc"])
            expires = datetime.fromisoformat(receipt["expires_at_utc"])
        except ValueError as error:
            raise ValueError("DESKTOP_BRIDGE_RECEIPT_INVALID: invalid receipt expiry") from error
        current = datetime.now(timezone.utc)
        require(issued.tzinfo is not None and expires.tzinfo is not None and issued <= current < expires and expires - issued <= timedelta(hours=8), "DESKTOP_BRIDGE_RECEIPT_EXPIRED: receipt is expired or clock is outside the eight-hour validity window")
        require(Path(receipt["workspace"]).resolve() == ROOT, "DESKTOP_BRIDGE_WORKSPACE_MISMATCH: workspace differs")
        require(process_matches(processes["server"], ["app-server", "--listen", endpoint["url"], "--ws-auth", "capability-token", "--ws-token-file", str(token_path)]), "DESKTOP_BRIDGE_PROCESS_STALE: server is not live")
        require(process_matches(processes["host"], ["desktop_bridge.py", "--claim-fd"]), "DESKTOP_BRIDGE_PROCESS_STALE: host is not live")
        require(isinstance(receipt["receiver_id"], str) and receipt["receiver_id"] and not any(character.isspace() for character in receipt["receiver_id"]), "DESKTOP_BRIDGE_RECEIPT_INVALID: receiver is invalid")
        require(process_matches(processes["tui"], ["--remote", endpoint["url"], "--remote-auth-token-env"], receipt["receiver_id"]), "DESKTOP_BRIDGE_PROCESS_STALE: TUI is not live")
        return {"format": value["format"], "repository": receipt["workspace"], "endpoint": endpoint,
                "authority_reference": value["authority_reference"], "receiver_id": receipt["receiver_id"],
                "bridge_id": receipt["bridge_id"], "alias": receipt["alias"]}
    raise ValueError("NO_SUPPORTED_DESKTOP_SESSION_BRIDGE: use a current codeexp2-desktop-session-bridge/2 receipt; aliases, legacy bindings and historical sessions cannot attach a Desktop TUI")


def process_matches(identity, fragments, exact_final_argument=None):
    """Confirm both lifetime and route inputs; PID alone can be reused."""
    result = subprocess.run(["/bin/ps", "-p", str(identity["pid"]), "-o", "pid=", "-o", "lstart=", "-o", "command="], text=True,
                            capture_output=True, timeout=3)
    fields = result.stdout.split()
    if result.returncode != 0 or len(fields) < 7 or not fields[0].isdigit() or int(fields[0]) != identity["pid"]:
        return False
    started_at = " ".join(fields[1:6])
    command = " ".join(fields[6:])
    return (started_at == identity["started_at"] and command and all(fragment in command for fragment in fragments)
            and (exact_final_argument is None or command.split()[-1] == exact_final_argument))


def binding_endpoint(binding):
    return binding.get("endpoint") or {"kind": "owned-unix-socket", "path": binding["socket_path"]}


def endpoint_label(binding):
    endpoint = binding_endpoint(binding)
    return endpoint.get("path") or endpoint["url"]


def endpoint_identity(endpoint):
    if endpoint["kind"] == "owned-unix-socket":
        s = Path(endpoint["path"]).stat()
        require(stat.S_ISSOCK(s.st_mode) and s.st_uid == os.getuid(), "Endpoint is not an owned Unix socket")
        return {"path": str(Path(endpoint["path"]).resolve()), "uid": s.st_uid, "device": s.st_dev, "inode": s.st_ino}
    if endpoint["kind"] == "loopback-websocket-capability":
        return {"url": endpoint["url"], "capability_token_sha256": endpoint["capability_token_sha256"]}
    raise ValueError("Unsupported endpoint identity")


def transport_identity():
    """Measure the imported implementation, not merely a requirements declaration."""
    import websockets
    from websockets.sync import client as sync_client
    dist = importlib.metadata.distribution("websockets")
    package = Path(websockets.__file__).resolve().parent
    require(dist.version == "17.2" and websockets.__version__ == dist.version, "Transport version differs from reviewed pin")
    require(package == Path(dist.locate_file("websockets")).resolve() and Path(sync_client.__file__).resolve() == package / "sync/client.py", "Shadowed transport implementation")
    files = {str(p.relative_to(package)): sha(p) for p in sorted(package.rglob("*")) if p.is_file() and p.suffix in {".py", ".so", ".dylib"}}
    require("sync/client.py" in files, "Missing measured transport implementation")
    return {"distribution": "websockets", "version": dist.version, "package": str(package), "files": files}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def remaining(deadline, ceiling):
    if deadline is None:
        return ceiling
    left = deadline - time.monotonic()
    require(left > 0, "Overall operation deadline exhausted; outcome unresolved")
    return min(ceiling, left)


def open_wire(endpoint, limits):
    try:
        from websockets.sync.client import connect, unix_connect
    except ImportError as error:
        raise RuntimeError("Install scripts/requirements-native-control.txt in an authorized environment") from error
    if endpoint["kind"] == "owned-unix-socket":
        return unix_connect(path=str(endpoint["path"]), uri="ws://localhost", legacy=True,
                            open_timeout=limits["connect_seconds"], close_timeout=2,
                            max_size=limits["frame_bytes"], max_queue=limits["queued_events"])
    if endpoint["kind"] == "loopback-websocket-capability":
        token = Path(endpoint["capability_token_path"]).read_text().strip()
        require(len(token) >= 32 and hashlib.sha256(token.encode()).hexdigest() == endpoint["capability_token_sha256"], "DESKTOP_BRIDGE_CAPABILITY_INVALID: capability changed before connection")
        return connect(endpoint["url"] + "/", legacy=True, open_timeout=limits["connect_seconds"], close_timeout=2,
                       max_size=limits["frame_bytes"], max_queue=limits["queued_events"],
                       additional_headers={"Authorization": "Bearer " + token})
    raise ValueError("Unsupported endpoint transport")


class Client:
    def __init__(self, binding, evidence, mode="observe", factory=open_wire, identity=endpoint_identity, deadline=None):
        self.deadline = deadline
        self.binding = binding
        self.evidence = private_dir(evidence)
        self.mode = mode
        self.receiver = binding.get("receiver_id")
        self.workspace = binding["repository"]
        self.pending = deque()
        self.sequence = 0
        self.generation = uuid.uuid4().hex
        self.limits = dict(BUDGETS)
        self.bytes = sum(p.stat().st_size for p in self.evidence.glob("events-*.jsonl"))
        self.ws = None
        self.closed = False
        self.log = None
        self.identity = identity
        self.transport = transport_identity() if factory is open_wire else {"fixture": True}
        self.endpoint = binding_endpoint(binding)
        self.backend = identity(self.endpoint)
        self.log_path = self.evidence / ("events-" + self.generation + ".jsonl")
        try:
            self.log = os.fdopen(os.open(self.log_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w")
            limits = {**self.limits, "connect_seconds": remaining(self.deadline, self.limits["connect_seconds"])}
            self.ws = factory(self.endpoint, limits)
            require(identity(self.endpoint) == self.backend, "Endpoint changed during connection")
            self.initialized = self.request("initialize", {"clientInfo": {"name": "codeexp2_native_control", "version": "1.0"}, "capabilities": {"experimentalApi": True}})
            require(isinstance(self.initialized, dict) and isinstance(self.initialized.get("userAgent"), str), "Incompatible initialize result")
            self.send({"method": "initialized", "params": {}})
        except BaseException:
            self.close()
            raise

    def trace(self, direction, value):
        line = json.dumps({"direction": direction, "generation": self.generation, "producer_pid": os.getpid(), "backend": self.backend, "transport_sha256": digest(self.transport), "message": value}, allow_nan=False) + "\n"
        self.bytes += len(line.encode())
        require(self.bytes <= self.limits["evidence_bytes"], "Evidence budget exceeded; collection incomplete")
        self.log.write(line)
        self.log.flush()

    def send(self, message):
        remaining(self.deadline, self.limits["rpc_seconds"])
        method = message.get("method")
        if method is not None:
            require(method == "initialized" or method in READ or (self.mode == "diagnostic" and method in EFFECT), "Wire method outside client scope")
            if (method.startswith("thread/") and method != "thread/start") or method.startswith("turn/"):
                require(self.receiver and message.get("params", {}).get("threadId") == self.receiver, "Wrong wire receiver")
        else:
            require(self.mode == "diagnostic" and set(message) == {"id", "result"} and message["result"] in [{"decision": "accept"}, {"decision": "decline"}], "Unscoped wire response")
        self.trace("sent", message)
        self.ws.send(json.dumps(message, allow_nan=False))

    def receive(self, timeout):
        raw = self.ws.recv(timeout=remaining(self.deadline, timeout))
        require(len(raw.encode() if isinstance(raw, str) else raw) <= self.limits["frame_bytes"], "Frame budget exceeded")
        message = strict_json(raw)
        require(isinstance(message, dict), "Protocol message must be object")
        self.trace("received", message)
        return message

    def request(self, method, params):
        require(method in READ or (self.mode == "diagnostic" and method in EFFECT), "Method outside client scope")
        if method.startswith("thread/") and method not in {"thread/start"} or method.startswith("turn/"):
            require(self.receiver and params.get("threadId") == self.receiver, "Wrong receiver")
        if method == "thread/start":
            require(self.receiver is None and params.get("cwd") == self.workspace, "Thread creation scope mismatch")
            require(params.get("sandbox") == "read-only" and params.get("approvalPolicy") == "on-request" and params.get("approvalsReviewer") == "user" and params.get("ephemeral") is False, "Unsupported diagnostic settings")
        if method == "command/exec":
            require(params.get("cwd") == self.workspace, "Command workspace mismatch")
            require(params.get("command") == ["/usr/bin/touch", str(Path(self.workspace) / "ordinary.txt")], "Command outside disposable ordinary probe")
            require(params.get("sandboxPolicy") == {"type": "workspaceWrite", "writableRoots": [self.workspace], "networkAccess": False}, "Ordinary probe permissions changed")
        remaining(self.deadline, self.limits["rpc_seconds"])
        self.sequence += 1
        request_id = self.generation + ":" + str(self.sequence)
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + remaining(self.deadline, self.limits["rpc_seconds"])
        while time.monotonic() < deadline:
            message = self.receive(max(.01, deadline-time.monotonic()))
            if message.get("id") == request_id and ("result" in message or "error" in message):
                if "error" in message:
                    raise RuntimeError(json.dumps(message["error"]))
                return message["result"]
            require(len(self.pending) < self.limits["queued_events"], "Event queue overflow; collection incomplete")
            self.pending.append(message)
        raise TimeoutError(method)

    def event(self, timeout=1):
        return self.pending.popleft() if self.pending else self.receive(timeout)

    def check_backend(self, state):
        require(self.backend == state["backend"] == self.identity(self.endpoint), "Connected backend differs from durable owner; no effects")
        if "transport" in state:
            require(self.transport == state["transport"], "Transport implementation changed; no effects")

    def verify(self):
        thread = self.request("thread/read", {"threadId": self.receiver, "includeTurns": False})["thread"]
        require(thread.get("id") == self.receiver and thread.get("cwd") == self.workspace, "Receiver/worktree mismatch")
        return thread

    def close(self):
        try:
            if self.ws is not None:
                self.ws.close()
        finally:
            if self.log is not None:
                self.log.close()
            self.closed = True


class Journal:
    def __init__(self, root, create=None):
        self.root = private_dir(root)
        self.path = self.root / "run-state.json"
        self.end_requested = False
        if create is not None:
            require(not self.path.exists(), "Never replay existing run")
            atomic(self.path, create)

    def read(self):
        require(stat.S_IMODE(self.path.stat().st_mode) == 0o600 and not self.path.is_symlink(), "Untrusted journal permissions")
        return load(self.path)

    def write(self, value):
        atomic(self.path, value)

    @contextmanager
    def guard(self, timeout=3):
        state = self.read()
        key = json.dumps([state["backend"], state.get("receiver_id") or state["run_id"]], sort_keys=True)
        locks = ROOT / "Launcher/build/native-control-state"
        locks.mkdir(mode=0o700, parents=True, exist_ok=True)
        private_dir(locks)
        fd = os.open(locks / (hashlib.sha256(key.encode()).hexdigest() + ".lock"), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            deadline = time.monotonic() + timeout
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    require(time.monotonic() < deadline, "Operation lock busy")
                    time.sleep(.01)
            custody = locks / (hashlib.sha256(key.encode()).hexdigest() + ".json")
            if custody.exists():
                require(load(custody)["owner_run"] == str(self.root), "Receiver already owned by another run")
            else:
                atomic(custody, {"owner_run": str(self.root), "backend": state["backend"], "receiver_id": state.get("receiver_id")})
            yield self.read()
        finally:
            os.close(fd)

    def send_once(self, key, description, send, allow_after_end=False, client=None):
        require(allow_after_end or not self.end_requested, "End requested; no new sends")
        with self.guard(timeout=remaining(client.deadline, 3) if client is not None else 3) as state:
            require(allow_after_end or not state["ended"], "Dispatch ended")
            if client is not None:
                client.check_backend(state)
            require(key not in state["intents"], "Prior send exists; reconcile without replay")
            state["intents"][key] = {"phase": "possible_send", "description": description}
            self.write(state)
            result = send()
            state["intents"][key]["phase"] = "response_sent" if result is None else "acknowledged"
            self.write(state)
            return result

    def end(self):
        self.end_requested = True
        with self.guard() as state:
            state["ended"] = True
            state["ended_at_utc"] = now()
            self.write(state)


def exact_touch(command, marker):
    if not isinstance(command, str) or any(c in command for c in "\n\r\x00;&|<>$`"):
        return False
    canonical = "/usr/bin/touch " + shlex.quote(str(marker))
    if command == canonical:
        return True
    try:
        words = shlex.split(command)
        return len(words) == 3 and words[0] in {"/bin/zsh", "/bin/bash", "/bin/sh"} and words[1] in {"-c", "-lc"} and words[2] == canonical
    except ValueError:
        return False


def history(client, state):
    cursor = None
    turns = []
    seen = set()
    for _ in range(16):
        page = client.request("thread/turns/list", {"threadId": client.receiver, "limit": 20, "itemsView": "full", "sortDirection": "desc", "cursor": cursor})
        turns.extend(page["data"])
        cursor = page.get("nextCursor")
        if not cursor:
            return turns
        require(cursor not in seen, "History pagination repeated")
        seen.add(cursor)
    raise RuntimeError("History incomplete; no unique-outcome claim")


def find_dispatch(turns, dispatch):
    matches = [t for t in turns if any(i.get("type") == "userMessage" and i.get("clientId") == dispatch for i in t.get("items", []))]
    require(len(matches) == 1, "Start identity missing or ambiguous; never replay")
    return matches[0]


def state_view(thread, ended=False):
    native = thread["status"]["type"]
    return {"transport": "connected", "receiver": "saved-notLoaded" if native == "notLoaded" else "verified-on-this-backend",
            "task": "unknown" if native == "notLoaded" else native,
            "request": "pending-approval" if "waitingOnApproval" in thread["status"].get("activeFlags", []) else "none-observed-in-metadata",
            "native_status": native, "observed_at_utc": now(),
            "dispatch_eligibility": {"eligible": False, "reason": "owner-ended" if ended else "Diagnostic/inspection only; product ACK and execution setup not qualified"}}


def evidence_record(binding, directory, client, operation, result="pass", reason="Bounded native observations collected", settings=None, complete=True):
    artifacts = []
    paths = list(Path(directory).glob("events-*.jsonl"))
    paths += [Path(directory) / name for name in ["qualification.json", "effective-settings.json", "observation.json", "transport.json"] if (Path(directory) / name).is_file()]
    for path in sorted(paths):
        artifacts.append({"id": path.stem, "path": path.name, "sha256": sha(path), "privacy": "private"})
    state = Journal(directory).read() if (Path(directory) / "run-state.json").exists() else {}
    transport = client.transport if client else state.get("transport")
    backend = client.backend if client else state.get("backend")
    record = {
        "format": "codeexp2-control-evidence/1", "origin": "observed", "run_id": Path(directory).name,
        "operation_id": operation, "observed_at_utc": now(),
        "scope": {"kind": "workspace-maintenance", "mission": None, "operation": operation,
                  "authority_reference": binding["authority_reference"], "repository_root": binding["repository"], "worktree_root": binding["repository"]},
        "actors": {"desktop_bridge_id": binding.get("bridge_id"), "desktop_alias": binding.get("alias"),
                   "receiver_session_id": binding.get("receiver_id")},
        "source": {"head": None, "client_sha256": sha(__file__), "dependencies_sha256": digest(transport) if transport else None, "dirty_manifest_sha256": None},
        "connection": {"endpoint": endpoint_label(binding), "backend_binding": json.dumps(backend, sort_keys=True) if backend else None,
                       "backend_generation": None, "cli_version": None, "server_version": None, "cli_sha256": None, "server_sha256": None},
        "effective_settings": {"approval_policy": settings.get("approvalPolicy") if settings else None,
                               "approvals_reviewer": settings.get("approvalsReviewer") if settings else None,
                               "permission_scope": settings.get("sandbox") if settings else None},
        "evidence_root": str(Path(directory).resolve()), "limits": dict(BUDGETS),
        "observations": [{"claim": operation, "kind": "native", "result": result, "artifact_ids": [a["id"] for a in artifacts], "reason": reason}],
        "collection": {"complete": complete, "gaps": [] if complete else [reason]}, "artifacts": artifacts,
        "unresolved_effects": [], "owner_acceptance": {"decision": "not_requested", "scope": None, "authority_reference": None}, "unknowns": {}}
    def unknowns(value, prefix=""):
        for k, v in value.items():
            field = prefix + k
            if v is None:
                record["unknowns"][field] = "Not applicable or not measured by this bounded operation; no qualification inferred."
            elif isinstance(v, dict) and k != "unknowns":
                unknowns(v, field + ".")
    unknowns(record)
    if (Path(directory) / "run-state.json").exists():
        state = Journal(directory).read()
        uncertain = [k for k, v in state["intents"].items() if v["phase"] in {"possible_send", "response_sent"}]
        uncertain += ["request:" + k for k, v in state["requests"].items() if not v["resolved"]]
        record["unresolved_effects"] = [{"operation_id": key, "effect": "Outcome not fully observed", "state": "uncertain", "next_action": "Read-only reconcile the exact owned operation; no replay"} for key in uncertain]
    atomic(Path(directory) / "evidence.json", record)
    return record


def observe(binding, directory, status=False):
    client = None
    try:
        client = Client(binding, directory)
        outcome = {"initialize": client.initialized, "backend": client.backend}
        if status:
            require(binding["receiver_id"], "Status needs explicit receiver")
            outcome["status"] = state_view(client.verify())
        atomic(Path(directory) / "observation.json", outcome)
        evidence_record(binding, directory, client, "status" if status else "preflight")
        return outcome
    except Exception as error:
        evidence_record(binding, directory, client, "status" if status else "preflight", "fail", str(error), complete=False)
        raise
    finally:
        if client:
            client.close()


def verify_owned_state(journal):
    state = journal.read()
    require(state["source"] == source_identity(), "Source changed; qualification/recovery binding needs review")
    require(state["receiver_id"] and state["binding"]["receiver_id"] == state["receiver_id"], "Unbound receiver")
    require(endpoint_identity(binding_endpoint(state["binding"])) == state["backend"], "Backend changed; no effects")
    require(Path(state["binding"]["repository"]).resolve() == journal.root / "workspace", "Owned workspace mismatch")
    return state


def source_identity():
    return {name: sha(Path(__file__).with_name(name)) for name in ["native_control.py", "native_evidence.py", "native_qualification.py", "requirements-native-control.txt"]}


def record_pending(journal, event, marker, turn_id):
    p = event.get("params", {})
    state = journal.read()
    require(event.get("method") == "item/commandExecution/requestApproval" and p.get("threadId") == state["receiver_id"] and p.get("turnId") == turn_id,
            "Unexpected approval identity")
    require(p.get("cwd") == state["binding"]["repository"] and exact_touch(p.get("command"), marker) and not p.get("networkApprovalContext"), "Unexpected approval action")
    logical = hashlib.sha256(json.dumps([p["threadId"], p["turnId"], p["itemId"], p["command"]]).encode()).hexdigest()
    with journal.guard() as current:
        old = current["requests"].get(logical)
        if old:
            require(old["wire_id"] == event["id"], "Approval round/wire identity ambiguous; no decision")
        else:
            current["requests"][logical] = {"wire_id": event["id"], "turn_id": turn_id, "item_id": p["itemId"], "command": p["command"], "resolved": False}
            journal.write(current)
    return logical


def collect_turn(client, journal, turn_id, action=None, marker=None, reconnect=False, deadline=None):
    deadline = deadline if deadline is not None else time.monotonic() + 150
    final = None
    deltas = []
    requests = {k for k, v in journal.read()["requests"].items() if v["turn_id"] == turn_id}
    command_items = {}
    while time.monotonic() < deadline:
        try:
            event = client.event(min(1, max(.01, deadline-time.monotonic())))
        except TimeoutError:
            continue
        p = event.get("params", {})
        require(p.get("threadId") in {None, client.receiver}, "Foreign receiver event")
        method = event.get("method")
        if "method" in event and "id" in event:
            require(action is not None, "Unexpected input request")
            logical = record_pending(journal, event, marker, turn_id)
            requests.add(logical)
            if reconnect:
                with journal.guard() as state:
                    state["pending_reconnect"] = {"turn_id": turn_id, "marker": str(marker), "logical_request": logical}
                    journal.write(state)
                client.close()
                result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "reconcile", "--run", str(journal.root), "--cancel"],
                                        text=True, capture_output=True, timeout=60)
                require(result.returncode == 0, "Separate-process reconciliation failed: " + result.stderr[-1000:])
                recovered = load(journal.root / "reconciliation.json")
                require(recovered["confirmed"], "Recovery incomplete")
                return {"status": "interrupted", "requests": sorted(requests), "separate_process_reconnect": True, "recovery": recovered}
            if action == "cancel":
                key = "interrupt:" + turn_id
                if key not in journal.read()["intents"]:
                    journal.send_once(key, "Cancel exact owned pending turn", lambda: client.request("turn/interrupt", {"threadId": client.receiver, "turnId": turn_id}), allow_after_end=True, client=client)
            else:
                key = "decision:" + logical
                if key not in journal.read()["intents"]:
                    journal.send_once(key, "Exact harmless probe " + action,
                                      lambda: client.send({"id": event["id"], "result": {"decision": action}}), client=client)
        if method == "serverRequest/resolved":
            with journal.guard() as state:
                for logical, value in state["requests"].items():
                    if value["turn_id"] == turn_id and value["wire_id"] == p.get("requestId"):
                        value["resolved"] = True
                        if "decision:" + logical in state["intents"]:
                            state["intents"]["decision:" + logical]["phase"] = "resolved"
                journal.write(state)
        if p.get("turnId") == turn_id and method == "item/agentMessage/delta":
            deltas.append(p.get("delta", ""))
        if p.get("turnId") == turn_id and method == "item/completed" and p.get("item", {}).get("type") == "commandExecution":
            command_items[p["item"]["id"]] = p["item"]
        if method == "turn/completed" and p.get("turn", {}).get("id") == turn_id:
            final = p["turn"]
        if final and all(journal.read()["requests"][k]["resolved"] for k in requests):
            return {"status": final["status"], "text": "".join(deltas), "requests": sorted(requests), "commands": list(command_items.values())}
    raise TimeoutError("Turn or late request resolution not confirmed")


def reconcile_intents(journal, turns):
    """Resolve only outcomes with an exact native identity; never replay."""
    with journal.guard() as state:
        for key, intent in state["intents"].items():
            if intent["phase"] not in {"possible_send", "response_sent"}:
                continue
            if key.startswith("start:"):
                try:
                    turn = find_dispatch(turns, key.removeprefix("start:"))
                except ValueError:
                    continue
                intent.update(phase="observed", turn_id=turn["id"])
            elif key.startswith("interrupt:") and any(t["id"] == key.removeprefix("interrupt:") and t["status"] in FINAL for t in turns):
                intent["phase"] = "observed"
            elif key.startswith("decision:") and state["requests"].get(key.removeprefix("decision:"), {}).get("resolved"):
                intent["phase"] = "resolved"
        journal.write(state)
        return {"uncertain_sends": [k for k, v in state["intents"].items() if v["phase"] in {"possible_send", "response_sent"}],
                "unresolved_requests": [k for k, v in state["requests"].items() if not v["resolved"]]}


def reconcile_run(root, cancel=False, end=False):
    deadline = time.monotonic() + BUDGETS["reconcile_seconds"]
    journal = Journal(root)
    client = None
    output = {"confirmed": False, "attempted_at_utc": now()}
    try:
        if end:
            journal.end()
        state = verify_owned_state(journal)
        client = Client(state["binding"], root, mode="diagnostic" if cancel else "observe", deadline=deadline)
        client.check_backend(state)
        thread = client.verify()
        turns = history(client, state)
        dispatch = state.get("active_dispatch")
        turn = find_dispatch(turns, dispatch) if dispatch else None
        output.update(status=state_view(thread, state["ended"]), turn_id=turn["id"] if turn else None,
                      final_status=turn["status"] if turn else None)
        if cancel and turn and turn["status"] not in FINAL:
            with journal.guard(timeout=remaining(deadline, 3)) as current:
                client.check_backend(current)
                resumed = client.request("thread/resume", {"threadId": client.receiver, "excludeTurns": True})
            require(resumed["cwd"] == client.workspace and resumed["approvalPolicy"] == "on-request" and resumed["approvalsReviewer"] == "user" and resumed["sandbox"]["type"] == "readOnly", "Effective diagnostic settings changed")
            key = "interrupt:" + turn["id"]
            if key not in journal.read()["intents"]:
                journal.send_once(key, "Exact owned cancellation", lambda: client.request("turn/interrupt", {"threadId": client.receiver, "turnId": turn["id"]}), allow_after_end=True, client=client)
            pending = state.get("pending_reconnect")
            output["events"] = collect_turn(client, journal, turn["id"], action="cancel", marker=Path(pending["marker"]) if pending else None, deadline=deadline)
            turns = history(client, state)
            turn = find_dispatch(turns, dispatch)
            output["final_status"] = turn["status"]
        background = client.request("thread/backgroundTerminals/list", {"threadId": client.receiver})
        require(not background.get("nextCursor"), "Process inventory incomplete")
        output.update(reconcile_intents(journal, turns))
        output["requests_resolved"] = not output["unresolved_requests"]
        output["background_terminals"] = background
        output["confirmed"] = all(t["status"] in FINAL for t in turns) and not output["uncertain_sends"] and output["requests_resolved"] and not background.get("data")
        output["executor_retirement"] = "not_proven; turn cleanup only"
        return output
    except Exception as error:
        output.update(confirmed=False, error=str(error))
        raise
    finally:
        if client:
            client.close()
        atomic(journal.root / "reconciliation.json", output)


def summary_run(root):
    journal = Journal(root)
    state = journal.read()
    reconciliation = load(journal.root / "reconciliation.json") if (journal.root / "reconciliation.json").exists() else None
    unknown = [k for k, v in state["intents"].items() if v["phase"] in {"possible_send", "response_sent"}]
    result = {"run_id": state["run_id"], "receiver_id": state["receiver_id"], "dispatch_ended": state["ended"],
            "source": state["source"], "uncertain_sends": unknown,
            "unresolved_requests": [k for k, v in state["requests"].items() if not v["resolved"]],
            "reconciliation": reconciliation, "publication": "not_requested", "executor_retirement": "not_proven",
            "next_action": "Inspect retained evidence; explicit new scope required before any ended work resumes." if state["ended"] else "Read-only reconcile exact owned effects before further work."}
    if (journal.root / "evidence.json").exists() and (journal.root / "qualification.json").exists():
        result["qualification_scope"] = qualification_view(journal.root)
    return result


def qualification_view(root, operation=None):
    """Check retained bytes/scope. This never grants current dispatch eligibility."""
    directory = private_dir(root)
    try:
        report = load(directory / "qualification.json")
        record = load(directory / "evidence.json")
        state = Journal(directory).read()
        require(report["source"] == source_identity() == state["source"], "Tested source changed")
        require(report["receiver_id"] == state["receiver_id"] and report["workspace"] == state["binding"]["repository"] and report["backend"] == state["backend"], "Qualification binding mismatch")
        expected = {"kind": "workspace-maintenance", "operation": "qualify", "repository_root": report["workspace"], "worktree_root": report["workspace"]}
        require(record["origin"] == "observed" and all(v["kind"] == "native" for v in record["observations"]), "Fixture/imported observation is not native proof")
        checked = evaluate(record, directory, expected)
        require(checked["record_valid"] and checked["summary"] == "pass", "Evidence incomplete, missing or changed")
        require(record["actors"]["receiver_session_id"] == report["receiver_id"] and record["effective_settings"] == {
            "approval_policy": report["settings"]["approvalPolicy"], "approvals_reviewer": report["settings"]["approvalsReviewer"], "permission_scope": report["settings"]["sandbox"]}, "Effective settings binding mismatch")
        require(record["source"]["client_sha256"] == state["source"]["native_control.py"], "Evidence client source mismatch")
        for name, expected_hash in state["source"].items():
            require(hashlib.sha256(safe_read(directory, "source/" + name, BUDGETS["evidence_bytes"])).hexdigest() == expected_hash, "Source snapshot missing/changed")
        measured = transport_identity()
        require(measured == state["transport"] == report["transport"] == load(directory / "transport.json"), "Measured transport changed")
        require(record["source"]["dependencies_sha256"] == digest(measured) and record["connection"]["backend_binding"] == json.dumps(state["backend"], sort_keys=True) and record["connection"]["endpoint"] == endpoint_label(state["binding"]), "Evidence connection/dependency binding mismatch")
        require(load(directory / "effective-settings.json") == report["settings"] == state["settings"], "Settings snapshot mismatch")
        require(report["passed"] and report["reconciliation"]["confirmed"] and state["ended"], "Live proof incomplete")
        require(not any(v["phase"] in {"possible_send", "response_sent"} for v in state["intents"].values()) and all(v["resolved"] for v in state["requests"].values()), "Whole-run effects unresolved")
        from native_qualification import verify_transcript
        verify_transcript(directory, record, report, state)
        operations = [case["name"] for case in report["cases"] if case["passed"]]
        require(set(operations) == {"ordinary", "stream-and-readiness", "accept", "decline", "cancel", "durable-reconnect"} and len(operations) == 6, "Required live operations missing")
        require(operation is None or operation in operations, "Operation not qualified")
        return {"historical_proof": "pass", "operations": operations, "receiver_id": report["receiver_id"],
                "current_dispatch_eligible": False, "current_readiness": "not_proven; fresh receiver/settings check required",
                "excluded": ["native UI", "existing standalone Terminal attachment", "unattended automatic review", "executor retirement"]}
    except Exception as error:
        return {"historical_proof": "not_proven", "reason": str(error), "current_dispatch_eligible": False}


def qualify(binding, directory):
    from native_qualification import run_qualification
    return run_qualification(binding, directory)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["preflight", "status", "qualify", "reconcile", "end", "summary"])
    parser.add_argument("--binding")
    parser.add_argument("--evidence")
    parser.add_argument("--run")
    parser.add_argument("--cancel", action="store_true", help="Explicitly cancel only the exact owned diagnostic turn")
    args = parser.parse_args(argv)
    try:
        require(not args.cancel or args.action in {"reconcile", "end"}, "Cancellation is not an observation")
        if args.action in {"preflight", "status", "qualify"}:
            require(args.binding and args.evidence and not args.run, "Binding and new evidence directory required")
            binding = load_binding(args.binding)
            directory = private_dir(args.evidence, new=True)
            atomic(directory / "binding.json", binding)
            output = qualify(binding, directory) if args.action == "qualify" else observe(binding, directory, args.action == "status")
        else:
            require(args.run and not args.binding and not args.evidence, "Use exact existing --run")
            output = summary_run(args.run) if args.action == "summary" else reconcile_run(args.run, args.cancel, args.action == "end")
        print(json.dumps(output, allow_nan=False))
        return 0 if output.get("confirmed", True) and output.get("passed", True) else 2
    except Exception as error:
        print(json.dumps({"result": "not_proven", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
