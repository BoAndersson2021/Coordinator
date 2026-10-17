# How to follow a plan, refresh that plan, verify the plan history and future before editing the plan

Reusable instructions for agents working from a plan in any repository. Apply
them alongside [Delivery Discipline](delivery-discipline.md) and the repository's
instructions. A plan records intended work; it does not grant execution authority
or prove completion.

This guide owns plan history, dependencies and edits. Use the
[runtime-target guide](how-not-to-overengineer.md) to choose evidence for runtime
steps and the [coordinator guide](how-to-coordinate-with-a-builder-agent.md) for
delegated execution and plan ownership. Refreshing a plan does not require a new
runtime run when no relevant implementation, evidence or assumption has changed.

1. **Find the plan that governs the task.** Identify the plan the user selected,
   its associated requirements and acceptance conditions, and any later explicit
   decisions. Read the entire relevant plan, including its remaining steps and
   referenced constraints. Do not choose a different plan merely because its
   filename or timestamp looks newer. If several plans conflict, identify the
   conflict before changing the affected work.

2. **Establish its history before editing.** Inspect repository status and the
   plan's uncommitted diff. Use the existing version history, decision notes and
   relevant earlier revisions to establish what changed and why. In Git, start
   with `git log --follow -- path/to/plan.md` and inspect the relevant commits.
   Include applicable user decisions made since the last recorded revision.
   Distinguish approved changes from proposals and abandoned alternatives. If
   history is missing, say so; do not invent an earlier decision or approval.

3. **Reconcile the plan with actual work.** Check the implementation, relevant
   artifacts and meaningful verification results for the current step and its
   prerequisites. Treat completion marks and agent reports as claims to verify.
   Preserve the distinction between completed source work, successful tests,
   installed behavior and a working runtime. Keep historical results within
   their observed scope; identify changes that require fresh verification.

4. **Check the future before changing the present.** Trace how the proposed edit
   affects later steps, their inputs, interfaces, acceptance checks and the final
   user outcome. Check dependencies in both directions: prerequisites needed by
   this step and later work that relies on it. Do not remove a requirement or
   replace an implementation without accounting for the later work that needs
   it. When a dependency changes, update the affected future steps together or
   explicitly mark them as blocked pending resolution.

5. **Follow the next eligible step.** Work on the next authorized step whose
   prerequisites are satisfied. Keep the plan's original outcome and acceptance
   conditions fixed unless the user has authorized changing them. A routine
   "continue" or "execute the next step" resumes that outcome. Do not silently
   substitute a new objective, skip a failing prerequisite, or turn a repair into
   an indefinite series of new phases. Apply Delivery Discipline's
   [shared repair limit](delivery-discipline.md#shared-repair-limit).

6. **Refresh when facts change.** Update the plan after meaningful completion,
   a failed assumption, a discovered blocker or a user decision. Use the plan's
   existing status conventions and stable step identifiers. Mark unverified work
   as unverified and blocked work as blocked. Record observed failure without
   changing the acceptance condition to make the step appear successful. An
   implementation being present does not establish that it is installed or live.

7. **Make the smallest coherent edit.** Change the affected status, reasoning,
   evidence references and dependent steps. Explain material changes with a brief
   note stating what changed, why, the supporting evidence and the effect on
   remaining work. Keep established requirements, unresolved failures and relevant
   decisions discoverable. Use the existing history rather than creating a new
   plan directory, duplicate specification or approval process for each update.

8. **Preserve history honestly.** Follow the governing change rules for frozen or
   explicitly immutable plans; use an authorized amendment rather than silently
   editing sealed history. An explicit owner-authorized revision follows those
   rules. For normal
   maintained plans, use their version history and existing change notes. Do not
   rewrite old results, erase a failed attempt, or attribute your decision to the
   user. When earlier guidance is superseded, identify the replacement and reason.
   Correct factual errors explicitly; preserving history does not require leaving
   false statements presented as current truth.

9. **Check for intervening changes before writing.** Re-read the affected content
   and inspect the latest diff before applying your edit. If another writer or
   user update changed it, reconcile those changes rather than overwriting them
   with your earlier snapshot. Preserve unrelated edits. Ask for clarification
   only when a material conflict cannot be resolved from the authorized scope
   and available evidence.

10. **Verify the updated plan as a whole.** Read the final diff and the resulting
    sequence. Check step references, prerequisite ordering, evidence links,
    remaining acceptance conditions and the route to the original finish line.
    Clearly identify the next eligible action and any remaining blocker. Make
    sure removed or superseded work has no unexplained dependents. Report plan
    edits separately from work actually executed; editing a plan does not change
    runtime state, undo effects or complete its steps.

Before editing, you should be able to explain what was intended, what actually
happened, why the edit is needed and how it affects the remaining path to the
user's outcome. If a necessary fact is unavailable, record that uncertainty and
limit the edit accordingly.

For routine updates, a short note is enough: "Step 3 remains blocked because the
real interface rejected the requested operation. The implementation exists, but
the runtime check failed. Steps 4 and 5 still depend on this result. Next: verify
the supported alternative within the existing scope." Link the actual evidence
when available. Never copy an example as if it were an observed result.
