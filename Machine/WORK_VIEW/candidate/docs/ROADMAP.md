# Machine implementation frontier

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` governs all new/edited features and all
adapters used, controlled or contacted by Machine. Manual lifecycle, messaging,
coordinator restart and handover cannot appear inside authorized workflow execution.
Missing support or proof must fail loudly and block effects.

## Installed enforcement

The reviewed V3 barrier covers CLI, core task transitions, native/manual delivery,
socket RPC/frame emission and scratch execution. Health fails with exit 3. The
mandatory pre-commit verifier tests actual staged blobs, requires successful
mandatory test IDs/completion, and blocks unknown executable integration or missing
regressions. Independent source review passed; 98 tests and 14 disposable commit
cases passed. Current automatic workflows remain unqualified and disabled.

## Required implementation sequence

The managed local HTML/JavaScript diagnostic dashboard adds automatically refreshed
ledger gauges and task evidence. Its launchd supervision is scoped to that display;
it does not implement or qualify the project execution sequence below.

1. Implement persistent coordination and typed project control with exact runtime
   identity/readiness, owned lifecycle, fencing and observable supervision.
2. Implement automatic send/collection, verification routing and handover, preserving
   existing task/queue/effect custody and all project execution/account contracts.
3. Prove automatic coordinator/worker recovery, lost acknowledgements, concurrent
   callers, deadlines and unsupported capability failures without duplicate effects.
4. Independently review protected changes, adopt reviewed source within owner scope,
   and qualify the real automatic path with zero execution interventions.
5. Extend authenticated scoped grants and qualified domain adapters for production;
   preserve independent verification and designated domain adoption boundaries.

A liveness check alone is insufficient. Manual terminal work, copied handoffs,
operator relays and user-operated restart tests cannot qualify this sequence.
Keep the failed fresh-start task and historical pilot/scratch evidence retained.
The [lifecycle proposal](proposals/ROLE_LIFECYCLE_CONTROL.md) is a design input;
no controller, production qualification or castle construction is established by it.

Use [the runbook](RUNBOOK.md), [invariant contract](WORKFLOW_INVARIANT.md) and
[documentation index](DOCUMENTATION_INDEX.md). Run the existing focused suite with
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` during development.
