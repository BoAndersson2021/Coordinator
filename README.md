# CodeExp2 — missions and reusable agent instructions

This repository holds reusable agent instructions and the registry for
cross-repository missions. Every mission is registered under `Missions/` before
it runs; product source stays in its own registered target repository. Several
missions may be ongoing, each with its own builder, plan and coordination state.
CodeExp2 is not an autonomous runtime or a qualified workflow executor.

## Start here

For desktop startup, open the **CodeExp2** alias. The local Swift
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

1. Read [AGENTS.md](AGENTS.md) for repository rules, the complete instruction
   catalog and how the guides work together.
2. Read [the current state and handover](Mission_Sofar.md) before continuing work.
   Reconcile it with the current user request, Git status and relevant plan.
3. Use [the mission registry and setup procedure](Missions/README.md) for all
   mission selection, registration and coordination. No mission runs through
   an unregistered root document or an external repository shortcut.

## Instruction corpus

[The AGENTS catalog](AGENTS.md#reusable-agent-instructions) is the canonical list:
eight standalone guides and an inline CLI workflow review procedure. It explains
which guides apply, how to combine them and how to hand them to agents elsewhere.

Delivery Discipline defines shared delivery rules and the repair limit. The
runtime-target, plan and coordinator guides cover real integration, plan history
and delegated execution. These four are repository neutral. The build,
communication and lifecycle contracts describe Machine scope; reuse elsewhere
requires mapping their requirements, paths and recorded state to the target.
The [guide to avoiding excessive blocks](docs/how-not-to-overblock-development.md)
covers hooks and governance: protect concrete effects and provide a tested path
for authorized development. Links between guides route relevant instructions
and do not create extra stages.

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
