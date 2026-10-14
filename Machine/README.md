# Mammuth Machine builder mission

This folder holds the design interpretation and working mission for the Codex builder developing the Mammuth Machine. The implementation repository is `/Users/boandersson/Desktop/Machine`; this folder belongs to the `CodeExp` repository and has no separate Git repository.

The mission is to turn the approved Design corpus into a persistent, human-directed studio coordination system that operates agents in separate game repositories. Machine preserves assignments, authority, results, evidence, and recovery state across agent replacement.

## Read first

1. [Builder instructions](AGENTS.md).
2. [Design and builder mission](DESIGN_AND_MISSION.md).
3. [Current mission checkpoint](CURRENT_MISSION.md).
4. The relevant sources in the [Machine Design corpus](../../Machine/Design/Intent.txt) and the three communication documents below.

## Repository boundaries

| Location | Responsibility |
| --- | --- |
| `Desktop/CodeExp/Machine` | This builder's mission, design interpretation, and development approach. |
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

The first inspection coordinator is installed in `Desktop/Machine`, with durable records and 37 passing focused checks. The selected Blender documentation assignment completed through the native attended-session route and was independently reviewed and closed, including reconciliation when its registered role changed. See the [current checkpoint](CURRENT_MISSION.md). The Design corpus remains unchanged and full studio qualification remains open.
