# How to end a task

When ending a task, state **what is done, what remains, and the recommended next
action**. Make it clear whether the requested outcome is complete, partial,
blocked or stopped by the owner. Do not leave the user to infer whether work
failed, is waiting, or has an available next step.

Use this with [Delivery Discipline](delivery-discipline.md) and the recipient's
required format. It grants no execution, publication or restart authority.

## The three required statements

1. **Done.** State the concrete result and the verification that supports it.
   Distinguish a draft, documentation, successful test, usable runtime result
   and owner acceptance. Do not present a requirement written down as a working
   implementation, or a message delivered as an action completed.
2. **Remains.** Name the unfinished work and material unknowns against the
   requested outcome. Distinguish failed, blocked and not yet attempted. If
   nothing remains within the requested scope, say so; do not invent follow-up
   work to fill the format. Identify uncertain pending effects explicitly.
3. **Recommended next action.** If an action option remains, recommend the
   smallest concrete step that advances the outcome and identify who should
   act. State whether it is authorized work to continue, a proposal needing an
   owner decision, an external dependency, or optional work beyond the task.
   If no viable action is available, name the exact blocker, who controls it
   when known, and what change would make progress possible. Unknown ownership
   must be reported as unknown, not guessed.

## Act on available work

Do not use a closing report to abandon necessary work that is already authorized
and feasible. Continue that work. When a real boundary requires returning to the
owner, explain the boundary and recommend the available option. Ask only for the
missing decision, access or authority; do not request consent already supplied.

Before marking a task **blocked**, **stopped** or merely **partial**, apply
Delivery Discipline's failure-resolution rule. A failed attempt is the start of
diagnosis: inspect the exact result and current state, locate the failing layer,
repair it or take a distinct supported route within scope, and verify against the
requested outcome. The shared repair limit ends repetition of an ineffective
approach, not work on the outcome. Do not close while an authorized feasible
diagnostic, repair, alternative or verification step remains. If none remains,
state the evidence that rules them out and the specific external change or owner
decision needed to continue.

A failed approach does not establish that the whole task has failed. If a
supported alternative remains, name it and recommend it, applying the shared
repair limit and existing scope. Do not end with only "blocked", "not
implemented" or "requires approval" when a concrete next option can be stated.
Do not silently switch execution routes, bypass a protection or replay an
uncertain operation to make the report look complete.

Respect an owner's stop or mission end. Preserve work and report unresolved
effects; a suggested future action does not authorize resumption. Separate
ending the conversation, completing the deliverable and verified executor
shutdown when their states differ.

## Keep the answer easy to act on

Use direct wording and the smallest useful structure. Three short labels or a
single clear sentence may be enough; headings are not mandatory. Avoid vague
offers such as "let me know", an unranked list of possibilities, or a convoluted
account of attempts that hides the recommendation. Do not add a hypothetical
next task to an otherwise complete simple answer.

For example, when a required host change is outside current access:

> **Done:** the conversion preflight passed and the setup requirements are
> documented. **Remains:** approval and cancellation controls are unproven.
> **Next:** the host integration owner should expose the supported controls so
> we can verify a disposable executor. Product execution stays blocked until
> that proof passes.

For a completed documentation request:

> **Done:** the guide is added and its links checked. **Remains:** nothing in
> the requested scope. **Next:** use it for subsequent task reports.

Agent-to-agent replies retain their structured communication contract. Express
the same facts in its existing outcome, checks, limitations and next-action
fields; do not replace a required JSON envelope with human presentation labels.
