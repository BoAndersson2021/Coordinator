# Historical Machine checkpoint

This dated document is historical context, not a mission registration, startup
guide or system-wide active mission. Bare `onboard` must not read into or resume
this work. New CodeExp2-coordinated work on Machine requires registration and
explicit selection through [Missions/](Missions/README.md#registered-missions).

Updated 2026-10-15 22:31:29 PDT (-0700).

Implementation checkpoint: Machine commit `d24f163`; supporting documentation and evidence through CodeExp2 commit `75ef3d3`.

**Machine is a persistent coordination and observation system for agent-driven development. It has managed diagnostics and an enforced stop on workflows whose automatic execution remains unqualified.**

Machine lives separately from the projects it coordinates. It retains assignments, agent/session bindings, delivery attempts, evidence and verification decisions across interruptions and coordinator changes. Project source, assets, scenes and domain acceptance stay in their own repositories. Models generate responses or tool requests; receiving harnesses assemble context, check permissions and execute tools. Machine adds durable coordination and evidence around that chain.

The implemented foundation includes:

- A CLI and transactional SQLite ledger for task, attempt, evidence and recovery custody.
- Native inspection communication components and existing evidence-reconciliation routes. New assignment dispatch is blocked by the execution invariant.
- A completed `./Machine work-view` feature, sharing one core task-state explanation with the dashboard: delivery custody, unestablished live execution, historical completion/review, attempts and original evidence timestamps. The CLI preserves retained report access; dashboard HTTP responses exclude report bodies.
- A local HTML/JavaScript dashboard. `./Machine dashboard` starts or reuses its managed service, verifies its identity and opens the authorized page automatically. macOS launchd keeps the diagnostic service alive independently of the terminal and starts it at login in the user's GUI session. The page refreshes every two seconds, visibly marks stale/disconnected observations and reconnects automatically. Closing the browser leaves the service running.
- Runtime guards, admission controls and a mandatory installed pre-commit verifier that evaluates the actual staged source and tests.

Both work-view surfaces read integrity-checked local records. They do not probe or start project agents, send assignments, collect replies or change task state. A fresh ledger read never refreshes the original task evidence or proves a live receiver. At this review, the ledger contains two tasks, one historical report and one historical review; live receiving execution remains unestablished. The dashboard service is listening locally, while `doctor` reports source integrity separately from failed workflow readiness.

The defining rule is `MACHINE_AUTOMATED_EXECUTION_REQUIRED`: **authorized workflow execution must require zero manual starts, stops, communication steps, coordinator restarts or handovers.** It governs Machine, every adapter it uses, controls or communicates with, and every new or edited feature. Missing capability or proof must fail loudly and block effects. No manual fallback, permit, saved thread or configuration flag qualifies an executor.

**Automatic project-agent lifecycle, persistent workflow orchestration, communication, verification routing and recovery remain unqualified. Workflow execution is blocked.** Dispatch, queue submission, scratch execution, handover and workflow verification/closure are denied before effects. `status`, `doctor`, `work-view` and `invariant-check` expose `workflow_invariant_failed` and exit 3. Source integrity or a connected dashboard does not supply workflow readiness.

This boundary follows a real acceptance failure: an assignment was queued without establishing a live receiving agent, and delivery was incorrectly interpreted as progress. The retained task `native-inspection-fresh-start-001` remains `delivered`, version 3, with one attempt and no completed report or review. Preserve its custody and history; supported reconciliation must precede another live attempt.

The latest implementation received independent source review and passed **114 tests**, including **20 mandatory invariant tests** through the enforced commit hook. Four work-view commit-gate cases covered valid source and rejection of missing invariant coverage, CLI/dashboard disagreement and manual next-step regressions. Installed CLI/API agreement and automatic browser reconnection were observed. These checks establish their specific diagnostic and enforcement scopes.

Dashboard process-loss recovery was also demonstrated. A later source reload exceeded its 20-second check and recovered automatically after **28.637 seconds**. That failed check remains preserved alongside the subsequent healthy observation; no recovery-time guarantee is established. Diagnostic-service recovery does not qualify project-agent or workflow recovery.

Development now means implementing and proving the missing automatic execution providers while preserving the guard. Develop candidates outside the watched installation; protected changes require independent review and recorded owner-authorized adoption. The source watcher reloads installed files but does not enforce reviewed-source isolation. Preserve frozen design packages, historical failures and private state. Every executable feature change needs meaningful staged invariant regressions; missing, skipped or unsuccessful mandatory coverage must block the commit loudly. Developer validation requires Node.js for the actual dashboard JavaScript tests; the running Python/browser service does not.

Start with [Machine’s README](/Users/boandersson/Desktop/Machine/README.md), [AGENTS.md](/Users/boandersson/Desktop/Machine/AGENTS.md), [runbook](/Users/boandersson/Desktop/Machine/docs/RUNBOOK.md) and [implementation frontier](/Users/boandersson/Desktop/Machine/docs/ROADMAP.md). Read the [work-view contract](/Users/boandersson/Desktop/Machine/docs/WORK_VIEW.md) and [dashboard contract](/Users/boandersson/Desktop/Machine/docs/DASHBOARD.md) for the implemented behavior and its limits. The former local verification record at `Machine/WORK_VIEW/README.md` remains in Git history following the user-authorized folder removal.
