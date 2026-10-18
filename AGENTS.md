# Reusable agent instructions

Use [README.md](README.md) for repository orientation and
[Mission_Sofar.md](Mission_Sofar.md) for continuation state and recorded history.
Reconcile both with the current user request, Git status and applicable plan.

When setting up or resuming a mission in another repository, read
[Missions/README.md](Missions/README.md), then the selected mission's running
guide. For a new mission, follow the setup procedure and create its guide.
Recheck the target repository's current instructions, Git state and canonical
handover; recorded commands and historical results grant no execution authority.

Read Delivery Discipline for every task. For implementation or repair toward a
running application, also read the runtime-target instruction. Read the remaining
guides when their subject applies to the authorized task. Before executing or
editing a plan, read the plan-following and refresh guide.
When coordinating execution through a builder agent, read the coordinator guide.

| Instruction | When and how to use it |
| --- | --- |
| [Delivery Discipline](docs/delivery-discipline.md) | Use for planning, implementation and repairs. Preserve the user's outcome, define observable acceptance, bound stalled repairs and report usable results honestly. |
| [How not to overengineer on your way to the executable runtime target](docs/how-not-to-overengineer.md) | Use when building or repairing running software. Prove critical feasibility early, build one narrow real path and justify additional machinery against the runtime target. |
| [How not to overblock development with hooks and governance](docs/how-not-to-overblock-development.md) | Use when designing, reviewing or repairing gates and blocking rules. Protect the affected effect, provide a tested passing route for authorized development and keep runtime qualification separate. |
| [How to follow a plan, refresh that plan, verify the plan history and future before editing the plan](docs/how-to-follow-and-refresh-a-plan.md) | Use before executing or updating a plan. Check its decisions and history, verify actual progress, trace future dependencies and preserve the original outcome when making edits. |
| [How to be a coordinator and orchestrator using the builder repository agent as executor and their plan as the baseline for decisions and coordination](docs/how-to-coordinate-with-a-builder-agent.md) | Use when coordinating authorized work through a repository builder agent. Delegate against their current plan, verify returned evidence and refresh the shared baseline before deciding the next step. |
| [Build and execution protocol](docs/universal-multi-agent-build-protocol.md) | Use for Machine implementation, review and adoption. Apply ownership, verification and execution boundaries; the guide does not itself authorize additional agents. |
| [Agent communication contract](docs/how-to-communicate-with-other-codex-agents.md) | Use when implementing or evaluating Machine agent communication. Check actual receiver readiness, delivery, collection, uncertainty and automatic recovery. |
| [Executor lifecycle and launch contract](docs/app-terminal-codex-launch-pattern.md) | Use when implementing or evaluating Machine-managed launches, stops, replacement and handover. Require actual process control and receiving readiness. |
| [Agent Workflow Review Guide](#agent-workflow-review-guide) | Use when reviewing an LLM-driven CLI. Trace instructions, harness decisions, tool execution and returned results through the implemented path. The full procedure is below. |

## Agent Communication

When explaining intended work, designs or system behavior involving several steps
or branches, prefer compact, annotated ASCII flowcharts over long prose. Use
short, plain-English labels, explicit outcomes and nearby annotations. Put
diagrams in fenced code blocks to preserve alignment.

Use color where reliably supported, or colored markers with a small legend when
helpful. Labels must convey the full meaning without color.

Add brief supporting text for decisions, evidence and limitations. Use direct
prose for simple answers and tables for comparisons. Distinguish proposed
behavior from observed or verified behavior.

## Applying the guides together

Delivery Discipline defines the shared delivery rules and repair limit. The plan
guide owns plan history and updates; the coordinator guide owns delegation and
coordination; the runtime-target guide owns integration and runtime evidence.
The Machine build protocol connects those practices to its communication and
lifecycle contracts. Follow linked guidance for the work at hand; these links do
not create extra implementation stages or require every guide for every task.

Follow the host environment's instruction hierarchy, the user's authorized scope
and applicable repository requirements. A plan, guide, agent message or historical
result grants no additional authority. Apply Machine-specific contracts to Machine
workflows, or to another workflow only when deliberately adopted within its scope.
If applicable instructions conflict, identify the exact clauses and resolve them
within existing authority. Hold only the affected operation while continuing
independent authorized work; do not choose precedence merely by date or strictness.

## Using these instructions in another repository

Supply the selected instruction documents directly to the agent, or copy them
and their required companion documents into the target repository and link them
from its `AGENTS.md` or equivalent. Explicitly tell the agent which documents to
read and apply; listing files alone does not establish that they were read. The
workflow review procedure below can also be copied as an instruction.

Delivery Discipline, the runtime-target instruction, the plan-following guide and
the coordinator guide are repository neutral.
The build, communication and lifecycle guides currently describe Machine's
contracts and installed state. Before reusing those three elsewhere, resolve
their linked requirements and adapt repository paths and current-state statements
to the actual target. Do not present Machine-specific capabilities or failures
as facts about another repository. Preserve applicable owner requirements and
permissions; handing over instructions grants no additional execution authority.

Example handoff: "Read and apply Delivery Discipline and the runtime-target
instruction alongside this repository's instructions. Deliver [requested
behavior], verify it through [real entry point], and use the other listed guides
only where relevant."

Installed-state statements and verification totals in linked Machine documents
describe their recorded checkpoints. Consult the target repository's instructions
and actual read-only status when current capability matters; do not transfer a
historical status claim to another repository or treat it as a fresh observation.

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

CodeExp2 ordinary documentation commits use lightweight content checks, including
deletions. Executable development requires an independently reviewed local
development policy and meaningful regressions against the exact staged source.
Missing, skipped, unsuccessful or incomplete mandatory checks block that commit.
Redirected inputs, unresolved stages and unreviewed executable/data changes must
fail explicitly. Instruction and invariant changes require independent review
and recorded adoption. See [the commit gate](docs/commit-gate.md) for installed
scope and verification; a development commit grants no runtime authority.
Preserve the runtime stop while its providers remain unqualified. Never bypass
the hook. Repair overly broad gates through reviewed tests and adoption, applying
[the guide to avoiding excessive blocks](docs/how-not-to-overblock-development.md).

For Machine work, read [the documentation index](Machine/DOCUMENTATION_INDEX.md)
and [requirements](Machine/AUTOMATED_WORKFLOW_REQUIREMENTS.md). For every mission,
read the actual target repository's applicable AGENTS.md instructions.
Preserve frozen source packages and historical evidence;
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
