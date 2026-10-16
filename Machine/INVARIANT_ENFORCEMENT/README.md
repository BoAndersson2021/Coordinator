# Installed invariant enforcement

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is installed across Machine and all current
adapter effect boundaries. Every future new/edited feature must preserve it,
with AGENTS.md requirements and the mandatory pinned staged pre-commit verifier.
Unqualified/unknown execution fails loudly before effects; there is no manual fallback.

V1 was independently rejected for raw wire bypass, hook enforcement and startup
failure gaps. V2 was rejected because mandatory tests could be skipped or excluded
from discovery. Both candidates, actual review reports and prior failures remain
retained unchanged. V3 received an actual independent source PASS for all 17 pins.
Its trusted runner requires successful mandatory test IDs and completion reports.

V3 passed 98 tests and 14 real disposable commit cases, including disabled staged
guards hidden by unstaged repairs, unknown adapters/scripts, missing/non-executable
or no-op hooks/checkers, removed/skipped/expected-failure/undiscovered mandatory
tests and early successful process exit. See VERIFICATION_V3.json and
HOOK_VERIFICATION_V3.json. These are guard/commit-gate proofs, not runtime automation.

REVIEW_ACCEPTANCE.json binds the actual independent PASS to REVIEW_MANIFEST_V3.json.
installation/RESULT.json records adoption, previous source and 87 private files
preserved. INSTALLED_VERIFICATION.json records actual exit-3 health/dispatch guards
and the installed hook's rejection of the old index without enforcement files.
Later owner-directed documentation synchronization is recorded separately in
../DOCUMENTATION_SYNC; runtime code and the installed verifier remain pinned.

Current workflow automation remains unqualified and execution is blocked. The
original failed native task remains in custody with one attempt; no project send,
lifecycle or permit consumption occurred during this enforcement/sync work.
Machine source and documentation are committed as `50dbd19`; the installed
pre-commit gate passed 17 invariant tests and the full 98-test suite.
[COMMIT_RECORD.json](COMMIT_RECORD.json) binds the commit and actual hook log.
Use the
[current documentation index](../DOCUMENTATION_INDEX.md) and
[runbook](/Users/boandersson/Desktop/Machine/docs/RUNBOOK.md).
