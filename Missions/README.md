# Missions

This folder is the mandatory registry and coordination home for every CodeExp2
mission. Product source and native execution remain in each mission's registered
target repository. Mission registration and coordination never live in a root
document or an unregistered external repository.

## Registered missions

| Mission | Purpose | Target repository | Running guide |
| --- | --- | --- | --- |
| BallisticsExperimental | Coordinate work on the experimental game repository | `/Users/boandersson/Desktop/BallisticsExperimental` | [Guide](BallisticsExperimental/README.md) |
| WEBSITE | Coordinate work in the website repository | `/Users/boandersson/Desktop/WEBSITE` | [Guide](WEBSITE/README.md) |

**Start a NEW mission** is always an additional choice. Establish its name,
target repository and intended outcome, then use the setup procedure below.

On every `onboard`, read this current table and check that each running guide
exists before presenting the choices. Do not open the guides or their targets
to build the menu. List every valid registered entry in registry order, without
preselection or recommendation. Registration means available for selection,
not running, connected, authorized to execute or ready to resume. An unavailable
guide is a broken registration: report it and hold only that mission. If the
registry is empty, still offer **Start a NEW mission**.

A valid registration requires both this table entry and its named
`Missions/<name>/README.md`, with the target and authorized mission scope recorded
in that guide. A directory alone is insufficient. `Packages/`,
`ControlWorkflowEvidence/` and shared design documents are support material,
not missions. Do not infer missions from other directories, Git history or
external repositories. No Machine mission is currently registered.

Several missions may be ongoing simultaneously. Each keeps its own builder
identity, scope, assignments, native plan/report/evidence references,
coordination handover and lifecycle notes under `Missions/<name>/`. Native
implementation artifacts and reports stay in the target's configured locations;
link them rather than copying product state here. Selection is this conversation's explicit
focus, not a global singleton. Switching focus does not stop other missions;
ending one affects only its own work and owned processes. Coordinate shared
repository/worktree ownership explicitly rather than starting conflicting writers.

Reusable installation packages:

- [Builder Communication v1](Packages/BuilderCommunication/README.md) — structured
  coordinator/builder messages and a scoped target `AGENTS.md` addition.

Accepted automation design: [Mission start and close](CONTROL_WORKFLOW_PROPOSAL.md)
reviews `MISSION X` / `END MISSION X`, installation checks, scoped publication
and verified retirement. Implementation is blocked at native-control qualification;
no mission CLI is installed. See the linked design's implementation checkpoint.

Each mission's instructions should identify its target repository, purpose,
startup procedure, relevant guidance, build and play commands, verification
requirements, and handover location. When a builder agent is involved, include
the mission's connection and coordination procedure.

Keep repository-specific instructions under a clearly named mission folder.
Link to the target repository's canonical instructions and handover so the
mission can resume from its current state next session.

Each running guide references its registered target's actual instructions,
canonical plan, handover and native execution entry points.

Follow the target repository's applicable instructions and the user's current
assignment. Recorded commands and historical results do not grant execution
authority or establish the repository's current status.

## Coordinator onboarding (`onboard`)

`onboard` is a conversational startup request for the CodeExp2 mission
coordinator. Complete these steps before reporting readiness to establish or
coordinate missions. This checklist does not install a mission CLI or qualify
automatic mission start/end.

1. **Load the workspace rules.** Read in full [README](../README.md),
   [AGENTS](../AGENTS.md), [current handover](../Mission_Sofar.md) and this mission
   index. Read the five shared guides: [Delivery Discipline](../docs/delivery-discipline.md),
   [coordination](../docs/how-to-coordinate-with-a-builder-agent.md),
   [plan history and refresh](../docs/how-to-follow-and-refresh-a-plan.md),
   [runtime delivery](../docs/how-not-to-overengineer.md) and
   [proportional gates](../docs/how-not-to-overblock-development.md).
   Read the [Builder Communication package](Packages/BuilderCommunication/README.md),
   its [contract](Packages/BuilderCommunication/CONTRACT.md) and
   [delivery settings template](Packages/BuilderCommunication/DELIVERY.md).
   Apply remaining guides when their subject applies; Machine-specific contracts
   do not become requirements for unrelated missions by default. Report missing
   or unread required documents instead of claiming complete onboarding.
2. **Establish current state.** Inspect CodeExp2's branch, HEAD, tracked and
   untracked changes, staged work and recent history. Reconcile these observations
   with the handover and current user request. Preserve existing work. Historical
   commands, approvals, thread IDs and readiness reports grant no new authority.
3. **Establish the mission scope.** Use the user's selected mission and outcome.
   For bare `onboard`, always present the current registered choices and **Start
   a NEW mission**. Do not inherit a selection from earlier conversation, recent
   history, the workspace handover or the only entry in the registry. With no
   explicit selection, finish at that menu without reading mission-specific
   guides, handovers, plans, target instructions or builder state. If the user
   explicitly selects a mission with the startup request, validate its
   registration before proceeding. For an authorized new mission, complete its
   registration below before any connection, launch or mission execution.
4. **Load the target's native baseline when selected.** Read the actual target's
   applicable instructions, orientation, canonical handover and relevant complete
   plan, including history and future dependencies. Inspect its current Git
   state and native startup entry before any authorized execution. Identify the
   builder, ownership boundaries, existing assignments and unresolved effects.
   Record an absent plan or unknown readiness explicitly. CodeExp2 onboarding
   does not replace the builder's own native onboarding.
5. **Prepare the coordination path.** For an authorized connection, verify the
   exact repository and builder identity through supported tools and collect a
   fresh matching completed ACK before assigning work. Read the target's installed
   communication contract and DELIVERY settings; compare package compatibility
   and read the complete source package before any authorized installation.
   Supply the rules the builder must actually read and apply. Use bounded
   assignments tied to the builder's current plan and observable acceptance.
   The builder executes in its repository; the coordinator collects complete
   reports, verifies evidence and reconciles the shared baseline before the next
   eligible step. Creating/replacing an agent or taking over its files requires
   the applicable authorization; saved session metadata proves no live receiver.
   Before execution readiness or a product assignment, complete all three
   [required mission execution setup steps](#required-mission-execution-setup).
   A completed communication ACK alone is insufficient.
6. **Return a concise readiness report and choices.** Identify yourself as
   **Coordinator**. State the documents actually read, observed workspace Git
   state and missing common
   prerequisites. Include **Available Missions** using the current registry and
   **Start a NEW mission** as the final option. With no explicit selection, state
   **No mission selected**; do not suggest a preferred mission or its next task.
   After explicit selection, report only that mission's authorized scope and
   actual intake/readiness results, keeping other missions' state separate. Keep
   coordinator onboarding readiness separate from builder receiving readiness
   and runtime qualification. No launches, messages, installation, product work
   or publication follows from `onboard` alone; continue work already authorized
   by the user without inventing another permission step.

Example menu for the current registry (regenerate it from the table each time):

```text
Coordinator ready. No mission selected.

Available Missions
1. BallisticsExperimental
2. WEBSITE
3. Start a NEW mission
```

## Concurrent CodeExp2 instances

The human may open several CodeExp2 instances and select a different mission in
each. Coordinators own the resulting coordination. Do not ask the human to track
session ownership, relay agent messages, prevent file collisions, merge routine
changes or arrange worktrees. Bring back only a material outcome, scope, budget,
risk or authority decision that cannot be resolved within existing authorization.

1. **Keep each selection local.** Bare onboarding still ends at the mission
   menu, without reading other missions' state. After selection, reconcile that
   mission's existing coordination record and current target state. Record the
   actual Coordinator session identity when available, target/worktree, builder,
   owned scope and outstanding assignments in the existing mission record.
   Unknown identities remain unknown; a saved identity is not a live ownership
   claim. Selecting the same mission in another instance does not transfer it
   or authorize duplicate dispatch.
2. **Resolve overlapping ownership before effects.** Within authorized scope,
   check the selected mission's records and supported host/session information
   for work using the same target, builder or files. Establish who owns any
   overlap through an authorized supported route; maintain disjoint assignments
   or arrange a single writer. Use an isolated worktree only when appropriate
   and authorized, preserving the builder's native plan and existing work.
   Separate worktrees do not isolate shared processes, assets or services.
   Do not load unrelated mission histories simply because another instance may
   exist, and do not require a global all-session check for disjoint work.
3. **Protect shared workspace changes.** Mission notes belong in their own
   folders. Before changing a shared file such as this registry or the root
   handover, re-read its current content and diff, preserve other work and
   reconcile intervening edits. When another writer is known, arrange one writer
   for the overlapping edit before writing. Serialize shared-index, branch,
   staging and publication operations; stage only the authorized changes and
   never commit another instance's work incidentally. A note is not an atomic
   lock, and an unchanged Git status does not prove another writer is absent.
4. **Handle uncertainty without user bookkeeping.** If ownership or a necessary
   communication route cannot be established, hold only the conflicting write,
   dispatch or lifecycle effect. Continue independent authorized work, report
   the concrete gap and pursue the smallest supported resolution within scope.
   Do not silently take over, launch a replacement, invent a transport or tell
   the human to manage another terminal. A genuine missing authority or provider
   capability remains an explicit dependency, not a claim of automatic safety.
5. **Close only owned work.** Update the mission's existing handover and ownership
   record when transferring or ending coordination. Reconcile uncertain effects
   before redispatch; release only the assignments and resources actually owned.
   Other missions, instances and shared services retain their state and authority.

These are Coordinator duties, not an installed cross-process lock or automatic
session controller. Existing communication, execution setup, lifecycle and
publication boundaries still apply. Opening another instance grants no agent
contact, launch, implementation or publication authority by itself.

## Set up a mission for a new repository

1. **Define the mission.** Record the user's intended outcome, repository name,
   local path and authorized scope. Distinguish investigation, implementation,
   build/run, and publication authority. Setting up running instructions does
   not itself authorize executing all the commands they describe.

2. **Register the mission.** Create `Missions/<name>/README.md` in CodeExp2
   and its exact name, purpose, target root and guide link in the registry table
   above. Use the minimum guide contents below. Record unknown native setup,
   connection and readiness facts as unverified until checked in later steps;
   registration itself proves no receiving readiness or runtime capability.
   Validate the table entry and guide before target setup, connection, launch,
   installation or mission execution. Keep coordination handovers and
   mission-specific decisions in that folder. An unregistered repository request
   enters this setup procedure rather than bypassing the registry.

   Each registration has independent scope and lifecycle. Do not replace another
   registration, overwrite its handover or close it when adding this mission.
   Keep native project plans and canonical continuation state in the target;
   link to them rather than maintaining competing copies in CodeExp2. Ordinary
   CodeExp2 instruction and registry maintenance is workspace work, not an
   implicit mission.

3. **Establish the target repository.** Keep the project at its agreed registered
   location rather than nesting product source inside CodeExp2. For an existing
   repository, inspect its current branch, HEAD, working tree, staging area and
   remotes before changing anything. Preserve existing work. Create, initialize
   or clone a repository only when that action is part of the user's request;
   do not re-import an existing mission's source to start another session.

4. **Read the applicable instructions.** Read CodeExp2's
   [AGENTS.md](../AGENTS.md) and
   [Delivery Discipline](../docs/delivery-discipline.md), together with the
   target repository's applicable ancestor and local instructions, orientation
   and handover. Read the coordinator guide for builder coordination, the runtime
   guide for application work, and the plan guide before executing or updating
   a plan. Identify the current assigned plan, or explicitly record that none is
   assigned. Do not transfer Machine-specific installed capabilities to another
   repository by assumption.
   The target's own onboarding, startup entry, governance and handover come
   first. Read entry scripts before running them and execute only the startup
   required for the authorized scope. Record missing or blocked steps explicitly;
   CodeExp2 onboarding is not a substitute for the target's native procedure.
   Complete the guide's native references from actual observations.

5. **Establish ownership and communication.** Record the coordinator's role,
   the execution owner and the repository each uses. If builder coordination is
   authorized, follow the
   [coordinator guide](../docs/how-to-coordinate-with-a-builder-agent.md).
   Discover the intended existing builder through supported tools, verify its
   repository and identity, and obtain a fresh acknowledgement before delegating
   work. A saved thread ID is a discovery hint, not proof of receiving readiness.
   Explicitly supply the instructions the builder must read and apply. Do not
   spawn a replacement or start work merely because the guide describes one.
   If the user authorizes a new repository agent, use the launch procedure below
   and verify a fresh matching ACK before assigning implementation.

6. **Complete required execution setup.** Perform and record all three
   [execution setup steps](#required-mission-execution-setup): native approval
   review, ordinary mission permissions, and approval/cancellation control.
   Provision, configure and connect the required host controls as part of mission
   establishment; checking whether they exist is not the complete setup task.
   Complete the bounded real verification below before declaring execution
   readiness or dispatching product implementation, builds or conversions.
   Registration and a messaging ACK do not satisfy this requirement. If a
   capability is missing, record `EXECUTION_BLOCKED` with the exact gap; continue
   independent read-only work within scope. Do not launch an uncontrolled builder
   to discover afterward whether its approvals can be reached.

7. **Record the real delivery path.** Identify the project's actual build,
   launch/play and focused verification commands, including their working
   directory, configuration and evidence locations. Define observable acceptance
   for the requested outcome and the behavior that must be preserved. Mark
   commands and capabilities as unverified when they have not been checked;
   execute them only within the current assignment's authority.

8. **Set the remote boundaries.** Record the approved fetch and push destination,
   branch and any source repository restrictions. Distinguish an imported source
   from the mission's publication remote. Inspect existing Git configuration
   before changing it, preserve applicable protection and hooks, and never infer
   permission to synchronize or push from a documented URL. When publication is
   authorized, verify the destination and scope before using an explicit branch
   refspec.

9. **Start with a bounded assignment and leave a handover.** Give the execution
   owner a concrete outcome, scope, preservation requirements and required
   evidence. Review returned results against that assignment. Update the target
   repository's canonical handover with the exact checkpoint, dirty work,
   evidence paths, unresolved limits and next authorized step. Keep the CodeExp2
   guide focused on how to resume; dated historical results must be clearly
   identified and rechecked next session.

## Required mission execution setup

These three steps are mandatory when establishing or resuming an execution
mission, including an investigation that expands into implementation or native
conversion. Apply them to the Coordinator and each executor at the boundaries
they control. Record the result in the selected mission's guide or coordination
record before declaring `EXECUTION_READY` or dispatching product work.

**Host controls are a mission establishment deliverable.** The Coordinator owns
arranging their provision/configuration, connecting the chosen executor through
them, and collecting proof that they work. Reuse working host facilities first.
If a control is missing, identify its host/provider owner and make its bounded
configuration, connection or repair a setup prerequisite within the authorized
mission scope. Do not defer it to product execution or describe the mission as
established merely because the missing control was documented. Establishment
remains incomplete until the required controls pass verification.

If a provider change requires authority or access the mission does not have,
record the exact owner, required change and missing authority. Continue useful
authorized setup work; do not invent a host API, widen permissions, or turn the
gap into an unrelated infrastructure project. A genuine external dependency may
block completion of establishment, but it does not remove this setup obligation.

Registration, bare onboarding and independent read-only investigation remain
available without qualifying an executor. Mark execution as unqualified; do not
describe registration or a completed messaging ACK as execution readiness.
Authorized disposable qualification probes may precede product work, provided
their approval and cancellation route is available before the probe starts.
This procedure does not authorize agent launches, permission changes, probes,
publication or resumption of an owner-ended mission by itself.

1. **Establish native approval review.** For unattended builders, select native
   automatic review (`approvals_reviewer = "auto_review"` with an eligible
   interactive approval policy, normally `on-request`; the CLI also provides
   `--approve-for-me`). Verify support in the installed version and the effective
   settings of the actual receiving session. A global config file, launcher flag
   or message saying "approved" is not proof that the host applied those settings.
   Manual review is eligible only for an explicitly chosen attended workflow
   whose prompt and response controls are actually accessible to the owner;
   never depend on an unseen Terminal. Keep denied, timed-out and unsupported
   approval categories visible. Automatic review does not guarantee acceptance
   or replace separate app/Computer Use consent.

2. **Establish ordinary mission permissions.** Identify the exact working root,
   read-only sources, writable output/scratch directories, necessary network
   access and native application/process requirements. Reconcile permission
   configuration layers, including modern profiles versus legacy sandbox
   settings, and verify effective access through harmless representative work.
   For builds/conversions, include the real required tool or application entry
   point. Configure access only within existing owner authority and host policy;
   missing authority blocks that change, not unrelated inspection. Do not rely
   on repeated escalation for routine approved work. `never` alone grants no
   additional access; broad full access is not the default repair for missing
   controls. Preserve source protection and unrelated project boundaries.

3. **Establish approval and cancellation control.** Configure and connect the
   supported host route that exposes the exact pending request/action and resources,
   receives a scoped decision, and confirms request resolution plus the actual
   action result. Bring any owner decision into the attended Coordinator
   conversation with a supported response path; never assign the owner a hidden
   terminal task. Separately prove cancellation of the exact executor turn while
   approval is pending, confirmation of its final state, and cleanup of any owned
   child processes. A queued message, archive operation, ACK or window ID is not
   cancellation/retirement proof. For shared builders, stop only the mission's
   turn/effects; preserve other work and the shared daemon. `END MISSION` ends
   dispatch eligibility and supersedes unexecuted approval authority for that
   mission. Reconcile uncertain effects rather than approving or replaying them.

### Required evidence and passing route

Use one small, disposable verification of the actual supported route:

- An ordinary representative edit/test or native operation succeeds within the
  configured access, without changing protected source assets.
- A harmless request that genuinely requires approval receives a scoped decision;
  request resolution and the actual operation result are observed.
- A declined request returns a visible explanation and does not execute.
- Cancellation while approval is pending produces a confirmed final turn state,
  prevents the pending action, and accounts for any owned processes.
- Reconnection/status reconciliation preserves pending/resolved/cancelled state
  without duplicate work. A disconnect or timeout is not permission to replay.

Retain the dated commands/events/results and relevant artifact hashes through the
existing mission evidence route. Bind them to provider/tool version, effective
permissions/reviewer, repository/workspace, receiver identity and configuration
scope. Record each of the three steps as `PASS`, `BLOCKED` or `NOT_PROVEN`, with
the supporting evidence and any excluded operation categories. Reuse existing
evidence only after verifying that its scope still matches the actual receiver
and route; repeat affected checks when the provider, configuration, permissions,
workspace or control route changes. Do not rerun a whole qualification merely
because another harmless task uses the same verified route.

All three steps must pass for the proposed execution scope. Otherwise record
`EXECUTION_BLOCKED`, the affected operation and smallest missing capability;
retain the registration and continue independent authorized inspection. Do not
silently switch executor, bypass policy, launch a replacement, or repeatedly ask
for consent already supplied. A supported alternative requires reconciliation
and its own applicable evidence. These are procedural requirements, not an
installed admission controller or a claim that the current task tools supply
approval responses or cancellation.

Official behavior references: [Auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review),
[permission profiles](https://learn.chatgpt.com/docs/permissions) and
[app-server approvals and turn control](https://learn.chatgpt.com/docs/app-server#approvals).
Recheck installed behavior before configuring a future execution route.

## Minimum contents of a mission guide

- Purpose, authorized scope and preservation requirements.
- Target repository path and links to its instructions, plan and handover.
- Coordinator/builder roles and the verified connection procedure, if applicable.
- Results and evidence for all three required execution setup steps, effective
  configuration/receiver binding, and any execution block or excluded scope.
- Host-control setup owner, configured connection, and any unresolved provision/
  repair prerequisite that keeps mission establishment incomplete.
- Read-only startup checks for current Git state and continuation state.
- Build, run/play and verification entry points, with evidence requirements.
- Approved remotes, source restrictions and commit/push boundaries.
- Handover procedure and any clearly dated checkpoint notes.

A future session should be able to find the correct repository, establish its
current state, connect to the intended executor when applicable, and identify
the next authorized action without relying on this chat's history.

## Start a new repository agent when authorized

```text
Inspect target's own onboarding / startup / governance / handover
    |
    v
Validate exact repo path, installed Codex and outstanding work
    |
    v
Verify the proposed approval/cancellation route; authorize bounded setup probes
    |
    v
Open Terminal there; pass known first task when starting Codex
    |
    v
Agent follows native repo onboarding before external mission additions
    |
    v
Discover actual new thread; collect matching completed readiness ACK
    |
    v
Complete all three execution setup steps with receiver-bound evidence
    |
    v
Assign bounded installation / work; preserve existing owners and dirty files
```

Follow the local [Codex launch law](../../DOCTRINE/Codex%20Initial-Prompt%20Launch%20Law.md)
and [launcher checklist](../../Tools%20%26%20Systems/Launchers/CODEX_LAUNCHER_PATTERN.md).
Validate the user-selected repository and executable first. For a known task,
change to that exact directory and launch Codex with a positional initial prompt
in the same Terminal command. Use the installed CLI's help to confirm syntax.
Do not open bare Codex and then inject text/Return, poll banners, or scrape its
terminal output to establish readiness. Do not override model, account, trust or
permissions merely to get the session started. Report any actual launch block.
An explicitly authorized mission execution configuration must be selected and
verified under the three setup steps above; do not silently inherit an unusable
manual approval path or change policy to conceal a missing control.

The initial task must instruct the agent to use its repository's actual native
onboarding and handover first, reconcile current scope and Git state, preserve
existing work, and return a fresh identity/readiness ACK. An old interrupted
task does not authorize resuming its pending implementation. A Terminal window
or thread listing alone proves no receiving readiness; collect the completed
matching response through supported tools. Keep the launch, connection and
assignment identities in the mission's existing evidence directory.
