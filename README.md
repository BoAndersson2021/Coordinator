# CodeExp2 — missions and reusable agent instructions

This repository holds reusable agent instructions and the registry for
cross-repository missions. Every mission is registered under `Missions/` before
it runs; product source stays in its own registered target repository. Several
missions may be ongoing, each with its own builder, plan and coordination state.
CodeExp2 is not an autonomous runtime or a qualified workflow executor.

## Start here

For desktop startup, open the **Valhall** alias. The local Swift
[launcher](Launcher/README.md) opens Terminal in this workspace and starts
interactive Codex with `onboard` already submitted. The alias points to the
generated app under `Launcher/build/`; preserve that directory.

The CodeExp2 agent's role is **Coordinator**, both to you and to repository
agents. At session startup, say **`onboard`**. The Coordinator must follow the
[onboarding checklist](Missions/README.md#coordinator-onboarding-onboard),
read the common rules, establish workspace state and present **Available Missions**
from the [registry](Missions/README.md#registered-missions) plus **Start a NEW mission**.
It must not choose, recommend or read into a mission by default. Only after your
explicit selection does it load that mission's guide, handover, plan and target.
For a new mission, register its name, repository and outcome in `Missions/` first.
The mission repository's builder owns implementation against its native plan;
CodeExp2 coordinates assignments, dependencies and evidence review.

You may use several CodeExp2 instances for different missions. Select the mission
and intended outcome in each; Coordinators handle ownership, shared edits and
conflict resolution under the
[concurrent-instance procedure](Missions/README.md#concurrent-codeexp2-instances).
Routine coordination and worktree management are not tasks for the human. The
Coordinator also reads the [shared native-control runbook](docs/native-control.md)
on every startup and carries out its applicable setup, checks, recovery and
closure steps automatically within the authorized task. You do not need to run
its command examples or prepare its bindings. Bare onboarding still stops at
the mission menu without connecting to a receiver or launching diagnostics.

Before a mission becomes execution-ready, the Coordinator must complete all
three [required execution setup steps](Missions/README.md#required-mission-execution-setup):
native approval review, ordinary mission permissions, and supported approval/
cancellation control, with evidence bound to the actual receiver. Missing
controls must be provisioned/configured and connected as part of mission
establishment, with a named owner for any required repair. Establishment stays
incomplete until they work; dependent execution is blocked before dispatch.
Registration and read-only
investigation remain available; this rule installs no host control or permission.

1. Read [AGENTS.md](AGENTS.md) for repository rules, the complete instruction
   catalog and how the guides work together.
2. Read [the current state and handover](Mission_Sofar.md) before continuing work.
   Reconcile it with the current user request, Git status and relevant plan.
3. Use [the mission registry and setup procedure](Missions/README.md) for all
   mission selection, registration and coordination. No mission runs through
   an unregistered root document or an external repository shortcut.

## Instruction corpus

New agent-facing material follows the [canonical structured guide](.agents/guides/structured-canonical-records.json),
read on startup and verified as installed/loaded on every authorized mission
establishment or pickup. The Coordinator completes missing setup and confirms
the receiving builder has read/applied it before declaring readiness. This
existing Markdown orientation remains a routing entry; the JSON guide is the
single authoritative record of the new authoring approach.

[The AGENTS catalog](AGENTS.md#reusable-agent-instructions) is the canonical list:
the structured canonical records guide, the existing shared guides and an inline
CLI workflow review procedure. It explains
which guides apply, how to combine them and how to hand them to agents elsewhere.

For app artwork and desktop aliases, use [How to make an icon for an app and desktop alias](.agents/guides/app-and-desktop-alias-icon.json). It requires reusing usable artwork and stopping after the installed icon and actual alias are visibly verified.

Delivery Discipline defines shared delivery rules and the repair limit. The
runtime-target, plan and coordinator guides cover real integration, plan history
and delegated execution. These four are repository neutral. The build,
communication and lifecycle contracts describe Machine scope; reuse elsewhere
requires mapping their requirements, paths and recorded state to the target.
The [guide to avoiding excessive blocks](docs/how-not-to-overblock-development.md)
covers hooks and governance: protect concrete effects and provide a tested path
for authorized development. Links between guides route relevant instructions
and do not create extra stages.

Use [How to end a task](docs/how-to-end-a-task.md) for closing reports: state
what is done, what remains and the recommended next action. When an action
option remains, recommend it clearly and identify its owner and authority needs.

## Scope and history

Mission-specific intake follows selection. Root handover notes contain workspace
state; each registered mission's folder contains its own coordination history
and links to native project instructions. Neither recent activity nor a saved
builder identity makes a mission the system default. Closing one mission leaves
other missions and shared services alone.

Machine-specific requirements remain in AGENTS and the scoped contract guides.
They apply within their stated scope and do not select a mission. The removed
local Machine folder and misplaced archives remain in Git history; their removal
does not authorize recreating a mission outside `Missions/`.

## Local commit checks and history

This checkout's CodeExp2 pre-commit hook allows ordinary text documentation
changes, blocks unverified executable/data changes and protects instruction and
invariant files through reviewed changes. The separate Machine repository has
its own verifier. Documentation edits grant no runtime authority. Git hooks are
local configuration; copying a guide or cloning documentation does not establish
that a hook is installed in another checkout.

See [the CodeExp2 commit gate](docs/commit-gate.md) for the reviewed development
route, its limited source inventory, staged checks and local adoption evidence.

Keep frozen evidence and old acceptance results within their original scope.
External Machine guide snapshots are not automatically updated by edits here.
See [the handover](Mission_Sofar.md) for remaining work and historical milestones.

The [shared native-control runbook](docs/native-control.md) documents the bounded
inspection and owned diagnostic entry, evidence limits and review/closure
templates. Its [delivery record](Missions/ControlWorkflowEvidence/20261019-session-lessons-delivery.md)
separates tested diagnostic capabilities from current product readiness.
