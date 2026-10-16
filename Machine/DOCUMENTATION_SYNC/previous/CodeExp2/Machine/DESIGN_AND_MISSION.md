# Mammuth Machine design and builder mission

## Purpose

Build the Mammuth Machine as a human-directed, AI-operated game-development studio whose institutional knowledge and production continuity survive individual agents and models. Machine is the coordination and management layer toward separate game repositories with agents working inside them.

The user defines creative direction, consequential decisions, budgets, and reserved acceptance. The initial Codex builder implements the studio machinery under that direction. The resulting system should enable routine execution within explicit delegated scope, with human attention focused on decisions, evidence, and exceptions.

## Design foundation

The implementation follows the corpus in `/Users/boandersson/Desktop/Machine/Design`.

| Source | Role |
| --- | --- |
| [Intent](../../Machine/Design/Intent.txt) | Overall studio purpose and present architectural status. |
| [The Mammuth Machine](../../Machine/Design/THE-MAMMUTH-MACHINE.txt) | Product and commercial mission. |
| [Architecture v1.2](../../Machine/Design/agentic-game-studio-v0.2-handoff/corpus/architecture-v1.2.txt) | Normative project machine, domain ownership, identities, verification, and recovery boundaries. |
| [Agentic Structure](../../Machine/Design/agentic-game-studio-v0.2-handoff/corpus/agentic-structure.txt) | Normative separation between persistent infrastructure and replaceable agents. |
| [Unified Operating Model](../../Machine/Design/agentic-game-studio-v0.2-handoff/corpus/unified-operating-model.txt) | Normative connection between knowledge, project machinery, agents, verification, and adoption. |
| [System Position](../../Machine/Design/agentic-game-studio-v0.2-handoff/corpus/system-position.txt) | Contextual relationship between studio infrastructure and game projects. |
| [Capability System v0.1](../../Machine/Design/studio-capability-system-v0.1/specification/STUDIO-CAPABILITY-SYSTEM-v0.1.md) | Separate normative capability extension, with declarative contracts and workflows. |
| [Benefit of System v0.2](../../Machine/Design/Benefit-of-System-v0.2.txt) | Intended value, costs, limitations, and the decisive production acceptance experiment. |

The v0.2 studio handoff is frozen; its project architecture remains v1.2. The v0.1 capability extension is independently versioned and inert until explicitly integrated and qualified. Its sixteen capabilities are responsibilities, not a requirement to deploy sixteen agents or sixteen services.

The installation manifest governs bootstrap behavior. It does not provide operational authority services. Conflicts in mandatory requirements block affected work until explicitly resolved. New implementation must preserve the source packages and identify any proposed departures separately.

## Ownership across repositories

Machine owns the reusable studio implementation: corpus resolution mechanisms, project and agent bindings, coordination, task records, adapter contracts, grant validation mechanisms, evidence custody, observability, and recovery procedures. Authoritative records remain with their designated domain owners.

Each game repository owns its game-specific intent and implementation: GDDs, source, authored assets, engine layout, runtime content, project tests, and integration history. Controlled artifact stores may hold builds and releases under the relevant project authority. Machine stores references, identities, and coordination evidence rather than importing those products into its own source tree.

Project bindings must identify the project and its repository or worktree, relevant source revisions, agent threads, supported operations, and authority owners. Registering a path or discovering a thread does not authorize work in that project.

## Coordination and communication design

Use the existing three-document communication system from `CodeExp`:

1. [Build protocol](../docs/universal-multi-agent-build-protocol.md) defines user, coordinator, builder, independent reviewer, and domain-validation lanes.
2. [Agent communication guide](../docs/how-to-communicate-with-other-codex-agents.md) defines thread discovery, UUID addressing, scoped messaging, waiting, and reading responses through a shared app server.
3. [Launch pattern](../docs/app-terminal-codex-launch-pattern.md) defines an explicit repository working directory, applicable instructions, a read-only initial action, and the harness execution boundary.

The communication approach has successful live use according to the user, including `CodeExp` and `Desktop/Project_Blender`. Local inspection also established CLI queue availability and working thread discovery. These establish the communication foundation; Machine-specific persistence, grant enforcement, and recovery require their own executable acceptance evidence.

### Request and result chain

1. The user supplies intent and authorized scope to Machine.
2. Machine resolves applicable pinned context and records a bounded assignment with acceptance conditions.
3. Machine verifies the target agent's thread UUID, project binding, actual workspace, and availability.
4. The communication adapter delivers the assignment to that thread.
5. The target Codex harness assembles context, including applicable repository instructions, and invokes the model.
6. The model generates a response or structured tool request. The harness checks and routes the request under its configured permissions.
7. Tools execute in the target execution environment. Results return to that model as new context.
8. The agent reports outputs, operation receipts, checks, and unresolved effects.
9. Machine collects the report, checks the relevant artifacts and evidence, and records the appropriate assignment state.
10. The designated owner authorizes adoption through the relevant domain boundary. Machine records the accepted identities and updates derived progress.

Thread transport does not enforce the full studio authority contract. Each protected operation requires enforcement at the receiving execution or domain-adoption boundary. Neither Machine's coordinator identity nor a prompt can widen tool access.

### Production defects and project builders

The owner's castle live-test correction establishes a separate project-builder lane. When a production role reports a concrete infrastructure defect, Machine retains the failed operation and pauses dependent work. It discovers an existing project system-builder session, verifies its UUID, repository/worktree, current context, execution surface and role acknowledgement, then records and sends a bounded repair handoff. Brainstorm and Modeling remain production roles; discovery must not treat every agent in the same repository as its builder.

The project builder owns the permitted repair and its focused validation. Machine checks the returned evidence and asks the existing production roles to rerun the exact failed readiness check before continuing the same assignment. Preserve unknown outcomes, task identities, scenes, baselines, route pins, execution/account/billing contracts and historical failures. Missing builder identity or repair authority remains explicit; it does not silently transfer the repair to Machine's bootstrap builder or authorize a new execution mode.

This is the intended coordination behavior. The installed inspection foundation does not yet implement automatic builder discovery or protected repair delegation. The [castle live-test record](CASTLE_LIVE_TEST.md) distinguishes the current operator-mediated handoff from that future capability.

CLI queueing depends on the installed CLI and shared server visibility. Bind the executable and endpoint explicitly and verify supported commands. The current local `codex` entry is a routing shim that may select repository wrappers from environment or directory context before forwarding arguments; a `-C` argument alone does not establish which wrapper runs.

### Persistent coordination

Define versioned records before relying on unattended dispatch:

- Project binding: stable project identity, repository or worktree, revision references, supported adapters, and designated owners.
- Agent binding: thread UUID, server identity, observed workspace and status, capabilities, and observation freshness.
- Assignment: task and operation identities, requesting principal, scope, pinned inputs, grant reference, resource and budget constraints, expected outputs, and acceptance requirements.
- Execution and delivery receipts: attempt identity, adapter or executor version, delivery outcome, reported execution outcome, candidate references, evidence references, and unresolved effects.
- Verification and adoption records: exact artifact and environment identities, requirement verdicts, independent review identity, owner authorization, accepted revision, and transition preconditions.
- Recovery records: interrupted or uncertain operations, affected resources, reconciliation evidence, confirmed outcome, and the authority permitting further action.

Delivery, execution completion, verification, adoption, and task closure are distinct transitions. A durable assignment record does not prove that its external effect occurred. Unknown delivery or mutation outcomes require reconciliation before retry where duplicate work or effects are possible.

## Initial builder mission

The current Codex builder constructs Machine until it can reliably coordinate its own development. The builder must inspect actual implementation, make bounded changes, run focused checks, and report evidence and limits. Agent conversations remain working context; accepted source, decisions, and receipts carry continuity.

The builder's first implementation objective is one complete coordination path. It should establish a project binding, record an authorized inspection assignment, address an existing project agent, collect and verify the response, and preserve the outcome across coordinator replacement. Game production workflows follow that foundation.

### Development sequence

| Increment | Required behavior | Acceptance evidence |
| --- | --- | --- |
| Operating contract | Machine root documentation and instructions establish studio scope, corpus relationships, domain owners, and startup behavior. | Review against the Design corpus and the user's explicit repository boundary. |
| Durable records | Versioned project, agent, assignment, receipt, and recovery records support validated state transitions. | Focused checks for unsupported schemas, stale preconditions, interruption, and evidence custody. |
| Read-only front door | Status or help exposes bindings, outstanding work, and unresolved operations without dispatch or setup. | Before/after inspection establishes that startup does not mutate coordination or project state. |
| Communication adapter | Verified project and thread bindings support scoped delivery and response collection. | Focused checks of wrong targets, unavailable threads, acknowledgement handling, and uncertain delivery; authorized live round trip separately. |
| First operational round trip | One bounded project inspection produces a report and artifact-bound verification record. | Actual target workspace, pinned inputs, report, independent checks, and recorded outcome. |
| Continuity and recovery | A replacement coordinator resumes from durable records and reconciles uncertain delivery or effects. | Deliberate interruption and uncertain acknowledgement demonstrate preserved work and prevention of duplicate dispatch or mutation. |
| Production capabilities | Authorized engineering, content, integration, build, test, and release workflows operate through qualified project adapters. | Incremental acceptance against the relevant Design contracts; real game output remains in external project custody. |

These increments describe intended work. This documentation request does not dispatch agents, register external projects, or activate workflows. Normal implementation choices remain the builder's responsibility within each authorized task; reserved decisions remain with their designated owners.

## Machine developing Machine

Machine may eventually coordinate improvements to its own implementation. It follows the same assignment, candidate, verification, and adoption boundaries used for external projects.

The builder of a candidate must not approve its own changes to authority, permissions, verification, recovery, or promotion. Evaluate replacements separately from the running version. Record independent verification and designated-owner approval before adoption, and preserve a recoverable previous version.

Replacing code does not reverse external effects or incompatible state migrations. Recovery must retain their records and use an authorized reconciliation or compensation operation where reversal is no longer valid.

## Success criteria

The first milestone is a demonstrable Machine coordination cycle with durable continuity and explicit authority, using the established agent dialogue path.

The eventual production test remains the Design corpus's bounded real gameplay feature: approved intent through implementation, assets, integration, build, testing, verification, reconciliation, and accepted progress, with deliberate interruption and uncertain-effect recovery. The feature and its source remain in the game project.

Measure accepted output, elapsed time, human supervision, total model and infrastructure cost, failed attempts, rework, defects, recovery time, and provenance completeness. Operational readiness and economic benefit require observed results against the exact qualified revisions.

## Automated role lifecycle frontier

The owner selected automated lifecycle control before native qualification. [The proposed lifecycle design](ROLE_LIFECYCLE_CONTROL_DESIGN.md) separates Machine coordination from the project controller and native harness, preserves the original roles and execution contract, and treats unmanaged enrollment and turn fencing as required integrations. It introduces no live controller, arbitrary execution adapter or native authority. Both corrected v29 source reviews and the135-test pass remain retained; castle construction waits for independently qualified lifecycle/native execution.
