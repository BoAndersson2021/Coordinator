# Managed local work dashboard

`./Machine dashboard` starts or reuses Machine's local diagnostic service, verifies
its exact root, source profile and launchd PID, then opens the auto-updating
HTML/JavaScript dashboard in the default browser. No Java runtime, package install,
external assets, terminal left open, or manual restart is required. This command
is an explicitly authorized diagnostic service installation, not project execution.

The server binds only `127.0.0.1:8765`. The macOS user LaunchAgent uses RunAtLoad
and KeepAlive: it starts at login and restarts after process loss. An in-process
watcher exits on changed dashboard/guard/entry source or assets so launchd reloads
the installed version automatically. Candidate development must stay outside the
watched installation; only independently reviewed bytes may be written there in
an owner-authorized adoption. The watcher itself does not enforce source-review
acceptance and is not proof of reviewed-source isolation. Normal start is idempotent. Occupied ports,
unsupported platforms, different existing service definitions, supervisor failures,
missing source or identity mismatch fail loudly; no terminal/manual fallback exists.
The service is available in this user's login session; it is not a system daemon
available while the machine is off or the user is logged out. Closing the browser
does not stop it. An explicit `./Machine dashboard` reopens its authorized page.

The page polls an authenticated local JSON snapshot every two seconds, with a
four-second request timeout and eight-second stale limit. Failed refreshes show a
prominent stale/disconnected banner, dim previous observations, and reconnect
automatically. Resuming a background page checks evidence freshness before reuse.
Dashboard connection health is separate from workflow readiness.

## Observation contract

Gauges count assignments, proven live receivers (currently zero), retained reports
and retained reviews. Task cards separately expose delivery custody, unestablished
live receiving execution, historical completion/review evidence, original evidence
time, attempts and source. Historical verified/rejected outcomes remain historical.
A freshly read ledger or retained receipt never establishes a live executor.

The server uses the existing read-only ledger integrity checks. It does not create
an absent ledger, refresh agent observations, poll agent sockets, send assignments,
launch workers, reconcile tasks, consume permits, or verify/close work. No mutation
HTTP routes exist. Report bodies, receipt bodies and transport configuration are
not returned. Unknown paths and methods cannot reach Machine's command dispatcher.

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` remains failed. All workflow effect guards
remain denied; the diagnostic server is not a qualified orchestration provider.
Both commands belong explicitly to the administrative command inventory; all new
modules/assets and mandatory dashboard regressions are covered by the commit gate.

Developer validation additionally requires Node.js to run the actual dashboard
JavaScript against deterministic DOM, clock and network failures. Missing Node,
failed stale/reconnection behavior or skipped mandatory coverage blocks the
pre-commit gate. Node is not required by the running Python/browser service.

## Local custody and failures

Per-root service configuration (including a random 256-bit browser token) lives in
`~/Library/Application Support/MammuthMachine/<root-hash>/service.json`, mode 0600
under a mode 0700 directory. The LaunchAgent is
`~/Library/LaunchAgents/com.mammuth.machine.dashboard.<root-hash>.plist`.
Structured service logs are in `~/Library/Logs/MammuthMachine/<root-hash>.log`.
None of these writes touch Machine's ledger, project files, or task/permit state.

The browser receives its token in the URL fragment, which is not sent in HTTP
requests or service logs. API requests require the token header and exact local
Host/Origin; cross-site requests and redirects are not accepted. Static files contain
no task data or token. The service sends no CORS permission and a restrictive CSP.
Keep the authorized browser URL private. This is the existing trusted local-user
model, not isolation against another process running as that same user.

If the ledger is damaged or unavailable, `/api/snapshot` returns an explicit 503
failure and the browser marks observations stale. If the service dies, launchd
restarts it and the browser reconnects without intervention. Startup waits at most
15 seconds after bootstrap for service identity/health, with each readiness call
bounded by the remaining deadline. Supervisor setup calls and subsequent browser
opening each have separate ten-second bounds. Terminal identity/browser failures
retain their specific reason and are never retried as transient connection loss.
Failure exits 3 with a visible error. OS and
browser permissions remain binding; an opening failure is explicitly reported.
`dashboard-serve` is the internal launchd entry point, not an operator-run terminal
procedure or a substitute for supervision. Never use it as a workflow workaround.
