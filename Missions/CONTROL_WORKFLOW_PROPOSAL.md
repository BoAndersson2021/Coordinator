# Mission start and close — design and red-team review

Status: ACCEPTED by the user on 2026-10-18 ("Proposal accepted"). Implementation
began with native-control feasibility checking. The read-only native connection
now passes; the first gate remains BLOCKED on per-session custody/retirement, as
recorded below. No mission CLI or automatic close controller is installed.
The design review used the current local source, CLI help, generated
protocol schemas and retained WEBSITE/BallisticsExperimental evidence. No mission
was ended, committed, pushed or retired during this review.

Review checkpoint, 2026-10-18: CodeExp2 HEAD `5ddad03`, with the WEBSITE setup
documentation still local; Desktop/Machine HEAD
`41e1cbc30b226412cf571439ec09b372ff7f725c` on `machine-v1.3`, clean. WEBSITE HEAD
`d4af3dfe8f42ed2c404523e369f6d13ee9694780`; freshly advertised remote main and
recorded origin/main both matched `a6d6dc39dd5a7ca0ab44ed30e67b2792a18dc612`,
leaving thirteen ahead commits. No Machine workflow or lifecycle command was
executed. Static Codex schema generation used an agent-owned temporary directory
that was removed afterward; it did not contact or stop a mission receiver.

The paragraph above is the original review checkpoint. The subsequent accepted
implementation probe has separately retained evidence in
[the feasibility result](ControlWorkflowEvidence/20261018-native-control.md).

## Human entry and implementation boundary

Keep two conversational entries in the attended CodeExp2 Codex session:

```text
MISSION WEBSITE
END MISSION WEBSITE
```

The future instruction router maps them to the accepted shell interfaces:

```sh
./mission start WEBSITE
./mission end WEBSITE
```

Add `./mission status WEBSITE` for observation and recovery decisions. These are
accepted interfaces to implement, not commands available today. Text entered in Codex is a
model request; it is not automatically a shell command. The coordinator must
invoke the runner and inspect returned results through its supported tools.

Use one thin Python front door with validated per-mission bindings and durable
operation records. Preserve the existing Codex receiving harness and tool route;
do not add another model client, API credential flow, dashboard, site generator
or independent implementation plan. A Python process does not inherit this
conversation's `tools` object: its real control adapter must use supported CLI
or app-server interfaces, or return typed actions for the attended coordinator
to execute and record. Qualify the chosen route before promising automation.

## Corrected start chain

```text
MISSION X
   |
   v
Resolve registered X -> canonical repository + approved mission profile
   |
   v
Lock this repository operation; reconcile unfinished run/effects
   |
   +--> existing receiver -> verify exact identity and fresh readiness
   |
   +--> no receiver       -> supported owned launch with native onboarding task
   |
   v
Repository's OWN onboarding / startup / governance / handover
   |
   v
Check installed communication contract AND live report route
   |
   +--> compatible and intact -> use it
   +--> missing               -> bounded install; validate and re-read instructions
   +--> drift / partial       -> preserve local changes; reconcile targeted update
   |
   v
Completed fresh ACK + compact JSON / hashed artifact proof
   |
   v
READY -> tell human current scope, state, limits and eligible next action
```

Resolve names from explicit mission registrations, not arbitrary shell text or
Desktop directory guesses. Validate the real path, Git root, branch/worktree and
remote configuration. Prevent two aliases or concurrent starts from acquiring
the same executor/repository. A repeated start reuses/reconciles its run rather
than launching another agent. Recheck scope if a different worktree is selected.

Capture HEAD, dirty files and bytes, existing index, ahead commits, native entry
documents and outstanding work before mutation. Dirty work is not automatically
an error and must not be silently cleaned, staged or attributed to this mission.
Expose publication obstacles at startup without blocking independent permitted
inspection. Never resume an old product task merely because handover lists it.

Native onboarding always precedes external mission additions. Inspect any entry
script before executing its required scoped startup. Preserve project-owned
proof, review, release, model/account and permission rules. A missing root start
script is not permission to invent one. Starting the mission reaches readiness;
it does not select a new site, experiment, tuning change or implementation task.

For a new attended Codex session, use the existing
[initial-prompt launch law](../../DOCTRINE/Codex%20Initial-Prompt%20Launch%20Law.md)
and [launcher checklist](../../Tools%20%26%20Systems/Launchers/CODEX_LAUNCHER_PATTERN.md).
Pass the actual onboarding task at process start. Do not inject a task into an
already open TUI. Preserve the exec-based launcher contract; do not silently add
a child/wait wrapper to manufacture ownership. Record the native launch/provider,
exact thread, run generation and owned Terminal tab/process control references.
Metadata and a window ID alone do not qualify shutdown custody.

## Installation check means compatibility, not existence

The profile must identify the package source revision/digest, contract version,
installed paths and accepted installed hashes, including documented native
formatting adaptations. Check the AGENTS route, target DELIVERY settings, artifact
directory, read/write scope, request/reply budgets and actual receiver readiness.
An install directory, version string, old ACK or hash file alone is insufficient.

Do not compare only the installed bytes with unformatted package bytes: WEBSITE
uses native Prettier formatting. Preserve recorded source/installed identities
and investigate unexplained drift. A newer package README alone need not trigger
reinstallation of an unchanged contract. Partial installation must remain visible
and recoverable; do not overwrite amended project instructions.

Run the bounded report exchange when establishing an unqualified route, and
check current readiness on reconnect. Do not rebuild the application to prove
documentation installation. Keep detailed reports in each target's existing
configured evidence directory, with compact JSON returns and hash verification.

## Corrected close chain

```text
END MISSION X
   |
   v
Record close intent; stop accepting new mission assignments
   |
   v
Drain current work, reconcile uncertain effects and owned project processes
   |
   v
Builder writes canonical native handover + full close report
Coordinator writes collaboration notes + checks the return
   |
   v
Freeze publish scope; preflight BOTH repositories and outbound history
   |
   +--> ambiguous ownership / failing check / unauthorized history -> CLOSE_BLOCKED
   |
   v
Stage exact owned changes; normal checks/hooks; commit and push TARGET
   |
   v
Verify target remote SHA; record target result in CodeExp2 mission notes
   |
   v
Commit and push CODEXP2; verify its remote SHA
   |
   +--> partial publication -> record completed steps; resume without duplicates
   |
   v
Supported retirement of exact mission executor; verify exit
Close only its owned Terminal tab; retain history and report evidence
   |
   v
CLOSED -> after-action report to human in CodeExp2
```

The native handover records actual completed work, tested source, unresolved
limits, dirty work, evidence, known processes and next eligible action. CodeExp2
collaboration notes record assignment/results, review findings, transport trouble,
recovery and lessons useful next session. Link full logs; do not paste private
session transcripts into permanent notes. Keep product decisions and acceptance
with their designated owners.

Use the target's existing canonical handover and a coordinator-only
`Missions/<name>/HANDOVER.md` for collaboration/close notes; keep the mission
README as running instructions. Link implementation plans instead of duplicating
them. Final publication/process receipts belong to the durable run record.

Keep the receiver quiescent during publication: no unrecorded edits or new turns
after freezing the candidate. Do not confuse a coordinator convention with an
enforced native fence; qualify actual concurrency control for the promised scope.
Do not force-cancel active work to make close appear immediate. Use bounded waits
and a visible block with the current task/effect state when it cannot settle.

## Publication semantics and authority

The accepted design's meaning of `END MISSION X` includes permission to stage,
commit and push the mission-owned scope to the registered repositories, branches
and remotes. Record that meaning in the approved mission policy before using it;
do not ask for routine confirmation again within that scope. It grants no force
push, hook bypass, source-remote access, deployment or unrelated publication.
Keep those boundaries explicit and expose real blockers instead of silently
omitting requested commits/pushes.

Determine ownership from the opening baseline and recorded work, not a guessed
directory or `git add .`. Shared files can contain old user changes and new
mission hunks: stage only an unambiguous reviewed candidate and validate its
index bytes. If changes cannot be separated safely, require reconciliation;
never discard or silently include the older work. Preserve an unrelated index.

Check every commit the push would publish, including ancestors already ahead
at mission start. WEBSITE currently has thirteen such commits. A new mission
commit on main does not prevent those ancestors being pushed too. Resolve their
publication scope explicitly; do not silently force, rebase, cherry-pick or
change branches. Existing hooks and source/evidence checks remain applicable.

There is no atomic transaction across two GitHub repositories. Commit/push the
target first, then write its verified SHA into coordinator notes and publish
CodeExp2. Preflight both destinations first, and record each actual result. If
the second push fails, return `PUBLISH_PARTIAL` with the first published SHA and
an exact resumable next action. Do not repeat a successful commit or report a
failed/unknown push as complete. Recheck remote advancement on retry.

The final coordinator SHA belongs in the external run receipt and human report;
do not create an endless series of commits trying to embed a commit's own final
SHA. A no-change repository needs a truthful no-op result, not an empty commit.
Raw ignored evidence stays local unless the assignment explicitly includes a
reviewed publication selection.

## Retirement is a real missing dependency

The WEBSITE launch evidence records Terminal window `23122` and a completed
onboarding turn. It does not establish an owned per-mission shutdown controller,
native admission fence or process-exit receipt. Current native CLI help exposes
queueing and app-server transport; the generated standard protocol includes
thread start/resume/read/list/archive and turn interruption. These declarations
do not establish actual runtime retirement behavior or safe TUI closure.

Never stop the shared Codex daemon to end one mission. Interrupting a turn,
archiving a thread, asking the model to quit or closing a window is not by itself
proof of complete retirement. Do not use broad process searches, raw signals to
an unowned PID, or close a window containing unrelated tabs. Qualify the native
per-session control route and retain ownership of mission-started services.
Archive history only as a separately defined lifecycle decision; retain evidence.
Leave the CodeExp2 coordinator session, shared tool connection and shared Codex
daemon available for the final human report and other missions. Closing a mission
ends its own dispatch eligibility, not the studio's shared communication service.

If publication fails, retain a recoverable quiescent mission and disclose why
close is blocked. If publication succeeds but retirement fails, report
`SHUTDOWN_BLOCKED`, keeping the exact remaining process/session state visible.
Neither state is `CLOSED`. A lost coordinator must reconcile the recorded intent,
remote outcomes and actual executor before another launch/push/retirement attempt.
Do not claim automatic restart recovery until the persistent control path is
actually qualified.

## Minimal new machinery and existing reuse

| Responsibility | Reuse or smallest required addition |
| --- | --- |
| Human intent and technical reasoning | Existing attended CodeExp2 Codex coordinator. |
| Native project authority | Each target's AGENTS, onboarding, real entry and canonical handover. |
| Mission orientation | Existing `Missions/<name>/README.md`. |
| Message and artifact format | Existing BuilderCommunication v1 package and target DELIVERY settings. |
| Delivery and collection | Existing supported Codex tools/native control interface; qualify script access rather than assuming in-model tools are importable. |
| Launch | Existing Codex initial-prompt law and native launcher mechanisms. |
| Publication | Git, normal hooks, existing approved remotes and explicit refspecs. |
| Machine-readable profile | One validated per-mission binding beside its guide: root/worktree, native entry, handover, remotes/branches, install/artifact paths and publication policy. It records decisions; it is not itself an authority grant. |
| Recovery | A locked durable run record and small operation journal with atomic writes, recording intents before effects and results after observation. No duplicate implementation roadmap. |
| Lifecycle custody | Existing qualified native provider if available; otherwise the precise missing provider is the first bounded engineering dependency. Do not build a parallel studio service speculatively. |

Existing [delivery](../docs/delivery-discipline.md),
[coordination](../docs/how-to-coordinate-with-a-builder-agent.md),
[plan](../docs/how-to-follow-and-refresh-a-plan.md) and
[runtime](../docs/how-not-to-overengineer.md) guides remain applicable. Reuse
Machine's [lifecycle design](../Machine/ROLE_LIFECYCLE_CONTROL_DESIGN.md) for its
custody, quiescence, uncertainty and recovery lessons. Its operations remain
proposals, not available commands. The inspected Desktop/Machine implementation
still unconditionally rejects workflow execution; its ledger or a wrapper cannot
be presented as a qualified provider or used to bypass its barrier.

CodeExp2's actual pre-commit hook currently blocks new executable/data changes
without its required reviewed regression-backed adoption. The one previous
owner-authorized instruction-file bypass is not a standing feature-development
policy. Qualify and adopt an implementation through the existing enforcement
requirements; do not rename an adapter or disable a hook to claim readiness.
This review changes no enforcement, Machine source or project state.

## Red-team findings resolved in this design

| Failure in the initial layout | Corrected behavior |
| --- | --- |
| Directory named X selects arbitrary shell/workspace | Registered canonical root, checked Git identity, typed arguments and scope. |
| Starting twice creates duplicate agents/installers | Repository/run lock, retained operation ID, fresh readiness and reconciliation before reuse/launch. |
| External setup bypasses native governance | Native onboarding/start/handover first, scoped installation afterward. |
| Folder exists means installed | Compatible source/installed identities, native AGENTS route, DELIVERY settings and actual report proof. |
| New package overwrites project amendments | Drift/partial states retain bytes and require a targeted reconciled update. |
| Long JSON is silently truncated | Bounded completion plus full report path/hash and complete coordinator collection. |
| End stages old dirty work or publishes ahead history | Baseline/hunk ownership, index verification and outbound commit inspection in both repos. |
| Two pushes treated as one success | Target-first checkpointed publication with explicit partial outcomes. |
| Archive/window close treated as executor exit | Qualified per-session retirement, native exit proof and exact owned-tab closure. |
| Failure or coordinator loss causes blind retries | Durable intents, effect reconciliation and resumable states; no false recovery claim. |
| Mission start silently resumes product implementation | READY reports context; actual work needs its assigned outcome. |
| Script is mistaken for an LLM or imports unavailable tools | Coordinator/harness and deterministic runner have explicit separate roles. |

## First implementation acceptance gate

Before building the complete start/end command, prove the critical native control
path in one explicitly authorized disposable mission: real attended launch,
native onboarding, exact receiver ACK, one compact/hash-bound report, supported
quiescence/retirement and observed exit of only the owned Terminal tab/processes.
Preserve normal accounts/configuration and the existing launch law. Retain a
specific capability failure if the native control surface cannot supply custody.

Then exercise missing/compatible/drifted installation, repeat/concurrent start,
interrupted close, dirty/shared files, pre-existing staged work, ahead history,
advanced remotes, hook rejection, first/second push failure, lost acknowledgements
and shutdown failure. Use disposable local Git remotes for failure cases; qualify
actual approved publication separately. Require no unrelated writes, publication,
terminal closure, duplicate effects or human terminal repair in the demonstrated
scope. Fixture passes alone do not qualify the full lifecycle.

Only after that real narrow path works should the natural-language routing and
two-repository end automation be adopted. Do not spend the first implementation
on another framework, dashboard, installer rewrite or tuning of unproven control.

## Implementation checkpoint — 2026-10-18

The user accepted this proposal. The first gate remains BLOCKED; later installer,
natural-language routing and two-repository close automation remain dependent on
that gate and have not been implemented.

```text
Accepted mission design
        |
        v
Installed CLI/schema inspection -> native methods declared
        |
        v
Proxy initialize, explicit socket -> no response within 10 seconds
Proxy initialize, default route   -> no response within  8 seconds
        |
        v
BLOCKED before disposable mission launch
        |
        +-> WEBSITE session untouched; shared daemon still reports running
        +-> no mission, model turn, process/spawn or retirement dispatched
```

Installed CLI and app-server daemon both report version `0.163.0`. The generated
experimental schema declares connection-scoped `process/spawn` / `process/kill`
and `process/exited`, but this does not bind a native Terminal launch to those
handles. `thread/unsubscribe` removes only the caller's subscription; it is not
an immediate session or Terminal shutdown contract. Neither custody nor a native
admission fence has been qualified.

Both bounded proxy attempts ended cleanly after their input was closed, with no
stdout or stderr response. The failure cause is NOT PROVEN; it does not establish
that the protocol methods are globally unavailable. No retry changed accounts,
models, permissions, configuration, the daemon, or existing sessions. Stop this
connection approach under Delivery Discipline's two-attempt repair limit.

Next dependency: establish the installed native harness's supported handshake
and exact per-session custody/retirement interface. Do not retry this same failed
connection approach without an explicit request for additional diagnosis. Do not
implement the surrounding runner, switch execution routes, bypass the hook, or
launch an executor with no qualified retirement path to obtain an apparent pass.
The original acceptance gate and complete start/end outcome remain unchanged.

### Corrected connection finding and development work

The user requested the needed regression work and challenged the overly broad
development hook. Continued inspection found the existing installed native
client's WebSocket handshake. The earlier probe sent raw JSON without that
handshake. Using the existing read-only client, initialization and an exact
coordinator `thread/read` both passed. See
[the actual observation](ControlWorkflowEvidence/20261018-native-websocket.log).
The preceding two-attempt connection block is superseded by this measured
progress; it does not remain a reason to stop authorized work.

This proves the read-only connection, not launch custody, a native work fence,
retirement, process-tree closure or recovery. No new mission/model turn or
lifecycle effect was sent. The first gate still requires those actual proofs.

The user also requested a reusable guide against excessive hooks and governance.
Its [new instruction](../docs/how-not-to-overblock-development.md) separates
development commits from runtime qualification. The bounded
[commit-gate correction](../docs/commit-gate.md) verifies the checker and its own
regressions through an independently reviewed development policy. This is enabling
maintenance, not completion of mission automation. Subsequent mission code needs
its own reviewed inventory and meaningful regressions; gate tests do not qualify
the mission runtime. The original start/end outcome remains the acceptance target.
