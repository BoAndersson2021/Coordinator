# Machine executor lifecycle and launch contract

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
unqualified; current health fails with `MACHINE_AUTOMATED_EXECUTION_REQUIRED`
and exit 3. Lifecycle is proposed, not an available command surface.

## Qualification

Every new/edited lifecycle feature requires invariant integration, meaningful
negative regressions, the staged pre-commit gate and independent review of
protected changes. Qualify owned start/stop, exact receiving readiness, fencing,
handover and recovery in fixtures, then the actual approved route. A user-operated
restart cannot establish automatic recovery. See the
[requirements](/Users/boandersson/Desktop/CodeExp2/Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md) and
[lifecycle proposal](/Users/boandersson/Desktop/CodeExp2/Machine/ROLE_LIFECYCLE_CONTROL_DESIGN.md).
