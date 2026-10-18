# Current state and handover

## Cleanup publication requested — 2026-10-18

The user authorized committing and pushing the local Machine/archive removal and
related documentation. The outbound history also includes `c7ad298`, the prior
communication-guidance commit. The protected-file deletion regression reproduced
a missing passing route in the local commit gate. A targeted correction permits
only explicitly reviewed deletion entries; code/data deletions retain exact
inventory and staged-regression requirements. This repair changes no Machine
runtime, workflow authority or external repository. See
[the gate documentation](docs/commit-gate.md) for the deletion contract.

All 18 regression tests passed, including the exact staged snapshot. Independent
source/policy review passed and the reviewed local gate was adopted with its
previous installation preserved. Publication uses the normal commit hook and
explicit `origin main:main` refspec. Identify the resulting source commit with
`git log -1 -- scripts/check_staged.py`; publication is complete only after the
actual remote SHA matches the committed HEAD.

## Misplaced archive copies removed — 2026-10-18

The user confirmed the early archive copies are stored elsewhere and requested
their removal. No `.tz` files were present; the three root archives were
`neural-b1r-7a8fa22.tar`, `neural-b1r-ae546bb.tar` and `neural-g2-187222a.tar`.
All three were unchanged tracked files with no remaining workspace references
before removal. They remain in Git history. No commit or push was performed.

## Local Machine folder removed — 2026-10-18

The user confirmed the material is retained elsewhere and explicitly authorized
removing CodeExp2's entire `Machine/` folder, including the previously preserved
untracked task-timeline candidate. This supersedes the local preservation and
resume instructions below. Tracked material remains in Git history; no new copy
was made here. The separate `/Users/boandersson/Desktop/Machine` repository and
mission target repositories were not changed. Workspace entry links now point to actual
external Machine documentation. Historical local paths below describe the old
layout, not files to recreate. This cleanup does not qualify workflow execution
or change the Machine invariant. No commit or push is part of this request.

Independent review passed for removal scope, active links and invariant
preservation. Verification found 1,071 tracked deletions under `Machine/`, eight
documentation updates outside it, no remaining local folder and an empty index;
`git diff --check` passed. Changes remain uncommitted.

## WEBSITE publication complete; retirement unqualified — 2026-10-18

The user entered `Mission WEBSITE`, then `Mission END WEBSITE`. Native onboarding
and fresh background readiness were verified without reinstall or product work.
A stalled builder staging approval was reconciled after the user explicitly
approved archival, coordinator takeover and publication of the close plus all
thirteen existing outbound commits. The builder is archived; its close turn is
interrupted. WEBSITE main was pushed and independently matched remote SHA
`d79c4d4038a69d2bcb539ae7406d32852b98735a`.

The close commit adds only 61 lines to native `Handover.md`. Prettier, owned
local links, exact index bytes and preservation checks passed. All 37 previous
dirty files remain; the target index is empty. GitHub accepted the existing
artwork with large-file warnings. No product build, deployment or motion approval
was performed. See [the WEBSITE coordination handover](Missions/WEBSITE/HANDOVER.md)
for commit scope, raw evidence paths and collaboration lessons.

CodeExp2 close notes are published after the verified target-first result;
identify their commit with `git log -1 -- Missions/WEBSITE/HANDOVER.md` and use
the external `.git/website-current-end.json` receipt for final SHAs. The separate
untracked `Machine/TASK_TIMELINE/` candidate stays excluded. No new assignments
are admitted. No Terminal or service was launched by this reconnect, and the
shared daemon remains available. Complete native process retirement and automatic
mission start/end remain unqualified (`SHUTDOWN_BLOCKED` under the accepted
contract); archival is not a process-exit receipt.

## Mission automation — accepted 2026-10-18

The user accepted [the mission start/end design](Missions/CONTROL_WORKFLOW_PROPOSAL.md)
for `MISSION X` / `END MISSION X` in CodeExp2. No mission CLI is installed.
The first native-control gate remains BLOCKED on exact executor custody and
retirement. The initial proxy probes used raw JSON without the existing native
WebSocket handshake. Further user-authorized investigation reused the installed
read-only client: initialization and an exact coordinator thread read passed.
See [the corrected result and raw observations](Missions/ControlWorkflowEvidence/20261018-native-control.md).
No new mission, model turn, process-handle or lifecycle operation was launched.

The earlier connection blocker is superseded by measured progress. The accepted
outcome is unchanged; installer, routing and two-repository close automation
still depend on the real narrow-path gate. Preserve pending WEBSITE setup
documentation, the separate task-timeline candidate and existing sessions.

The user requested [a guide against excessive blocking](docs/how-not-to-overblock-development.md),
now linked from AGENTS. The [development commit-gate correction](docs/commit-gate.md)
has 16 passing real-fixture regressions and independent exact-byte review.
Its recorded adoption and current scope are in
[the gate evidence](Missions/ControlWorkflowEvidence/20261018-commit-gate.md).
It admits only the reviewed checker and regression suite; future mission
features require their own source inventory and meaningful tests. It grants no
Machine runtime or mission lifecycle authority. At the adoption checkpoint no
source commit or push had been made. The user subsequently authorized committing
and pushing the current mission/gate work; identify the publication commit with
`git log -1 -- Mission_Sofar.md`. The separate task-timeline candidate retains
its recorded exclusion.

Subsequent user update, 2026-10-18: the user manually terminated the WEBSITE
Terminal. Read-only inspection of builder `01a15088-a22b-72e1-ab5b-ef34cc3e799b`
still returned thread status `idle` and last turn `completed`; it does not prove
process retirement. Record the Terminal as ended by user report, retain the
thread/evidence, and require fresh readiness before any future assignment.
This does not resolve the native-control blocker or qualify automatic shutdown.

## Continuing this work

Start with [README.md](README.md) and [AGENTS.md](AGENTS.md). The AGENTS catalog
contains eight standalone instructions plus the inline workflow review procedure.
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

The section above records the newly accepted mission automation work and its
specific blocker. The remaining sections retain the earlier Machine handover.
Apply the user's next request to the existing plan or document, and use the
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
98-test suite. See onboarding (`Machine/README.md`, historical path),
current checkpoint (`Machine/CURRENT_MISSION.md`, historical path), requirements (`Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md`, historical path)
and documentation index (`Machine/DOCUMENTATION_INDEX.md`, historical path).

The subsequent managed dashboard increment (`Machine/DASHBOARD/README.md`, historical path) is
installed and running, with Machine source committed as `574e834`. Machine opens
the HTML/JavaScript page automatically; launchd keeps its local diagnostic service
available and recovers process loss. The page refreshes every two seconds and
marks failures/stale observations. Independent V2 source review, 113 tests,
five real disposable commit-gate cases and actual automatic process/browser
recovery passed. All 87 private Machine files remain unchanged. This qualifies
only the diagnostic display; automatic project workflows remain blocked.

The subsequent work-view completion (`Machine/WORK_VIEW/README.md`, historical path) is installed
and committed in Machine as `d24f163`. CLI and dashboard share task-state explanations; 114 tests,
independent source review and four real staged-commit cases passed. The actual
automatic source reload took 28.637 seconds, exceeding its retained failed
20-second probe; the browser subsequently reconnected automatically. Workflow
execution remains blocked, with all 87 private Machine files unchanged.
