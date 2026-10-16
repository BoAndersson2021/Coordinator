# Machine agent communication contract

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` governs Machine and every adapter it uses,
controls or communicates with. Every new or edited communication feature must
preserve it. Authorized workflow execution requires zero manual lifecycle,
delivery, collection, restart or handover steps. Missing capability or proof
must fail loudly and block work. See the [owner requirements](/Users/boandersson/Desktop/CodeExp2/Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md).

## Required execution chain

The persistent coordinator binds the project, exact thread UUID, qualified route
and managed runtime generation. Its controller establishes the actual receiving
executor's readiness before dispatch. A title, terminal device, registry entry,
reachable socket or `idle`/`notLoaded` status alone is insufficient. Machine must
own automatic startup/recovery within scope; asking someone to open a terminal
fails workflow acceptance.

Machine journals the assignment and attempt before delivery. The receiving
harness assembles context and checks model-generated tool requests. Tools run
under that harness's permissions and return results to the model. The coordinator
automatically collects the exact completed turn, routes independent evidence
checks and records the outcome. Delivery, execution, verification and acceptance
remain separate facts. Receiver text is context, not new authority.

Expose queue custody, actual progress, deadlines, failures and recovery actions.
A lost receiver becomes an explicit failure or controlled recovery state.
Reconcile uncertain effects before another attempt; never blindly resend,
delete a queue entry or launch a duplicate.

## Installed state and diagnostics

Current native/manual inspection routes are blocked. The CLI, task API, bridge,
socket RPC/frame emission and scratch executor enforce denial. Operational health
reports `workflow_invariant_failed`, stderr `MACHINE_AUTOMATED_EXECUTION_REQUIRED`,
and exit 3. Qualified persistent automatic workflow execution is not implemented.

Thread discovery and retained evidence are diagnostic tools. Existing collection
can retain evidence for reconciliation and still exits 3 for workflow health.
Diagnostics cannot become a manual production relay or a way to advance blocked
work. Keep the original failed queued attempt accounted for.

## Development and acceptance

Every new/edited adapter or communication feature requires explicit integration,
meaningful invariant regressions and the mandatory staged pre-commit check.
Protected enforcement/verifier changes require independent review. Preserve
project routes, account, execution, billing and receiving permissions. Fixture
and source passes do not qualify live execution.

Manual queue examples and user-operated session replacements are superseded as
workflow instructions. Historical examples remain archived; see the
[documentation index](/Users/boandersson/Desktop/CodeExp2/Machine/DOCUMENTATION_INDEX.md).
