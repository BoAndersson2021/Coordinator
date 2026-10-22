"""Private, human-facing task-session admission, reconciliation and closure."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import uuid

from native_evidence import strict_json


FORMAT = "human-session-continuity/1"
GUIDES = (
    ".agents/guides/structured-canonical-records.json",
    ".agents/guides/resource-discovery-and-reuse.json",
    ".agents/guides/rule-enforcement.json",
    ".agents/guides/bounded-delivery-session.json",
    ".agents/guides/human-facing-visual-communication.json",
    ".agents/guides/app-and-desktop-alias-icon.json",
    "docs/delivery-discipline.md", "docs/how-to-end-a-task.md",
    "docs/how-to-not-confuse-the-user.md", "docs/how-to-drive-session-continuity.md",
    "docs/how-not-to-overengineer.md", "docs/how-not-to-overblock-development.md",
    "docs/how-to-follow-and-refresh-a-plan.md", "docs/how-to-coordinate-with-a-builder-agent.md",
    "docs/universal-multi-agent-build-protocol.md", "docs/how-to-communicate-with-other-codex-agents.md",
    "docs/app-terminal-codex-launch-pattern.md",
)
TERMINAL = {"completed", "failed", "stopped", "no_active_turn"}
OUTCOMES = {"complete", "partial", "blocked", "stopped", "ongoing"}
AUTHORITIES = {"authorized", "owner_decision", "external_dependency", "none"}


def fail(code, detail):
    raise ValueError(code + ": " + detail)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_directory(path, create=False):
    path = Path(path).absolute()
    if create:
        path.mkdir(parents=True, exist_ok=True)
    info = path.lstat()
    if not path.is_dir() or path.is_symlink() or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        if create and path.is_dir() and not path.is_symlink() and info.st_uid == os.getuid():
            os.chmod(path, 0o700)
            info = path.lstat()
        if not path.is_dir() or path.is_symlink() or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            fail("HUMAN_SESSION_CUSTODY_INVALID", "session directory must be owner-only")
    return path.resolve()


def atomic(path, value):
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        descriptor = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as handle:
            handle.write(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


@contextmanager
def exclusive_lock(path):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


@contextmanager
def locked(directory):
    with exclusive_lock(directory / ".lock"):
        yield


class Session:
    def __init__(self, directory, workspace):
        self.directory = private_directory(directory, create=True)
        self.workspace = Path(workspace).resolve()
        self.path = self.directory / "session.json"

    def load(self):
        if not self.path.is_file() or self.path.is_symlink():
            fail("HUMAN_SESSION_MISSING", "admit the task session first")
        info = self.path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            fail("HUMAN_SESSION_CUSTODY_INVALID", "session record must be a private regular file")
        value = strict_json(self.path.read_text())
        if value.get("format") != FORMAT:
            fail("HUMAN_SESSION_INVALID", "unknown session record")
        return value

    def admit(self, requested_outcome, authorized_scope):
        if not isinstance(requested_outcome, str) or not requested_outcome.strip():
            fail("GUIDE_ADMISSION_MISSING", "requested outcome is required")
        if not isinstance(authorized_scope, str) or not authorized_scope.strip():
            fail("GUIDE_ADMISSION_MISSING", "authorized scope is required")
        entries = []
        for relative in GUIDES:
            path = self.workspace / relative
            if not path.is_file() or path.is_symlink():
                fail("GUIDE_ADMISSION_MISSING", relative)
            version = None
            if path.suffix == ".json":
                try:
                    parsed = strict_json(path.read_text())
                except (OSError, ValueError) as error:
                    raise ValueError("GUIDE_ADMISSION_INVALID: " + relative) from error
                if not isinstance(parsed, dict):
                    fail("GUIDE_ADMISSION_INVALID", relative)
                version = parsed.get("version")
            else:
                path.read_text()
            entries.append({"path": relative, "sha256": digest(path), "version": version,
                            "applicability": "active", "delivery": "included_in_session_admission"})
        with locked(self.directory):
            if self.path.exists():
                previous = self.load()
                if previous["state"] != "closed":
                    fail("GUIDE_ADMISSION_EXISTS", "existing session must be reconciled and closed")
                history = private_directory(self.directory / "history", create=True)
                atomic(history / (previous["session_id"] + ".json"), previous)
            value = {"format": FORMAT, "session_id": uuid.uuid4().hex, "task_id": uuid.uuid4().hex, "workspace": str(self.workspace),
                     "requested_outcome": requested_outcome, "authorized_scope": authorized_scope,
                     "state": "admitted", "admitted_at_utc": now(), "guide_manifest": entries,
                     "terminal_observation": None, "terminal_history": [],
                     "reconciliation": {"state": "not_needed", "evidence_refs": [], "uncertain_effects": []},
                     "human_closure": None}
            atomic(self.path, value)
        return value

    def require_active(self):
        value = self.status()
        if value["state"] not in {"admitted", "working"}:
            fail("HUMAN_SESSION_NOT_ACTIVE", "admit a new task session before material work")
        return value

    def begin_work(self):
        with locked(self.directory):
            value = self.load(); self.verify_guides(value)
            if value["state"] not in {"admitted", "working"}:
                fail("HUMAN_SESSION_NOT_ACTIVE", "admit a new task session before material work")
            if value["state"] == "admitted":
                value["state"] = "working"
                atomic(self.path, value)
            return value

    def verify_guides(self, value):
        if Path(value["workspace"]).resolve() != self.workspace:
            fail("GUIDE_ADMISSION_INVALID", "workspace differs")
        if len(value.get("guide_manifest", [])) != len(GUIDES):
            fail("GUIDE_ADMISSION_INVALID", "guide bundle differs")
        for entry, relative in zip(value["guide_manifest"], GUIDES):
            if entry.get("path") != relative or entry.get("sha256") != digest(self.workspace / relative) or entry.get("applicability") != "active":
                fail("GUIDE_BUNDLE_STALE", relative)
            if relative.endswith(".json"):
                try:
                    parsed = strict_json((self.workspace / relative).read_text())
                except (OSError, ValueError) as error:
                    raise ValueError("GUIDE_BUNDLE_STALE: " + relative) from error
                if entry.get("version") != parsed.get("version"):
                    fail("GUIDE_BUNDLE_STALE", relative)

    def terminal(self, kind, source):
        if kind not in TERMINAL or not isinstance(source, str) or not source.strip():
            fail("HUMAN_SESSION_INVALID", "terminal kind and source are required")
        with locked(self.directory):
            value = self.load(); self.verify_guides(value)
            if value["human_closure"] is not None or value["state"] != "working" or value["terminal_observation"] is not None:
                fail("HUMAN_SESSION_CLOSED", "a closed session cannot accept a terminal observation")
            value["state"] = "reconciling"
            value["terminal_observation"] = {"kind": kind, "source": source, "observed_at_utc": now()}
            value["reconciliation"] = {"state": "required", "evidence_refs": [], "uncertain_effects": []}
            atomic(self.path, value)
        return value

    def evidence(self, kind, path):
        path = Path(path)
        if not path.is_absolute():
            path = self.workspace / path
        try:
            resolved = path.resolve(strict=True)
            info = path.lstat()
        except OSError as error:
            raise ValueError("RECONCILIATION_INVALID: evidence is unavailable") from error
        if path.is_symlink() or not resolved.is_relative_to(self.workspace) or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            fail("RECONCILIATION_INVALID", "evidence must be a private regular file within this workspace")
        return {"kind": kind, "path": str(resolved), "sha256": digest(resolved), "privacy": "private"}

    def reconcile(self, evidence_refs, uncertain_effects=None, receiver_id=None, turn_id=None):
        required = {"log", "result", "receiver_state", "source_state"}
        if not isinstance(evidence_refs, list) or not evidence_refs or not all(isinstance(v, dict) for v in evidence_refs):
            fail("RECONCILIATION_REQUIRED", "structured durable evidence is required")
        uncertain_effects = [] if uncertain_effects is None else uncertain_effects
        if not isinstance(uncertain_effects, list) or not all(isinstance(v, str) and v.strip() for v in uncertain_effects):
            fail("RECONCILIATION_INVALID", "uncertain effects must be nonempty strings")
        validated = []
        for entry in evidence_refs:
            if set(entry) != {"kind", "path", "sha256", "privacy"} or entry["privacy"] != "private" or not isinstance(entry["kind"], str):
                fail("RECONCILIATION_INVALID", "invalid evidence descriptor")
            checked = self.evidence(entry["kind"], entry["path"])
            if checked != entry:
                fail("RECONCILIATION_INVALID", "evidence identity changed")
            validated.append(checked)
        if not required.issubset({entry["kind"] for entry in validated}):
            fail("RECONCILIATION_REQUIRED", "log, result, receiver state and source state are required")
        if not isinstance(receiver_id, str) or not receiver_id or not isinstance(turn_id, str) or not turn_id:
            fail("RECONCILIATION_INVALID", "exact receiver and turn identity are required")
        by_kind = {entry["kind"]: entry for entry in validated}
        try:
            result = strict_json(Path(by_kind["result"]["path"]).read_text())
            receiver = strict_json(Path(by_kind["receiver_state"]["path"]).read_text())
            source = strict_json(Path(by_kind["source_state"]["path"]).read_text())
        except (OSError, ValueError) as error:
            raise ValueError("RECONCILIATION_INVALID: structured evidence is unreadable") from error
        if result.get("thread") != receiver_id or result.get("turn", {}).get("id") != turn_id:
            fail("RECONCILIATION_INVALID", "result does not belong to the exact receiver and turn")
        if receiver.get("id") != receiver_id or receiver.get("active_turn") is not None:
            fail("RECONCILIATION_INVALID", "receiver state does not prove terminal ownership")
        if source != {"workspace": str(self.workspace), "receiver_id": receiver_id, "turn_id": turn_id}:
            fail("RECONCILIATION_INVALID", "source state does not bind the exact receiver and turn")
        with locked(self.directory):
            value = self.load(); self.verify_guides(value)
            if value["state"] != "reconciling":
                fail("RECONCILIATION_REQUIRED", "record a terminal observation first")
            value["reconciliation"] = {"state": "complete", "evidence_refs": validated, "uncertain_effects": uncertain_effects}
            value["terminal_history"].append({"terminal_observation": value["terminal_observation"], "reconciliation": value["reconciliation"]})
            value["terminal_observation"] = None
            value["state"] = "working"
            atomic(self.path, value)
        return value

    def close(self, outcome, done, remains, next_action, authority):
        if outcome not in OUTCOMES or authority not in AUTHORITIES:
            fail("CLOSURE_RECORD_INCOMPLETE", "unknown outcome or authority")
        if not all(isinstance(v, str) and v.strip() for v in [done, remains]):
            fail("CLOSURE_RECORD_INCOMPLETE", "done and remains are required")
        if outcome == "complete":
            if next_action is not None or authority != "none":
                fail("CLOSURE_RECORD_INCOMPLETE", "complete scope uses next_action null and authority none")
        elif not isinstance(next_action, str) or not next_action.strip() or authority == "none":
            fail("CLOSURE_RECORD_INCOMPLETE", "unfinished work needs a next action and authority")
        with locked(self.directory):
            value = self.load(); self.verify_guides(value)
            if value["reconciliation"]["state"] == "required":
                fail("RECONCILIATION_REQUIRED", "terminal state must be reconciled before closure")
            if value["human_closure"] is not None:
                fail("HUMAN_SESSION_CLOSED", "closure already recorded")
            value["human_closure"] = {"outcome": outcome, "done": done, "remains": remains,
                                      "next_action": next_action, "next_action_authority": authority,
                                      "uncertain_effects": value["reconciliation"]["uncertain_effects"]}
            value["state"] = "closed"
            atomic(self.path, value)
        return value

    def status(self):
        with locked(self.directory):
            value = self.load(); self.verify_guides(value)
            return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["admit", "terminal", "reconcile", "close", "status"])
    parser.add_argument("--directory", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--outcome"); parser.add_argument("--scope")
    parser.add_argument("--kind", choices=sorted(TERMINAL)); parser.add_argument("--source")
    parser.add_argument("--receiver-id"); parser.add_argument("--turn-id")
    parser.add_argument("--evidence", action="append", default=[]); parser.add_argument("--uncertain", action="append", default=[])
    parser.add_argument("--done"); parser.add_argument("--remains"); parser.add_argument("--next-action")
    parser.add_argument("--authority", choices=sorted(AUTHORITIES))
    args = parser.parse_args(argv)
    session = Session(args.directory, args.workspace)
    if args.action == "admit": value = session.admit(args.outcome, args.scope)
    elif args.action == "terminal": value = session.terminal(args.kind, args.source)
    elif args.action == "reconcile":
        entries = []
        for raw in args.evidence:
            kind, separator, path = raw.partition(":")
            if not separator or not kind or not path:
                fail("RECONCILIATION_INVALID", "evidence must be kind:absolute-or-relative-path")
            entries.append(session.evidence(kind, path))
        value = session.reconcile(entries, args.uncertain, args.receiver_id, args.turn_id)
    elif args.action == "close": value = session.close(args.outcome, args.done, args.remains, args.next_action, args.authority)
    else: value = session.status()
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
