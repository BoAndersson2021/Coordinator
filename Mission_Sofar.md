# Current state and handover

## Continuing this work

Start with [README.md](README.md) and [AGENTS.md](AGENTS.md). The AGENTS catalog
contains seven standalone instructions plus the inline workflow review procedure.
The guides now share delivery rules, plan ownership, a single repair limit,
coordination boundaries and distinctions between diagnostics and workflow
qualification. Use only the guides relevant to the requested task.

The latest work is instruction and documentation reconciliation. It does not
launch Machine, qualify a runtime or authorize repository work elsewhere. No
native application was delivered; the abandoned native MVP experiment and its
repair packages, local experiment dependencies and temporary state were deleted
at the user's direction. Do not revive that work or retry closed diagnostics
merely because a new session starts.

Before continuing, inspect `git status --short` and the relevant plan and history.
Use `git log -1 --oneline -- Mission_Sofar.md` to identify this handover's revision. The
separate `Machine/TASK_TIMELINE/` candidate remains intentionally untracked and
outside the documentation commit; preserve it and do not include it with a broad
`git add .`. Resume it only if the user requests that work, after checking its
actual candidate state and recorded failures.

Ordinary text documentation commits work through the local CodeExp2 hook.
Executable/data changes still need meaningful staged invariant verification;
agent instruction and invariant-file edits require review. The Machine repository
has a separate hook and runtime barrier. Instructions and local hook metadata do
not constitute a runtime allow path or a transferable execution grant.

There is no newly authorized runtime implementation step in this handover. Apply
the user's next request to the existing plan or document, and use the
[plan guide](docs/how-to-follow-and-refresh-a-plan.md) before changing its baseline.
For delegated execution, use the [coordinator guide](docs/how-to-coordinate-with-a-builder-agent.md).

## Historical Machine implementation checkpoint

The remainder records earlier installed milestones and verification results. Its
test totals, commit identities and statements about running services belong to
those observations; they are not a fresh health check. Consult the target
repository's current instructions and read-only status when runtime capability
matters. Preserve the original evidence and consumed-attempt history.

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is installed and enforced for Machine and
every adapter it uses, controls or communicates with, including all new/edited
features. Authorized workflow execution requires zero manual starts/stops,
communication, coordinator restarts or handovers, with visible failures that block.

The V3 guard has independent source PASS, 98 passing tests and 14 real disposable
commit-hook cases. It blocks native/manual dispatch, socket effect submission,
scratch execution, handovers and workflow verification/closure before effects.
Operational health fails loudly with invariant code and exit 3. The mandatory
installed verifier evaluates index blobs and requires actual successful mandatory
test IDs and runner completion; unsafe or missing integration blocks commits.

Automatic lifecycle, persistent orchestration, communication and recovery remain
unqualified. The native acceptance test is FAIL: its exact queued input had no
established live receiver. One delivery attempt remains in custody. Historical
pilot/scratch successes remain evidence for their original scopes only; the
consumed scratch permit cannot be replayed. No castle/production readiness is claimed.

CodeExp2 supplies development context and evidence; Desktop/Machine supplies
persistent records and the enforced barrier. This is not a qualified automatic
execution loop. Machine enforcement and documentation are committed as
`50dbd19`; its installed pre-commit gate passed 17 invariant tests and the full
98-test suite. See [onboarding](Machine/README.md),
[current checkpoint](Machine/CURRENT_MISSION.md), [requirements](Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md)
and [documentation index](Machine/DOCUMENTATION_INDEX.md).

The subsequent [managed dashboard increment](Machine/DASHBOARD/README.md) is
installed and running, with Machine source committed as `574e834`. Machine opens
the HTML/JavaScript page automatically; launchd keeps its local diagnostic service
available and recovers process loss. The page refreshes every two seconds and
marks failures/stale observations. Independent V2 source review, 113 tests,
five real disposable commit-gate cases and actual automatic process/browser
recovery passed. All 87 private Machine files remain unchanged. This qualifies
only the diagnostic display; automatic project workflows remain blocked.

The subsequent [work-view completion](Machine/WORK_VIEW/README.md) is installed
and committed in Machine as `d24f163`. CLI and dashboard share task-state explanations; 114 tests,
independent source review and four real staged-commit cases passed. The actual
automatic source reload took 28.637 seconds, exceeding its retained failed
20-second probe; the browser subsequently reconnected automatically. Workflow
execution remains blocked, with all 87 private Machine files unchanged.
