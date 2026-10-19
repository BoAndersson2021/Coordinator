"""Offline native-control regressions. No native server or model calls."""
import copy
import json
import os
import hashlib
import struct
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import native_control as control
from native_evidence import evaluate, strict_json, safe_read


class Wire:
    def __init__(self, response=None, events=None, error=None):
        self.sent = []
        self.queue = list(events or [])
        self.response = {"userAgent": "fixture"} if response is None else response
        self.error = error
        self.closed = False

    def send(self, raw):
        message = json.loads(raw)
        self.sent.append(message)
        if message.get("method") == "initialize":
            self.queue.append({"id": message["id"], "result": self.response})

    def recv(self, timeout):
        if self.error:
            raise self.error
        if not self.queue:
            raise TimeoutError("Injected no reply")
        value = self.queue.pop(0)
        return value if isinstance(value, str) else json.dumps(value)

    def close(self):
        self.closed = True


class NativeControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(control, "ROOT", self.root)
        self.root_patch.start()
        self.binding = {"format": "codeexp2-native-binding/1", "repository": str(ROOT), "socket_path": "/fixture/native.sock",
                        "coordinator_session_id": "fixture-coordinator", "authority_reference": "fixture only", "receiver_id": "fixture-receiver"}
        self.identity = {"path": "/fixture/native.sock", "uid": os.getuid(), "device": 1, "inode": 2}

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def client(self, wire=None, **kwargs):
        directory = self.root / str(len(list(self.root.iterdir())))
        directory.mkdir(mode=0o700)
        wire = wire or Wire()
        return control.Client(self.binding, directory, factory=lambda *_: wire, identity=lambda _: self.identity, **kwargs), wire

    def journal(self):
        directory = self.root / "run"
        directory.mkdir(mode=0o700)
        state = {"run_id": "fixture-run", "backend": self.identity, "receiver_id": "fixture-receiver", "ended": False,
                 "intents": {}, "requests": {}, "binding": self.binding}
        return control.Journal(directory, state)

    def test_all_foundation_fixtures_and_owner_acceptance_separation(self):
        directory = ROOT / "docs/fixtures/native-control-evidence-v1"
        bundle = strict_json((directory / "cases.json").read_text())
        self.assertEqual(len(bundle["cases"]), 21)
        for case in bundle["cases"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(evaluate(case["record"], directory, bundle["trusted_scope"]), case["expected"])

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_values(self):
        for raw in ['{"result": "fail", "result": "pass"}', '{"value": NaN}', '{"value": Infinity}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict_json(raw)

    def test_safe_artifact_reader_rejects_symlink_fifo_and_oversize(self):
        (self.root / "outside").write_text("outside")
        (self.root / "link").symlink_to(self.root / "outside")
        os.mkfifo(self.root / "pipe")
        for name in ["link", "pipe"]:
            with self.subTest(name=name), self.assertRaises((OSError, ValueError)):
                safe_read(self.root, name, 10)
        with self.assertRaises(ValueError):
            safe_read(self.root, "outside", 2)

    def test_readonly_wire_cannot_bypass_scope_or_receiver_checks(self):
        client, wire = self.client()
        try:
            before = len(wire.sent)
            for method, params in [("turn/start", {"threadId": "fixture-receiver"}), ("thread/read", {"threadId": "other"}), ("thread/delete", {})]:
                with self.subTest(method=method), self.assertRaises(ValueError):
                    client.send({"id": 9, "method": method, "params": params})
            with self.assertRaises(ValueError):
                client.send({"id": 5, "result": {"decision": "accept"}})
            self.assertEqual(len(wire.sent), before)
        finally:
            client.close()
        self.assertTrue(wire.closed)

    def test_incompatible_initialize_closes_owned_resources(self):
        wire = Wire(response={"unsupported": True})
        with self.assertRaises(ValueError):
            self.client(wire)
        self.assertTrue(wire.closed)

    def test_handshake_refusal_and_timeout_leave_no_work_effect(self):
        for error in [OSError("Injected handshake rejection"), TimeoutError("Injected initialize timeout")]:
            wire = Wire(error=error)
            with self.subTest(error=error), self.assertRaises(type(error)):
                self.client(wire)
            self.assertTrue(wire.closed)
            self.assertEqual([m["method"] for m in wire.sent], ["initialize"])

    def test_changed_endpoint_rejected_before_initialize(self):
        directory = self.root / "changed"
        directory.mkdir(mode=0o700)
        wire = Wire()
        values = iter([self.identity, {**self.identity, "inode": 3}])
        with self.assertRaises(ValueError):
            control.Client(self.binding, directory, factory=lambda *_: wire, identity=lambda _: next(values))
        self.assertTrue(wire.closed)
        self.assertEqual(wire.sent, [])

    def test_malformed_oversized_and_queue_overflow_fail_visibly(self):
        for events, error in [(['not json'], ValueError), (["x" * (1048576 + 1)], ValueError), ([{"method": "event"}] * 33, ValueError)]:
            wire = Wire(events=events)
            with self.subTest(kind=error), self.assertRaises(error):
                self.client(wire)
            self.assertTrue(wire.closed)

    def test_metadata_status_does_not_become_dispatch_eligibility(self):
        for native in ["notLoaded", "idle", "active"]:
            view = control.state_view({"status": {"type": native}})
            self.assertFalse(view["dispatch_eligibility"]["eligible"])
        self.assertEqual(control.state_view({"status": {"type": "notLoaded"}})["receiver"], "saved-notLoaded")
        self.assertEqual(control.state_view({"status": {"type": "idle"}}, True)["dispatch_eligibility"]["reason"], "owner-ended")

    def test_exact_action_rejects_shell_injection_and_permission_amendments(self):
        marker = self.root / "marker"
        command = "/usr/bin/touch " + str(marker)
        self.assertTrue(control.exact_touch(command, marker))
        self.assertTrue(control.exact_touch("/bin/zsh -lc '" + command + "'", marker))
        for bad in [command + " extra", command + "; echo x", command + "\n", command.replace(str(marker), "$(echo x)"), None]:
            self.assertFalse(control.exact_touch(bad, marker))

    def test_lost_ack_intent_blocks_retry_and_disk_failure_sends_nothing(self):
        journal = self.journal()
        calls = []
        def fail():
            calls.append(1)
            raise TimeoutError("Injected lost acknowledgement")
        with self.assertRaises(TimeoutError):
            journal.send_once("dispatch", "fixture", fail)
        with self.assertRaises(ValueError):
            journal.send_once("dispatch", "fixture", lambda: calls.append(2))
        self.assertEqual(calls, [1])
        with patch.object(journal, "write", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                journal.send_once("other", "fixture", lambda: calls.append(3))
        self.assertEqual(calls, [1])

    def test_end_is_durable_and_cannot_be_overridden_by_stale_client(self):
        journal = self.journal()
        stale = control.Journal(journal.root)
        stale.read()
        journal.end()
        with self.assertRaises(ValueError):
            stale.send_once("approval", "fixture", lambda: self.fail("Sent after end"))
        self.assertTrue(control.Journal(journal.root).read()["ended"])

    def test_end_persistence_failure_blocks_the_receiving_client(self):
        journal = self.journal()
        with patch.object(journal, "write", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                journal.end()
        with self.assertRaises(ValueError):
            journal.send_once("after-failed-end", "fixture", lambda: self.fail("Sent after end intent"))

    def test_different_run_cannot_claim_same_canonical_receiver(self):
        journal = self.journal()
        journal.send_once("first", "fixture", lambda: {})
        second_root = self.root / "second-run"
        second_root.mkdir(mode=0o700)
        second = control.Journal(second_root, journal.read())
        with self.assertRaises(ValueError):
            second.send_once("second", "fixture", lambda: self.fail("Competing owner sent"))

    def test_summary_is_observation_only_and_preserves_partial_states(self):
        journal = self.journal()
        state = journal.read()
        state.update(source={"fixture": "bytes"}, active_dispatch="dispatch")
        state["intents"]["unknown"] = {"phase": "possible_send"}
        state["requests"]["pending"] = {"resolved": False}
        journal.write(state)
        before = journal.path.read_bytes()
        result = control.summary_run(journal.root)
        self.assertEqual(journal.path.read_bytes(), before)
        self.assertEqual(result["uncertain_sends"], ["unknown"])
        self.assertEqual(result["unresolved_requests"], ["pending"])
        self.assertEqual(result["executor_retirement"], "not_proven")

    def test_two_processes_share_operation_lock_and_send_once(self):
        journal = self.journal()
        script = """import sys; from pathlib import Path
sys.path.insert(0,sys.argv[1]); import native_control as n
n.ROOT=Path(sys.argv[2]); j=n.Journal(sys.argv[3])
try:
 j.send_once('race','fixture',lambda: open(sys.argv[4],'a').write('x'))
except ValueError: pass
"""
        target = self.root / "sends"
        with patch.object(control, "ROOT", self.root):
            children = [subprocess.Popen([sys.executable, "-B", "-c", script, str(ROOT / "scripts"), str(self.root), str(journal.root), str(target)], stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
            for child in children:
                out, err = child.communicate(timeout=10)
                self.assertEqual(child.returncode, 0, (out, err))
        self.assertEqual(target.read_text(), "x")

    def test_lost_start_reconciles_by_unique_identity_not_text(self):
        turn = {"id": "owned", "items": [{"type": "userMessage", "clientId": "dispatch", "text": "same text"}]}
        self.assertEqual(control.find_dispatch([turn], "dispatch")["id"], "owned")
        for turns in [[], [turn, {**turn, "id": "duplicate"}]]:
            with self.assertRaises(ValueError):
                control.find_dispatch(turns, "dispatch")
        with self.assertRaises(ValueError):
            control.find_dispatch([turn], "different-dispatch")

    def test_incomplete_or_repeated_history_never_proves_unique_dispatch(self):
        class Pages:
            receiver = "fixture"
            def request(self, *args):
                return {"data": [], "nextCursor": "repeated"}
        with self.assertRaises(ValueError):
            control.history(Pages(), {})

    def test_replayed_request_handled_once_and_ambiguous_round_refuses(self):
        journal = self.journal()
        marker = self.root / "marker"
        event = {"id": 8, "method": "item/commandExecution/requestApproval", "params": {"threadId": "fixture-receiver", "turnId": "turn", "itemId": "item", "cwd": str(ROOT), "command": "/usr/bin/touch " + str(marker)}}
        a = control.record_pending(journal, event, marker, "turn")
        self.assertEqual(control.record_pending(journal, event, marker, "turn"), a)
        self.assertEqual(len(journal.read()["requests"]), 1)
        changed = {**event, "id": 9}
        with self.assertRaises(ValueError):
            control.record_pending(journal, changed, marker, "turn")
        foreign = copy.deepcopy(event)
        foreign["params"]["threadId"] = "other"
        with self.assertRaises(ValueError):
            control.record_pending(journal, foreign, marker, "turn")

    def test_late_resolution_after_completion_is_collected(self):
        journal = self.journal()
        state = journal.read()
        state["requests"]["logical"] = {"wire_id": 8, "turn_id": "turn", "resolved": False}
        journal.write(state)
        events = iter([{"method": "turn/completed", "params": {"threadId": "fixture-receiver", "turn": {"id": "turn", "status": "interrupted"}}}, {"method": "serverRequest/resolved", "params": {"threadId": "fixture-receiver", "requestId": 8}}])
        class Events:
            receiver = "fixture-receiver"
            def event(self, timeout):
                return next(events)
        outcome = control.collect_turn(Events(), journal, "turn")
        self.assertEqual(outcome["status"], "interrupted")
        self.assertTrue(journal.read()["requests"]["logical"]["resolved"])

    def test_source_changed_recovery_has_no_native_effect(self):
        journal = self.journal()
        state = journal.read()
        state["source"] = {"bad": "changed"}
        journal.write(state)
        with self.assertRaises(ValueError):
            control.verify_owned_state(journal)

    def test_qualification_reuse_checks_source_settings_receiver_and_artifacts(self):
        journal = self.journal()
        binding = {**self.binding, "repository": str(journal.root)}
        settings = {"approvalPolicy": "on-request", "approvalsReviewer": "user", "sandbox": {"type": "readOnly"}}
        report = {"source": control.source_identity(), "backend": self.identity,
                  "receiver_id": "fixture-receiver", "workspace": str(journal.root), "settings": settings,
                  "passed": True, "reconciliation": {"confirmed": True},
                  "cases": [{"name": n, "passed": True} for n in ["ordinary", "stream-and-readiness", "accept", "decline", "cancel", "durable-reconnect"]]}
        state = journal.read()
        state.update(source=report["source"], binding=binding)
        journal.write(state)
        control.atomic(journal.root / "qualification.json", report)
        control.evidence_record(binding, journal.root, None, "qualify", settings=settings)
        self.assertEqual(control.qualification_view(journal.root)["historical_proof"], "not_proven")
        self.assertFalse(control.qualification_view(journal.root)["current_dispatch_eligible"])
        self.assertEqual(control.qualification_view(journal.root, "native-ui")["historical_proof"], "not_proven")
        original = (journal.root / "qualification.json").read_bytes()
        for changed in [{**report, "receiver_id": "other"}, {**report, "source": {"changed": "bytes"}}, {**report, "settings": {**settings, "approvalsReviewer": "auto_review"}}]:
            control.atomic(journal.root / "qualification.json", changed)
            self.assertEqual(control.qualification_view(journal.root)["historical_proof"], "not_proven")
        (journal.root / "qualification.json").write_bytes(original)
        (journal.root / "qualification.json").unlink()
        self.assertEqual(control.qualification_view(journal.root)["historical_proof"], "not_proven")

    def test_whole_run_reconciliation_preserves_unrelated_uncertainty(self):
        journal = self.journal()
        state = journal.read()
        state["intents"] = {"ordinary": {"phase": "possible_send"}, "start:unique": {"phase": "possible_send"}, "interrupt:final": {"phase": "possible_send"}}
        state["requests"]["old"] = {"resolved": False, "turn_id": "old-turn"}
        journal.write(state)
        result = control.reconcile_intents(journal, [{"id": "final", "status": "interrupted", "items": [{"type": "userMessage", "clientId": "unique"}]}])
        self.assertEqual(result, {"uncertain_sends": ["ordinary"], "unresolved_requests": ["old"]})
        self.assertEqual(journal.read()["intents"]["start:unique"]["phase"], "observed")
        self.assertEqual(journal.read()["intents"]["interrupt:final"]["phase"], "observed")

    def test_recovery_backend_swap_blocks_effect_and_records_failed_attempt(self):
        journal = self.journal()
        state = journal.read()
        state.update(source=control.source_identity(), active_dispatch="unique")
        journal.write(state)
        class Swapped:
            def __init__(self, *args, **kwargs):
                self.backend = {**state["backend"], "inode": 999}
                self.binding = state["binding"]
                self.identity = lambda _: self.backend
            check_backend = control.Client.check_backend
            def close(self):
                pass
            def verify(self):
                raise AssertionError("Read/effect after backend mismatch")
        control.atomic(journal.root / "reconciliation.json", {"confirmed": True})
        with patch.object(control, "verify_owned_state", return_value=state), patch.object(control, "Client", Swapped):
            with self.assertRaises(ValueError):
                control.reconcile_run(journal.root, cancel=True)
        self.assertFalse(control.load(journal.root / "reconciliation.json")["confirmed"])
        client, wire = self.client(mode="diagnostic")
        client.backend = {**self.identity, "inode": 999}
        with self.assertRaises(ValueError):
            journal.send_once("unsafe", "fixture", lambda: self.fail("Effect after swap"), client=client)
        self.assertNotIn("unsafe", journal.read()["intents"])
        client.close()

    def test_recovery_deadline_is_shared_by_rpc_pages_and_collection(self):
        client, wire = self.client()
        try:
            client.deadline = 30
            with patch.object(control.time, "monotonic", return_value=29):
                self.assertEqual(control.remaining(client.deadline, 10), 1)
            before = len(wire.sent)
            with patch.object(control.time, "monotonic", return_value=31):
                with self.assertRaises(ValueError):
                    client.request("thread/read", {"threadId": client.receiver})
            self.assertEqual(len(wire.sent), before)
        finally:
            client.close()
        journal = self.journal()
        with patch.object(control.time, "monotonic", return_value=31):
            with self.assertRaises(TimeoutError):
                control.collect_turn(None, journal, "turn", deadline=30)

    def test_loaded_transport_version_path_and_bytes_are_measured(self):
        import types
        package = self.root / "websockets"
        (package / "sync").mkdir(parents=True)
        (package / "__init__.py").write_text("fixture")
        target = package / "sync/client.py"
        target.write_text("first implementation")
        module = types.ModuleType("websockets")
        module.__file__ = str(package / "__init__.py")
        module.__version__ = "17.2"
        sync = types.ModuleType("websockets.sync")
        sync.client = types.SimpleNamespace(__file__=str(target))
        dist = types.SimpleNamespace(version="17.2", locate_file=lambda _: package)
        with patch.dict(sys.modules, {"websockets": module, "websockets.sync": sync}), patch.object(control.importlib.metadata, "distribution", return_value=dist):
            first = control.transport_identity()
            target.write_text("second implementation")
            self.assertNotEqual(first, control.transport_identity())
            module.__version__ = "other"
            with self.assertRaises(ValueError):
                control.transport_identity()
            module.__version__ = "17.2"
            dist.locate_file = lambda _: self.root / "shadowed"
            with self.assertRaises(ValueError):
                control.transport_identity()

    def test_native_transcript_requires_correlated_receipts_and_separate_process(self):
        from native_qualification import verify_transcript
        directory = self.root
        workspace = directory / "workspace"
        workspace.mkdir()
        (workspace / "ordinary.txt").touch()
        (directory / "markers").mkdir()
        (directory / "markers/accept.txt").touch()
        state = {"receiver_id": "receiver", "binding": {"repository": str(workspace)}, "backend": self.identity, "transport": {"fixture": True}}
        settings = {"cwd": str(workspace), "approvalPolicy": "on-request", "approvalsReviewer": "user", "sandbox": {"type": "readOnly"}}
        report = {"settings": settings, "diagnostic_readiness": {"nonce": "NONCE"}, "cases": [{"name": "ordinary"}]}
        rows = {"initial": [], "reconnected": []}
        def add(direction, message, generation="initial"):
            rows[generation].append({"direction": direction, "generation": generation, "producer_pid": 1 if generation == "initial" else 2, "backend": self.identity, "transport_sha256": control.digest(state["transport"]), "message": message})
        def rpc(method, params, result, generation="initial"):
            wire_id = generation + str(len(rows[generation]))
            add("sent", {"method": method, "id": wire_id, "params": params}, generation)
            add("received", {"id": wire_id, "result": result}, generation)
        def notice(method, params, generation="initial", wire_id=None):
            add("received", {"method": method, "params": {"threadId": "receiver", **params}, **({"id": wire_id} if wire_id is not None else {})}, generation)
        rpc("thread/start", {"cwd": str(workspace), "ephemeral": False, "sandbox": "read-only", "approvalPolicy": "on-request", "approvalsReviewer": "user"}, {"thread": {"id": "receiver"}, **settings})
        rpc("command/exec", {"command": ["/usr/bin/touch", str(workspace / "ordinary.txt")], "cwd": str(workspace), "sandboxPolicy": {"type": "workspaceWrite", "writableRoots": [str(workspace)], "networkAccess": False}}, {"exitCode": 0})
        for index, name in enumerate(["stream-and-readiness", "accept", "decline", "cancel", "durable-reconnect"]):
            tid, dispatch = name + "-turn", name + "-dispatch"
            report["cases"].append({"name": name, "turn_id": tid, "dispatch_id": dispatch})
            rpc("turn/start", {"threadId": "receiver", "clientUserMessageId": dispatch, "input": [{"text": "NONCE"}]}, {"turn": {"id": tid, "status": "inProgress"}})
            notice("item/completed", {"turnId": tid, "item": {"type": "userMessage", "clientId": dispatch}})
            generation = "reconnected" if name == "durable-reconnect" else "initial"
            if name == "stream-and-readiness":
                notice("item/agentMessage/delta", {"turnId": tid, "delta": "NONCE"})
            else:
                marker = directory / "markers" / (name + ".txt")
                params = {"turnId": tid, "itemId": name + "-item", "command": "/usr/bin/touch " + str(marker), "cwd": str(workspace)}
                notice("item/commandExecution/requestApproval", params, wire_id=index)
                if generation == "reconnected":
                    notice("item/commandExecution/requestApproval", params, generation, index)
                if name in {"accept", "decline"}:
                    add("sent", {"id": index, "result": {"decision": name}})
                else:
                    rpc("turn/interrupt", {"threadId": "receiver", "turnId": tid}, {}, generation)
                if name == "accept":
                    notice("item/completed", {"turnId": tid, "item": {"id": name + "-item", "type": "commandExecution", "command": params["command"], "status": "completed", "exitCode": 0}})
                notice("serverRequest/resolved", {"requestId": index}, generation)
            notice("turn/completed", {"turn": {"id": tid, "status": "interrupted" if name in {"cancel", "durable-reconnect"} else "completed"}}, generation)
        rpc("thread/backgroundTerminals/list", {"threadId": "receiver"}, {"data": [], "nextCursor": None}, "reconnected")
        rpc("thread/archive", {"threadId": "receiver"}, {}, "reconnected")
        record = {"artifacts": [{"path": "events-" + g + ".jsonl"} for g in rows]}
        def write():
            for g, events in rows.items():
                (directory / ("events-" + g + ".jsonl")).write_text("".join(json.dumps(e) + "\n" for e in events))
        write()
        verify_transcript(directory, record, report, state)
        original = copy.deepcopy(rows)
        for mutation in ["no-logs", "lost-receipt", "same-process", "duplicate-decision", "wrong-backend", "wrong-cwd", "wrong-permissions", "missing-receiver"]:
            rows = copy.deepcopy(original)
            if mutation == "no-logs":
                rows["initial"] = []
            elif mutation == "lost-receipt":
                rows["initial"] = [e for e in rows["initial"] if not (e["direction"] == "received" and e["message"].get("result", {}).get("exitCode") == 0)]
            elif mutation == "same-process":
                for e in rows["reconnected"]:
                    e["producer_pid"] = 1
            elif mutation == "duplicate-decision":
                rows["initial"].append(next(e for e in rows["initial"] if e["direction"] == "sent" and e["message"].get("result") == {"decision": "accept"}))
            elif mutation == "wrong-backend":
                rows["initial"][0]["backend"] = {**self.identity, "inode": 99}
            elif mutation in {"wrong-cwd", "wrong-permissions"}:
                params = next(e["message"]["params"] for e in rows["initial"] if e["message"].get("method") == "command/exec")
                if mutation == "wrong-cwd":
                    params["cwd"] = "/wrong-workspace"
                else:
                    params["sandboxPolicy"] = {"type": "dangerFullAccess"}
            else:
                next(e["message"] for e in rows["reconnected"] if e["message"].get("method") == "thread/archive")["params"] = {}
            write()
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, KeyError)):
                verify_transcript(directory, record, report, state)

    def test_visual_fixture_hashes_dimensions_lineage_and_reorder(self):
        directory = ROOT / "docs/fixtures/visual-review"
        review = strict_json((directory / "REVIEW.json").read_text())
        options = {v["id"]: v for v in review["options"]}
        self.assertEqual(set(options), {"option-1", "option-2", "option-3"})
        self.assertEqual(set(review["reordered_display"]), set(options))
        self.assertEqual(review["selection"], {"base_id": "option-3", "sidebar_id": "option-1"})
        for item in list(options.values()) + [review["refinement"]]:
            data = safe_read(directory, item["path"], 1024*1024)
            self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
            self.assertEqual(list(struct.unpack('>II', data[16:24])), item["dimensions"])
        self.assertEqual(review["refinement"]["lineage"], ["option-3", "option-1"])
        self.assertEqual(review["owner_acceptance"]["decision"], "not_requested")


if __name__ == "__main__":
    unittest.main()
