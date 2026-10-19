import unittest
import tempfile
import copy
from pathlib import Path
from qualify_host_control import exact_touch
from native_host_control import Client, BUILDER, REPOSITORY, retire_dispatch, restore_settings


class ApprovalScopeTests(unittest.TestCase):
    marker = Path("/private/tmp/thor.marker")

    def test_exact_command_and_native_shell_wrapper(self):
        command = "/usr/bin/touch /private/tmp/thor.marker"
        self.assertTrue(exact_touch(command, self.marker))
        self.assertTrue(exact_touch("/bin/zsh -lc '"+command+"'", self.marker))

    def test_shell_command_separators_never_count_as_argument_whitespace(self):
        for command in [
            "/usr/bin/touch\n/private/tmp/thor.marker",
            "/bin/zsh\n-lc '/usr/bin/touch /private/tmp/thor.marker'",
            "/bin/zsh -lc '/usr/bin/touch\n/private/tmp/thor.marker'",
            "/usr/bin/touch /private/tmp/thor.marker; echo extra",
            "/usr/bin/touch /private/tmp/thor.marker && echo extra",
            "/usr/bin/touch /private/tmp/thor.marker | cat",
        ]:
            with self.subTest(command=command):
                self.assertFalse(exact_touch(command, self.marker))

    def test_other_effects_and_malformed_commands_refuse(self):
        for command in [
            "/usr/bin/touch /private/tmp/wrong.marker",
            "/usr/bin/touch /private/tmp/thor.marker /private/tmp/extra",
            "touch /private/tmp/thor.marker",
            "/usr/bin/touch $(echo /private/tmp/thor.marker)",
            "'unclosed", None,
        ]:
            with self.subTest(command=command):
                self.assertFalse(exact_touch(command, self.marker))

    def test_unrelated_thread_and_unlisted_mutation_rejected_before_send(self):
        client = Client.__new__(Client)
        for method, params in [("thread/delete", {"threadId": "01a14b73-b7a5-7062-865e-ebd47b6b3ce0"}), ("turn/start", {"threadId": "unrelated"})]:
            with self.subTest(method=method), self.assertRaises(ValueError):
                client.request(method, params)


class FakeRecoveryClient:
    def __init__(self, final=True, background=None, missing=False):
        self.pending = []
        self.calls = []
        self.interrupted = False
        self.final = final
        self.background = background or {"data": [], "nextCursor": None}
        self.missing = missing

    def verify(self):
        return {"id": BUILDER, "cwd": REPOSITORY}

    def request(self, method, params):
        self.calls.append((method, params))
        if method == "thread/turns/list":
            return {"data": [] if self.missing else [{"id": "owned-turn", "status": "interrupted" if self.interrupted and self.final else "inProgress", "items": [{"type": "userMessage", "clientId": "unique-dispatch", "content": []}]}], "nextCursor": None}
        if method == "thread/resume":
            return {}
        if method == "turn/interrupt":
            self.interrupted = True
            if self.final:
                self.pending.append({"method": "turn/completed", "params": {"threadId": BUILDER, "turn": {"id": "owned-turn", "status": "interrupted"}}})
            return {}
        if method == "thread/backgroundTerminals/list":
            return self.background
        raise AssertionError("Unexpected operation: "+method)

    def receive(self, timeout):
        raise TimeoutError("Injected missing completion")

    def close(self):
        pass


class RetirementTests(unittest.TestCase):
    dispatch = {"client_id": "unique-dispatch", "text": "unique request"}

    def recover(self, fake, known=None):
        with tempfile.TemporaryDirectory() as directory:
            return retire_dispatch(directory, self.dispatch, known, {"data": [], "nextCursor": None}, factory=lambda _: fake)

    def test_lost_start_response_is_reconciled_without_redispatch(self):
        fake = FakeRecoveryClient()
        result = self.recover(fake)
        self.assertTrue(result["confirmed"])
        interrupts = [p for m,p in fake.calls if m == "turn/interrupt"]
        self.assertEqual(interrupts, [{"threadId": BUILDER, "turnId": "owned-turn"}])
        self.assertFalse(any(m == "turn/start" for m,p in fake.calls))

    def test_interrupt_ack_without_final_state_is_not_cleanup(self):
        result = self.recover(FakeRecoveryClient(final=False))
        self.assertFalse(result["confirmed"])
        self.assertEqual(result["final_status"], "inProgress")

    def test_remaining_process_prevents_cleanup_claim(self):
        result = self.recover(FakeRecoveryClient(background={"data": [{"processId": "owned-child"}], "nextCursor": None}))
        self.assertFalse(result["confirmed"])
        self.assertEqual(result["new_background_terminal_ids"], ["owned-child"])

    def test_unknown_or_mismatched_start_does_not_interrupt_other_work(self):
        for fake, known in [(FakeRecoveryClient(missing=True), None), (FakeRecoveryClient(), "different-turn")]:
            result = self.recover(fake, known)
            self.assertFalse(result["confirmed"])
            self.assertFalse(any(m == "turn/interrupt" for m,p in fake.calls))

    def test_identical_payload_from_a_different_dispatch_is_not_owned(self):
        class OtherDispatch(FakeRecoveryClient):
            def request(self, method, params):
                result = super().request(method, params)
                if method == "thread/turns/list":
                    for turn in result["data"]:
                        turn["items"][0]["clientId"] = "different-dispatch"
                        turn["items"][0]["content"] = [{"type": "text", "text": "unique request"}]
                return result
        fake = OtherDispatch()
        result = self.recover(fake)
        self.assertFalse(result["confirmed"])
        self.assertFalse(any(m == "turn/interrupt" for m,p in fake.calls))


class FakeSettingsClient:
    def __init__(self, lose_update_response=False):
        self.baseline = {"cwd": REPOSITORY, "approvalPolicy": "on-request", "approvalsReviewer": "auto_review", "sandbox": {"type": "workspaceWrite"}, "activePermissionProfile": {"id": ":workspace"}}
        self.current = copy.deepcopy(self.baseline)
        self.current["approvalsReviewer"] = "user"
        self.lose_update_response = lose_update_response
        self.updates = 0

    def request(self, method, params):
        if method == "thread/resume":
            return copy.deepcopy(self.current)
        if method == "thread/settings/update":
            self.updates += 1
            self.current.update({k:params[k] for k in ["approvalPolicy", "approvalsReviewer"]})
            if self.lose_update_response:
                self.lose_update_response = False
                raise TimeoutError("Injected lost update response")
            return {}
        raise AssertionError(method)


class SettingsTests(unittest.TestCase):
    def test_restoration_reads_actual_settings_and_preserves_permissions(self):
        fake = FakeSettingsClient()
        result = restore_settings(fake, fake.baseline, "user")
        self.assertEqual(result["approvalsReviewer"], "auto_review")
        self.assertEqual(result["sandbox"], fake.baseline["sandbox"])
        self.assertEqual(fake.updates, 1)

    def test_finalizer_can_reconcile_lost_restoration_response(self):
        fake = FakeSettingsClient(lose_update_response=True)
        with self.assertRaises(TimeoutError):
            restore_settings(fake, fake.baseline, "user")
        result = restore_settings(fake, fake.baseline, "user")
        self.assertEqual(result["approvalsReviewer"], "auto_review")
        self.assertEqual(fake.updates, 1)

    def test_intervening_unowned_setting_change_is_preserved(self):
        fake = FakeSettingsClient()
        fake.current["approvalPolicy"] = "never"
        with self.assertRaises(RuntimeError):
            restore_settings(fake, fake.baseline, "user")
        self.assertEqual(fake.updates, 0)


if __name__ == "__main__":
    unittest.main()
