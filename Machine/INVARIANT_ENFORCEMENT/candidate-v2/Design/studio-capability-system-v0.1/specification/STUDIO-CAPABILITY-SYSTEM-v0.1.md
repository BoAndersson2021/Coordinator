# STUDIO CAPABILITY SYSTEM v0.1

Status: normative capability contract; operational enforcement unimplemented. Compatible with frozen studio v0.2 and project architecture v1.2.

## Scope and ontology
Sixteen first-class **capabilities**, not sixteen agents, services, or authorities. Each registry entry defines scope, owner, inputs, outputs, dependencies, permitted effects, prohibited effects, state ownership, failure mode, and evidence. All protected mutations require independent authority validation and domain-owner commit.

## Governance and precedence
LAWS are mandatory studio invariants. RULES are scoped practices and may be overridden only by an authorized exception where permitted. SPECIFICATION defines intended behavior; CONTRACTS define interfaces and obligations. Neither tool execution nor a newer implementation silently supersedes approved design. Conflicts in mandatory requirements block affected work.

## Citizen boundaries
- LAWS: register mandatory invariants; no implicit override.
- RULES: register scoped operational practices; explicit exception only.
- CONTRACTS: versioned machine-readable obligations, not grants.
- TOOLS: effect-classified adapters; disabled until implementation and enforcement proven.
- VERIFICATION: evaluates artifact-bound evidence; cannot self-authorize adoption.
- RED TEAM: bounded adversarial review; findings are not mutation authority.
- AUTHORITY: grant validity, scope, expiry, revocation; separate from orchestration.
- STATE: federated domain-owned state; no universal mutation service.
- OBSERVABILITY: derived, possibly stale observations; never authoritative commit.
- PLANNING: executable decomposition proposals; ROADMAP owns milestones.
- INSPECTION: observed state with source and revision; distinguish inference.
- SPECIFICATION: product behavior and acceptance, not interface enforcement.
- TESTING: runs experiments and records raw results; VERIFICATION certifies against contracts.
- HARDENING LOOP: bounded repair/retest coordination, no unrestricted write access.
- DOCUMENTATION & RECONCILIATION: detect staleness and propose corrections; never choose newer code over approved intent automatically.
- ROADMAP & PROGRESS CONTROL: milestone identity and accepted evidence, not task execution.

## Execution law
Resolve pinned context -> inspect -> specify -> plan -> validate grant -> execute candidate -> test -> verify and risk-scoped red team -> bounded hardening -> domain-authorized adoption -> reconcile documentation -> advance roadmap against evidence. This is a logical dependency pattern, not a mandatory serial schedule.

## Failure and recovery
Each operation must record owner, scope, expected revision, operation identity, effects, evidence and outcome. Unknown external outcomes close conflicting authority and prohibit blind retry until authoritative reconciliation. Rollback is legal only before escaped irreversible effects; otherwise issue a compensating authorized operation. A task receipt does not prove an external effect.

## Acceptance and limits
Static validation proves package structure, registry identity, reference resolution, conservative effect declarations, and file integrity only. It does NOT prove authority enforcement, isolation, durable persistence, live Unreal/Blender adapters, or release readiness. All runtime qualification remains closed until separately demonstrated.
