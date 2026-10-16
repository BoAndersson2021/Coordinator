# Machine coordination contract

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` applies to Machine and every adapter it
uses, controls or communicates with, including all new/edited features. Once a
workflow is authorized, lifecycle, communication, handovers and recovery must be
automatic and observable. Missing support or proof fails loudly before effects.

## Enforced boundary

Current providers are unqualified. The CLI and each effect boundary deny new
workflow execution, including native/manual dispatch, queue RPC/frame emission,
scratch execution, handover and workflow verification/closure. No configuration,
caller label, permit, source PASS, thread metadata or override enables execution.
Health commands report `workflow_invariant_failed`, stderr code
`MACHINE_AUTOMATED_EXECUTION_REQUIRED`, and exit 3.

Read-only diagnostics and explicit local preparation are not execution authority.
Existing acknowledgements, uncertainty, reports and reconciliation remain retainable
for custody; they do not enable dispatch or acceptance. Reply collection never
sends and still reports failed workflow health. Diagnostic operations cannot supply
manual execution steps in an allegedly automated workflow.

## Persistent custody

The private SQLite ledger retains schema-versioned projects, agent bindings,
assignments, attempts, receipts, reports, reviews and events. Transactions preserve
operation identity, input digests, expected versions and event/evidence consistency.
Unknown effects require reconciliation before retry. Do not transplant state,
overwrite bindings, discard consumed permits or erase old attempts.

The native fresh-start task remains `delivered`, version 3, with one attempt. That
state describes queue acknowledgement only. The live test failed receiver liveness;
no execution/report/verification is established. Preserve the exact queue entry
until supported reconciliation; never resend, delete or launch a substitute as
an unrecorded workaround. History and domain acceptance remain separate facts.

## Required future execution chain

A persistent coordinator must resolve authorized scope, pin source/context and
bind exact managed runtime identity. A qualified project controller owns lifecycle,
fencing, readiness and recovery. The receiving harness assembles context, checks
model requests and executes tools. Machine automatically collects the exact turn,
routes independent verification and records outcome. No human terminal action,
message relay or copied handoff may be required.

Expose task/attempt, executor/generation, current state, last actual progress,
deadline, block/failure reason and recovery action. Unsupported capability blocks
rather than becoming indefinite waiting. Preserve project source, scenes, account,
endpoint, billing, receiving permissions and designated adoption owners.

## Change control

Every new/edited feature must preserve the invariant and pass the mandatory staged
pre-commit gate with meaningful regression coverage. Protected changes require
independent review. The local operator/host remains trusted; records are not
cryptographically authenticated grants. [The invariant](WORKFLOW_INVARIANT.md)
and [runbook](RUNBOOK.md) govern current operation; [foundation evidence](FOUNDATION_ACCEPTANCE.md)
retains historical behavior and cannot re-enable its former manual routes.
