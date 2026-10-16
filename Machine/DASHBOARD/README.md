# Installed managed dashboard

Machine now starts and keeps a local HTML/JavaScript work dashboard. The actual
`./Machine dashboard` command installed its per-user macOS LaunchAgent, verified
the exact supervised process and opened the page in the default browser. It is
running at `127.0.0.1:8765`; the automatically opened browser tab carries a private
authorization fragment. Use the same Machine command to reopen it automatically.
Do not distribute the token or replace startup with a manually run server.

The page refreshes integrity-checked local ledger observations every two seconds.
Gauges and task cards separate delivery custody, unproven live receiving execution,
retained reports and historical review verdicts. Original evidence timestamps do
not become fresh when the ledger is reread. Missing/stale/failed refreshes are
prominent and reconnect automatically, including a stalled response body.

The service uses launchd KeepAlive and RunAtLoad; closing a terminal does not stop
it. It restarts after process loss and starts at login in this user's GUI session.
The page is not kept open against an intentional browser close. This is diagnostic
supervision only: project/workflow automation remains unqualified and blocked by
`MACHINE_AUTOMATED_EXECUTION_REQUIRED`. No worker/queue/permit/task effects occurred.

## Review and verification

- V1 source review rejected stalled-body refresh, PID-prefix identity and startup
  failure/deadline handling; its exact candidate, report and failures are retained.
- Corrected V2 has independent exact-source PASS for 17 pins. Manifest SHA-256:
  `aefb50e537af4942a4d72334b549aeb76caebcc825091efb5bead628f655e556`.
- All 113 tests passed. The installed staged verifier now requires 20 mandatory
  successful invariant IDs, including real JavaScript behavior tests. Developer
  validation needs Node.js; the running dashboard does not.
- Five actual disposable commit cases passed: valid source committed; missing
  staged invariant coverage, skipped browser coverage, disabled stale watchdog
  and unregistered runtime JavaScript were blocked.
- Live automated fault injection suspended the exact dashboard PID for 12 seconds
  and killed it. launchd restarted it with a different PID/instance, without a
  manual restart or handover. Chrome visibly reconnected and reported one restart.
- All 87 private Machine files remain byte-identical to the pre-change baseline.
  The failed native task remains delivered/version 3/one attempt, without a report.

See [source review](INDEPENDENT_REVIEW_V2.json), [manifest](REVIEW_MANIFEST_V2.json),
[adoption](installation/RESULT.json), [tests](V2_FINAL_TESTS.log),
[commit gate](HOOK_VERIFICATION.json), [managed recovery](MANAGED_RECOVERY.json),
[browser verification](UI_VERIFICATION.json), and the
[operating contract](/Users/boandersson/Desktop/Machine/docs/DASHBOARD.md).
`candidate` is frozen rejected V1; `candidate-v2` is the exact reviewed adopted
source snapshot. Backups and preliminary/failing results are archival evidence.

The source watcher reloads the watched installation; it does not enforce
reviewed-source isolation. Develop candidates outside that installation and
write only reviewed source there during owner-authorized adoption. Machine source
is committed as `574e834`; the enforced commit hook passed 20 mandatory invariant
tests and the full 113-test suite. [COMMIT_RECORD.json](COMMIT_RECORD.json) retains
the commit identity and actual hook output. Companion evidence is tracked here.

The subsequent [work-view follow-up](../WORK_VIEW/README.md) completes the CLI
feature using this dashboard’s shared core projection. Its source changes are
installed and committed in Machine as `d24f163`; the dashboard commit above remains historical.
