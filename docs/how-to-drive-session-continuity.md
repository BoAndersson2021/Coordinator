# How to drive session continuity and next actions

Use this guide whenever a task involves an agent session, process, build, test,
delivery attempt, external operation, or any other state that can stop, fail,
complete, or become uncertain. Apply it with Delivery Discipline, How to end a
task, and the [human-facing visual communication guide](../.agents/guides/human-facing-visual-communication.json)
when a workflow, dependency, state change or decision would be clearer as an
annotated illustration. This guide grants no authority to resume, retry, launch,
publish, or change scope.

## Core rule

`stopped`, `failed`, `completed`, and `no active turn` describe an observed
state. They do not by themselves decide the user outcome, close the work, or
remove the need to inspect what happened next.

Before ending a turn after any such state, reconcile the session log and durable
evidence, then choose exactly one truthful continuation state:

| State | Required response |
| --- | --- |
| Requested outcome is verified complete | State the usable result and the next available user action, if any. |
| A safe, authorized next action exists | Take it; do not turn routine continuation into a user relay. |
| A distinct safe diagnostic or recovery exists | Take it and explain the observable boundary. |
| A material owner decision is required | State the concrete decision, options, and consequence of each. |
| No authorized path remains | Report the specific evidence-backed blocker and what would reopen progress. |

Never leave the user with only a terminal word such as “failed,” “stopped,” or
“complete” when the product outcome remains unresolved.

## Reconcile before reporting

For a managed session or external effect:

1. Inspect the latest session/log events, durable receipt, process/lease state,
   output artifacts, and current source state as applicable.
2. Distinguish the harness or collector state from the underlying operation. A
   collector failure, missing active turn, or UI disconnect can coexist with a
   completed operation.
3. Classify the outcome: completed, failed, uncertain, interrupted, or still
   running. Record the evidence that supports the classification.
4. Identify the smallest next action that advances the original requested
   outcome without replaying an uncertain effect.
5. Continue automatically when that action is within existing authority.

Do not treat a report, receipt, test pass, process exit, or agent message as
full product completion unless it verifies the requested acceptance boundary.

## Drive, do not narrate

Status messages should tell the user where the work is headed:

> The build stopped before packaging. I am checking the preserved output and
> will either repair the packaging step or report the exact missing capability.

Do not narrate a failure and wait silently when the next safe action is already
known. Conversely, do not retry a side effect blindly: reconcile identity,
receipts, logs, and current state first.

When a completed technical substep leaves the user’s product goal incomplete,
say what remains and name the next available route. Example:

> The candidate is built. Native qualification has not run. Next, run the
> isolated app verification before treating it as usable.

## Session-log closure checklist

Before declaring closure for work involving a session, verify and report:

- the final session/receiver/process state;
- whether its final message, logs, and artifacts were collected;
- whether any effect is uncertain or needs reconciliation;
- the relation between the substep result and the user’s original outcome;
- the next action, owner, and authority boundary when work remains.

If a managed builder finishes, the Coordinator must review its completion
against durable evidence before reporting the product outcome. A completed
builder turn is not an automatic user-facing acceptance state.

## Stop conditions

Continue available authorized work. Pause only for an explicit owner pause.
Report blocked only after the same unresolved blocker has persisted through the
required investigation/recovery attempts and no authorized path remains. Honor
an explicit owner stop, but preserve the state and describe the reopening path.

This is an agent-interpreted continuity guide. The actual session transport,
receipt, lifecycle, and recovery contracts remain their own sources of truth.
