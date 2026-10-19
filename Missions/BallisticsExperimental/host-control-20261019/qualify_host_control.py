"""Bounded native accept/decline/cancel probes on the existing builder only."""
import argparse
import json
import shlex
import time
import uuid
from pathlib import Path
from native_host_control import Client, BUILDER, REPOSITORY, retire_dispatch, restore_settings


def exact_touch(command, marker):
    if not isinstance(command, str) or any(c in command for c in "\n\r\x00;&|<>$`"):
        return False
    canonical = "/usr/bin/touch " + shlex.quote(str(marker))
    if command == canonical:
        return True
    try:
        words = shlex.split(command or "")
        if len(words) == 3 and words[0] in {"/bin/zsh", "/bin/bash", "/bin/sh"} and words[1] in {"-lc", "-c"}:
            return words[2] == canonical
    except ValueError:
        return False
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["auto", "accept", "decline", "cancel"])
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args()
    run = Path(args.evidence)
    client = Client(run)
    marker_root = Path("/Users/boandersson/Desktop/CodeExp2/Launcher/build/thor-host-control/qualification")
    marker_root.mkdir(parents=True, exist_ok=True)
    marker = marker_root / (run.name + ".marker")
    if marker.exists():
        raise RuntimeError("Probe marker already exists; never replay")
    turn_id = None
    completed = False
    approval_seen = False
    replay_seen = False
    command_items = []
    start_baseline = None
    interrupted = False
    settings_restored = False
    settings_may_change = False
    dispatch = None
    try:
        thread = client.verify()
        if thread["status"]["type"] not in {"idle", "notLoaded"}:
            raise RuntimeError("Builder busy; no probe dispatch")
        start_baseline = client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
        client.save("baseline-settings.json", start_baseline)
        before_processes = client.request("thread/backgroundTerminals/list", {"threadId": BUILDER})
        client.save("before-processes.json", before_processes)
        reviewer = "auto_review" if args.phase == "auto" else "user"
        probe = {
            "protocol": "builder-communication/1", "message_id": "THOR-HOST-PROBE-"+run.name,
            "assignment_id": "BE-HOST-SETUP-20261019-THOR", "reply_to": "THOR-HOST-ACK-20261019-1",
            "type": "assignment", "sender": {"role": "coordinator", "session_id": None},
            "recipient": {"role": "builder", "session_id": BUILDER}, "repository": REPOSITORY,
            "summary": "Coordinator Thor: one disposable native control qualification probe; no product work.",
            "body": {
                "baseline": {"head": "bf8753ed55da5e94e9e85042c98b0b0d6b6559c9", "branch": "main", "dirty_paths": None, "state_evidence": None, "limitations": ["Preserve existing dirty work."]},
                "outcome": "Exercise exact native approval action for phase "+args.phase,
                "scope": "Immediately call exec_command exactly ONCE with cmd="+repr("/usr/bin/touch "+str(marker))+", workdir="+repr(REPOSITORY)+", sandbox_permissions=require_escalated and justification='Disposable Coordinator Thor host-control qualification marker outside builder workspace'. Omit prefix_rule. The marker path is explicitly authorized setup scratch. No other commands or file edits in this turn.",
                "constraints": ["Do not delegate, retry, change permissions, use shell redirection, create alternate markers, install anything, build or run game/replay. A decline or interruption is the expected test outcome, not a defect to repair.", "Native server temporarily selects reviewer "+reviewer+" for this setup-only probe. Coordinator responds to the exact request or interrupts it. Existing automatic reviewer is restored afterward.", "If command approval is unavailable, report it; do not route around it. No need to reread all docs for this single bounded probe; use fresh readiness baseline."],
                "acceptance_checks": ["Exact one requested command/action, native request resolution and actual marker outcome; cancellation checked separately by Coordinator."],
                "return_evidence": ["After the single tool result, immediately return compact JSON completion with outcome, changed_paths, checks, evidence, limitations and next_action. No additional tool calls. On interruption no final is expected."]
            }
        }
        client.save("request.json", probe)
        dispatch = {"client_id": str(uuid.uuid4()), "text": json.dumps(probe), "message_id": probe["message_id"]}
        client.save("dispatch.json", dispatch)
        settings_may_change = True
        result = client.request("turn/start", {"threadId": BUILDER, "clientUserMessageId": dispatch["client_id"], "approvalPolicy": "on-request", "approvalsReviewer": reviewer, "input": [{"type": "text", "text": dispatch["text"]}]})
        turn_id = result["turn"]["id"]
        client.save("started.json", result)
        print(json.dumps({"phase": args.phase, "turn": turn_id, "marker": str(marker)}), flush=True)
        deadline = time.monotonic()+240
        while time.monotonic()<deadline:
            try:
                message = client.pending.pop(0) if client.pending else client.receive(min(30, max(.1, deadline-time.monotonic())))
            except TimeoutError:
                print(json.dumps({"waiting": args.phase}), flush=True)
                continue
            params = message.get("params", {})
            if "method" in message and "id" in message:
                client.save("approval-request.json" if not approval_seen else "replayed-approval-request.json", message)
                if message["method"] != "item/commandExecution/requestApproval" or params.get("threadId") != BUILDER or params.get("turnId") != turn_id or params.get("cwd") != REPOSITORY or not exact_touch(params.get("command"), marker) or params.get("networkApprovalContext"):
                    client.request("turn/interrupt", {"threadId": BUILDER, "turnId": turn_id})
                    interrupted = True
                    raise RuntimeError("Unexpected request; exact turn interrupted without approval")
                print(json.dumps({"pending_request": message["id"], "phase": args.phase, "command": params["command"]}), flush=True)
                if args.phase == "auto":
                    raise RuntimeError("Automatic reviewer unexpectedly required manual decision")
                if args.phase == "cancel" and not approval_seen:
                    approval_seen = True
                    original_item = params["itemId"]
                    client.close()
                    client = Client(str(run)+"-reconnect-pending")
                    current = client.verify()
                    client.save("pending-state.json", current)
                    client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
                    continue
                if args.phase == "cancel":
                    replay_seen = params["itemId"] == original_item
                    if not replay_seen:
                        raise RuntimeError("Reconnected request does not match original item")
                    client.request("turn/interrupt", {"threadId": BUILDER, "turnId": turn_id})
                    interrupted = True
                else:
                    decision = "accept" if args.phase == "accept" else "decline"
                    client.send({"id": message["id"], "result": {"decision": decision}})
                    approval_seen = True
            if message.get("method") == "item/completed" and params.get("threadId") == BUILDER and params.get("turnId") == turn_id:
                if params.get("item", {}).get("type") == "commandExecution":
                    command_items.append(params["item"])
            if message.get("method") == "turn/completed" and params.get("threadId") == BUILDER and params["turn"]["id"] == turn_id:
                client.save("completed.json", params)
                status = params["turn"]["status"]
                completed = True
                break
        if not completed:
            raise TimeoutError("Probe did not reach final turn state")
        restored = restore_settings(client, start_baseline, reviewer)
        client.save("restored-settings.json", restored)
        settings_restored = True
        client.close()
        client = Client(str(run)+"-reconnect-final")
        after = client.verify()
        saved = client.request("thread/turns/list", {"threadId": BUILDER, "limit": 1, "itemsView": "full", "sortDirection": "desc"})
        client.save("final-history.json", saved)
        observed = next(t for t in saved["data"] if t["id"] == turn_id)
        after_processes = client.request("thread/backgroundTerminals/list", {"threadId": BUILDER})
        client.save("after-processes.json", after_processes)
        expected_marker = args.phase in {"auto", "accept"}
        paths = [run/"events.jsonl", Path(str(run)+"-reconnect-pending")/"events.jsonl", Path(str(run)+"-reconnect-final")/"events.jsonl"]
        messages = [json.loads(line)["message"] for path in paths if path.exists() for line in path.read_text().splitlines()]
        request_ids = {m["id"] for m in messages if m.get("method")=="item/commandExecution/requestApproval" and m.get("params",{}).get("turnId")==turn_id}
        resolved = [m for m in messages if m.get("method")=="serverRequest/resolved" and m.get("params",{}).get("requestId") in request_ids]
        guardian_approved = [m for m in messages if m.get("method")=="guardianWarning" and "review approved" in m.get("params",{}).get("message","")]
        commands = [item for item in observed.get("items",[]) if item.get("type")=="commandExecution"]
        requested_items = {m["params"]["itemId"] for m in messages if m.get("method")=="item/commandExecution/requestApproval" and m.get("params",{}).get("turnId")==turn_id}
        exact_actions = (len(commands)==1 and exact_touch(commands[0].get("command"),marker)) if expected_marker else (len(requested_items)==1 and len(commands)<=1 and all(exact_touch(i.get("command"),marker) for i in commands))
        action_result = (commands[0].get("status")=="completed" and commands[0].get("exitCode")==0) if expected_marker and exact_actions else (exact_actions and all(i.get("status") in {"declined","failed"} for i in commands))
        resolution_proven = bool(guardian_approved) if args.phase=="auto" else bool(resolved)
        passed = marker.exists() == expected_marker and observed["status"] == ("interrupted" if args.phase == "cancel" else "completed") and (approval_seen or args.phase == "auto") and (replay_seen if args.phase == "cancel" else True) and before_processes == after_processes and resolution_proven and exact_actions and action_result
        report = {"phase": args.phase, "turn_id": turn_id, "marker": str(marker), "marker_exists": marker.exists(), "approval_seen": approval_seen, "replayed_pending_request": replay_seen, "status": status, "reconnected_status": observed["status"], "thread_status": after["status"], "command_items": commands, "native_request_resolution": resolved, "native_automatic_review": guardian_approved, "exactly_one_scoped_action": exact_actions, "before_processes": before_processes, "after_processes": after_processes, "passed": passed, "scope": "Host control qualification only; no product/runtime qualification."}
        (run/"RESULT.json").write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps({k:v for k,v in report.items() if k!="command_items"}), flush=True)
        if not passed:
            raise RuntimeError("Native probe acceptance failed; inspect retained evidence")
    finally:
        retirement = None
        if dispatch is not None and not completed:
            retirement = retire_dispatch(run, dispatch, turn_id, before_processes)
            print(json.dumps({"cleanup": retirement}), flush=True)
        if start_baseline and settings_may_change and not settings_restored:
            restorer = None
            try:
                if retirement is not None and not retirement["confirmed"]:
                    raise RuntimeError("Executor retirement unresolved; settings restoration held")
                restorer = Client(run/("settings-recovery-"+uuid.uuid4().hex))
                restorer.verify()
                restored = restore_settings(restorer, start_baseline, reviewer)
                restorer.save("restored-settings.json", restored)
                settings_restored = True
            except Exception as error:
                diagnosis = {"settings_restore_uncertain": str(error), "turn": turn_id}
                (run/"SETTINGS_RESTORE_UNCERTAIN.json").write_text(json.dumps(diagnosis,indent=2)+"\n")
                print(json.dumps(diagnosis), flush=True)
            finally:
                if restorer is not None:
                    restorer.close()
        client.close()


if __name__ == "__main__":
    main()
