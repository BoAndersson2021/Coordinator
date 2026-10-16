# Mammuth Machine

Machine is studio coordination infrastructure for agents in separate project
repositories. Games, source, assets, scenes and domain adoption stay in those
projects. Models generate responses or tool requests; receiving harnesses enforce
permissions and execute tools. Machine owns persistent coordination and evidence.

## Current operating state

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is installed and enforced across the CLI,
core task API, native/manual delivery, socket RPC/frame emission and scratch
execution. Every new or edited feature and every used/controlled/communicating
adapter must preserve it. Missing proof or support fails loudly and blocks before
effects. No manual starts/stops, messages, restarts or handovers are permitted
inside workflow execution. No override or manual fallback is enabled.

The current providers lack qualified persistent orchestration, managed lifecycle,
automatic communication and recovery. Workflow execution is therefore blocked.
The guard's independent V3 PASS, 98 tests and 14 disposable commit-hook cases prove
enforcement behavior; they do not qualify automated operation.

## Read-only front door

`./Machine status --json`, `./Machine doctor --json`, `./Machine work-view` and
`./Machine invariant-check` expose the failed invariant on stdout/stderr and
exit 3. Doctor preserves source integrity as a separate observation. Help remains
available with `./Machine --help`. Retained tasks/evidence remain inspectable;
retrieval success is not workflow readiness. Startup never initializes or dispatches.

The original native acceptance task remains delivered in transport custody,
version 3, with one attempt. No live Brainstorm receiver was established; the
acceptance verdict is FAIL. Its queue entry and receipts remain retained. Historical
pilot/scratch successes are not enabled execution paths under the new invariant.

## Development and commit protection

Read [AGENTS.md](AGENTS.md), [the invariant](docs/WORKFLOW_INVARIANT.md),
[coordination](docs/COORDINATION.md), [runbook](docs/RUNBOOK.md) and
[documentation index](docs/DOCUMENTATION_INDEX.md). The builder workspace is
[CodeExp2/Machine](../CodeExp2/Machine/README.md).

The mandatory installed pre-commit verifier evaluates Git index blobs in isolation.
Executable edits require staged invariant regressions. Unknown executable files,
commands/adapters, missing enforcement, disabled hooks, skipped/omitted/failed
mandatory tests and absent completion reports block loudly. Changes to protected
rules or the installed verifier require independent review and recorded adoption.
Run focused validation with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.

Private state remains outside Git. Frozen Design packages and historical evidence
retain their bytes. Current invariant guidance supersedes manual workflow examples;
[the implementation frontier](docs/ROADMAP.md) records remaining automation work.
