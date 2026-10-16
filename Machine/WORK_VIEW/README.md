# Original work-view feature completed

The dashboard increment exposed truthful task evidence in HTML/JavaScript but left
the original `Machine work-view` CLI unchanged. This follow-up completes that
feature through one core task-state projection used by both surfaces.

`./Machine work-view` now exposes explicit workflow, delivery, execution, completion,
verification and evidence-freshness states, alongside original timestamps and
attempt identity. CLI JSON and dashboard HTTP task fields agree. Legacy CLI task
identifiers/state/report access are preserved; HTTP never receives report bodies.
The old manual `bridge-collect` next-step instruction is removed. Neither view
contacts agents, changes task state or establishes live execution from receipts.

The failed task remains `delivered`, version 3, one attempt:

```text
workflow_status:     blocked
delivery_status:     receipt_retained
execution_status:    not_established
completion_status:   no_completed_report
verification_status: not_reviewed
evidence_freshness:  historical_record
```

All 114 tests passed. The unchanged installed verifier passed four real disposable
commit cases: valid candidate accepted; missing staged invariant coverage,
CLI/dashboard disagreement and manual next-step regressions blocked. The enhanced
comparison is part of an already mandatory invariant test, not optional coverage.

Independent V2 exact-source PASS binds all 11 adopted files. V1 had static source
PASS, but its real fixture test failed canonical path identity and blocked adoption;
that source, failure and report remain unchanged. V2 corrects only the fixture path.
All 87 private Machine files remain byte-identical; checker/policy remain unchanged.

The existing launchd source watcher reloaded the reviewed installation without a
manual lifecycle command. Its 20-second acceptance probe failed; actual structured
source-change/listen events show automatic recovery after 28.637 seconds. The
failure is preserved rather than extending or claiming that deadline passed.
Subsequent read-only CLI/API checks passed, and Chrome visibly reconnected with
the new PID and a second observed restart. No restart-time guarantee is established.

See [source review](INDEPENDENT_REVIEW_V2.json), [manifest](REVIEW_MANIFEST_V2.json),
[tests](V2_TESTS.log), [commit gate](HOOK_VERIFICATION.json),
[adoption](installation/RESULT.json), [failed reload probe](ADOPTION_AND_RELOAD_FAILURE.log),
[current installed checks](INSTALLED_VERIFICATION.json), and
[the operating contract](/Users/boandersson/Desktop/Machine/docs/WORK_VIEW.md).
`candidate` is frozen V1; `candidate-v2` is the reviewed adopted source. Historical
evidence and frozen Design packages retain their bytes.

This increment is installed and committed in Machine as `d24f163`. Workflow execution remains blocked
and automatic project lifecycle/orchestration remains unqualified.

[COMMIT_RECORD.json](COMMIT_RECORD.json) binds the Machine commit, all 11 reviewed
source pins and the actual successful enforced-hook output. Companion evidence is
tracked in CodeExp2; the failed reload probe remains retained.
