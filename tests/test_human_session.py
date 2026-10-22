"""Offline regressions for human session continuity."""
import os
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import human_session as human


class HumanSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name) / "workspace"; self.workspace.mkdir()
        for relative in human.GUIDES:
            path = self.workspace / relative; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"format": "fixture", "version": 1}) if path.suffix == ".json" else relative + "\n")
        self.directory = Path(self.temp.name) / "session"
        self.session = human.Session(self.directory, self.workspace)

    def tearDown(self): self.temp.cleanup()

    def admit(self): return self.session.admit("Build continuity", "CodeExp2 docs and controls")

    def test_admission_records_all_guides_private_and_detects_drift(self):
        state = self.admit()
        self.assertEqual(len(state["guide_manifest"]), len(human.GUIDES))
        self.assertEqual(oct(self.directory.stat().st_mode & 0o777), "0o700")
        (self.workspace / human.GUIDES[0]).write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "GUIDE_BUNDLE_STALE"):
            self.session.status()

    def test_terminal_requires_reconciliation_before_closure(self):
        self.admit(); self.session.begin_work(); self.session.terminal("no_active_turn", "collector state")
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            self.session.close("partial", "collector ended", "task is uncertain", "inspect logs", "authorized")
        evidence = []
        payloads = {
            "log": {"events": "collected"},
            "result": {"thread": "receiver", "turn": {"id": "turn"}},
            "receiver_state": {"id": "receiver", "active_turn": None},
            "source_state": {"workspace": str(self.workspace.resolve()), "receiver_id": "receiver", "turn_id": "turn"},
        }
        for kind, payload in payloads.items():
            path = self.workspace / ("private-" + kind + ".json"); path.write_text(json.dumps(payload)); os.chmod(path, 0o600)
            evidence.append(self.session.evidence(kind, path))
        self.session.reconcile(evidence, ["collector/result race"], "receiver", "turn")
        state = self.session.close("partial", "builder turn completed", "native evidence is pending", "review exact artifacts", "authorized")
        self.assertEqual(state["state"], "closed")
        self.assertEqual(state["human_closure"]["uncertain_effects"], ["collector/result race"])

    def test_complete_scope_cannot_invent_next_work(self):
        self.admit()
        with self.assertRaisesRegex(ValueError, "CLOSURE_RECORD_INCOMPLETE"):
            self.session.close("complete", "done", "none", "make more work", "authorized")
        state = self.session.close("complete", "done", "none", None, "none")
        self.assertEqual(state["human_closure"]["next_action"], None)

    def test_no_terminal_closure_is_allowed_after_admission(self):
        self.admit()
        state = self.session.close("complete", "documentation request completed", "none", None, "none")
        self.assertEqual(state["state"], "closed")

    def test_terminal_observation_is_serial_and_cannot_follow_closure(self):
        self.admit(); self.session.begin_work(); self.session.close("complete", "done", "none", None, "none")
        with self.assertRaisesRegex(ValueError, "HUMAN_SESSION_CLOSED"):
            self.session.terminal("completed", "late event")

    def test_closed_session_is_preserved_before_a_new_task_is_admitted(self):
        first = self.admit(); self.session.close("complete", "done", "none", None, "none")
        second = self.session.admit("Different task", "new scope")
        self.assertNotEqual(first["session_id"], second["session_id"])
        history = self.directory / "history" / (first["session_id"] + ".json")
        self.assertTrue(history.is_file())
        self.assertEqual(self.session.require_active()["session_id"], second["session_id"])

    def test_second_terminal_cannot_discard_pending_reconciliation(self):
        self.admit(); self.session.begin_work(); self.session.terminal("failed", "first terminal")
        with self.assertRaisesRegex(ValueError, "HUMAN_SESSION_CLOSED"):
            self.session.terminal("completed", "contradictory terminal")

    def test_evidence_requires_private_regular_files_and_required_kinds(self):
        self.admit(); self.session.begin_work(); self.session.terminal("completed", "fixture")
        path = self.workspace / "result.json"; path.write_text("result")
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_INVALID"):
            self.session.evidence("result", path)
        os.chmod(path, 0o600)
        with self.assertRaisesRegex(ValueError, "RECONCILIATION_REQUIRED"):
            self.session.reconcile([self.session.evidence("result", path)])

    def test_exact_receiver_turn_reconciliation_rejects_unrelated_private_files(self):
        self.admit(); self.session.begin_work(); self.session.terminal("completed", "fixture")
        payloads = {
            "result": {"thread": "receiver", "turn": {"id": "turn"}},
            "receiver_state": {"id": "receiver", "active_turn": None},
            "source_state": {"workspace": str(self.workspace.resolve()), "receiver_id": "receiver", "turn_id": "turn"},
            "log": {"fixture": True},
        }
        evidence = []
        for kind, payload in payloads.items():
            path = self.workspace / (kind + ".json"); path.write_text(json.dumps(payload)); os.chmod(path, 0o600)
            evidence.append(self.session.evidence(kind, path))
        self.session.reconcile(evidence, receiver_id="receiver", turn_id="turn")
        self.assertEqual(self.session.status()["terminal_history"][0]["terminal_observation"]["kind"], "completed")

    def test_real_bundle_admission_strictly_parses_repository_guides(self):
        with tempfile.TemporaryDirectory() as directory:
            state = human.Session(Path(directory) / "state", ROOT).admit("real bundle", "offline")
            self.assertEqual(len(state["guide_manifest"]), len(human.GUIDES))
            self.assertTrue(all("applicability" in entry for entry in state["guide_manifest"]))

    def test_concurrent_terminal_observations_leave_one_monotonic_record(self):
        self.admit(); self.session.begin_work()
        outcomes = []
        def record(kind):
            try:
                self.session.terminal(kind, kind + " source")
                outcomes.append("accepted")
            except ValueError as error:
                outcomes.append(str(error).split(":", 1)[0])
        workers = [threading.Thread(target=record, args=(kind,)) for kind in ("completed", "failed")]
        for worker in workers: worker.start()
        for worker in workers: worker.join()
        self.assertEqual(outcomes.count("accepted"), 1)
        self.assertEqual(self.session.status()["state"], "reconciling")

    def test_symlink_session_directory_is_rejected_without_chmodding_target(self):
        target = Path(self.temp.name) / "target"; target.mkdir(mode=0o755); os.chmod(target, 0o755)
        link = Path(self.temp.name) / "link"; link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "HUMAN_SESSION_CUSTODY_INVALID"):
            human.Session(link, self.workspace)
        self.assertEqual(target.stat().st_mode & 0o777, 0o755)

    def test_shared_control_lock_serializes_competing_collectors(self):
        lock = Path(self.temp.name) / "control.lock"
        entered = []
        first_entered = threading.Event()
        release = threading.Event()
        def first():
            with human.exclusive_lock(lock):
                entered.append("first")
                first_entered.set()
                release.wait(timeout=2)
        def second():
            with human.exclusive_lock(lock):
                entered.append("second")
        one = threading.Thread(target=first); two = threading.Thread(target=second)
        one.start()
        self.assertTrue(first_entered.wait(timeout=2))
        two.start(); threading.Event().wait(.03)
        self.assertEqual(entered, ["first"])
        release.set(); one.join(); two.join()
        self.assertEqual(entered, ["first", "second"])


if __name__ == "__main__":
    unittest.main()
