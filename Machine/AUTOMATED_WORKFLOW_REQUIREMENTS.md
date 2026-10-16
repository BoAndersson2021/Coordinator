# Workflow execution requirements

Status: owner requirement, recorded 2026-10-16. The stop barrier is now installed
and verified. Automatic workflow providers remain unqualified and blocked;
live communication acceptance remains FAIL.

This is a Machine-wide enforced invariant, `MACHINE_AUTOMATED_EXECUTION_REQUIRED`,
covering every adapter Machine uses, controls or communicates with. All new or
edited features must preserve it. Require executable checks at the execution
and adapter boundaries, instructions in AGENTS.md, and a mandatory pre-commit
gate that tests the exact staged implementation and blocks loudly on violations.
Unqualified, missing or unknown capabilities must deny execution. No silent
fallback, override flag or manual execution path may satisfy the invariant.

Owner instruction:

> You can not have any manual start/stop/handovers or coms in the workflow execution - specially silent and invisible.

## Required behavior

After the user authorizes a workflow, Machine must operate its execution through
supported, controlled interfaces. Routine execution must require zero human
terminal actions, process starts/stops, message relays, receipt preparation,
coordinator restarts, or handovers between sessions. A conversation that a user
must keep open or replace manually cannot supply the persistent execution loop.
Human intent and reserved owner decisions remain explicit inputs; they cannot
conceal manual execution dependencies inside an allegedly automated workflow.

Machine must establish the exact executor's identity and runtime readiness,
arrange any required admitted startup, supervise execution, deliver assignments,
collect replies, route subsequent work, and recover across coordinator or worker
replacement. Required retirement, restart and handover steps must be controlled
and recorded by the system. Terminal windows may expose activity, but opening,
closing, typing into, or transferring information between them cannot be a
prerequisite for workflow progress.

Every transition must be observable: task and attempt identities, executor
identity and generation, current state, last actual progress, applicable deadline,
reason for a block/failure, and any recovery action. Machine must detect an
absent receiver, lost executor or failed controller and publish a specific
failure or recovery state. It cannot remain silently queued or label a missing
executor as routine waiting. A success verdict requires the completed work and
the required independent checks.

Automation must preserve project routes, accounts, execution contracts and
receiving permissions. A missing lifecycle capability must produce a visible
capability failure. Ad hoc Terminal scripting, a different execution route, or
a request that the user start the role does not satisfy this requirement.
Develop and qualify the supported control path; do not hide the missing path.

## Acceptance evidence

| Scenario | Required observed result |
| --- | --- |
| Required role initially absent | System establishes an authorized managed executor and proves exact runtime readiness, or exposes a specific capability/authority failure before dispatch. The whole-workflow success test requires the automated startup path to work. |
| Assignment and response | System delivers the recorded assignment and collects its actual matching completed reply, without a person relaying messages or invoking individual send/collect steps. |
| Worker stops during work | System detects the loss, exposes it, preserves task/queue/effect custody and performs supported recovery within the admitted scope. No manual terminal restart or duplicate work. |
| Coordinator is replaced | A controlled test injects the interruption; the persistent system recovers its loop and outstanding work without a person opening a new conversation or copying a handoff. |
| Retirement or handover is required | System owns the operation, verifies fencing and custody, records completion and establishes the successor before routing work to it. |
| Runtime/control route is unsupported | Explicit visible failure names the missing capability and affected task. This passes the failure-detection check and fails whole-workflow operational acceptance. |
| Delivery or effect outcome is uncertain | System retains and reconciles the exact attempt before further effects. No blind resend or second launch. |
| End-to-end completion | Work completes through automatic lifecycle, communication and recovery; independent verification binds actual outputs and source identities. Operator intervention count for execution is zero. |

Record lifecycle events, communication attempts, actual receiving turns,
recovery events, final verification, and all operator interventions. Any manual
execution dependency fails the end-to-end test, including interventions omitted
from the visible progress report. Merely detecting the dependency is useful
failure behavior, not acceptance of the automated workflow.

## Current gap and next implementation scope

The historical bridge queued to saved threads and collected on explicit command.
The installed invariant now blocks its execution route before new effects.
CodeExp2 currently supplies the coordinator loop; Machine does not supervise its
lifecycle. The failed test also depended on manually restarting the coordinator
and an unverified project receiver. These facts fail the owner's requirement.

The implementation scope must join persistent orchestration, verified executor
lifecycle, automatic send/collection, visible failure detection and recovery.
Adding a pre-send liveness check alone cannot qualify this workflow. Use the
[proposed lifecycle design](ROLE_LIFECYCLE_CONTROL_DESIGN.md) as an existing
design input, preserving its project-controller and native-harness ownership.
It remains proposed and requires implementation and qualification.

Preserve and reconcile the existing task `native-inspection-fresh-start-001`,
attempt `15b871be-1900-4c3d-bee9-9edbd11fc245`, before another live attempt.
The [failure record](COMMUNICATION_BRIDGE/LIVE_ACCEPTANCE_FAILURE.json) and prior
raw evidence remain retained. The installed guard enforces the stop; it does not implement or activate the
missing control service. See [the enforcement evidence](INVARIANT_ENFORCEMENT/README.md)
and [documentation status](DOCUMENTATION_INDEX.md).
