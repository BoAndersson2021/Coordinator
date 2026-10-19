"""Fixed harmless probes for native_control qualify; never a product executor."""
import copy
import json
from pathlib import Path
import uuid
import shutil
import shlex

from native_control import (Client, Journal, atomic, collect_turn, endpoint_identity,
                            evidence_record, exact_touch, find_dispatch, history,
                            now, reconcile_run, require, source_identity, summary_run, transport_identity, digest, safe_read, strict_json, BUDGETS)


def run_qualification(binding, directory):
    require(binding["receiver_id"] is None, "Qualification creates a fresh receiver; no existing agent attachment")
    workspace = directory / "workspace"
    workspace.mkdir()
    markers = directory / "markers"
    markers.mkdir()
    snapshot = directory / "source"
    snapshot.mkdir(mode=0o700)
    for name in source_identity():
        shutil.copyfile(Path(__file__).with_name(name), snapshot / name)
        (snapshot / name).chmod(0o600)
    owned = copy.deepcopy(binding)
    owned["repository"] = str(workspace)
    journal = Journal(directory, {
        "format": "codeexp2-native-run/1", "run_id": directory.name, "created_at_utc": now(),
        "binding": owned, "backend": endpoint_identity(binding["socket_path"]),
        "source": source_identity(), "transport": transport_identity(), "receiver_id": None, "ended": False,
        "intents": {}, "requests": {}, "active_dispatch": None, "pending_reconnect": None,
    })
    client = None
    settings = None
    passed = False
    report = {"scope": "Owned durable disposable diagnostics only; no native UI or existing TUI attachment", "cases": [], "passed": False}
    try:
        client = Client(owned, directory, mode="diagnostic")
        client.check_backend(journal.read())
        atomic(directory / "transport.json", client.transport)
        created = journal.send_once("thread-create", "Create one disposable saved receiver", lambda: client.request("thread/start", {
            "cwd": str(workspace), "ephemeral": False, "sandbox": "read-only",
            "approvalPolicy": "on-request", "approvalsReviewer": "user",
            "developerInstructions": "This is an explicitly authorized disposable CodeExp2 protocol diagnostic. Use only the exact harmless requested temporary marker operation once. Never inspect repositories, credentials or other files; never use network tools, delegate, launch agents or retry a denied/interrupted tool. The connected diagnostic client handles exact scoped approvals. Do not request persistent permissions or amendments."
        }), client=client)
        settings = {k: created.get(k) for k in ["cwd", "approvalPolicy", "approvalsReviewer", "sandbox", "model"]}
        require(settings["cwd"] == str(workspace) and settings["approvalPolicy"] == "on-request" and settings["approvalsReviewer"] == "user" and settings["sandbox"]["type"] == "readOnly", "Effective settings not applied")
        receiver = created["thread"]["id"]
        owned["receiver_id"] = receiver
        client.receiver = receiver
        with journal.guard() as state:
            state["receiver_id"] = receiver
            state["binding"] = owned
            state["settings"] = settings
            journal.write(state)
        atomic(directory / "effective-settings.json", settings)
        print(json.dumps({"progress": "receiver-created", "receiver_id": receiver}), flush=True)
        before = client.request("thread/backgroundTerminals/list", {"threadId": receiver})
        require(before == {"data": [], "nextCursor": None} or (not before.get("data") and not before.get("nextCursor")), "Disposable receiver already has processes")
        ordinary = journal.send_once("ordinary", "One harmless in-sandbox touch", lambda: client.request("command/exec", {
            "command": ["/usr/bin/touch", str(workspace / "ordinary.txt")], "cwd": str(workspace),
            "sandboxPolicy": {"type": "workspaceWrite", "writableRoots": [str(workspace)], "networkAccess": False}, "timeoutMs": 10000}), client=client)
        require(ordinary["exitCode"] == 0 and (workspace / "ordinary.txt").is_file(), "Ordinary operation failed")
        report["cases"].append({"name": "ordinary", "passed": True, "exit_code": ordinary["exitCode"]})

        def turn(name, prompt, action=None, marker=None, reconnect=False):
            dispatch = str(uuid.uuid4())
            with journal.guard() as state:
                require(not state["ended"], "Ended diagnostic")
                state["active_dispatch"] = dispatch
                journal.write(state)
            started = journal.send_once("start:" + dispatch, "One named diagnostic turn " + name,
                                       lambda: client.request("turn/start", {"threadId": receiver, "clientUserMessageId": dispatch, "input": [{"type": "text", "text": prompt}]}), client=client)
            tid = started["turn"]["id"]
            require(started["turn"]["status"] == "inProgress", "No active turn observed")
            outcome = collect_turn(client, journal, tid, action, marker, reconnect)
            require(outcome["status"] == ("interrupted" if action == "cancel" else "completed"), "Unexpected final status")
            if action:
                require(outcome["requests"], "No real approval request")
                require(marker.exists() == (action == "accept"), "Unexpected actual marker effect")
            if not reconnect:
                native = find_dispatch(history(client, journal.read()), dispatch)
                commands = [i for i in native.get("items", []) if i.get("type") == "commandExecution"]
                if action:
                    require(len(commands) <= 1 and all(exact_touch(i.get("command"), marker) for i in commands), "Repeated/unexpected command")
                    if action == "accept":
                        require(len(commands) == 1 and commands[0]["status"] == "completed" and commands[0].get("exitCode") == 0, "Command success not proven")
                    else:
                        require(all(i["status"] in {"declined", "failed"} for i in commands), "Declined/cancelled command executed")
                require(client.verify()["status"]["type"] == "idle", "Receiver not idle after turn")
                outcome["native_commands"] = commands
            outcome.update({"name": name, "passed": True, "turn_id": tid, "dispatch_id": dispatch})
            report["cases"].append(outcome)
            atomic(directory / "qualification.json", report)
            print(json.dumps({"progress": name, "passed": True, "turn_id": tid}), flush=True)
            return outcome

        nonce = "CODEEXP2-" + uuid.uuid4().hex
        chat = turn("stream-and-readiness", "Reply with exactly " + nonce + ". No tools or other text.")
        require(chat["text"].strip() == nonce, "Streamed nonce mismatch")
        report["diagnostic_readiness"] = {"nonce": nonce, "turn_id": chat["turn_id"], "scope": "Disposable diagnostic only; not a product builder ACK"}
        for name, action, reconnect in [("accept", "accept", False), ("decline", "decline", False), ("cancel", "cancel", False), ("durable-reconnect", "cancel", True)]:
            marker = markers / (name + ".txt")
            require(not marker.exists(), "Never replay a marker")
            prompt = "Use exec_command exactly ONCE with cmd=" + repr("/usr/bin/touch " + shlex.quote(str(marker))) + ", workdir=" + repr(str(workspace)) + ", sandbox_permissions='require_escalated', justification='One harmless CodeExp2 disposable qualification marker'. Omit prefix_rule. No other tools, file inspection or network. Never retry a denied or interrupted command. After the result, finish with one short sentence."
            turn(name, prompt, action, marker, reconnect)
        client.close()
        client = None
        # This is observation-only unless the preceding owned turn is still active.
        reconciled = reconcile_run(directory)
        require(reconciled["confirmed"], "Final requests/process reconciliation incomplete")
        journal.end()
        try:
            journal.send_once("after-end-probe", "Must never send", lambda: (_ for _ in ()).throw(AssertionError("Sent after end")))
        except ValueError:
            report["end_guard"] = True
        else:
            raise RuntimeError("End guard failed")
        archived = Client(owned, directory, mode="diagnostic")
        try:
            archived.verify()
            with journal.guard() as current:
                archived.check_backend(current)
                archived.request("thread/archive", {"threadId": receiver})
        finally:
            archived.close()
        report["settings"] = settings
        report["source"] = source_identity()
        report["transport"] = journal.read()["transport"]
        report["backend"] = journal.read()["backend"]
        report["receiver_id"] = receiver
        report["workspace"] = str(workspace)
        report["reconciliation"] = reconciled
        report["summary"] = summary_run(directory)
        report["archived"] = True
        report["passed"] = True
        passed = True
        return report
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        if client:
            client.close()
        if not passed and journal.read().get("receiver_id"):
            try:
                report["failure_cleanup"] = reconcile_run(directory, cancel=True, end=True)
            except Exception as error:
                report["cleanup_uncertain"] = str(error)
        atomic(directory / "qualification.json", report)
        evidence_record(owned, directory, None, "qualify", "pass" if passed else "fail",
                        "Disposable native qualification; see qualification.json for per-operation results and excluded scope", settings, complete=passed)


def verify_transcript(directory, record, report, state):
    """Reconstruct bounded claims from pinned native frames, never case flags alone.

    Private local custody is the trust boundary. Hashes do not authenticate a
    hostile same-user producer; imported records are not an admission route.
    """
    receiver, workspace = state["receiver_id"], state["binding"]["repository"]
    events = []
    generations = set()
    for artifact in record["artifacts"]:
        if not artifact["path"].startswith("events-") or not artifact["path"].endswith(".jsonl"):
            continue
        rows = [strict_json(line) for line in safe_read(directory, artifact["path"], BUDGETS["evidence_bytes"]).decode().splitlines()]
        require(rows, "Empty native trace")
        generation = rows[0]["generation"]
        require(generation not in generations and artifact["path"] == "events-" + generation + ".jsonl", "Trace generation mismatch")
        generations.add(generation)
        for row in rows:
            require(row["generation"] == generation and row["backend"] == state["backend"] and row["transport_sha256"] == digest(state["transport"]), "Trace backend/dependency mismatch")
            require(isinstance(row["producer_pid"], int) and row["producer_pid"] > 0 and row["direction"] in {"sent", "received"}, "Trace producer/direction missing")
            require(row["message"].get("params", {}).get("threadId") in {None, receiver}, "Foreign native trace receiver")
        require(len({r["producer_pid"] for r in rows}) == 1, "Trace process changed")
        events.extend(rows)
    require(events, "No native transcripts; pass flags are insufficient")
    sent = [r for r in events if r["direction"] == "sent"]
    received = [r for r in events if r["direction"] == "received"]
    for row in sent:
        message = row["message"]
        method = message.get("method", "")
        if (method.startswith("thread/") and method != "thread/start") or method.startswith("turn/"):
            require(message.get("params", {}).get("threadId") == receiver, "Missing/wrong native RPC receiver")

    def rpc(method):
        pairs = []
        for request in sent:
            m = request["message"]
            if m.get("method") != method:
                continue
            replies = [r["message"] for r in received if r["generation"] == request["generation"] and r["message"].get("id") == m["id"] and "method" not in r["message"]]
            require(len(replies) == 1 and "result" in replies[0] and "error" not in replies[0], "Missing/ambiguous native RPC receipt: " + method)
            pairs.append((request, replies[0]["result"]))
        return pairs

    def notices(method, turn_id=None):
        return [r for r in received if r["message"].get("method") == method and (turn_id is None or r["message"]["params"].get("turnId", r["message"]["params"].get("turn", {}).get("id")) == turn_id)]

    created = rpc("thread/start")
    require(len(created) == 1, "Expected exactly one native receiver creation")
    request, result = created[0]
    p = request["message"]["params"]
    require(result["thread"]["id"] == receiver and result["cwd"] == workspace and p["cwd"] == workspace and p["ephemeral"] is False, "Native creation binding mismatch")
    require(p["sandbox"] == "read-only" and p["approvalPolicy"] == "on-request" and p["approvalsReviewer"] == "user", "Native requested settings changed")
    require({k: result[k] for k in report["settings"]} == report["settings"], "Native effective settings mismatch")
    ordinary = rpc("command/exec")
    require(len(ordinary) == 1 and ordinary[0][0]["message"]["params"]["command"] == ["/usr/bin/touch", str(directory / "workspace/ordinary.txt")] and ordinary[0][1]["exitCode"] == 0, "Native ordinary operation not proven")
    ordinary_params = ordinary[0][0]["message"]["params"]
    require(ordinary_params.get("cwd") == workspace and ordinary_params.get("sandboxPolicy") == {"type": "workspaceWrite", "writableRoots": [workspace], "networkAccess": False}, "Native ordinary workspace/permissions changed")
    require((directory / "workspace/ordinary.txt").is_file(), "Ordinary marker missing")
    cases = {c["name"]: c for c in report["cases"]}
    require(len(cases) == len(report["cases"]) == 6, "Duplicate/missing cases")
    starts = rpc("turn/start")
    require(len(starts) == 5, "Unexpected/repeated native dispatch")
    interrupts = rpc("turn/interrupt")
    require(len(interrupts) == 2, "Unexpected/repeated cancellation")
    expected_decisions = set()
    for name in ["stream-and-readiness", "accept", "decline", "cancel", "durable-reconnect"]:
        case = cases[name]
        tid, dispatch = case["turn_id"], case["dispatch_id"]
        matches = [(r, result) for r, result in starts if r["message"]["params"].get("clientUserMessageId") == dispatch]
        require(len(matches) == 1 and matches[0][1]["turn"]["id"] == tid and matches[0][1]["turn"]["status"] == "inProgress", "Native dispatch/turn binding mismatch")
        users = notices("item/completed", tid)
        require(any(r["message"]["params"]["item"].get("type") == "userMessage" and r["message"]["params"]["item"].get("clientId") == dispatch for r in users), "Native user-message identity absent")
        final = notices("turn/completed", tid)
        expected = "interrupted" if name in {"cancel", "durable-reconnect"} else "completed"
        require(final and all(r["message"]["params"]["turn"]["status"] == expected for r in final), "Native final state absent/conflicting")
        approvals = notices("item/commandExecution/requestApproval", tid)
        if name == "stream-and-readiness":
            require(not approvals, "Unexpected chat approval")
            nonce = report["diagnostic_readiness"]["nonce"]
            require(nonce in matches[0][0]["message"]["params"]["input"][0]["text"] and "".join(r["message"]["params"]["delta"] for r in notices("item/agentMessage/delta", tid)).strip() == nonce, "Native nonce stream not proven")
            continue
        marker = directory / "markers" / (name + ".txt")
        require(approvals and len({(r["message"]["id"], r["message"]["params"]["itemId"], r["message"]["params"]["command"]) for r in approvals}) == 1, "Native approval identity ambiguous")
        approval = approvals[0]["message"]
        p = approval["params"]
        require(p["cwd"] == workspace and exact_touch(p["command"], marker) and not p.get("networkApprovalContext"), "Native action scope changed")
        require(marker.exists() == (name == "accept"), "Marker outcome mismatch")
        resolution = notices("serverRequest/resolved")
        require(any(r["message"]["params"].get("requestId") == approval["id"] and r["generation"] in {a["generation"] for a in approvals} for r in resolution), "Native request resolution absent")
        responses = [r for r in sent if "method" not in r["message"] and r["message"].get("id") == approval["id"] and r["generation"] in {a["generation"] for a in approvals}]
        if name in {"accept", "decline"}:
            require(len(responses) == 1 and responses[0]["message"]["result"] == {"decision": name}, "Native decision missing/repeated/changed")
            expected_decisions.add((responses[0]["generation"], approval["id"]))
        else:
            require(not responses, "Cancellation sent an approval decision")
            exact = [(r, res) for r, res in interrupts if r["message"]["params"] == {"threadId": receiver, "turnId": tid}]
            require(len(exact) == 1, "Exact native cancellation absent")
            if name == "durable-reconnect":
                require(len({a["generation"] for a in approvals}) >= 2 and len({a["producer_pid"] for a in approvals}) >= 2 and exact[0][0]["producer_pid"] != matches[0][0]["producer_pid"], "Separate-process pending reconnect not proven")
        commands = {r["message"]["params"]["item"]["id"]: r["message"]["params"]["item"] for r in notices("item/completed", tid) if r["message"]["params"]["item"].get("type") == "commandExecution"}
        require(len(commands) <= 1 and all(exact_touch(i["command"], marker) for i in commands.values()), "Repeated/unexpected native command")
        if name == "accept":
            require(len(commands) == 1 and all(i["status"] == "completed" and i.get("exitCode") == 0 for i in commands.values()), "Accepted command success absent")
        else:
            require(all(i["status"] in {"declined", "failed"} for i in commands.values()), "Denied/interrupted command executed")
    actual_decisions = {(r["generation"], r["message"].get("id")) for r in sent if "method" not in r["message"]}
    require(actual_decisions == expected_decisions, "Unscoped wire decision")
    background = rpc("thread/backgroundTerminals/list")
    require(background and all(not r.get("data") and not r.get("nextCursor") for _, r in background), "Native process inventory incomplete/nonempty")
    require(len(rpc("thread/archive")) == 1, "Owned receiver archival absent")
