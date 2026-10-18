# Machine build and execution protocol

This contract applies to Machine-managed work. Use
[Delivery Discipline](delivery-discipline.md) for shared delivery rules,
the [plan guide](how-to-follow-and-refresh-a-plan.md) for the builder's baseline,
the [coordinator guide](how-to-coordinate-with-a-builder-agent.md) for delegation
and the [runtime-target guide](how-not-to-overengineer.md) for real integration.
The [communication contract](how-to-communicate-with-other-codex-agents.md) owns
delivery/collection requirements; the [lifecycle contract](app-terminal-codex-launch-pattern.md)
owns managed startup, readiness, shutdown and recovery. Apply those requirements
at their relevant boundaries. Copying this guide does not activate Machine or
impose its installed state on an unrelated repository.

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is mandatory for Machine and every adapter
it uses, controls or communicates with, including every new or edited feature.
Authorized execution requires zero manual starts/stops, relays, session restarts
or handovers. Missing support or proof must produce a visible failure and block
work before effects. See the [owner requirements](/Users/boandersson/Desktop/Machine/docs/WORKFLOW_INVARIANT.md).

## Ownership

The user sets intent, scope, budget and reserved decisions. Machine owns persistent
coordination, automatic communication and supervision. Project controllers own
admitted lifecycle, fencing and process custody. Receiving harnesses own context,
permissions and tool execution. Models generate responses or structured requests;
model statements do not establish runtime authority or acceptance. Projects retain
their source, assets, scenes and domain adoption boundaries.

Builders produce candidates; independent reviewers inspect pinned source and
negative paths. Separate implementation, verification and domain acceptance.
Builders cannot approve their own authority, permission, enforcement, verification,
recovery or promotion changes.

## Development procedure

Keep the requested outcome fixed, test critical feasibility early within the
authorized diagnostic scope, and apply the
[shared repair limit](delivery-discipline.md#shared-repair-limit). Required
safeguards accompany delivery; passing them alone does not establish that the
requested workflow works. A blocked approach does not stop independent authorized
maintenance. Documentation-only work is verified as documentation.

1. Inspect instructions, repository state, entry points, implementation and focused
   validation. Begin read-only; startup grants no workflow work.
2. Define the result, owned files, interfaces, preserved state, authority and
   acceptance evidence. Identify all lifecycle/communication/recovery dependencies.
3. Require exact runtime identity and qualified automatic control at execution
   boundaries. Unknown/unqualified adapters deny work; metadata cannot establish
   a live executor. Unsupported capabilities are explicit failures.
4. Make the smallest targeted change in the existing implementation. Isolate it
   when required by mutation risk, frozen inputs or authorized concurrent work;
   do not create a separate repair package by default. Preserve private state.
5. Add meaningful invariant regressions for every new/edited executable feature.
   The target repository's executable commit route must test index blobs through
   its installed verifier. Missing, skipped, undiscovered or unsuccessful mandatory
   tests block that route. Machine has its own verifier; CodeExp2 currently allows
   ordinary documentation and blocks unverified executable changes. Neither hook
   grants runtime authority or requires a runtime test for an ordinary text edit.
6. Independently review protected changes. Adopt only reviewed bytes within owner
   scope, retaining previous source and uncertain/escaped-effect history.
7. Report installed behavior, checks, failures and remaining gaps. A receipt,
   source PASS, successful build or commit is not workflow acceptance.

Source development and diagnosis are maintenance, not evidence of automated
execution. A person performing a missing execution step cannot count as a
successful workflow run.

## Execution and recovery acceptance

The persistent system must operate authorized lifecycle, exact dispatch, receiving
execution, reply collection, verification routing and handover automatically.
Expose every transition, block, deadline and recovery action. Detect missing
receivers and failed controllers; do not label absent execution as waiting.
Retain uncertain outcomes and reconcile before retry or replacement.

Cover initially absent workers, worker loss, controlled coordinator interruption
and automatic recovery, lost acknowledgements, concurrent callers, expired
scope, unsupported controls and verified output. The real automatic path must
complete with zero human execution interventions. Loud capability failure proves
detection and fails whole-workflow acceptance.

The [enforcement record](/Users/boandersson/Desktop/Machine/docs/WORKFLOW_INVARIANT.md) preserves the
reviewed barrier and its checkpoint verification results. Use the
[maintained status](/Users/boandersson/Desktop/Machine/docs/DOCUMENTATION_INDEX.md) and the target repository's
read-only observations for current capability. Historical test totals and
pilot/scratch passes retain their original scopes; they are not fresh readiness
checks. Manual bridges and terminal handovers are not enabled fallbacks.
