# Universal multi-agent project build protocol

Use this protocol when one Codex conversation coordinates work that a second Codex task or agent builds in a project repository. It applies to applications, command-line tools, libraries, pipelines, documentation, and other project work. The repository determines the implementation surface; this protocol does not assume that every project needs an app, a CLI, a particular stack, or the same tests.

## Roles and lanes

| Lane | Owner | Responsibility |
| --- | --- | --- |
| Product intent and acceptance | User or designated domain owner | Defines the desired outcome, constraints, priorities, externally meaningful decisions, and which actions need explicit authorization. Makes final product and domain-quality decisions. |
| Coordination | Lead agent in the current conversation | Inspects project truth, turns intent into bounded tasks and evidence, selects/addresses builder tasks, manages dependencies, monitors progress, resolves interface questions, and reports the result. |
| Implementation | One or more assigned builder agents | Inspect assigned areas, make changes within their ownership, run focused checks, and report files, commands, results, and remaining gaps. |
| Independent review and verification | Coordinator or separately assigned reviewer | Checks the actual diff against the request, inspects important interfaces and edge cases, runs appropriate independent checks, and distinguishes verified behavior from assumptions. |
| Operational or domain validation | User, operator, or qualified reviewer when needed | Tests effects that code-level checks cannot establish, such as real deployment, hardware behavior, generated media quality, business correctness, or user acceptance. |

One agent may hold multiple lanes when the task is small, but keep implementation and independent review distinct enough to catch mistakes. The user retains decisions that affect product scope, external systems, costly operations, or domain acceptance.

## Working protocol

### 1. Define the outcome and boundaries

Translate the request into a short build brief:

- What observable behavior or artifact should exist when the work is done?
- Which repository and source plan or issue define the current truth?
- What must remain intact?
- Which commands, external changes, costs, deployments, publication, or real-world actions are outside authorization?
- What evidence will count as complete?

Treat approval for implementation as authorization only for the implementation and checks implied by the request. Do not infer approval for publishing, deploying, sending messages externally, deleting data, running costly workloads, or making domain acceptance decisions.

### 2. Inspect the project before assigning implementation

The coordinator or builder first checks the repository path, status, applicable `AGENTS.md` and nested instructions, existing plans, launch paths, relevant code, and focused validation commands. Use read-only inspection before setup or delivery commands that may change state. Identify repository-specific constraints and mismatch between documentation and behavior before proposing repairs.

Choose the implementation surface from repository evidence. For example, a project may need a library API, terminal command, existing app screen, launch script, package, or documentation update. Do not add an app wrapper or new architecture merely because another project used one.

Write a small acceptance matrix connecting each requested outcome to the code path and evidence that will verify it. Keep unresolved product choices visible; resolve routine implementation details using the plan and project conventions.

### 3. Assign lanes and prevent conflicting edits

Break work into bounded responsibilities with clear ownership, dependencies, and outputs. Each builder should know:

- its repository and scope;
- the files or component it owns;
- the interface it must preserve or provide;
- tests/checks it must run;
- actions it must not take;
- the milestone at which it should report back.

If builders work concurrently, prefer separate worktrees or clearly disjoint ownership. If they share one checkout, appoint one writer per overlapping area, communicate before touching another agent's files, and coordinate tests that create shared outputs. The coordinator should avoid competing edits in a builder-owned area; make targeted fixes only after coordinating ownership or when the builder's lane has ended.

### 4. Address the right Codex task

Use a Codex thread UUID to address a task visible through the shared Codex app server. A terminal process number, `/dev/ttys…` device, agent label, or display title is not a reliable cross-conversation address. The general steps are in [How to communicate with other Codex agents](how-to-communicate-with-other-codex-agents.md).

Before sending implementation work, verify the target task's UUID, repository path, status, and recent context. Send a concise, bounded request and later read the target thread to confirm receipt and outcome. A successful queue or message only means that input was accepted; it does not prove the work completed. Use terminal queueing only if the installed Codex CLI supports it and can reach the same app server.

Keep messages concrete and short. Include the result needed, repo path, scope, constraints, verification evidence, and reporting expectation. Split a prompt if the messaging tool has a size limit. Do not send messages through email, chat, or another external service unless the user explicitly authorized that route.

### 5. Coordinate progress and blockers

At useful milestones, ask for a brief report containing what changed, what remains, the latest validation, and any blocker. The coordinator should monitor both task status and shared repository state. If a progress message fails, distinguish a messaging/approval-policy failure from a blocked repository operation; continue through other authorized evidence such as thread reads and a read-only diff when available.

If a task reports `waitingOnApproval`, find the exact pending action and its reason. Do not assume the status itself means that every project change needs user permission. Conversely, do not bypass a real approval gate. If the pending action cannot be inspected or requires a user decision, present that specific action and why it is required; do not ask for broad approval.

### 6. Verify the delivered behavior

The builder reports exact commands and outcomes. The coordinator then:

1. checks the working tree and diff for scope, accidental artifacts, and unrelated changes;
2. compares implementation behavior with the request, repository instructions, and existing contracts;
3. runs focused tests and checks appropriate to the changes, independently when practical;
4. checks relevant failure paths, boundary conditions, and state preservation;
5. records checks that were intentionally not run and why.

Use harmless fixtures, dry runs, or synthetic inputs for orchestration where they are sufficient. Do not call synthetic evidence proof of a live integration, production readiness, generated-content quality, or domain acceptance. For user-facing apps, distinguish build/compile and command-construction checks from actually launching the app or exercising external permissions. Run a live flow only when it is within authorization and necessary for the stated acceptance criteria.

### 7. Close with a reviewable handoff

The final report should state the resulting behavior first, link the main files or artifact, summarize the meaningful validation, and identify material limits. Include whether changes remain uncommitted and whether any live operation was performed. Keep the user's requested publish/commit/deploy approval as the final step when it is required; do not perform those actions based only on successful tests.

## Reusable assignment brief

Adapt this to the repository and task; remove irrelevant fields rather than filling them with assumptions.

```text
Build: [observable outcome]
Repository: [absolute path]
Source of truth: [plan/docs/code paths]
Own: [component/files; coordinate before overlap]
Preserve: [behavior/data/contracts]
Do not: [out-of-scope external, costly, or domain actions]
Verify: [specific commands/checks and expected evidence]
Report: changed files, commands/results, remaining limits, blockers.
```

## Reusable acceptance record

```text
Outcome:
Implementation owner(s):
Files/artifacts:
Verification and results:
Independent review findings and resolution:
Live/external/domain checks not performed:
Remaining risks or decisions:
Working tree / commit / publish state:
```

## Protocol principles

- Repository truth and the user's request outrank patterns copied from another project.
- Divide responsibilities around interfaces and ownership, not agent count.
- Preserve state and provenance; prefer reversible, focused changes.
- Keep expensive, external, destructive, and domain-acceptance actions within explicit authorization.
- Treat tool success, test success, and real-world acceptance as separate evidence.
- Report uncertainty and unverified boundaries plainly.
