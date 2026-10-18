# CodeExp2 — missions and reusable agent instructions

This repository holds reusable agent instructions and cross-repository mission
guides. Machine lives in `/Users/boandersson/Desktop/Machine`. The local
`Machine/` material was removed at the user's direction because it is retained
elsewhere. CodeExp2 is not an autonomous runtime or a qualified workflow executor.

## Start here

1. Read [AGENTS.md](AGENTS.md) for repository rules, the complete instruction
   catalog and how the guides work together.
2. Read [the current state and handover](Mission_Sofar.md) before continuing work.
   Reconcile it with the current user request, Git status and relevant plan.
3. For another repository, start with [mission guidance](Missions/README.md).
   For Machine work, read its own [README](/Users/boandersson/Desktop/Machine/README.md),
   [instructions](/Users/boandersson/Desktop/Machine/AGENTS.md) and
   [requirements](/Users/boandersson/Desktop/Machine/docs/WORKFLOW_INVARIANT.md).

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

## Recorded implementation and current boundaries

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` requires zero manual lifecycle,
communication and handover steps during Machine workflow execution, with visible
failures before unsupported effects. The recorded installed barrier enforces a
stop while automatic workflow providers remain unqualified.

The external [dashboard contract](/Users/boandersson/Desktop/Machine/docs/DASHBOARD.md)
and [work-view contract](/Users/boandersson/Desktop/Machine/docs/WORK_VIEW.md)
describe the recorded diagnostic features. Those milestones do not establish that a service is
running now or that project execution is qualified. Use actual read-only target
observations when current capability matters.

The abandoned native MVP experiment and its repair ladder were deleted. There is
no delivered native application to resume. The unfinished local task-timeline
candidate was included in the user-authorized removal of `Machine/`.

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
