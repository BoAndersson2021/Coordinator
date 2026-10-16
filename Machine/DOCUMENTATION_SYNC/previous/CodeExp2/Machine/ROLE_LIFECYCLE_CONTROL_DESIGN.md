# Automated role lifecycle control — proposed design v0.1

Current owner requirement: [workflow execution](AUTOMATED_WORKFLOW_REQUIREMENTS.md)
must have zero manual start/stop, communication or handover steps. This proposed
design is an input to that work, not an implemented capability. Qualification
must also cover the persistent coordinator loop, automatic communication and
visible failure/recovery. The historical design and authorization statements
below do not supply operational acceptance or a manual fallback.

Status: design only, requested by the owner after both original roles passed the corrected v29 source/artifact review. No lifecycle service, grant, enrollment, restart, native qualification or scene change is activated by this document. The frozen Design packages remain unchanged.

## Outcome and ownership

Machine should request a bounded replacement of an external project's agent through a typed project control interface. The project controller should establish custody, fence new work, retire the old managed session, launch the exact approved replacement and return durable evidence. Routine steps inside an admitted operation should continue automatically; a technical failure should retain the operation and its authority rather than require another ordinary dispatch approval.

| Owner | Responsibility |
| --- | --- |
| User/domain authority | Approve the consequential lifecycle scope, source/configuration, budget and adoption boundary. |
| Machine | Project/thread bindings, assignment and operation journal, exact request delivery, evidence collection, independent verification and progress. |
| Project lifecycle controller | Enforced admission, role ownership, quiescence, process custody, allowlisted launch configuration, recovery and project readiness publication. |
| Native role harness/provider | Enforce the turn-admission fence and cooperative session lifecycle; supply actual session/process/turn receipts. |
| Model | Perform the admitted agent task through its harness and report results. Model text cannot acknowledge process retirement, mint a lease or authorize adoption. |

Machine stores references and coordination evidence. Blender source, project runtime records, scenes and assets stay in Blender_Project. The initial Machine inspection coordinator remains inspection-only until this additional adapter is implemented, independently verified and explicitly activated.

## Observed chain and missing behavior

The existing native queue delivers to an exact registered CLI thread. The harness assembles context, invokes the model, checks its generated tool requests, executes tools and returns results. Actual completed turns prove that the original Brainstorm and Modeling sessions processed the source reviews.

The reviewed `qualification_admission.compose_role` returns the exact canonical working directory, existing session launcher and staged receipt/role/thread/resume/endpoint/store environment. It does not retire or launch a session. `session_onboarding --launch` executes Codex in its calling attended environment. The current app launcher omits the staged admission envelope and supplies no complete exact-role replacement transaction. An app-server `notLoaded` status does not prove that an attended role has stopped.

The Terminal UI tool refused access. The lifecycle route therefore needs a qualified native/project control interface; it must not depend on UI keystrokes, Terminal scripting, model instructions to quit, or an undisclosed execution migration.

Three receiving-layer gaps matter: supported retirement/launch custody, a real turn-admission fence, and publication of canonical readiness from the completed onboarding evidence. Configured-baseline startup also needs a supported fixed read-only preservation path; the current staged route rejects its arbitrary durable submission. No baseline is created or replaced to get around that limit.

## Typed interface

Proposed operations are `inspect`, `prepare_replacement`, `commit_replacement`, `observe_operation` and `reconcile_operation`. These are interface names to implement, not commands available today. There is no arbitrary shell, caller-supplied executable, environment map or generic process-kill operation.

A replacement envelope binds schema version, operation UUID, project/worktree identity, original role and thread UUID, expected role generation, controller/provider identity, source release and manifest digest, launch-profile digest, managed terminal/session/descriptor binding digest, owner-decision reference, independent review references, original qualification criteria and an absolute deadline. The terminal binding comes from verified native custody, never a caller-selected terminal path. Project-specific scene/endpoint/preservation bindings travel as a pinned project scope whose interpretation remains with the project executor.

The controller constructs argv and an allowlisted environment from its reviewed launch profile. It preserves the existing account, model/developer configuration, canonical workspace, attended execution and original UUID. It rejects source/configuration drift, unsupported fields, expired or revoked decisions, wrong roles and requests whose grant does not cover the effect. A registered path, successful message delivery or session initialization supplies none of that authority.

The first bounded local implementation may use the explicitly documented operator/host trust boundary and independently sealed owner decision. It must not label that as cryptographic authentication. Same-UID file ownership or a nonce alone does not isolate principals. A production unattended capability requires the applicable authenticated scoped-grant provider to be separately implemented and qualified.

## Ownership and enrollment

Managed roles run under a project-owned supervisor in the existing attended execution environment. Its lifecycle record binds the project, role, original thread, generation, provider instance, controller-owned child handle, process identity, launch/configuration digests and control endpoint. It also freezes the actual inherited controlling terminal device, session/process-group identity, foreground relationship and standard descriptors. The persistent entry retains that same terminal/session/descriptor binding across managed replacements. The native provider supplies a custody acknowledgement before the role is available for work. Machine imports the verified receipt rather than manufacturing that ownership from a thread observation.

Today's unmanaged roles remain explicitly unmanaged. A future bootstrap must establish a supported native-harness cooperative retirement/enrollment capability. Fresh completed tool receipts and narrow role-owned process observations can contribute evidence, but a title, stale onboarding record, PID/start pair or model statement cannot by itself authorize retirement. A check followed by a raw signal must not be described as an atomic identity guarantee.

The initial qualification uses disposable managed-role fixtures. Legacy enrollment is a separate integration acceptance gate. Inheriting today's unmanaged terminal/session/descriptors is not established by the inspected primitives. If a qualified bootstrap instead requires a new managed terminal, that initial binding change requires its own explicit owner scope and evidence; receipt editing or terminal attachment cannot fake inheritance. Until the native enrollment primitive and custody are proven, the controller reports `enrollment_unsupported` and changes no existing role. No duplicate session is launched on the same thread to evade enrollment. The owner's choice is automated control; manual Terminal work is not the default fallback.

## Replacement protocol

| State | Required evidence and next transition |
| --- | --- |
| `requested` | Machine commits the exact request and delivery intent before sending it. |
| `prepared` | Controller validates admission and exact generation, acquires the project/role lease, then the native harness acknowledges a fence against new turns and deliveries. Existing queued IDs and active work are retained. |
| `quiesced` | Actual harness evidence proves the current turn completed, queue state is reconciled and project operations/restorations/preservation are settled. Observed idle alone is insufficient. |
| `retire_intent` | Controller durably records the exact managed child and retirement request before the effect. |
| `retired` | Owning supervisor confirms cooperative exit and reaping of its direct role child. Adapter descendants require cleanup/reaping receipts from their actual parent or qualified native provider; the wrapper cannot claim it reaped grandchildren. A signal acknowledgement or missing process is not the completion receipt. Unknown descendant custody blocks launch. |
| `launch_intent` | Controller freezes the replacement profile and generation and records a single launch intent before the effect. |
| `started` | Native provider acknowledges the exact launch instance, thread, source/configuration and owned child. Launch acknowledgement does not award readiness. |
| `verified` | Actual completed onboarding turn, loaded adapter identity, original ordered checks and preservation evidence satisfy the project gate. Controller publishes canonical readiness from these same receipts. |
| `committed` | Exact project evidence is sealed; Machine records independent acceptance and releases the dispatch fence under the admitted policy. |
| `outcome_unknown` | Effect or custody is uncertain. Retain operation, lease/fence, launch nonce and all receipts; inspect and reconcile before another effect. |

The controller must serialize replacements across all callers at the receiving boundary. Machine's ledger lock alone cannot prevent another caller from launching a duplicate. The native harness must enforce quiescence; a launcher wrapper or a prompt asking the model to stay idle cannot close the admission race.

Each operation ID permanently binds one request digest. A duplicate returns the retained operation with no new effect; changed inputs under that ID reject. A durable journal precedes each retirement or launch. This supplies explicit recovery, not an exactly-once guarantee for external effects. A lost launch response is reconciled against the provider's exact instance receipt without a host process census or a second launch.

The absolute deadline never renews after coordinator/controller replacement. At expiry, stop new effects and collect submitted receipts. Preserve unknown custody. Configuration rollback does not reconcile an uncertain process or scene result. A separately admitted restoration may resume the preserved previous profile only after the replacement is definitively stopped and relevant state is settled; never blindly restart both versions.

## Blender integration

Use the existing source review, qualified admission and role-composition contracts. The controller consumes canonical sealed actual PASS reports, not an agent's completion claim. The v29 source/artifact reviews and 135-test pass remain valid evidence for that exact source; changed launcher/controller integration needs its own reviewed release and validation.

For a separately approved native qualification, retain the original selected target and role UUIDs, obtain fresh narrow binding/custody evidence, run guarded startup, then stage Brainstorm followed by Modeling. Each initial onboarding turn performs capabilities, path and objects with empty arguments exactly once in order. Its capability result supplies loaded-source evidence. Publish `ready_roles` only after validating those same completed turn receipts; do not queue an extra refresh sequence to obtain the flag.

Require distinct adapter process identities, unchanged source/target, settled recovery state and eligible preservation. A configured baseline whose fixed staged verification path is unavailable blocks loading. The proposed maximum 900-second native budget and applicable shorter receipt freshness rules remain separate from this design work. No native clock starts here.

## Implementation slices and acceptance

1. Implement and independently review the versioned lifecycle records, receiving-controller protocol and fake owned-child provider in isolated fixtures. Prove wrong project/thread/generation, missing ownership, changed profile, expired authority and duplicate IDs cause no effects.
2. Qualify fence/retirement/startup custody in managed fixtures. Race two callers, inject interruption before/after each external effect, lose acknowledgements, crash the coordinator/controller and reuse a simulated PID. Require retained uncertainty and zero duplicate launches or stray retirement.
3. Implement the native provider through a documented permitted harness control surface. Qualify unmanaged enrollment separately; retain a concrete capability gap if the installed native harness cannot provide cooperative retirement and turn fencing.
4. Integrate allowlisted qualified role composition and canonical readiness publication. Test missing qualification variables, wrong loaded source, duplicate reads, queued work during quiescence, failed preservation and retained unknown guards. Do not import Blender or game content into Machine.
5. Add Machine's typed adapter and recovery view. Preserve the existing inspection operation and transport history; no generic shell or automatic adoption endpoint is introduced.
6. After independent source review and the exact owner activation decision, qualify the real attended lifecycle route against its frozen version. Then resume native adapter qualification and the original castle task. A fixture pass, design seal or source review cannot award that native result.

These slices are the proposed implementation order. The owner's current instruction authorizes this design; it does not activate the new controller or permit live retirement/loading. The next implementation assignment should own an isolated candidate, declared files, meaningful checks and a concrete independently reviewed activation boundary.
