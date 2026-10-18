# How to work on BallisticsExperimental as a CodeExp2 agent

Use this guide when coordinating an authorized BallisticsExperimental mission
from CodeExp2. It records the working arrangement and lessons from this session.
The user's current request, applicable repository instructions and verified
state govern execution. This document does not start an experiment, launch an
agent or grant publication authority.

## Your role and the two repositories

| Location | Purpose and ownership |
| --- | --- |
| `/Users/boandersson/Desktop/CodeExp2` | Your coordinator workspace: reusable guidance, mission instructions and coordination decisions. |
| `/Users/boandersson/Desktop/BallisticsExperimental` | The standalone game repository. Its builder owns assigned implementation, tests, builds, runtime verification and technical evidence. |
| `https://github.com/WRRTREPO/BallisticsExperimental.git` | The approved experimental remote. Publication requires authority from the current session. |

Translate the user's intended result into a bounded assignment, establish the
builder's readiness, review the returned source and evidence, and decide the
next eligible action within scope. The user owns product decisions and reserved
approvals. Acceptance of an investigation does not adopt its candidate physics.

Keep implementation ownership clear. Review source and logs independently, but
avoid editing the builder's files while it works. Agree who owns each native
run. A coordinator takeover requires reconciling outstanding work and authority.
In this session, the coordinator handled reviewed Git publication and the later
handover amendment after the builder completed implementation and verification.

BallisticsExperimental stays in its own Desktop repository. Always specify the
target working directory for file and Git operations. A command issued from
CodeExp2 must not accidentally stage game files into CodeExp2 or change its
unrelated `Machine/TASK_TIMELINE/` candidate.

## Read the canonical instructions first

Read CodeExp2's [AGENTS.md](../../AGENTS.md), [README.md](../../README.md) and
[handover](../../Mission_Sofar.md), then apply the relevant portable guides:

- [Delivery Discipline](../../docs/delivery-discipline.md) for every task.
- [Coordinator guide](../../docs/how-to-coordinate-with-a-builder-agent.md)
  before delegated execution.
- [Runtime-target guide](../../docs/how-not-to-overengineer.md) for running
  application work.
- [Plan-following guide](../../docs/how-to-follow-and-refresh-a-plan.md) before
  following or updating an assigned plan.

In the game repository, read [AGENTS.md](../../../BallisticsExperimental/AGENTS.md),
[README.md](../../../BallisticsExperimental/README.md) and
[MISSION_PROTOCOL.md](../../../BallisticsExperimental/MISSION_PROTOCOL.md).
Apply applicable ancestor instructions, including the
[Desktop instructions](../../../AGENTS.md), and nested instructions for the
assigned paths.

The game's `MISSION_PROTOCOL.md` is canonical for startup, builder connection
and handover. Use its latest current-state section and retain historical
checkpoints in their original scope. This guide routes to that protocol; it
does not replace it or maintain a second implementation plan.

Machine's execution barriers, installed providers and qualification history
remain within their applicable scope. BallisticsExperimental explicitly does
not adopt them merely by referencing CodeExp2's portable guidance. Respect
CodeExp2's own hooks when changing CodeExp2; inspect the game's actual hooks
when committing there. Never bypass either repository's enforcement.

## Establish the actual mission baseline

Start with read-only inspection in the game repository:

```sh
be_repo=/Users/boandersson/Desktop/BallisticsExperimental
git -C "$be_repo" rev-parse --show-toplevel
git -C "$be_repo" status --short --branch
git -C "$be_repo" rev-parse HEAD
git -C "$be_repo" log -5 --oneline
git -C "$be_repo" diff --stat
git -C "$be_repo" diff --cached --name-only
git -C "$be_repo" remote -v
git -C "$be_repo" config --get push.default
```

Read relevant diffs and retained evidence. Record branch, exact HEAD, dirty and
staged paths, current assignment, applicable plan or none, and outstanding work.
For native work, also identify the actual engine, configuration, tuning and
source bytes used by the build. QuickPlay includes uncommitted changes, so HEAD
alone is insufficient build identity.

The user made this an experimental mission. Imported `GAME_DELIVERY_PLAN.md`,
`GAME_PLAN_OVERVIEW.md`, `Engineering/PLAN.md` and upstream work packets are
historical references. They do not select the next task. If no experimental
plan is assigned, record **experimental plan: none**. If one is assigned, use
the builder's current plan and its history; reconcile prerequisites and future
dependencies before changing it.

An investigation-only assignment stays within its stated inspection,
instrumentation and execution limits. The later user instruction to resolve
the signed-speed defect authorized that repair; the preceding read-only work
did not authorize it by itself. Continue routine work already authorized without
asking for repeated confirmation.

## Connect to the existing builder

Use the host's supported Codex thread tools. Read their installed schemas;
tool availability and argument shapes can change. The interface used during
this session exposed `list_threads`, `read_thread`, `send_message_to_thread`
and `wait_threads` through `mcp__codex_tui__` tools.

Historical rediscovery hints, recorded on 2026-10-18:

| Role | Thread UUID | Expected working directory |
| --- | --- | --- |
| CodeExp2 coordinator | `01a14b70-e481-7e13-9cb1-6d5f0d0e814a` | `/Users/boandersson/Desktop/CodeExp2` |
| BallisticsExperimental builder | `01a14b73-b7a5-7062-865e-ebd47b6b3ce0` | `/Users/boandersson/Desktop/BallisticsExperimental` |

These identify earlier sessions, not current receiver readiness. Do not launch
a replacement or additional agents merely because this guide lists them.

1. List threads and match the intended UUID and repository directory. Read the
   candidate's recent turns to reconcile identity, role and outstanding work.
   A title, `active` status or old ACK is insufficient.
2. Send a fresh, unique `BE-CONNECT-<UTC>-<suffix>` orientation token. Request a
   completed final ACK containing the exact token, thread identity, cwd/repo
   root, branch/HEAD/status, instructions read, plan or none, blockers and
   readiness. During this check, prohibit edits, builds and game execution.
3. Inspect the actual reply and completed turn, matching delivery/turn/cursor
   identifiers where available. A send receipt proves delivery information,
   not readiness, implementation or completion.
4. Only then deliver the bounded authorized assignment. Keep prompts within the
   installed size limit; this session's tool accepted at most 1,000 UTF-8 bytes.
   Link to an existing assignment or a short local assignment file when needed.

Example argument shapes from this session:

```text
list_threads({limit: 20})
read_thread({threadId: "<verified-builder>", turnLimit: 5,
             includeOutputs: true, maxOutputCharsPerItem: 6000})
send_message_to_thread({threadId: "<verified-builder>",
                        prompt: "<fresh token and bounded request>"})
wait_threads({targets: [{threadId: "<verified-builder>"}], timeoutMs: 30000})
```

Omit model overrides unless the user requests them. Respect pagination and
truncation; a wait timeout is not a completion result. If delivery is uncertain,
read the target and reconcile possible effects before retrying. Do not send
duplicates or use terminal input, transcript scraping or another application as
a substitute transport. Report the exact communication gap and continue only
independent authorized work.

Avoid mutual waiting: the builder returns a completed result, and the
coordinator reviews it and sends the next decision. The builder should not need
the coordinator's entire user-facing turn to finish before returning its result.

## Assign and coordinate one bounded result

An assignment should state the target repository, current baseline or plan step,
user-visible result, permitted changes and execution, preservation requirements,
acceptance checks, required evidence, file ownership and return conditions.
Use existing mission records; create an assignment file only when it helps make
the work concrete. Do not build a separate governance system around a repair.

For example, the collision assignment required reproducing the accepted negative
speed, fixing its owning constrained-contact boundary, preserving suspension and
tuning, adding meaningful regressions, running native qualification and the
mandatory timing guard, and returning raw evidence. It withheld commit/push
until the user subsequently requested publication.

Let the builder make routine implementation choices within scope. Send review
findings when they affect correctness or acceptance, with exact source and
observed failure. Do not repeatedly interrupt it, prescribe speculative systems
or duplicate its implementation. Keep the user informed of material findings,
uncertainty and remaining work.

Carry Delivery Discipline's shared repair limit across both agents: after two
consecutive ineffective repairs against the same integration blocker, stop that
approach and report the failed assumption. Renaming a task does not reset the
count. A deliberate baseline reproduction is evidence of the original failure;
a passing fixture alone does not establish progress on a failing native path.

## Preserve product law and the existing machine

Before movement-related work, read the approved
[Tube Movement Law 001](../../../BallisticsExperimental/Docs/Product/TUBE_MOVEMENT_LAW_001.md),
including active Amendment A and the stiffness clarification.

- `S` is forward-only spline travel; `Theta` is full-360-degree circumferential
  travel. Chassis orientation does not determine travel direction.
- `H` is permitted bounded magnetic suspension displacement, with its own
  velocity. Preserve and inspect existing normal-radius dynamics. It is not an
  independently controllable travel axis and must not directly create travel.
- Soft low-speed suspension and progressive high-speed attachment are intended.
  Reference curves and numerical experiments do not become production tuning
  through a passing test.
- Preserve the authoritative V2 worker, fixed `1/120s` simulation step, owed
  steps, accepted-state publication and smooth rival presentation. Rendering
  frequency is independent. Do not redesign presentation to hide solver faults.

For the signed-speed repair, forward travel became a joint contact constraint
before validation, hashing and publication. An `abs()` or unexplained final
speed clamp would not establish a correct contact response. Preserve the
user-approved removal of rival pack blocking unless a new assignment explicitly
changes that gameplay decision.

The complete original invariant catalog was not supplied. Follow the canonical
document's approved wording and explicit gaps; do not invent missing clauses.
Do not assume player/rival equivalence from shared structures, tuning names or
worker ownership. Trace their executed solvers and state commitment.

## Use the actual build and play path

From the game repository, choose the command appropriate to the assignment:

| Purpose | Command |
| --- | --- |
| Build without launching | `./QuickPlay.sh --build-only` |
| Build and play the current game | `./QuickPlay.sh` |
| Build and verify timing/presentation/collision regressions | `./QuickPlay.sh --timing-guard` |

The first builds without launching. Ordinary QuickPlay builds and plays the
actual working tree, including uncommitted edits. The timing guard builds and
runs its required focused checks and rendered workload. Execute the commands
needed by the authorized task; documentation and publication do not require an
identity-only rebuild or a new game run.

Preserve existing logs before operations overwrite stable outputs. Use the
checkout lock and Unreal `-WaitMutex`; preserve unrelated processes. Do not use
`-NoMutex`, install SDK governance, enable optional bridge plugins, package the
source game or run imported admission workflows merely to use QuickPlay.

For changes touching timing, worker/solver, collision, stability, telemetry,
camera/presentation, HUD or displayed time, the final executable must pass
`./QuickPlay.sh --timing-guard` under the game's current
[guard instructions](../../../BallisticsExperimental/Tests/CollisionPacing/README.md).
The session's mandatory gates included:

- Both pinned native tests, `Ballistics.Collision.Pacing` and
  `Ballistics.Collision.TimingGuard`, and a fresh successful receipt for the
  rendered 120-second workload; no failed, skipped or incomplete mandatory tests.
- Fixed 120Hz simulation, observed throughput within 114..126Hz, source
  admission by step 16, and worker/camera/HUD freshness within 250ms.
- Continuous crossings by all six rivals beyond the first wall's clear plane
  by step 1200, plus an actual matching player impact.
- Actual accepted close passing, wall contact and zero rival pack-block notices.
- Correct accepted HUD source identity, values and age, including retained
  frames, and the minute-widget/camera-cache checks.

Read the current contract before executing; this list does not replace it.
A default-off guard pass does not qualify an opted-in diagnostic. The separate
`./QuickPlay.sh --forward-qualification` route exercises the bounded opted-in
shadow workload and captured-state replay; its scope is documented in the
[collision report](../../../BallisticsExperimental/Engineering/Investigations/BE-COLLISION-FORWARD-001/REPORT.md).

## Review evidence before declaring success

Compare the builder's return against the assignment and actual files. Inspect
the owning source, changed paths, fresh native reports/receipt, raw logs,
telemetry, source/configuration identities, artifact hashes and owned-process
shutdown. Separate builder claims from your independent checks and user
acceptance. Do not describe your own edits as independently reviewed.

Record HEAD plus dirty-source identity, engine/configuration, tuning, command,
run identity and simulation steps where relevant. Freeze executable source
through its qualifying run; reconcile subsequent edits before carrying results
forward. Diagnostic instrumentation must be identified. In this session, exact
reversal of saved printf insertions reconciled instrumented source hashes with
the unmodified tested worker bytes.

Keep these distinctions explicit:

| Evidence | What it establishes |
| --- | --- |
| Successful build or launch | Compilation or startup, within that run's scope. |
| Controlled solver fixture | Its admitted inputs and exercised branches. A fixture rejected before contact proves no contact behavior. |
| Captured real-worker replay | Agreement for that capture and ABI; not full host scheduling or cross-platform determinism. |
| Authoritative state transition | Physical behavior for the observed case; rendered transforms alone are insufficient. |
| Passing attached contact/hold workload | That workload's continuity and timing; not racing-speed or all-lifecycle qualification. |

Preserve failed attempts as failures. The initial collision fix passed the
opted-in workload but failed the final default-off guard at a half-wall. That
failure blocked completion until the owning representation case was repaired
and both affected native workloads passed on the final source. The signed-speed
finding itself proved accepted negative velocity, not measured backward station
travel in the original failing step.

Use the deliverables required by the assignment. Investigation packages in
`Engineering/Investigations/` retain reports, machine-readable results,
manifests and raw evidence. Preserve sealed packages, including their historical
source bindings. Write new evidence to a new authorized location or `Saved/`;
check runner defaults so they do not modify frozen investigations. Document
missing evidence and adoption blockers rather than manufacturing a pass.

## Handle Git and the remote deliberately

The source game was imported once. Never fetch, pull, clone again from, sync
with or push to `wrrtrepo/ballistics27`, through any remote name, capitalization
or transport. Do not recreate its removed remote URL. Preserve local provenance
and archived history without publishing their refs.

The sole approved remote is `origin`, with both fetch and push URL:

```text
https://github.com/WRRTREPO/BallisticsExperimental.git
```

Preserve `push.default=nothing`. When publication is authorized:

1. Recheck repository root, branch, HEAD, dirty/staged paths and actual remote
   URLs. Inspect approved remote main with
   `git -C "$be_repo" ls-remote origin refs/heads/main`.
2. Review and stage only the authorized source, documentation and evidence.
   Preserve unrelated work. Verify manifest entries and staged bytes, including
   the exact pointer/object/raw-byte relationships for LFS captures.
3. Use existing Git LFS for large raw artifacts before staging. During this
   session, two approximately 128MB input captures required exact-path
   `.gitattributes` rules. Preserve their raw hashes and keep oversized raw blobs
   out of ordinary Git history. Those two rules are already published.
4. Commit through normal hooks and configuration. Do not bypass checks, rewrite
   identities, force-push, recreate orphan history or publish archive/import refs
   or tags. Reconcile an advanced remote within the authorized scope.
5. For an authorized main push, use the explicit refspec:

   ```sh
   git -C "$be_repo" lfs fsck HEAD
   git -C "$be_repo" push origin main:refs/heads/main
   git -C "$be_repo" rev-parse HEAD
   git -C "$be_repo" ls-remote origin refs/heads/main
   git -C "$be_repo" status --short --branch
   ```

Verify push success, matching local/remote SHAs and final working-tree state.
An LFS upload message alone does not prove the branch was published. A request
to commit a handover does not automatically include pushing it; report that
distinction. Existing user authorization persists, so do not request it again
for steps already covered by the current assignment.

## Close the mission and prepare the next session

Update the game's `MISSION_PROTOCOL.md` when authorized, recording the latest
implementation/publication checkpoint, actual local-versus-remote state,
evidence paths, qualified scope, remaining gaps, process shutdown, assigned plan
or none, and next eligible user decision. Put current pickup information where
it is easy to find while retaining historical results.

Keep frozen reports and manifests unchanged. A later documentation amendment
can supersede historical publication statements without rewriting the tested
source identity. Make that distinction explicit. Record transport changes such
as completed LFS setup so the next agent does not repeat a finished operation.

End with the usable result, meaningful validation, material limits and Git
status. State whether work is local, committed or pushed. Leave the builder idle
after its completed return; do not infer a successor experiment from a report.

### Session checkpoint — verify again before use

Recorded on 2026-10-18 while writing this guide:

- Published experimental implementation: `b1bf5d4798eff9e2378fb16635af8ea904ae056c`,
  covering forward-only static contact, wall representation repair and retained
  qualification evidence.
- Local handover-only commit: `f002b51bbe129bba1be8f124898092e74bfab7f7`.
  The target working tree was clean and main was one commit ahead of
  `origin/main`; that documentation commit had not been pushed.
- Final opted-in workload: 14,400 records, exact captured canonical/shadow
  replays and public fault closure passed. It predominantly held at a pylon.
- Final default-off guard: 14,417 steps over 120.062123 seconds, maximum
  worker/camera/HUD gap 107.621ms, 23 rival passes, zero pack blocks and a passing
  first-wall outcome. These are retained observations, not a fresh runtime run.
- The high-severity collision-terminal comparison remains NOT PROVEN because
  its controlled opening was rejected before contact. Four native thermal
  recovery cycles did demonstrate the existing 180-step duration.
- Production suspension adoption remains BLOCKED on authored normal-state
  mapping/envelope/tuning, contact-time/input-event semantics, reciprocal vehicle
  state/contact and accepted-source visual response. The intermittent hitch is
  unresolved. Experimental plan: none; no successor implementation is assigned.

For fresh work, start from the target's current handover and Git state, establish
the existing builder connection, and execute the user's next bounded assignment.
