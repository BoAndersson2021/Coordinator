# Machine native communication increment

Live recovery checkpoint: new CodeExp2 coordinator thread
`01a142a2-a322-7693-a3b5-6cfdd7106150` read onboarding and collected the existing
task after restart. Its exact original input remains queued; no completed
receiving turn or report exists yet. State remains `delivered`, version 3, with
one delivery attempt and no resend. Installed source, tracked project files and
saved scene/selection files match their baselines. See the
[recovery result](live-fresh-start-001/RECOVERY_RESULT.json). Acceptance remains
pending receiving execution, independent report review and closure. Continue
collecting the same task; do not prepare/send again or launch/resume a project
agent as a workaround.

Original delivery checkpoint: task `native-inspection-fresh-start-001` was delivered
once from fresh CodeExp2 coordinator thread `01a1429f-2f18-7723-aa35-abf67cac7b6c`.
It was `delivered`, version 3. That coordinator stopped before collection as
required. The new session recovered this same task as recorded above. See
[the retained delivery checkpoint](live-fresh-start-001/DELIVERY_CHECKPOINT.json)
and [the original acceptance procedure](FRESH_START_TEST.md). Acceptance remains
pending; the historical pre-test records below are retained unchanged.

The owner requested a useful communication expansion followed by verification,
independent red teaming, fixes and reverification, then a live test from a fresh
CodeExp2 start. The owner explicitly approved the existing Machine agent as the
independent reviewer.

The candidate adds direct delivery of recorded inspections to an existing native
project role, exact reply collection, interruption recovery without resend, and
a local work view. It preserves the current project execution route and existing
independent inspection review. It introduces no agent launcher or background loop.

The corrected ten-file candidate is now installed in Desktop/Machine after an
actual independent source PASS and 81 passing candidate tests. Prior source is
retained under `installation/previous/`; all existing private state bytes were
preserved. The final fresh-session live assignment test remains pending.

- `BASELINE.json` and `PRESERVATION_BASELINE.json` pin installed source and state.
- `REVIEW_MANIFEST_V1.json` freezes the first ten-file candidate in `candidate/`.
- `VERIFICATION_V1.json` records 73 passing tests and the read-only real-socket check.
- `BUILDER_REDTEAM_V1.json` records two subsequently reproduced defects.
- `candidate-v2/` and `REVIEW_MANIFEST_V2.json` freeze the corrected source and regressions.
- `INDEPENDENT_REVIEW_V1.json` retains the actual completed REJECT; V2 retains the
  actual completed PASS in thread `01a13808-1755-7643-9165-f2035aa16d16`.
- `VERIFICATION_V2.json` records the expanded 81-test pass.
- `REVIEW_ACCEPTANCE.json` binds the actual completed source review to exact bytes.
- `installation/RESULT.json` records installation and preservation.
- `INSTALLED_VERIFICATION.json` records all 81 installed tests passing and 87
  existing private-state files unchanged; source integrity and local work-view pass.
- `HANDOFF_CLARIFICATION.json` records the reviewer's nonblocking restart-order correction.
- [Fresh-start acceptance](FRESH_START_TEST.md) defines the remaining real test.

Prior failures and candidates remain retained. Source/fixture validation and a
read-only protocol check do not establish a successful live assignment round trip.
Implementation is committed in Desktop/Machine as `7fd3b78`; its ten
committed source hashes match the independently accepted V2 manifest. See
[the commit record](COMMIT_RECORD.json). Accompanying CodeExp2 evidence retains
the pending live-acceptance checkpoint.
