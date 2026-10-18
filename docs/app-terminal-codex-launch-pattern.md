# Machine executor lifecycle and launch contract

This Machine-specific contract owns executor startup, readiness, retirement and
recovery. Use [Delivery Discipline](delivery-discipline.md) for shared rules,
the [runtime-target guide](how-not-to-overengineer.md) for feasibility and real
integration, and the [communication contract](how-to-communicate-with-other-codex-agents.md)
for dispatch and collection. The [coordinator guide](how-to-coordinate-with-a-builder-agent.md)
assigns builder work against its plan; the [build protocol](universal-multi-agent-build-protocol.md)
connects these responsibilities. None of these documents supplies a live controller.

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` applies to every new/edited launch, stop,
restart, handover and adapter feature. Execution requires zero manual terminal
actions or session transfers, with visible status and loud blocking failures.
The older user-operated Terminal pattern is historical development guidance,
superseded for Machine workflow execution.

## Required control chain

After the user authorizes scope, a persistent coordinator admits a typed operation
through a qualified project controller. Bind exact workspace, role/thread UUID,
runtime generation, approved source and launch profile, account, endpoint,
execution contract and budget. The supervisor owns actual process/session handles
and supplies startup, readiness, retirement and recovery receipts.

The native harness loads instructions, assembles model context, checks generated
tool requests, executes permitted tools and returns results. A prompt, PID,
registry entry or launch acknowledgement alone cannot establish readiness.

The system automatically supervises progress, detects loss, fences new work and
preserves queued/active attempts. Retirement requires owned-process completion
and custody evidence. Replacement requires reconciliation, a single recorded
launch intent and successor readiness before dispatch. Manual Terminal actions,
requests that a model quit, ad hoc signals, route changes and duplicate launches
cannot substitute for missing controller support.

## Visible failures and authority

Expose operation, task/attempt, executor/generation, current state, last progress,
deadline, blocker and recovery action. Unsupported enrollment, missing liveness,
permissions or custody must fail loudly and block dependent work. Owner intent
and reserved decisions do not widen harness/OS permissions or conceal manual
execution. Terminal windows may display a controlled executor; human interaction
with them cannot be required for workflow progress.

Read-only orientation and developer diagnostics do not initialize, dispatch or
activate work. The Machine controller and automatic coordinator lifecycle remain
unqualified in the recorded checkpoint; its health failed with
`MACHINE_AUTOMATED_EXECUTION_REQUIRED` and exit 3. The lifecycle proposal supplies
no available command surface. Use the [maintained status](/Users/boandersson/Desktop/Machine/docs/DOCUMENTATION_INDEX.md)
and actual read-only target observations when deciding current capability.

## Qualification

Every new/edited lifecycle feature requires invariant integration, meaningful
negative regressions, the staged pre-commit gate and independent review of
protected changes. Investigate the critical real interface early through an
authorized feasibility probe, after safeguards needed for that probe's effects.
This is distinct from qualifying the whole workflow: check required start/stop,
receiving readiness, fencing, handover and recovery cases in fixtures and through
the actual approved route. Neither stage may bypass the installed stop barrier.
An operator-driven diagnostic cannot establish automatic lifecycle or recovery.
See the [requirements](/Users/boandersson/Desktop/Machine/docs/WORKFLOW_INVARIANT.md) and
[lifecycle proposal](/Users/boandersson/Desktop/Machine/docs/proposals/ROLE_LIFECYCLE_CONTROL.md).
