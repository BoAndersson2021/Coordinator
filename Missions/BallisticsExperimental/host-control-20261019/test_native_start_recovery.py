"""One real pending-approval probe simulating a discarded turn/start reply."""
import json
import time
import uuid
from pathlib import Path
from native_host_control import Client, BUILDER, REPOSITORY, retire_dispatch, restore_settings
from qualify_host_control import exact_touch


def main():
    root = Path(__file__).resolve().parent
    run = root / "lost-start-1"
    client = Client(run)
    baseline = None
    dispatch = None
    before_processes = None
    marker = Path("/Users/boandersson/Desktop/CodeExp2/Launcher/build/thor-host-control/qualification/lost-start-1.marker")
    assert not marker.exists(), "No replay of existing marker"
    retired = None
    try:
        thread = client.verify()
        assert thread["status"]["type"] in {"idle", "notLoaded"}
        baseline = client.request("thread/resume", {"threadId": BUILDER, "excludeTurns": True})
        before_processes = client.request("thread/backgroundTerminals/list", {"threadId": BUILDER})
        probe = json.loads((root/"probe-cancel-1/request.json").read_text())
        probe["message_id"] = "THOR-LOST-START-20261019-1"
        probe["sender"]["session_id"] = "01a15430-c8d2-74c0-86bc-04dfd8a42dc7"
        probe["body"]["scope"] = "Immediately call exec_command exactly ONCE with cmd="+repr("/usr/bin/touch "+str(marker))+", workdir="+repr(REPOSITORY)+", sandbox_permissions=require_escalated and a justification question for this disposable qualification marker outside the builder workspace. Omit prefix_rule. No other tool calls, edits or product work. Coordinator will interrupt while this request is pending; no retry."
        client.save("request.json", probe)
        dispatch = {"client_id": str(uuid.uuid4()), "text": json.dumps(probe), "message_id": probe["message_id"]}
        client.save("dispatch.json", dispatch)
        # Intentionally discard the returned turn id: recovery gets only the persisted dispatch.
        client.request("turn/start", {"threadId": BUILDER, "clientUserMessageId": dispatch["client_id"], "approvalPolicy": "on-request", "approvalsReviewer": "user", "input": [{"type": "text", "text": dispatch["text"]}]})
        deadline = time.monotonic()+120
        while time.monotonic()<deadline:
            message = client.pending.pop(0) if client.pending else client.receive(30)
            if "method" in message and "id" in message:
                params = message.get("params", {})
                assert message["method"]=="item/commandExecution/requestApproval" and params.get("threadId")==BUILDER and params.get("cwd")==REPOSITORY and exact_touch(params.get("command"),marker)
                client.save("pending.json", message)
                break
        else:
            raise TimeoutError("No pending approval observed")
        client.close()
        retired = retire_dispatch(run, dispatch, None, before_processes)
        assert retired["confirmed"] and retired["final_status"]=="interrupted" and not marker.exists()
    finally:
        if dispatch is not None and retired is None:
            retired = retire_dispatch(run, dispatch, None, before_processes)
        if baseline is not None and retired and retired["confirmed"]:
            restorer = Client(run/"settings-readback")
            try:
                restorer.verify()
                settings = restore_settings(restorer, baseline, "user")
                restorer.save("restored.json", settings)
            finally:
                restorer.close()
        client.close()
    result = {"pass": True, "retirement": retired, "marker_absent": not marker.exists(), "scope": "Real native discarded-start-response reconciliation and exact cancellation; no product work or duplicate start."}
    (run/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result),flush=True)


if __name__ == "__main__":
    main()
