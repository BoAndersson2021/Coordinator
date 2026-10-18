# How to be a coordinator and orchestrator using the builder repository agent as executor and their plan as the baseline for decisions and coordination

Reusable instructions for coordinating authorized work through an agent in a
builder repository. Read [Delivery Discipline](delivery-discipline.md) and the
[plan-following guide](how-to-follow-and-refresh-a-plan.md). For executable
software, also apply the [runtime-target guide](how-not-to-overengineer.md).
This document authorizes no agent launches, messages or repository operations.

The user owns the requested outcome, scope and reserved decisions. The coordinator
selects eligible work, manages dependencies, resolves implementation choices within
authorized scope and checks returned evidence. The builder agent owns implementation and execution
inside its assigned repository and permissions. The builder's current applicable
plan is the shared working baseline. It remains subordinate to the user's intent,
repository instructions and actual observed results.

When the host workspace has a mission registry, resolve work through that
registry before assigning it. Keep separate scope, builder bindings, plan
references, outstanding effects and handovers for each mission. Several missions
may remain ongoing; conversation focus is not a system-wide active-mission slot.
Selecting or closing one does not replace or terminate the others. Preserve
explicit ownership and dependency boundaries when missions share resources.

Delivery Discipline owns the shared delivery rules and repair limit. The plan
guide governs changes to the shared baseline; this guide governs who coordinates
and executes it. For Machine-managed work, also apply the
[build protocol](universal-multi-agent-build-protocol.md),
[communication contract](how-to-communicate-with-other-codex-agents.md) and
[lifecycle contract](app-terminal-codex-launch-pattern.md). Their automatic-workflow
requirements apply to Machine scope and are not implied capabilities of every
repository using this portable guide.

1. **Establish the builder and baseline before assigning work.** Verify the
   intended repository or worktree, branch, agent/session identity, current plan
   path and revision, applicable instructions and outstanding work. Confirm actual
   executor availability through the supported interface. A saved session or
   delivery acknowledgement does not prove a live builder. If communication or
   execution is unavailable, report the block rather than presenting absent
   execution as ordinary waiting.

2. **Understand the builder's plan before directing it.** Read the relevant plan,
   its history, completed evidence, current blocker and remaining dependencies.
   Ask the builder for missing repository facts when needed and authorized.
   Reconcile its status against available implementation and results. Do not
   invent a competing roadmap from a short progress summary. If the plan no
   longer serves the user's outcome, identify the mismatch and coordinate a
   targeted correction through the plan-following procedure.

3. **Coordinate against one shared source of planned work.** Reference the
   builder's existing step identifiers and acceptance conditions in assignments
   and decisions. Keep any coordination notes to the cross-repository dependencies
   and decisions they need to record. Link to repository plans rather than
   maintaining duplicate implementation plans that can silently disagree. For
   several repositories, establish a baseline for each builder and make their
   shared interfaces and dependency order explicit.

4. **Delegate a bounded next step.** Select work whose prerequisites are satisfied
   and whose scope is authorized. State the plan revision and step, intended
   result, repository boundaries, constraints, acceptance check and required
   return evidence. Tell the builder when to report a blocker or material scope
   change. Leave routine implementation choices to the builder within those
   limits. Do not request an entire speculative subsystem when one real
   integration step will answer the immediate question.

5. **Let the builder execute in its repository.** Use the supported communication
   route to deliver the assignment to the verified executor. The receiving
   harness applies repository context and permissions and runs permitted tools;
   coordinator wording cannot widen that access. Avoid parallel edits to the
   builder's owned files or a second executor doing the same work. A takeover or
   reassignment requires explicit scope and reconciliation of outstanding work.
   Independent authorized assignments may run concurrently with disjoint ownership.
   Do not quietly perform missing executor actions yourself and report the
   delegated workflow as successful. Where automatic operation is required,
   manual lifecycle or communication remains a failed acceptance condition.

6. **Track progress without disrupting execution.** Retain the assignment's
   identity, current state, agreed limits and outstanding questions in the
   existing coordination surface. Distinguish delivery, active execution,
   reported completion, verification and acceptance. Use supported progress
   signals and bounded waits instead of repeatedly interrupting the builder or
   issuing duplicate instructions. On a deadline or executor loss, expose the
   failure and reconcile actual work and uncertain effects before retrying or
   replacing the agent.

7. **Check the return against the assigned step.** Require a clear result,
   changed artifacts or revision, relevant checks, runtime observations when
   required, unresolved failures and the builder's proposed next step. Inspect
   the evidence needed for the coordination decision. A completion message, test
   count or commit alone does not prove the user's scenario works. Arrange
   independent review where the repository requires it; neither the builder nor
   the coordinator may label their own work independently reviewed.

8. **Reconcile the baseline before deciding what follows.** Compare the returned
   result with the assigned plan revision and any intervening changes. Have the
   plan owner update actual status, evidence and affected future dependencies, or
   make an authorized plan edit using the same procedure. Edit only when status,
   evidence, decisions or dependencies changed; an unchanged update needs no
   ceremonial plan rewrite. Do not silently rewrite
   the builder's plan from stale coordination notes. A failed step stays failed
   or blocked until evidence supports another status. Historical failures and
   changed decisions must remain discoverable.

9. **Make the smallest justified coordination decision.** Continue to the next
   eligible step when evidence supports it. Return a concrete defect to the
   owning builder when repair is needed. Hold dependent work when a prerequisite
   fails, while continuing independent authorized work where useful. Bring only
   material scope, budget, authority or unresolved design decisions to the user;
   do not ask for another approval for every routine step. Apply Delivery
   Discipline's [shared repair limit](delivery-discipline.md#shared-repair-limit)
   across coordination rounds and builders.

10. **Keep the user informed about the original outcome.** Explain what now
    works, what evidence supports that conclusion, what remains blocked and how
    the next action advances the target. Identify which repository and agent own
    the remaining work. Preserve enough context for another coordinator to resume
    from the existing plan and assignment history. Do not turn coordination into
    a new product, framework or recurring documentation exercise.

A handoff can be short:

> Execute step [ID] of [plan path and revision] in [repository/worktree] toward
> [observable result], within [scope and constraints]. Verify with [acceptance
> check]. Return the changed revision/artifacts, observed results, blockers and
> proposed plan update. Report before taking on a material scope change.

Use the repository's existing tools and records. Creating a guide or writing an
assignment does not establish that a builder is running or that work occurred.
