# Accepted mission runner — first feasibility gate

Date: 2026-10-18. Result: **BLOCKED before mission launch**.

The user accepted [the mission start/end design](../CONTROL_WORKFLOW_PROPOSAL.md).
This bounded check investigated its critical native control dependency. It did
not implement the runner or satisfy its launch/retirement acceptance gate.

## Baseline and actual execution

CodeExp2 HEAD was `5ddad03e16d3728bae68adbe55ea2fba6e0c1fb4`. The opening index
was empty. Opening unstaged work was `Missions/Packages/BuilderCommunication/README.md`
and `Missions/README.md`; untracked work was `Machine/TASK_TIMELINE/`,
`Missions/CONTROL_WORKFLOW_PROPOSAL.md` and `Missions/WEBSITE/`. Those changes were
preserved; the mission index and accepted proposal received scoped updates.

The installed CLI and running daemon both reported `0.163.0`. Static schema
generation used `codex app-server generate-json-schema --experimental --out`
with an agent-owned temporary directory. No configuration or package was changed.

| Attempt | Real interface and request | Observed result |
| --- | --- | --- |
| 1 | `codex app-server proxy --sock /Users/boandersson/.codex/app-server-control/app-server-control.sock`; JSON-line `initialize`, client `codeexp2_mission_feasibility` version `0.1.0`, experimental API opt-in | No response within 10 seconds; only the initialize request was sent. |
| 2 | `codex app-server proxy` using native default discovery; JSON-line `initialize`, same client/version, no experimental opt-in | No stdout response within 8 seconds. |
| Cleanup | Close each owned proxy's stdin; wait for its exit | Both proxy processes exited 0 without stderr; no termination fallback was needed. |
| Shared daemon observation | `codex app-server daemon version` after probes | Reports `running`, CLI/daemon/app-server version `0.163.0`. |

Each client waited for initialization before issuing further operations. Neither
initialization completed, so no `initialized`, thread read/start/resume, model
turn, process spawn/kill, archive or retirement request was sent. The planned
harmless process-handle test was **not reached**. There was no new Terminal
window or disposable mission to clean up. Existing WEBSITE and CodeExp2 sessions
were not addressed or modified by these probes.

## What the inspected interface establishes

The generated experimental schema declares `process/spawn`, `process/kill`, and
`process/exited`. Its handles are connection-scoped and apply to processes
created through `process/spawn`. It does not establish custody of an independently
started native Terminal Codex process, its server-side thread or descendants.
Successful use of these methods was not measured.

Official [App Server documentation](https://learn.chatgpt.com/docs/app-server)
describes the initialize/initialized handshake and the experimental process API.
It also specifies that `thread/unsubscribe` removes the current connection's
subscription; the last subscriber's absence leads to unloading only after an
inactivity grace period. This is insufficient evidence of immediate Terminal
exit, a work-admission fence or complete executor retirement.

The exact reason for the observed proxy initialization silence is **NOT PROVEN**.
The advertised daemon control socket has not been qualified as the required
JSON-RPC endpoint. The default route also failed this probe. Do not infer from
these results that every native interface is unavailable, or report an
unattempted retirement as a failed retirement test.

## Consequence and next action

The accepted plan requires supported custody and retirement before its disposable
mission launch. That prerequisite is missing, so the launch/report/retirement
test and subsequent full runner remain blocked. No full workflow, persistent
recovery, installation automation, publication or shutdown capability is claimed.

Two bounded connection attempts failed without progress through the real path.
Under [Delivery Discipline](../../docs/delivery-discipline.md#shared-repair-limit),
stop repeating this approach. Additional diagnosis requires an explicit request.
The precise next technical dependency is the installed harness's supported
handshake and native per-session fence/custody/retirement contract. Do not switch
account, model, daemon, execution route or launch architecture to manufacture a
passing result. The original start/end acceptance conditions stay intact.

CodeExp2's executable-change hook remains unchanged. Its reviewed adoption and
meaningful staged regressions are still required before publishing executable
features. No commit or push was attempted in this check.

## Evidence

[Raw diagnostic log](20261018-native-control.log), 9,592 bytes, SHA-256:

`b02125dca601a13d9e163d00fd1811d775610c2c36e59973a347dfe1ae886979`

The log retains the requests, timeout results, clean proxy exits, after-probe
daemon observation, relevant generated method/parameter definitions and hashes
of the raw temporary artifacts. The original generated schema and JSON probe
artifacts remain at the temporary path recorded there. Temporary storage is not
a durable installation location; this retained log is the repository evidence.

## Correction after further authorized investigation

The user subsequently requested the regression work and challenged the broad
development block. Inspection of the existing installed native client exposed
the missing WebSocket handshake in the earlier raw-JSON probe. The existing
read-only client then initialized successfully and read the exact coordinator
thread. [The subsequent raw observation](20261018-native-websocket.log) records
the installed source hash, thread identity, cwd and active status. Its connection
was closed without dispatch or lifecycle operations.

The initial connection blocker and instruction to stop that approach are now
superseded by measured progress. Native connection availability is proven in
this read-only scope. Exact executor custody, work fencing and retirement remain
unqualified; no passing shutdown or complete mission workflow is claimed.
