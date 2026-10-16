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

## Supervised diagnostic display

`dashboard` and internal `dashboard-serve` are explicitly administrative diagnostics.
They manage only a loopback, token-protected, read-only ledger display through
macOS launchd. Automatic service recovery/browser refresh do not qualify any
project lifecycle, communication, handover or execution provider. Source modules,
static assets and meaningful dashboard invariant regressions are in the staged
gate inventory. Unknown HTTP routes cannot dispatch CLI commands. Stale or failed
observations must remain visible; source reload/recovery must be system-owned.
The workflow guard has no new allow branch. See [DASHBOARD.md](DASHBOARD.md).

## Commit gate

Adoption copies the reviewed `.githooks/pre-commit` and
`scripts/check_workflow_invariant.py` to the Git directory under
`machine-invariant-hooks/`, then sets `core.hooksPath` to that absolute directory.
The installed verifier validates the staged snapshot. A staged or unstaged
replacement of the tracked hook/checker cannot replace the installed policy.
Policy replacement requires a separately reviewed adoption; a missing installed
verifier blocks loudly. This installation is retained in the adoption record.

The validator materializes Git index blobs into an isolated temporary snapshot
and runs its invariant regressions and complete suite. Mandatory named
invariant tests must remain in the staged test class and report actual successful
execution IDs. Skips, expected failures, suppressed discovery, unsuccessful tests
and missing completion reports block in both invariant-only and full-suite runs. Unstaged guard code or tests cannot qualify the
index. Missing required enforcement files, a non-executable staged hook, disabled
hook/checker behavior, missing/broken runtime imports, unsupported files, unknown runtime
modules/commands, removed effect guards, failed tests or a timeout produce
`MACHINE_AUTOMATED_EXECUTION_REQUIRED: COMMIT BLOCKED` and nonzero exit.
Executable edits require staged invariant regressions. The executable inventory covers source modules, scripts, adapter/provider
directories and executable/code files elsewhere in Machine. It is closed; no
newly introduced adapter inherits execution permission. Raw wire RPC and
non-text effect-frame bypasses are also denied before socket writes.

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

## Installed verification and related guidance

The exact V3 enforcement source received independent PASS, with 98 passing tests
and 14 real disposable-commit cases. These establish the stop barrier and commit
gate; automatic workflow operation remains unqualified. The local installed
verifier is pinned under the Git directory, so tracked replacements cannot replace
its policy during a commit. See [the runbook](RUNBOOK.md),
[documentation index](DOCUMENTATION_INDEX.md) and [roadmap](ROADMAP.md).
