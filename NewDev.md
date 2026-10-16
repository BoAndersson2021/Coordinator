2026-10-15 21:44:25 PDT (-0700)

I’d describe Machine as **a persistent coordination system for agent-driven development, with a working foundation and an enforced stop on workflows that require manual intervention.**

Machine lives separately from the projects it coordinates. Its job is to retain assignments, agent/session bindings, delivery attempts, evidence and verification decisions across interruptions and coordinator changes. Project code and assets stay in their own repositories.

The implemented foundation includes:

- A CLI and persistent transactional coordination ledger.
- A native communication bridge for inspecting agent threads, submitting assignments and collecting responses.
- Admission controls, evidence custody and recovery records.
- Runtime guards and a mandatory pre-commit verifier.

Its defining rule is `MACHINE_AUTOMATED_EXECUTION_REQUIRED`: **authorized workflow execution must require zero manual starts, stops, communication steps or handovers.** Missing capability or proof must produce a visible failure and block execution before effects. Every new or edited feature must preserve that rule.

The distinction a new developer must understand is that **Machine enforces this requirement today, but does not yet provide the complete automation needed to satisfy it.** Automatic agent lifecycle, persistent orchestration and recovery remain unqualified, so workflow execution is blocked.

That boundary came from a real acceptance failure: Machine successfully queued an assignment without establishing a live receiving agent. Queue delivery was incorrectly interpreted as operational progress. The implementation now prevents that foundation from being presented as a functioning autonomous workflow.

Development therefore means building and proving the missing automation while preserving the guard. The current enforcement passed independent review, 98 tests and 14 commit-gate scenarios; those establish enforcement coverage, not autonomous operational readiness.

Start with [Machine’s README](/Users/boandersson/Desktop/Machine/README.md), [AGENTS.md](/Users/boandersson/Desktop/Machine/AGENTS.md) and [runbook](/Users/boandersson/Desktop/Machine/docs/RUNBOOK.md).
