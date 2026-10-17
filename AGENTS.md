# Delivery discipline

Read and follow [Delivery Discipline](docs/delivery-discipline.md) for planning,
implementation and repairs. It is a standalone instruction that can be handed to
agents in other repositories. Keep the user's outcome fixed, prove critical
feasibility early, and apply its two-attempt limit to stalled repair chains.

# Mandatory Machine execution invariant

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` governs Machine and every adapter it uses,
controls or communicates with. Every new or edited feature must preserve zero
manual lifecycle, communication, coordinator restart or handover steps during
authorized workflow execution. Missing capability/proof must fail loudly and
block work before effects. No silent/manual fallback or metadata-as-liveness.

The installed guard and pinned pre-commit verifier in Desktop/Machine enforce
the stop while automation remains unqualified. Every executable feature change
must include meaningful staged invariant regressions; skipped, undiscovered,
expected-failure or unsuccessful mandatory tests and missing completion must
block the commit. Never bypass the hook or weaken enforcement. Protected changes
require independent review and recorded adoption. Development/diagnosis is not
an accepted automated workflow or a substitute for its missing runtime providers.

CodeExp2's pre-commit hook blocks staged changes without reviewed verification.
A reviewed documentation-only exception is bound to an exact parent and staged
tree; it grants no executable-feature or workflow authority.
Feature development requires reviewed invariant enforcement and meaningful staged
regressions before an allow path can be installed. Never disable or bypass the
hook to commit.

Read [the documentation index](Machine/DOCUMENTATION_INDEX.md),
[requirements](Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md), and the actual target
repository AGENTS.md. Preserve frozen source packages and historical evidence;
old manual examples cannot re-enable workflow execution. The review procedure
below remains applicable within this invariant and the user's authorized scope.

# Agent Workflow Review Guide

When asked to review how an LLM-driven CLI works in a repository, trace the implemented path from the user's request to work in the repository and back. Keep component roles explicit: the model generates a response or structured tool request; the CLI harness assembles context, checks and routes requests, runs tools through an execution environment, and returns tool results to the model as new context.

## Review procedure

1. Find the instruction files the CLI loads, including root and nested `AGENTS.md` files. Identify how those instructions enter the model's context.
2. Find the documented entry command and trace it through launch scripts, command dispatchers, harness code, permission checks, tool definitions, and the tool executor.
3. Verify where commands actually execute, what environment and access they receive, and how results return to the model. Distinguish the model's generated request from the harness's decision and the tool's execution.
4. Compare the implementation with the docs. Check identity and session setup, receipts, permissions, work admission, and whether initialization changes state. Do not infer behavior from names or descriptions alone.
5. Begin with read-only inspection and status/help commands. Read the implementation before running setup, claim, or delivery commands, since they may write files or change coordination state.
6. If behavior and documentation disagree, identify the layer that owns the behavior, make a targeted correction there, update the related documentation, and use the existing focused validation route when available.

Report the observed chain and the specific mismatch before describing any repair. Keep changes within the requested scope. Do not broaden tool access or treat session initialization as permission to perform repository work.
