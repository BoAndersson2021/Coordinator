# Bounded admission — retained history, execution disabled

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` applies to every admission feature and
adapter. The scratch executor is currently unqualified and rejects before permit
locking, consumption or target initialization. A permit or owner label cannot
bypass the invariant. Permit inspection reports ineligible; operational health
fails loudly with the invariant code and exit 3.

The earlier single-use, session-bound scratch initialization succeeded once and
reuse rejected. Its consumed permit and receipts remain preserved. That historical
success establishes its former bounded scope, not current execution permission or
qualified automation. General project mutation/admission remains unimplemented.

Administrative admission/issuance records remain local operator assertions. They
bind the recorded owner decision, exact session/workspace, scratch target, deadline,
request bytes and source profile; they are not authenticated general grants.
Preparation cannot confer execution permission. Existing permits are not silently
migrated, renewed or replayed when source/docs change.

Every new/edited admission/execution path requires invariant integration and
meaningful staged regression coverage. The mandatory installed pre-commit verifier
must block missing enforcement or unsuccessful mandatory tests. Protected changes
require independent review and recorded adoption. Automatic lifecycle, receiving
identity, communication and recovery must be qualified before any execution route
is enabled; no manual terminal start or handover is a fallback.

See [the invariant](WORKFLOW_INVARIANT.md), [coordination](COORDINATION.md) and
[runbook](RUNBOOK.md). Historical admission proof remains in CodeExp2/Machine/ADMISSION_TEST.
