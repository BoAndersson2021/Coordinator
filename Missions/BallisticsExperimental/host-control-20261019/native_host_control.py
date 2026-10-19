"""Mission-scoped client for the installed Codex Unix WebSocket protocol."""
import argparse
import json
import time
import uuid
from pathlib import Path
from websockets.sync.client import unix_connect

BUILDER = "01a14b73-b7a5-7062-865e-ebd47b6b3ce0"
REPOSITORY = "/Users/boandersson/Desktop/BallisticsExperimental"


class Client:
    def __init__(self, evidence):
        self.evidence = Path(evidence)
        self.evidence.mkdir(exist_ok=False)
        self.log = (self.evidence / "events.jsonl").open("x")
        self.ws = unix_connect(
            path=str(Path.home() / ".codex/app-server-control/app-server-control.sock"),
            uri="ws://localhost", open_timeout=10, max_size=64 * 1024 * 1024, legacy=True,
        )
        self.sequence = 0
        self.pending = []
        self.request("initialize", {"clientInfo": {"name": "codeexp2_coordinator_thor", "version": "1.0.0"}, "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized", "params": {}})

    def send(self, value):
        self.log.write(json.dumps({"direction": "sent", "message": value}) + "\n")
        self.log.flush()
        self.ws.send(json.dumps(value))

    def receive(self, timeout=30):
        value = json.loads(self.ws.recv(timeout=timeout))
        self.log.write(json.dumps({"direction": "received", "message": value}) + "\n")
        self.log.flush()
        return value

    def request(self, method, params, timeout=30):
        if method not in {"initialize", "thread/list", "thread/read", "thread/turns/list", "thread/items/list", "thread/resume", "thread/settings/update", "thread/backgroundTerminals/list", "turn/start", "turn/interrupt"}:
            raise ValueError("Method outside this mission client's scope")
        if method not in {"initialize", "thread/list"} and params.get("threadId") != BUILDER:
            raise ValueError("Wrong builder")
        self.sequence += 1
        request_id = self.sequence
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            message = self.receive(max(.1, deadline - time.monotonic()))
            if message.get("id") == request_id and ("result" in message or "error" in message):
                if "error" in message:
                    raise RuntimeError(json.dumps(message["error"]))
                return message["result"]
            self.pending.append(message)
        raise TimeoutError(method)

    def save(self, name, value):
        (self.evidence / name).write_text(json.dumps(value, indent=2) + "\n")

    def verify(self):
        result = self.request("thread/read", {"threadId": BUILDER, "includeTurns": False})
        self.save("thread.json", result)
        thread = result["thread"]
        if thread["id"] != BUILDER or thread["cwd"] != REPOSITORY:
            raise RuntimeError("Builder identity/repository mismatch")
        return thread

    def close(self):
        self.ws.close()
        self.log.close()


def find_dispatch(client, dispatch):
    """Reconcile a start by its saved client message identity, never redispatch."""
    cursor = None
    matches = {}
    for _ in range(4):
        page = client.request("thread/turns/list", {"threadId": BUILDER, "limit": 20, "itemsView": "full", "sortDirection": "desc", "cursor": cursor})
        for turn in page["data"]:
            for item in turn.get("items", []):
                if item.get("type") != "userMessage":
                    continue
                if item.get("clientId") == dispatch["client_id"]:
                    matches[turn["id"]] = turn
        cursor = page.get("nextCursor")
        if matches or not cursor:
            break
    if len(matches) != 1:
        raise RuntimeError("Start outcome unresolved: expected exactly one matching persisted user message")
    return next(iter(matches.values()))


def terminal_keys(value):
    keys = [item.get("processId", item.get("id")) for item in value.get("data", [])]
    if any(key is None for key in keys) or value.get("nextCursor"):
        raise RuntimeError("Background process ownership cannot be fully enumerated")
    return set(keys)


def retire_dispatch(evidence, dispatch, known_turn=None, before_processes=None, factory=Client):
    """Confirm final state/processes after errors, using a fresh native connection."""
    client = None
    result = {"confirmed": False, "turn_id": known_turn, "error": None}
    try:
        client = factory(Path(evidence) / ("cleanup-" + uuid.uuid4().hex))
        client.verify()
        turn = find_dispatch(client, dispatch)
        if known_turn is not None and turn["id"] != known_turn:
            raise RuntimeError("Saved turn and dispatch identity disagree")
        result["turn_id"] = turn["id"]
        if turn["status"] not in {"completed", "failed", "interrupted"}:
            client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
            client.request("turn/interrupt", {"threadId": BUILDER, "turnId": turn["id"]})
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    event = client.pending.pop(0) if client.pending else client.receive(max(.1, deadline-time.monotonic()))
                except TimeoutError:
                    break
                if event.get("method") == "turn/completed" and event.get("params", {}).get("threadId") == BUILDER and event["params"]["turn"]["id"] == turn["id"]:
                    break
            turn = find_dispatch(client, dispatch)
        result["final_status"] = turn["status"]
        result["background_terminals"] = client.request("thread/backgroundTerminals/list", {"threadId": BUILDER})
        if before_processes is None:
            raise RuntimeError("No before-process inventory; cleanup remains unproven")
        result["new_background_terminal_ids"] = sorted(terminal_keys(result["background_terminals"]) - terminal_keys(before_processes))
        result["confirmed"] = turn["status"] in {"completed", "failed", "interrupted"} and not result["new_background_terminal_ids"]
    except Exception as error:
        result["error"] = str(error)
    finally:
        Path(evidence, "RETIREMENT.json").write_text(json.dumps(result, indent=2)+"\n")
        if client is not None:
            client.close()
    return result


def restore_settings(client, baseline, expected_reviewer):
    """Restore only owned probe settings, then read back actual effective state."""
    current = client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
    if current.get("cwd") != REPOSITORY or baseline.get("cwd") != REPOSITORY:
        raise RuntimeError("Settings repository mismatch")
    for key in ["sandbox", "activePermissionProfile"]:
        if current.get(key) != baseline.get(key):
            raise RuntimeError("Unrelated permission state changed; refusing to overwrite it")
    desired = (baseline["approvalPolicy"], baseline["approvalsReviewer"])
    actual = (current["approvalPolicy"], current["approvalsReviewer"])
    if actual != desired:
        if actual != ("on-request", expected_reviewer):
            raise RuntimeError("Intervening approval-settings change; restore ownership unresolved")
        client.request("thread/settings/update", {"threadId": BUILDER, "approvalPolicy": desired[0], "approvalsReviewer": desired[1]})
    readback = client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
    if any(readback.get(k) != baseline.get(k) for k in ["approvalPolicy", "approvalsReviewer", "sandbox", "activePermissionProfile", "cwd"]):
        raise RuntimeError("Effective settings restoration not confirmed")
    return {k: readback.get(k) for k in ["approvalPolicy", "approvalsReviewer", "sandbox", "activePermissionProfile", "cwd"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["inspect", "ack"])
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--request")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    client = Client(args.evidence)
    dispatch = None
    turn_id = None
    final_observed = False
    before_processes = None
    try:
        thread = client.verify()
        print(json.dumps({"builder": BUILDER, "cwd": thread["cwd"], "status": thread["status"]}), flush=True)
        if args.action == "inspect":
            return
        if thread["status"]["type"] not in {"idle", "notLoaded"}:
            raise RuntimeError("Builder is already active; no dispatch")
        request = json.loads(Path(args.request).read_text())
        if request["recipient"]["session_id"] != BUILDER or request["repository"] != REPOSITORY:
            raise ValueError("Wrong request target")
        baseline = client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
        client.save("effective-settings.json", baseline)
        print(json.dumps({"effective": {k: baseline.get(k) for k in ["approvalPolicy", "approvalsReviewer", "sandbox", "activePermissionProfile", "cwd"]}}), flush=True)
        before_processes = client.request("thread/backgroundTerminals/list", {"threadId": BUILDER})
        client.save("before-processes.json", before_processes)
        dispatch = {"client_id": str(uuid.uuid4()), "text": json.dumps(request), "message_id": request["message_id"]}
        client.save("dispatch.json", dispatch)
        result = client.request("turn/start", {"threadId": BUILDER, "clientUserMessageId": dispatch["client_id"], "input": [{"type": "text", "text": dispatch["text"]}]})
        turn_id = result["turn"]["id"]
        client.save("started.json", result)
        print(json.dumps({"turn_started": turn_id}), flush=True)
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            try:
                message = client.pending.pop(0) if client.pending else client.receive(min(60, max(.1, deadline-time.monotonic())))
            except TimeoutError:
                print(json.dumps({"waiting_for_turn": turn_id}), flush=True)
                continue
            if "method" in message and "id" in message:
                client.save("unexpected-server-request.json", message)
                raise RuntimeError("Unexpected approval/input request; exact-turn cleanup follows")
            if message.get("method") == "turn/completed":
                params = message["params"]
                if params.get("threadId") == BUILDER and params["turn"]["id"] == turn_id:
                    client.save("completed.json", params)
                    final_observed = True
                    turns = client.request("thread/turns/list", {"threadId": BUILDER, "limit": 1, "itemsView": "full", "sortDirection": "desc"})
                    client.save("collected.json", turns)
                    finals = [i["text"] for t in turns["data"] if t["id"] == turn_id for i in t.get("items", []) if i["type"] == "agentMessage" and i.get("phase") == "final_answer"]
                    print(json.dumps({"turn": turn_id, "status": params["turn"]["status"], "finals": finals}), flush=True)
                    if params["turn"]["status"] != "completed":
                        raise RuntimeError("Builder turn did not complete successfully")
                    return
        raise TimeoutError("Assignment exceeded bounded time; exact-turn cleanup follows")
    except BaseException:
        if dispatch is not None and not final_observed:
            retirement = retire_dispatch(args.evidence, dispatch, turn_id, before_processes)
            print(json.dumps({"cleanup": retirement}), flush=True)
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()
