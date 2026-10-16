# Machine build and execution protocol

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is mandatory for Machine and every adapter
it uses, controls or communicates with, including every new or edited feature.
Authorized execution requires zero manual starts/stops, relays, session restarts
or handovers. Missing support or proof must produce a visible failure and block
work before effects. See the [owner requirements](/Users/boandersson/Desktop/CodeExp2/Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md).

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

1. Inspect instructions, repository state, entry points, implementation and focused
   validation. Begin read-only; startup grants no workflow work.
2. Define the result, owned files, interfaces, preserved state, authority and
   acceptance evidence. Identify all lifecycle/communication/recovery dependencies.
3. Require exact runtime identity and qualified automatic control at execution
   boundaries. Unknown/unqualified adapters deny work; metadata cannot establish
   a live executor. Unsupported capabilities are explicit failures.
4. Build an isolated candidate. Preserve frozen sources and private state. Where
   concurrent work is authorized, use disjoint ownership or worktrees.
5. Add meaningful invariant regressions for every new/edited executable feature.
   The mandatory pre-commit gate tests index blobs through its installed verifier.
   Missing, skipped, undiscovered or unsuccessful mandatory tests block.
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

Machine currently has an independently reviewed fail-closed barrier, 98 passing
tests and 14 disposable commit-hook proofs. Workflow automation remains
unqualified and blocked. Historical pilot/scratch passes retain their original
scopes. Manual bridges and terminal handovers are not enabled fallbacks.
