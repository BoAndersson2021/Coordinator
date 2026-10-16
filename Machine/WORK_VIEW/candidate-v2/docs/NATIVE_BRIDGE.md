# Native inspection bridge — execution disabled by invariant

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` governs this bridge and all future edits
or adapter integrations. Current automatic lifecycle/orchestration is unqualified,
so new sends fail before connection, ledger intent or queue submission. Native
socket RPC and raw frame emission also block queue/unknown execution methods.
There is no manual dispatch, alternate transport or runtime override fallback.

## Retained interfaces and evidence

The bridge retains exact project route/registry bindings, source pins, thread and
workspace checks, journaled attempts and matching queue receipts. Those checks do
not establish a live receiving executor. `idle` and `notLoaded` status alone are
insufficient. The failed fresh-start test demonstrated that a saved thread can
accept a queue entry without an observed running receiver.

Existing collection is evidence reconciliation only: it scans bounded history from
the saved anchor, requires exact original input equality, rejects ambiguous turns,
and retains only a matching completed turn with an explicit final answer. Collection
never sends or starts/resumes a role. Queued/running/unknown observations remain
observable facts, not workflow acceptance. Health output includes the failed
invariant and exits 3 even when evidence retrieval succeeds.

The original task `native-inspection-fresh-start-001`, attempt
`15b871be-1900-4c3d-bee9-9edbd11fc245`, remains in custody. Do not prepare or send
it again or silently remove its queue entry. Implement supported automatic
reconciliation before another live attempt.

`work-view` now uses the same read-only work-state projection as the dashboard,
with explicit delivery, execution, completion, review and evidence-time fields.
The CLI preserves retained report access; dashboard HTTP data excludes report
bodies. No manual collect/relay instruction is presented as the next workflow
step. See [the work-view contract](WORK_VIEW.md).

## Transport and control limits

The client uses the existing bound user-owned Unix socket and preserves native
project execution/account/billing contracts. Initialization and allowlisted read
RPCs/control frames remain available for diagnostics. No arbitrary execution RPC,
process control, Blender access or lifecycle provider is introduced by this guard.
Missing/broken enforcement or adapter imports fail with structured invariant error
and exit 3. Diagnostics cannot be used as a manual workflow relay.

## Qualification and development

The guard has independent V3 source PASS, 98 tests and 14 disposable commit-hook
proofs. These establish enforcement, not automated execution. New/edited bridge,
RPC, lifecycle or recovery features must preserve the invariant, extend meaningful
regressions, and pass the staged pre-commit gate. Protected changes require
independent review. Required live acceptance covers automatic receiver startup,
exact receiving readiness, dispatch, collection, visible failure and recovery,
with zero human execution interventions. See [the invariant](WORKFLOW_INVARIANT.md),
[runbook](RUNBOOK.md) and [frontier](ROADMAP.md).
