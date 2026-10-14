# Machine bounded admission — live acceptance

The approved smallest implementation is installed and its live acceptance check passed. The existing Machine workspace agent accepted a locally recorded scratch initialization permit without another owner task approval, executed it once, and received an executable rejection when it attempted reuse. This is a local operator capability, not authenticated grants or general project execution.

## Observed gap and request chain

The earlier behavior assessment found that startup supplied repository instructions but no work admission. Its scratch test stopped at the receiving model's authority check before any CLI initialization request; neither the harness nor CLI had rejected an executed write. The targeted correction adds explicit local admission and a receiving-side fixed executor, with a documented narrow exception to the other-thread-message rule. A message remains a pointer to local authority rather than authority itself.

The observed chain was the owner's agreement in the coordinator task → independent candidate review → owner-directed installation → fresh existing-session observation → recorded owner decision → CLI admission → durable single permit issuance → pending bridge delivery record → actual thread transport → receiving harness context → model tool request → harness execution environment → CLI actor/scope/freshness checks → durable consume → exact `Ledger.initialize` → tool result → completed receiving turn → independent byte and ledger checks. The model proposed tool requests; the harness executed them and returned results. No new agent, model API, native project role, or billing route was introduced.

## Implemented scope

Eight reviewed files add `session-admit`, `permit-issue`, read-only `permit-inspect`, and `permit-execute`, with documentation and 14 focused tests. The permit binds actual ambient coordinator/receiving thread UUIDs and matching session environment, owner assertion, source/profile hashes, exact existing canonical scratch root and device/inode, initialization owner, immutable request bytes/path, and expiry within 15 minutes. The only domain operation is the existing initializer for that scratch root. No command/executable/environment argument is accepted.

The separate `.machine/admission` store preserves the old SQLite schema and bytes. Issuance is reserved before publication; execution is consumed before the initializer. Interrupted issuance/execution remains blocked and is never automatically retried. Success also consumes the permit. Checksums and environment values are local custody assertions; a same-user operator can modify them. This does not enforce a hostile-principal sandbox or replace harness permissions.

## Evidence and measurements

| Check | Actual result |
| --- | --- |
| Candidate suite | 51 tests passed, exit 0, 10.546 seconds; 14 new admission tests and 37 existing coordinator tests. |
| Independent source review | PASS, turn `01a13832-8349-7ea0-81d8-158fd7d7f802`; all eight manifest hashes checked. Reviewer inspected tests without running them. |
| Installed preflight | Completed read-only, turn `01a13834-aea0-7741-b9f5-a3b8c5daf2a3`; actual Machine cwd/thread/session confirmed. |
| Receiving permit inspection | Eligible true, no blocker, turn `01a13835-98ac-7c93-ab36-152d4ed8f6de`; agent explicitly accepted one fixed command without duplicate owner task approval. |
| Actual initialization | Child exit 0, succeeded, turn `01a13836-06f2-7db0-87d4-009a16cfa0aa`; raw harness tool result retained, 0.015175 seconds for the execution call. |
| Actual reuse attempt | Child exit 2, consumed/no replay, turn `01a13836-b84a-7bc2-8e2e-14dfec15c9c4`; Python capture wrapper exited 0. |
| Independent scratch check | One initialization event, owner `BehaviorTest`; all 49 scratch file hashes unchanged by reuse. |
| Independent preservation check | Every non-admission Machine file matches the exact eight-file adoption; old SQLite bytes unchanged; frozen sources and launcher unchanged. |

Receiving thread: `01a13808-1755-7643-9165-f2035aa16d16`. Coordinator: `01a13696-5178-7d03-bf4e-f97d365abf9d`. Admission: `f465a556-0d2e-4317-af60-122d61487830`. Permit: `dfe1d3bf-c00f-4534-bb9f-c46e695d3289`, now `succeeded` and permanently ineligible for reuse. Scratch root: `/private/tmp/machine-agent-behavior-m00nxp6a/studio`.

Owner quote was retained exactly as “Agreed. You run it” under the approved bounded implementation/acceptance scope. The independent reviewer did not grant adoption or execution authority. Owner-directed adoption copied only the eight matching files and retained recoverable prior source at `/private/tmp/machine-admission-prior-t4t6hqj9`; no files were deleted. Candidate manifest SHA-256: `6216b9eeee3be10a1f1c2985129dfd5843e9a26ac930ec4b63b7b3ea008b8791`.

See [result](RESULT.json), [review](REVIEW.json), [adoption](ADOPTION.json), [actual receiving tool results](ACTUAL_TOOL_RESULTS.json), and [scoped harness execution records](ACTUAL_EXECUTION_LOG.json). Pending dispatch records and actual transport receipts are separate; a receipt alone did not establish execution. No automatic resend occurred. The initial source-review send was recorded after sending, explicitly noted in its dispatch record; subsequent preflight/inspection/execution/reuse deliveries were recorded pending before sending.

## Remaining frontier

This closes the demonstrated scratch delegation gap for one explicit session and operation. General authenticated authority, revocation, arbitrary work admission, native role lifecycle, production adapters, and controlled self-replacement remain unimplemented. External projects remain inspection-only through Machine. No game source or castle content was introduced; the castle and native role qualification remain outstanding. The Machine implementation is sealed in local commit `dd89d38` (`feat: add bounded session admission for scratch initialization`). This evidence is committed separately in CodeExp; adoption-time records retain their original uncommitted observation.
