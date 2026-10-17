# Mammuth Machine builder mission

This folder holds the design interpretation and working mission for the Codex builder developing the Mammuth Machine. The implementation repository is `/Users/boandersson/Desktop/Machine`; this folder belongs to the `CodeExp2` repository and has no nested Git repository.

The mission is to turn the approved Design corpus into a persistent, human-directed studio coordination system that operates agents in separate game repositories. Machine preserves assignments, authority, results, evidence, and recovery state across agent replacement.

## Read first

1. [Workspace instructions and guide catalog](../AGENTS.md) and
   [current handover](../Mission_Sofar.md).
2. [Builder instructions](AGENTS.md).
3. [Design and builder mission](DESIGN_AND_MISSION.md).
4. [Recorded mission checkpoint](CURRENT_MISSION.md) and
   [operating structure](CURRENT_STRUCTURE.yaml): CodeExp2 supplies development
   coordination; Machine holds persistent custody and the enforced stop barrier.
5. Relevant sources in the [Machine Design corpus](../../Machine/Design/Intent.txt)
   and the applicable instruction guides below.

The [communication expansion record](COMMUNICATION_BRIDGE/README.md) tracks the implementation, independent review, and failed fresh-CodeExp2 live acceptance. The owner's [workflow requirements](AUTOMATED_WORKFLOW_REQUIREMENTS.md) require automated lifecycle, communication and recovery with visible status and zero manual execution steps. The current system fails that requirement.

## Repository boundaries

| Location | Responsibility |
| --- | --- |
| `Desktop/CodeExp2/Machine` | This builder's mission, design interpretation, and development approach. |
| `Desktop/Machine` | Mammuth Machine implementation, studio specifications, contracts, adapters, coordination, and validation. |
| Separate game repositories | Game design, game source, authored assets, runtime content, builds, and project integration. |

Machine records references and controlled bindings to game repositories. Do not introduce a game, game source, game assets, or a sample game into either this mission folder or the Machine implementation repository. The logical game-project layout in Architecture v1.2 describes external projects operated by Machine; it is not a scaffold for Machine itself.

## Instruction corpus and communication foundation

The [workspace catalog](../AGENTS.md#reusable-agent-instructions) lists all seven
standalone guides and the inline CLI review procedure. Delivery Discipline owns
shared rules; the runtime, plan and coordinator guides refine their respective
subjects. The [guide map](../AGENTS.md#applying-the-guides-together) explains scope,
permissions and conflict handling. Read only the companions relevant to the task.

Machine-managed workflows additionally use:

- [Build and execution protocol](../docs/universal-multi-agent-build-protocol.md):
  ownership, staged verification and evidence-based acceptance.
- [Agent communication contract](../docs/how-to-communicate-with-other-codex-agents.md):
  actual receiver readiness, scoped delivery, collection and uncertain outcomes.
- [Executor lifecycle and launch contract](../docs/app-terminal-codex-launch-pattern.md):
  managed startup, readiness, retirement and recovery.

Historical successful communication in other projects motivated these contracts;
it does not establish qualified automatic Machine operation. Installed-repository
copies retain their own recorded provenance and may differ from guidance here.

## Recorded implementation and current boundaries

The [enforcement evidence](INVARIANT_ENFORCEMENT/README.md) records adoption of
`MACHINE_AUTOMATED_EXECUTION_REQUIRED` in Desktop/Machine. Unqualified workflow
execution is blocked; the retained native live acceptance is FAIL. Source review
and failure-detection checks do not qualify automatic operation. Use the
[requirements](AUTOMATED_WORKFLOW_REQUIREMENTS.md),
[documentation status](DOCUMENTATION_INDEX.md) and target repository's current
read-only observations before relying on a capability. Its
[operating runbook](/Users/boandersson/Desktop/Machine/docs/RUNBOOK.md) belongs to
that implementation repository.

The [dashboard](DASHBOARD/README.md) installation is recorded at Machine commit
`574e834`; [shared CLI/dashboard work-view completion](WORK_VIEW/README.md) is
recorded at `d24f163`. Those records include observed automatic service/browser
recovery and meaningful validation within their scopes. They do not prove that
the dashboard is running now or that project workflows are qualified.

No native application was delivered. The abandoned native MVP experiment was
removed at the user's direction. The separate task-timeline candidate remains
unfinished and is outside the instruction/documentation commit. Read the
[workspace handover](../Mission_Sofar.md) before choosing further work; startup
and documentation do not authorize dispatch, installation or retries.
