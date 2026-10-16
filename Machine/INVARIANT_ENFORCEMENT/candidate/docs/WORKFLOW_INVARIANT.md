# Enforced automated execution invariant

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` governs Machine and every adapter it uses,
controls or communicates with, including all future features and edits.
Execution must require zero manual process starts/stops, coordinator restarts,
message relays or handovers. All lifecycle, communication and recovery must be
controlled by the system within the authorized scope. Every missing capability,
lost receiver, uncertain effect and failure must be observable and block unsafe
progress. User intent and reserved owner decisions do not supply hidden manual
execution steps.

## Current enforcement

The existing coordinator, native/manual inspection routes and scratch adapter
have no qualified end-to-end automation provider. They are explicitly
unqualified. There is no production allow branch, override flag, environment
switch, caller-provided certificate or automatic fallback. This increment
enforces a stop; it does not implement the missing automation.

The CLI classifies every command. Unknown operations fail closed. Workflow
dispatch, new queue submissions, handovers, permit execution and workflow
verification/closure raise a structured invariant error and exit 3 before any
ledger, socket or permit-consumption effect. The core task API, bridge sender,
socket RPC effect boundary and scratch executor each enforce the same guard.
Public and private queue RPC entry paths are covered. Adding runtime modules or
CLI operations requires explicit integration and invariant regression coverage.

Read-only help and evidence inspection remain available. Explicit local setup
and assignment preparation are administrative records only; they confer no
workflow execution permission. Existing acknowledgements, uncertainty, reports
and reconciliation remain retainable so the failed live task is not erased.
The gate never sends, deletes its queue entry, restarts an executor or consumes
its scratch permit as a recovery convenience.

Operational health commands print the retained observation and a structured
`workflow_invariant_failed` result, write the error to stderr and return exit 3.
`doctor` retains `source_integrity_pass` as its observation status, never overall
workflow readiness. Evidence/setup responses also expose the invariant and
their limited command scope. Existing raw receipts remain historical facts.

## Commit gate

The installed hook must be `.githooks/pre-commit` via
`git config core.hooksPath .githooks`. It runs
`scripts/check_workflow_invariant.py --staged` and blocks on failure.

The validator materializes Git index blobs into an isolated temporary snapshot
and runs its complete suite. Unstaged guard code or tests cannot qualify the
index. Missing required enforcement files, unsupported files, unknown runtime
modules/commands, removed effect guards, failed tests or a timeout produce
`MACHINE_AUTOMATED_EXECUTION_REQUIRED: COMMIT BLOCKED` and nonzero exit.
Executable edits require staged invariant regressions. The source inventory is
closed; no newly introduced adapter inherits execution permission.

Historical unit tests inject a guard test double only to retain coverage of
their isolated ledger/permit algorithms. Production CLI subprocesses and the
new invariant tests use the real denial barrier. Their passes establish gate
behavior, never automatic operation or live project acceptance.

Future provider support must preserve these checks, add actual managed executor
identity/liveness, automatic lifecycle, communication, supervision and recovery,
and obtain independent review and live qualification. A source declaration or
passing hook cannot substitute for that runtime evidence. The local Git hook
and Python guards operate within the existing trusted-host development model;
they do not control tools invoked directly outside Machine.
