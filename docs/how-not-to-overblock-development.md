# How not to overblock development with hooks and governance

The user's standard: "We don't build a CIA bunker here."

Safeguards must help deliver working software. Apply this guide when designing,
reviewing or repairing hooks, verification gates, approval rules and workflow
blocks. Use it with [Delivery Discipline](delivery-discipline.md). It grants no
permission to bypass an existing rule or publish unqualified runtime behavior.

```text
Requested action
      |
      v
Which concrete effect needs protection?
      |
      +-> ordinary document edit -> content / link / normal commit checks
      +-> executable development -> staged-source regressions
      +-> protected policy edit  -> required independent review and adoption
      +-> live workflow         -> required runtime capability and authority
      |
      v
Check that boundary
      |
      +-> passes -> continue the authorized work
      +-> fails  -> stop the affected effect; explain and repair the cause
                     |
                     +-> continue independent authorized work
```

## Rules for useful safeguards

1. **Name the failure being prevented.** Tie each gate to a concrete effect:
   staging someone else's work, publishing to the wrong remote, dispatching to
   an absent receiver, or terminating an unrelated process. "More secure" is not
   enough to justify a new restriction.

2. **Distinguish development, commit, adoption and execution.** Missing runtime
   qualification can block a live launch without blocking source inspection,
   regression development or a properly verified development commit. A committed
   candidate is not automatically installed or authorized to execute. Keep the
   applicable checks at each actual boundary.

3. **Give legitimate work a passing route.** A hook that rejects every executable
   regardless of its tests is a stop barrier, not a complete development gate.
   When development is authorized, repair that missing admission path through
   the required review and regressions. Define what evidence permits progress;
   do not leave the agent with "blocked forever" as its only compliant outcome.

4. **Block only what depends on the failed check.** A missing executor shutdown
   capability affects workflows requiring that executor. It does not by itself
   invalidate an unrelated documentation commit. Do not turn one failed service,
   stale receipt or dirty file into a repository-wide freeze.

5. **Verify the actual implementation before declaring a limitation.** Read the
   installed hook, native interface and existing guides. Check transport framing,
   configuration and the intended entry point. A timeout from an incorrectly
   formed request proves that request failed; it does not prove the underlying
   capability is absent. Correct the claim when better evidence arrives.

6. **Make rejections actionable.** State the rejected operation, failed condition,
   evidence and smallest corrective action. Distinguish a missing check, failing
   regression, unsupported provider and authority limit. Do not tell the user
   "tests are required" when the hook has no way to recognize passing tests.

7. **Test both refusal and progress.** A gate needs a legitimate passing case
   alongside meaningful negative cases. For a commit gate, test real disposable
   commits, exact staged bytes, unstaged repairs hiding staged failures, missing
   or skipped mandatory tests and incomplete runners. Preserve ordinary document
   work. Denial tests alone cannot establish a usable development path.

8. **Reuse the machinery already present.** Prefer the existing verifier, native
   client, repository test runner and Git workflow. Fix the owning layer before
   inventing another registry, approval service, policy package or parallel
   roadmap. Additional machinery must enable a demonstrated required step.

9. **Keep approvals proportional and respect existing authority.** Use required
   independent review for protected policy changes. Do not invent a fresh owner
   confirmation for every routine test, reversible edit or previously authorized
   action. A reviewer report also cannot grant authority the user withheld.

10. **Do the engineering after identifying the block.** Inspect, reproduce,
    correct, test and return to the requested outcome within authorized scope.
    Apply Delivery Discipline's repair limit to ineffective approaches, then use
    an evidenced supported alternative when available. Do not use a failed
    approach as a reason to abandon independent useful work.

## Applying this to CodeExp2

The mission controller needs executable development checks and actual native
lifecycle proof. These are separate acceptance questions. A reviewed gate can
permit a tested development candidate while the candidate still rejects an
unqualified launch. That preserves the execution invariant and permits work
toward satisfying it.

Do not use `--no-verify`, weaken mandatory regressions, relabel executable inputs
as documentation or silently route around a runtime stop to claim success.
Repair the overly broad gate at its source. Preserve existing work, frozen
evidence and independent-review requirements. Report what is verified, what is
still unavailable, and the next concrete engineering step.
