# Mammuth Machine builder mission

This folder holds the design interpretation and working mission for the Codex builder developing the Mammuth Machine. The implementation repository is `/Users/boandersson/Desktop/Machine`; this folder belongs to the `CodeExp2` repository and has no nested Git repository.

The mission is to turn the approved Design corpus into a persistent, human-directed studio coordination system that operates agents in separate game repositories. Machine preserves assignments, authority, results, evidence, and recovery state across agent replacement.

## Read first

1. [Builder instructions](AGENTS.md).
2. [Design and builder mission](DESIGN_AND_MISSION.md).
3. [Current mission checkpoint](CURRENT_MISSION.md).
4. [Current operating structure](CURRENT_STRUCTURE.yaml): the CodeExp2 agent is the development coordinator; Machine holds persistent custody and the enforced stop barrier. Automatic workflow execution remains unqualified and blocked.
5. The relevant sources in the [Machine Design corpus](../../Machine/Design/Intent.txt) and the three communication documents below.

The [communication expansion record](COMMUNICATION_BRIDGE/README.md) tracks the implementation, independent review, and failed fresh-CodeExp2 live acceptance. The owner's [workflow requirements](AUTOMATED_WORKFLOW_REQUIREMENTS.md) require automated lifecycle, communication and recovery with visible status and zero manual execution steps. The current system fails that requirement.

## Repository boundaries

| Location | Responsibility |
| --- | --- |
| `Desktop/CodeExp2/Machine` | This builder's mission, design interpretation, and development approach. |
| `Desktop/Machine` | Mammuth Machine implementation, studio specifications, contracts, adapters, coordination, and validation. |
| Separate game repositories | Game design, game source, authored assets, runtime content, builds, and project integration. |

Machine records references and controlled bindings to game repositories. Do not introduce a game, game source, game assets, or a sample game into either this mission folder or the Machine implementation repository. The logical game-project layout in Architecture v1.2 describes external projects operated by Machine; it is not a scaffold for Machine itself.

## Communication foundation

The coordination approach uses these existing `CodeExp` documents:

- [Universal multi-agent project build protocol](../docs/universal-multi-agent-build-protocol.md): role separation, bounded assignments, ownership, independent review, and acceptance evidence.
- [How to communicate with other Codex agents](../docs/how-to-communicate-with-other-codex-agents.md): discovery, thread UUID addressing, scoped messages, and response collection.
- [Terminal and Codex launch pattern](../docs/app-terminal-codex-launch-pattern.md): repository-scoped launch, instruction loading, permission boundaries, and read-only startup.

The user reports successful live use of this approach in `CodeExp` and projects including `Desktop/Project_Blender`. It is the established communication foundation. Machine must add durable coordination and enforceable transitions around it.

## Current stage

`MACHINE_AUTOMATED_EXECUTION_REQUIRED` is installed in Desktop/Machine, covering
Machine and all used/controlled/communicating adapters and every new/edited
feature. Current unqualified workflow execution is blocked loudly. V3 has
independent source PASS, 98 tests and 14 real disposable commit-hook proofs; none
qualifies automatic operation. The native live acceptance is FAIL. Historical
pilot/scratch evidence is preserved, not an enabled fallback. See the
[current checkpoint](CURRENT_MISSION.md), [requirements](AUTOMATED_WORKFLOW_REQUIREMENTS.md),
[documentation index](DOCUMENTATION_INDEX.md) and
[operating runbook](/Users/boandersson/Desktop/Machine/docs/RUNBOOK.md).
