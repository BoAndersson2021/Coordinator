# Machine operating and development runbook

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is mandatory for Machine and all adapters,
including every new or edited feature. Runtime workflows must have automatic
lifecycle, communication, handover and recovery with zero manual execution steps.
Unsupported or unverified dependencies fail loudly and block progress.

## Current state and diagnosis

Workflow execution is intentionally blocked: automatic orchestration/lifecycle is
unqualified. The installed barrier and pre-commit protection are verified; they
are not an enabled automated studio. Source development and diagnostics are
maintenance, never substitutes for missing execution infrastructure.

The coordinator may inspect `./Machine status --json`, `./Machine doctor --json`,
`./Machine work-view` or `./Machine invariant-check`. Expected health result is
`workflow_invariant_failed`, invariant code on stderr, exit 3. Doctor reports
source integrity separately. Do not swallow nonzero status or turn it into a
readiness pass. `task-show`/`evidence-show` retrieve custody with limited scope.

No person should be instructed to open Brainstorm, restart a coordinator, relay
messages, prepare receipts, stop a process or copy a handover to finish a workflow.
Do not run new dispatch, lifecycle, scratch execution or workflow closure as a
workaround. The receiving harness/OS permissions and project contracts remain
binding. If an operation reports an unexpected failure, retain its actual output,
state and exact identities and diagnose within authorized maintenance scope.

## Managed diagnostic dashboard

`./Machine dashboard` automatically starts/reuses a macOS launchd service and opens
the local HTML/JavaScript dashboard. The service is kept alive independently of
the terminal; the page refreshes every two seconds and automatically reconnects.
Refresh failure or observations older than eight seconds are prominently marked
stale. Service connection health never means workflow readiness. All task data
comes from integrity-checked local custody, with original evidence timestamps;
no project receiver is probed or started. The failed task/queue remains unchanged.
Startup/supervisor/browser failures exit 3 visibly, with no manual fallback.
See [the dashboard contract](DASHBOARD.md) for managed files and failure behavior.

## Existing failed attempt

Task `native-inspection-fresh-start-001` remains `delivered`, version 3, with one
attempt, `15b871be-1900-4c3d-bee9-9edbd11fc245`. This is transport custody only.
No live receiver was established; acceptance is FAIL. Preserve the exact queued
input, receipt and history. Never resend, silently delete, launch a substitute,
renew scope or manufacture verification. Supported reconciliation must precede
another live attempt. No blind retry of uncertain external effects is permitted.

## New or edited features

Follow AGENTS.md, isolate changes and add meaningful invariant regressions. Unknown
adapters/commands/executables must remain denied. The installed pinned verifier
checks the actual Git index through core.hooksPath under the Git directory's
machine-invariant-hooks. Unstaged fixes do not qualify staged code. Missing,
skipped, expected-failure, undiscovered or failed mandatory tests, missing runner
completion and disabled hooks/checkers block the commit loudly.

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` for focused
validation. Protected enforcement/verifier changes require independent review and
recorded adoption. Do not disable/bypass the hook, weaken regressions, or use a
source/fixture pass as runtime qualification. Developer installation/maintenance
is distinct from workflow lifecycle and must not become a hidden dependency.

## Automatic execution acceptance

Require system-owned startup/readiness, exact dispatch and receiving turn,
automatic collection and verification routing, visible process/controller loss,
automatic handover/recovery after controlled interruption, bounded deadlines and
retained uncertain effects. Count all human execution interventions; any one fails
the whole-workflow test. A visible capability failure proves detection and fails
operational acceptance. [The frontier](ROADMAP.md) describes outstanding work.
