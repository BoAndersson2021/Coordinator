# Mammuth Machine

**Workflow execution is blocked:** `MACHINE_AUTOMATED_EXECUTION_REQUIRED` is a
mandatory executable invariant for Machine and all its adapters. Current
providers lack qualified automatic lifecycle, communication and recovery.
`status`, `doctor`, `work-view`, `bridge-collect`, `permit-inspect` and
`invariant-check` report this failure and exit 3. Source integrity and retained
observations remain separate fields. New dispatch, handovers, execution and
workflow verification/closure are rejected before effects. See
[the invariant contract](docs/WORKFLOW_INVARIANT.md).

Machine is a human-directed studio coordinator for agents working in separate game repositories. It preserves assignments, delivery attempts, reports, verification records, and recovery state across coordinator replacement. Games, game source, game design, and game assets remain in their project repositories.

## Start here

Requires Python 3.9 or newer and Git. The coordinator uses the Python standard library; it installs no dependencies and makes no model or network calls.

```sh
./Machine
./Machine status --json
./Machine doctor --json
./Machine --help
```

These commands are read-only. Opening Machine does not create state, register projects, dispatch work, start project applications, or resume interrupted operations. `doctor` checks the frozen Design source digests, the capability inventory, communication snapshots, and any existing ledger integrity. A pass establishes these checks only.

## Operating contract

- The user owns intent and reserved decisions; each protected domain retains its designated adoption owner.
- Machine owns studio coordination. Project bindings are references to external Git worktrees, not permission grants.
- Agents execute through their own Codex harness, repository instructions, adapters, and execution environment.
- Delivery, execution completion, verification, adoption, and closure are separate facts.
- Uncertain delivery blocks another dispatch until explicit reconciliation is recorded.
- Agent reports cannot become accepted project source through this coordinator.

Read [AGENTS.md](AGENTS.md), the [coordination contract](docs/COORDINATION.md), and the [implementation frontier](docs/ROADMAP.md). The builder mission lives in [`CodeExp/Machine`](../CodeExp/Machine/README.md).

## Design and communication sources

The [Design corpus](Design/Intent.txt) contains frozen Agentic Game Studio v0.2 with project Architecture v1.2, the independently versioned Capability System v0.1, and the value proposition. The game-project layout in Architecture v1.2 applies to external projects, not Machine's own source layout. Source packages remain unchanged.

The coordinator adopts the established communication approach from `CodeExp`:

- [Multi-agent build protocol](docs/communications/universal-multi-agent-build-protocol.md).
- [Thread dialogue](docs/communications/how-to-communicate-with-other-codex-agents.md).
- [Terminal launch](docs/communications/app-terminal-codex-launch-pattern.md).

[Snapshot provenance](docs/communications/provenance.json) records the originating repository revision and exact file digests. Updating these references requires an explicit reviewed source update; a newer document does not automatically change active task context.

## Explicit local setup

```sh
./Machine init --owner OWNER
```

This creates a private `.machine/state.sqlite3` ledger. The local operating model trusts the operator and host file custody. Declared owner names and authorization text are assertions, not authenticated principals or a general grant service. External project assignments support read-only inspection. [Bounded admission](docs/ADMISSION.md) adds one single-use, session-bound initialization permit for an exact disposable scratch directory. General protected mutation, source adoption, builds, release promotion, and publication are not implemented.

The [native inspection bridge](docs/NATIVE_BRIDGE.md) retains queue/reply custody code. New native and manual deliveries are disabled by the invariant. Existing reply collection remains available for reconciliation with an explicit failed invariant result; it never sends. The command-operated coordinator is not qualified automatic orchestration. Startup performs no delivery or lifecycle operation.

## Validate

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Checks use disposable external Git workspaces and local receipts. They exercise wrong targets, stale inputs and versions, uncertain delivery, operation replay, evidence integrity, concurrent coordinators, and process interruption. They do not run a game or Blender. Live dialogue evidence is recorded separately from fixture evidence.
