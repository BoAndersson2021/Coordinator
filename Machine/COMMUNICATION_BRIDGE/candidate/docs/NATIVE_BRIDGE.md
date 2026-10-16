# Native inspection communication bridge

This bridge removes manual delivery and receipt-file preparation from the
existing inspection workflow. The CodeExp2 coordinator still reasons about the
assignment and independently reviews the reply. Machine sends the recorded
inspection, collects the matching completed answer, and preserves recovery state.

The initial route supports one existing registered Brainstorm or Modeling role
per Blender project binding. It uses the project's active pinned route, existing
account and local Codex control socket. It never launches a daemon, creates or
resumes an agent, starts a model turn on another execution route, changes billing,
or accesses Blender. The receiving harness retains execution permissions.

## Configure once, explicitly

Use an existing project and agent binding. Inspect their actual identities first.
Configuration validates the active project release, source inventory, literal
adapter digest recipe and registry. It records the exact manifest digest and
endpoint in the existing project record. It cannot silently replace a bound route.

```sh
./Machine bridge-configure --project blender-project \
  --endpoint unix:/Users/boandersson/.codex/app-server-control/app-server-control.sock \
  --registry /Users/boandersson/Desktop/Blender_Project/.runtime/session.json \
  --role brainstorm \
  --route-manifest /Users/boandersson/Desktop/Blender_Project/Routes/releases/routing-governance-v1/MANIFEST.json \
  --operation-id NEW_UUID
./Machine bridge-observe --agent blender-brainstorm-01a136be --operation-id NEW_UUID
```

These UUIDs are new operation identities, not literal `NEW_UUID` arguments.
Configured paths and the role registry must still match the actual project.
The local operator remains trusted; hashes do not authenticate a principal.

## Send a prepared inspection and collect its answer

Prepare a new authorized inspection with the existing `task-prepare` command.
The brief remains limited to the pinned AGENTS.md and README.md inputs. Then:

```sh
./Machine bridge-send --id TASK --expected-version 1 --operation-id ATTEMPT_UUID
./Machine bridge-collect --id TASK
./Machine work-view
```

Send refreshes the actual thread/workspace observation, captures the latest
history position, rechecks the existing dispatch gates and commits delivery
intent before `thread/queue/add`. Only the newly committed sender may submit.
The queue request uses the attempt UUID as `clientUserMessageId`. A matching
queue acknowledgement records delivery; no acknowledgement implies no claim
of execution. Repeating send never submits again, even with a different UUID
against the pending or delivered task.

Collection never sends. It scans bounded paginated native history back to the
saved position and requires exact user-input equality with the retained envelope.
Quoted prompts and unrelated turns cannot match. Multiple matching turns reject
as ambiguous. Only a completed turn with an explicit final answer becomes a
report. Failed, interrupted and in-progress turns remain observable execution
outcomes. A completed report remains `reported` until the existing independent
review and closure steps occur.

`work-view` reads retained task state and reports without a connection. Call
`bridge-collect` explicitly to refresh live evidence. There is no background
poller or automatic startup dispatch. A project-role move or pinned-source change
requires inspection through the existing replacement or release process.

## Interruption and recovery

A cut after dispatch intent, a lost queue acknowledgement, or failed receipt
persistence leaves pending or uncertain delivery. After coordinator replacement,
run status and `work-view`, then collect that same task. An exact matching queued
input or actual turn can reconcile delivery. Absence from history does not prove
non-delivery and does not permit automatic resend. A cut before submission can
therefore require manual reconciliation; the bridge favors visible uncertainty
over duplicated work. Historical manually delivered tasks retain their existing
inspection/reconciliation route.

## Protocol and validation scope

The standard-library client connects only to an existing user-owned Unix socket.
It implements bounded WebSocket framing and request deadlines and exposes only
thread metadata/history reads, queue inspection and queue addition. It sends the
required initialization handshake with experimental protocol capability enabled.
No generic RPC, shell or execution method is exposed by the CLI.

The protocol was checked against locally generated installed-version schemas and
the [official app-server documentation](https://learn.chatgpt.com/docs/app-server).
Queue addition was inspected in the installed experimental schema. The existing
[CLI queue command](https://learn.chatgpt.com/docs/cli/reference) uses the same
attended-session delivery route. Protocol compatibility requires verification
after an installed Codex change.

Run the existing full validation route:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Fixture tests establish dispatch/recovery behavior and native byte-stream parsing.
Read-only real-socket checks establish observation compatibility only. A real
send, completed reply and fresh coordinator restart are separate live acceptance.
