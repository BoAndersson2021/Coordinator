# CodeExp2 session lessons build plan

Revision 3, 2026-10-19. The approved revision 2 dependency order is preserved. **Status: COMPLETE within the approved bounded scope. All stages, final native/visual walkthroughs, independent source/admission review, exact staged-source checks, local policy adoption and second-reader continuity passed.** Original points 1 through 6 retain their identities. Point 4 is split into an early evidence foundation and later runtime qualification.

The intended result is one usable CodeExp2 control path: inspect the actual receiving agent, perform explicitly authorized work, recover uncertain delivery without blind replay, show evidence within its tested scope, review visual alternatives and produce a reliable continuation record.

PANEL remains owner-ended. Its native chat, agent-status and notices slice is a future consumer after explicit resumption. This workspace work does not resume PANEL or grant product dispatch authority. The reviewed shared client and development policy adoption are recorded below; historical planning checkpoints retain their original scope.

## Baseline and implementation boundary

The accepted [mission start and close design](../Missions/CONTROL_WORKFLOW_PROPOSAL.md) remains the lifecycle baseline. These improvements supply bounded connection and reporting components for it. Complete mission routing, publication automation, native executor admission fencing and process-tree retirement remain outside these six items. A completed turn or empty background-terminal list cannot establish executor exit.

| Observed input | Reuse candidate | Qualification limit |
| --- | --- | --- |
| [Scoped client](../Missions/BallisticsExperimental/host-control-20261019/native_host_control.py), [regressions](../Missions/BallisticsExperimental/host-control-20261019/test_host_control.py) and [dependency declaration](../Missions/BallisticsExperimental/host-control-20261019/requirements.txt) | WebSocket connection, receiver checks, persisted dispatch identity and restoration patterns | Source inspected at CodeExp2 `ceeb9fc`; mission-specific bindings remain intact. Inspection does not qualify a generalized client. |
| [PANEL verification](/Users/boandersson/Desktop/PANEL/Evidence/Protocol/panel-protocol-350bb55681d1/VERIFICATION.json) and [manifest](/Users/boandersson/Desktop/PANEL/Evidence/Protocol/panel-protocol-350bb55681d1/MANIFEST.json) | Dated managed-session stream, operation, approval and recovery evidence | Codex 0.163.0 diagnostic scope only. Existing standalone TUI attachment, native approval UI and unattended automatic review were not established. |
| [Visual decision record](../Missions/PanelToBo/VISUAL-REVIEW.json) and [PANEL closure](../Missions/PanelToBo/README.md) | Stable alternatives, accepted composition, artifact lineage and continuation point | Design acceptance and owner-ended status remain separate from runtime qualification. |

Coordinator Odin (actual session `01a15430-7ddb-7f60-809e-a8443e7b9e1d`) owns this workspace implementation, tests, fixtures and continuation. The owner authorized every remaining step with “Execute all steps and dont seek my sub level approval. Go to end of plan then report”. No target-repository builder or product assignment was introduced. Source, instructions, HEAD and unrelated dirty work were rechecked; independent reviewer `/root/native_control_review` owns no implementation files. Preserve other instances' work and the existing index. Delegation requires an authorized route and the [Builder Communication contract](../Missions/Packages/BuilderCommunication/CONTRACT.md), including a fresh matching completed ACK before product assignments.

## Red team findings and corrections

These are defects found in the first plan, not claims that the proposed runtime has been tested. This is a Coordinator review, not independent implementation review.

| Finding | Severity and failure scenario | Correction in revision 2 |
| --- | --- | --- |
| F01 Evidence foundation arrived late | High: earlier steps produce incompatible records, and later qualification cannot reconstruct their scope. | Build the minimal point 4a record first; execute point 4b qualification after recovery. |
| F02 No concrete usable entry point | High: libraries and passing unit tests could satisfy every item while the Coordinator still cannot run the workflow. | Define one proposed client entry and a complete operator walkthrough with explicit success criteria. |
| F03 Deduplication omitted concurrent controllers | High: two clients can both read pending and both send a decision. An atomic file replacement alone does not serialize them. | Hold one OS-managed operation lock per canonical backend/receiver across cooperating clients; reconcile durable intents after takeover. State the limit against other native consumers. |
| F04 Request correlation was underspecified | High: reconnect may reuse or change wire IDs; one item can receive distinct requests. | Separate connection-local RPC identity from a proven logical approval binding. Uncertain correlation never authorizes a resend. |
| F05 Recovery could mistake incomplete history for certainty | High: a bounded search finds one match but misses another or a missing page; disk failure loses intent before a send. | Require complete relevant history or a native unique lookup, persist intent before send and exercise crash/storage failures. Unknown stays unresolved. |
| F06 Status and ACK bootstrap could mislead | High: a socket or idle record looks ready; requiring a prior ACK even for the readiness exchange creates a cycle. | Separate transport, receiver, task, request and dispatch eligibility. Authorize the bounded onboarding/ACK exchange separately from product dispatch. |
| F07 Approval authority and closure races were incomplete | High: reconnect reuses a stale decision, or a queued approval is sent after owner end. | Bind decisions to current authorized action and actor; record end intent before further sends and reconcile in-flight effects. |
| F08 Proof integrity could be confused with sufficiency | High: a matching hash, marker file or nearby binary is treated as proof of the actual backend or exactly one effect. | Require endpoint binding, native outcomes and operation-specific evidence; hashes establish byte identity only. |
| F09 Visual work was unnecessarily serialized | Medium: independent review templates wait for runtime qualification; fixture selection looks like owner acceptance. | Point 5 branches after 4a; synthetic choices are labeled fixtures, with readable labels, zoom and a durable accepted-asset route. |
| F10 Completion and evidence handling were too vague | High: a clean-looking summary hides pending work, logs grow without bound or private frames enter publication. | Add bounded private evidence, explicit unresolved effects, restart checks and a separate release walkthrough. |

## Correct dependency order

```text
4a Evidence and scope foundation
 |
 +--> 2 Transport --> 1 Receiver and eligibility --> 3 Recovery --> 4b Qualification
 |                                                                    |
 |                                                                    v
 +--> 5 Visual review -----------------------------------------------> 6 Closure
       independent build track                           visual input only when relevant
```

| Stage | Original point | Prerequisites | Completion result |
| --- | --- | --- | --- |
| 4a | 4 — Evidence foundation | Bounded inventory and authorized scope | Minimal records, limits and fixtures agreed; no new framework. |
| 2 | 2 — Transport | 4a | Installed supported connection and initialization actually pass. A useful failure is diagnostic progress, not transport completion. |
| 1 | 1 — Receiver and status | 2 | Exact receiver and current dispatch eligibility are distinguishable from stored metadata. |
| 3 | 3 — Recovery | 1 and 4a | Cooperating clients cannot blindly repeat uncertain sends or approval decisions. |
| 4b | 4 — Runtime qualification | 2, 1 and 3 | Requested operations have scope-matching evidence and current readiness. |
| 5 | 5 — Visual review | 4a only | Alternatives and accepted composition can be inspected and reopened. |
| 6 | 6 — Closure and continuation | 1, 3 and 4b; 5 for visual decisions | Actual known effects, unresolved effects and next action survive handover. |

**Main sequence: 4a → 2 → 1 → 3 → 4b → 6.** Build point 5 alongside that sequence after 4a. Draft the closure template early; its live-state acceptance waits for point 4b. A nonvisual task does not wait for point 5.

Current checkpoint: the full chain has been implemented through the single shared entry. The [delivery and continuity record](../Missions/ControlWorkflowEvidence/20261019-session-lessons-delivery.md) binds each stage to current evidence, independent review and adoption checks. Earlier preflight and 4a records remain historical, not proof of later source.

## Proposed delivery surface

Use one small shared client at `scripts/native_control.py`, focused regressions at `tests/test_native_control.py`, and two templates at `docs/templates/visual-review.md` and `docs/templates/task-closure.md`. These paths are implemented. `scripts/native_evidence.py` checks the 4a records and `scripts/native_qualification.py` owns the fixed diagnostics and transcript proof reader; they share the same bounded entry, not a mission runner.

The single entry exposes `preflight`, `status`, `reconcile`, `qualify`, `end` and `summary`, with an explicit binding input and evidence destination. `preflight`, `status`, `summary` and default `reconcile` observe only. Qualified effect paths accept a typed, scoped operation; they never expose arbitrary RPC or shell passthrough. `qualify` requires a validated disposable probe specification. Cancellation is an explicit owned-turn action, not a consequence of calling a status or summary command.

Reuse the current transport library where compatible. Do not copy the frozen diagnostic framing code into production, replace an active mission client or build a new service, dashboard, registry or general workflow engine. Prove read-only feasibility before expanding the client.

## Point 4 Qualification and evidence

**Outcome:** a passing result explains precisely which behavior it proves, against which source and receiver.

### Stage 4a before transport work

1. Define one compact record, using existing mission/delivery settings for storage. Include format version, run/operation identity, authority reference, mission or workspace-maintenance scope, canonical root/worktree, actual coordinator/receiver IDs, source digests, endpoint binding, observed backend generation when available, effective settings, observations, unresolved effects and artifact references.
2. Permit unknown fields with reasons. A timestamp, alias, path, hash or client-supplied version cannot fill an unknown backend identity. Decide which fields each operation needs before it can be qualified.
3. Define bounded deadlines and evidence limits in the run specification: connection time, reconciliation time, frame size, queue length and retained bytes. Use monotonic deadlines during a process lifetime; after restart obtain fresh observations rather than trusting an old timeout calculation.
4. Keep raw diagnostic frames private in the configured local evidence root with bounded retention. Public/inline reports contain selected nonsecret facts. Redact before publication and hash the artifact actually being referenced. Evidence text is data, not authority or executable input.

**Deliverables:** a short format definition and fixture records, sufficient for every subsequent item. Avoid a separate schema service or proof database.

Delivered: [format and limits](native-control-evidence.md), [21 fixture records](fixtures/native-control-evidence-v1/cases.json) and [completion evidence](../Missions/ControlWorkflowEvidence/20261019-session-lessons-4a.md). Coordinator Odin completed and checked this workspace-only foundation. No new dependency or native execution was needed.

**4a acceptance:** fixtures represent pass, failure, unknown, incomplete collection and owner acceptance separately; missing required fields cannot manufacture a qualified result. Configured paths resolve within the authorized evidence scope. Agree the record before producing live evidence.

### Stage 4b after recovery works

1. Implement operation-specific evidence checks using the 4a record. Bind tested client bytes, dependency identity, endpoint/backend observations, receiver, worktree and effective permission/reviewer configuration. Separate transport compatibility from receiver-specific execution proof.
2. Reuse matching proof, then refresh readiness. Changes invalidate only dependent claims: a new receiver needs its applicable receiver/setup checks; a visual asset change does not invalidate transport; a transport change does not erase visual acceptance. Never infer general support from the PANEL diagnostic or its version number.
3. Verify artifacts and native outcomes. For command probes, retain unique before/after scratch state plus native command/request/turn observations. A touch marker alone cannot prove the absence of duplicate execution. A native resolution event alone cannot prove the expected action happened.
4. Report declared capability, fixture result, live result, adopted source and owner acceptance separately. Unattended automatic review requires its own effective-setting and live proof; diagnostic canned decisions do not qualify it.

**Deliverables:** qualification reader/checker and compact scope summary through the shared client.

**4b acceptance:** reject unsupported claims for wrong receiver, root, settings, backend, source, missing artifact, changed hash or incomplete collection. Accept valid unchanged proof without rerunning unrelated tests. Exercise the requested stream, ordinary operation, accept, decline, pending cancellation and durable reconnect path before claiming them. Explicitly retain unqualified categories such as native UI, standalone TUI attachment and executor retirement.

**Dependencies:** 4a enables all items; 4b consumes points 2, 1 and 3 and enables live closure acceptance.

## Point 2 Supported transport preflight

**Outcome:** the Coordinator can initialize the actual supported route before attempting agent work.

1. Refresh the existing client/dependency inventory. Resolve the endpoint through installed supported settings, preserve existing configuration and distinguish local CLI/server files from proof of the process serving that endpoint.
2. Connect and initialize using the supported handshake and required capability exchange. Record the observed route and endpoint ownership/backend binding where available. If a needed binding cannot be established, report it unknown and hold only operations that require it.
3. Bound waits, frame size and buffering. On constructor failure, malformed message, timeout or budget exhaustion, close owned resources and return a useful error. Never silently drop an approval event or convert a partial stream into success.
4. Keep this path read-only with respect to agent work: no resume, launch, model turn, settings mutation or automatic fallback to another backend. Native access failures use the host's supported permission route.

**Deliverables:** executable `preflight` path, 4a evidence and transport regressions.

**Acceptance:** the installed authorized real route initializes successfully. Fixtures cover handshake rejection, inaccessible endpoint, wrong endpoint binding, incompatible initialization, malformed/oversized frames, queue overflow and initialization failure cleanup; all send zero work effects. Preserve the raw-JSON/WebSocket failure as a fixture rather than retrying that failed live strategy.

**Dependency:** 4a first; point 1 depends on successful real initialization. Stop an ineffective approach under [Delivery Discipline](delivery-discipline.md), continuing independent template work.

## Point 1 Actual receiver and truthful status

**Outcome:** saved history, transport reachability, agent work and permission to dispatch appear as separate facts.

1. Bind the registered mission or authorized workspace-maintenance task, canonical repository/worktree, exact receiver and backend. Preserve actual structured IDs and lowercase roles. Alias and color remain presentation metadata.
2. Implement `status` with the following independent fields and evidence timestamps. A native thread read is an observation, not proof of an executor's entire lifecycle.

| Field | Examples | Meaning |
| --- | --- | --- |
| Transport | connected, disconnected, unknown | This control connection's state. |
| Receiver | verified on this backend, saved `notLoaded`, unknown | Which receiver was actually observed here. |
| Task | active, idle, completed, failed, interrupted, unknown | Exact known turn/task state. Completion remains task-scoped. |
| Request | pending, resolved, uncertain, none observed | Approval or input request state within the observed scope. |
| Dispatch eligibility | eligible for named operation, blocked with reason | Current authority, ownership, setup and applicable completed ACK. |

3. Resolve ACK bootstrap explicitly. An authorized bounded onboarding/readiness exchange may obtain the first ACK through an already available approval/cancellation route. It is not product dispatch and does not require a previous ACK for itself. Product assignments require the fresh matching completed ACK plus all [required execution setup](../Missions/README.md#required-mission-execution-setup).
4. Recheck receiver/root, current scope, end intent and applicable settings before effectful dispatch. Invalidate eligibility on disconnect, changed backend/receiver or scope, expired readiness under the declared run policy, unresolved prior effect or ownership conflict. Do not resume a stored thread merely to display it as online.
5. Where the native interface cannot prevent a concurrent noncooperating actor from changing state after a read, qualify only the supported exclusive/cooperating-client scope. Do not claim that a local check is a native admission fence.

**Deliverables:** runnable `status`, receiver binding and dispatch eligibility checks in the shared client.

**Acceptance:** wrong receiver, sibling worktree, stale ACK, changed settings, prior end intent and lost connection cannot permit an effect. An initialized socket with a stored `notLoaded` thread stays visibly unloaded. An idle record without the required readiness/setup remains ineligible. A live read verifies an authorized managed receiver; standalone TUI attachment remains unproven.

**Dependency:** point 2; provides ownership/state inputs to points 3, 4b and 6.

## Point 3 Recovery without blind replay

**Outcome:** an uncertain reply or reconnect never silently turns into repeated work or a repeated approval decision.

1. Serialize cooperating controllers with one OS-managed operation lock keyed to canonical backend/receiver, independent of mission alias or config-file spelling; include operation ownership in the durable record. Hold it across reconciliation and send, with bounded acquisition. A new holder after a crash must reconcile outstanding intent before new work. A stale PID or unlocked file is not evidence that the previous effect did not happen.
2. Separate outgoing RPC identity by connection generation, direction and request ID from logical native approval identity. Correlate replay only through a proven backend/receiver/turn/item/action binding. If repeated approval rounds or changed IDs are ambiguous, mark unresolved rather than merging or resending. One event-consumption path handles a frame once; the raw log may honestly contain repeated deliveries.
3. Durably record operation identity, exact authorized action and send intent before sending. If that write fails, send nothing. Record acknowledgement and observed outcome separately. After a crash between intent and acknowledgement, use read-only reconciliation; never infer failure from missing local acknowledgement.
4. For a lost start response, use the persisted unique client-message identity and exact receiver/turn. Require complete relevant enumeration or a supported unique lookup. Truncated, unavailable, conflicting or ambiguous history remains unresolved; never dispatch again or interrupt guessed work.
5. Track decision intent, possible send, native resolution and action outcome independently. A send failure can leave its outcome unknown. If replay cannot be disambiguated through the supported interface, automatic recovery stops at that boundary. Do not promise exactly-once server execution.
6. Each approval requires a current authority reference for that exact action and a designated decision owner. A diagnostic command allowlist is not general approval authority. Use only an explicitly selected attended route or qualified native automatic review as applicable. Other native consumers remain outside the local lock; exclusive control must be established for claimed automatic behavior.
7. Collect late request-resolution events after turn completion within the declared bound. Reconcile gaps; a deadline reports uncertainty. Cancellation targets only the exact owned turn through the qualified route. Restore only settings this operation changed, after checking for intervening changes.

**Deliverables:** default read-only `reconcile`, guarded typed effect paths, minimum durable recovery state and cross-process/crash regressions.

**Acceptance:** meaningful tests cover two cooperating clients racing, callback-plus-queue replay, changed/reused wire IDs, distinct approval rounds, external resolution, late resolution, lost start response, incomplete pagination, crash before/after send, torn intent and disk-full failure. Observe at most one attempted send per proven logical dispatch/decision within the qualified client scope; report uncertainty when proof is unavailable. An authorized durable live test demonstrates pending reconnect, exact cancellation, final turn state and matching request resolution with the pending marker effect absent. Unresumable ephemeral history remains a visible limitation.

**Dependency:** points 1 and 4a; enables 4b. A local lock does not qualify native executor fencing or control over another application.

## Point 5 Reviewable visual alternatives

**Outcome:** the human can inspect alternatives, request a combination and reopen the exact accepted refinement later.

1. Build `docs/templates/visual-review.md` with stable option IDs, ordering, readable names, concise text descriptions, real dimensions, source/hash and supported viewing actions. Use existing artifact viewers or native Preview first. Add a tiny helper only for a demonstrated gap.
2. Check the assets actually render, support useful zoom and can be reached through the intended keyboard/viewer flow. Distinguish these review-surface checks from a full accessibility audit. If a tool denies a route, use an allowed viewing method without bypassing that restriction.
3. Record selection by stable option ID and hash, plus requested composition. Reordering alternatives cannot change an existing choice. A refinement has its own identity and references; it is not automatically accepted because its sources were accepted.
4. Record the owner's actual decision and scope. Save the accepted asset in the target's established design location within authorized write scope and link it from the native handover. Mark illustrative status as mock. Missing assets remain visible; generated scratch storage alone is insufficient.

**Deliverables:** template and a three-option fixture walkthrough using existing viewing tools. No image generation, new hosting service or PANEL design reopening is required.

**Acceptance:** a labeled fixture replays base option 3 plus sidebar from 1, preserves the choice after reorder and reopens the exact refinement from a durable fixture target. Missing/changed assets are detected. Synthetic decisions are never recorded as fresh owner acceptance. Demonstrate actual viewability and zoom; do not claim untested accessibility, UI behavior or graphics performance.

**Dependency:** 4a only. Visual decisions feed point 6 when relevant; transport problems do not block this package.

## Point 6 Reliable closure and continuation

**Outcome:** a new Coordinator can understand the checkpoint without the transcript and cannot accidentally restart owner-ended work.

1. Build `docs/templates/task-closure.md` and `summary` around [How to end a task](how-to-end-a-task.md). Include completed outcome, acceptance scope, evidence, source/dirty-work ownership, remaining limits, uncertain effects, known owned processes, publication state and one exact next action with prerequisites.
2. On an authorized owner-end action, immediately disable new sends in the receiving client, then record end intent durably under the same cooperating-client operation lock. Every cooperating sender checks it under that lock before sending. The persisted end boundary revokes unsent mission authority; sends that won the race before it remain possible in-flight effects. This provides no instantaneous fence over other native consumers. Read-only summary generation itself never cancels a turn, changes settings or ends a mission. If the end record cannot be persisted, block further sends in that client and expose cross-client end state as unresolved rather than report a reliable close.
3. Reconcile sends already in flight and pending requests through points 1 and 3. A pending approved action may already have happened; end intent cannot undo it. Use only qualified owned cancellation where authorized. Unknown effect or incomplete process inventory remains explicit and prevents a fully reconciled cleanup claim.
4. Keep separate fields for dispatch ended, task final, requests resolved, effects reconciled, publication and executor retirement. Preserve unknown values. For missions using the accepted lifecycle design, incomplete publication or retirement cannot become its fully `CLOSED` result. Owner-ended dispatch can still be recorded honestly with remaining effects listed.
5. Write product continuation in the native target and coordination links in its mission folder. Workspace-only work uses workspace documentation. Link point 5 decisions only for visual tasks. Never stop the shared daemon or unrelated work. A new Coordinator must re-establish ownership and scope; a reused alias or next-step sentence cannot resume an ended mission.

**Deliverables:** closure template, observation-only `summary` and client-local enforcement of recorded end intent through the existing operation guards. No complete lifecycle controller is added.

**Acceptance:** exercise clean completion, pending approval, end versus decision race, end persistence failure, uncertain in-flight send, lost connection, incomplete process inventory, partial publication and owner-ended state. A second reader locates the exact evidence and proposed continuation without the transcript. Reopening the records preserves ended dispatch and unresolved effects. Another mission's state and processes remain untouched. Native executor exit still requires its separate lifecycle proof.

**Dependency:** points 1, 3 and 4b for live acceptance; point 5 only for visual task input. The template can be drafted after 4a.

## Integrated acceptance and adoption

Run the real interaction through the proposed client entry, not only imported test functions. Use one explicitly authorized durable disposable receiver, a unique owned scratch root and the native approval/cancellation route available before the probe begins. Use the supported managed route; do not launch a replacement or resume a live standalone Terminal to make the test possible. If no eligible receiver/route exists, report the exact setup owner and missing capability, keeping live qualification unproven.

1. `preflight` initializes and `status` identifies the actual receiver and current eligibility without work effects.
2. A validated `qualify` run streams a unique chat response, performs the ordinary representative operation and exercises scoped accept, visible decline and pending cancellation. Retain native outcomes and scratch results. Test default read-only actions for zero mutations.
3. Break and restore the test connection while pending, invoke `reconcile` after restart and show no blind redispatch or repeated decision. Retain late resolution and any remaining uncertainty. Complete matching 4b claims only after checking the collected artifacts.
4. In a separate end-race case, record authorized end intent and verify that subsequent unsent decisions/dispatch are rejected, while possible prior effects are reconciled. `summary` reports the real state without causing cleanup itself.
5. Produce the handover, include the point 5 fixture result where relevant and have a fresh reader reconstruct state and the next action. Fixture decisions remain labeled synthetic. Do not require a fresh human design decision to test a template.

Release is complete for these six items only when the shared entry works through this walkthrough, meaningful failure regressions pass, required source adoption is recorded, both templates are usable and remaining unsupported categories are explicit. A failed real connection, only fixture passes or a blocked demonstration is partial delivery, not completion.

The [existing commit gate](commit-gate.md) still requires independent exact-byte review/adoption for executable/data inventory, meaningful mandatory staged-source regressions and applicable instruction changes. This Coordinator plan review cannot satisfy that future independent requirement. Use the normal hook; ordinary document/template changes receive lightweight content/reference checks. No commit, push, agent launch or runtime authority follows from this planning revision.

Apply the shared two-attempt repair limit to an unchanged integration blocker, carrying failed attempts forward. Continue independent useful work. Update affected dependencies and evidence here when facts change rather than adding another plan or governance system.

**Execution result:** every stage is implemented and its runtime/fixture scope is demonstrated. See the delivery record for final staged checks and local policy adoption. No implementation stage is deferred to another “next” approval. Future product use still requires the selected mission, exact authority, a fresh matching builder ACK and current receiver/setup checks. PANEL remains owner-ended.

## Preflight checkpoint

The owner approved the chain with “Ok chain approved. Preflight it”. Coordinator Odin's [2026-10-19 preflight](../Missions/ControlWorkflowEvidence/20261019-session-lessons-preflight.md) passed the bounded read-only feasibility check: dependency available, 12 existing offline regressions passed, matching native CLI/server 0.163.0, WebSocket initialization and exact own stored-thread read successful. The stored thread was `notLoaded`; no live Terminal attachment is claimed.

Native access required the host-approved route outside the default sandbox. No receiver was launched, resumed, assigned work or granted new settings. That one-shot diagnostic was not the proposed shared client and did not complete 4a. The later 4a completion is recorded above; at that historical checkpoint runtime implementation acceptance was still outstanding. Revision 3 and its delivery record now provide final source admission and owned diagnostic acceptance; PANEL remains owner-ended.

## Review and change record

- 2026-10-19 — First draft by Coordinator Odin preserved the six original points with serial order 2, 1, 3, 4, 5, 6. It was untracked and has no committed Git history. Its SHA256 before this revision was `ec64f6e397e926b492a8c3075468b5e4d91c10232646fbbf89714e0bdae23ef2`.
- 2026-10-19 — At the owner's explicit red-team request, revision 2 corrected F01 through F10 in the proposed design. Point 4 now has stages 4a and 4b; point 5 is independent after 4a. Added a concrete delivery surface, concurrency/crash/authority checks and integrated acceptance. These are plan fixes; runtime behavior remains unimplemented and unqualified under this plan. The accepted lifecycle baseline, existing mission code and owner-ended PANEL state are preserved.
- 2026-10-19 — Owner approved the revision 2 dependency chain and requested preflight. Read-only feasibility passed with dated evidence linked above; status updated without changing the approved sequence or marking implementation stages complete.
- 2026-10-19 — Owner instructed “OK execute next”. Coordinator Odin completed stage 4a as workspace documentation and synthetic fixtures: one format definition, explicit limits, 21 records and 23 passing content/filesystem checks. Point 2 is now next eligible; no native source, mission state or gate was changed.

## Revision 3 implementation and findings

The owner authorized the complete remaining chain. The implementation preserved one narrow real route and used private, owned saved diagnostics. The shared `preflight` and exact own-session `status` passed; the latter honestly reports `saved-notLoaded` and product-ineligible. Final `qualification-4` passed ordinary operation, nonce stream, scoped accept, decline, pending cancel and a different-process pending reconnect/cancel. Retained native frames, source snapshots, effective settings and loaded transport implementation are checked before historical proof reuse. All owned diagnostic dispatch is ended; final requests/effects reconcile, and the receiver is archived. No native executor-retirement claim is made.

Independent review found and fixed R1–R6: insufficient proof booleans, whole-run cleanup gaps, endpoint-swap effects, missing overall recovery deadline, unmeasured imported transport, and incomplete transcript workspace/permission/receiver validation. Final review and its whitespace-only exact-byte refresh passed the exact 13-file development inventory, unchanged trusted verifier, preserved prior policy requirements and one additional mandatory regression wrapper. The wrapper requires all 28 exact native-control offline regressions with native transport forbidden. These checks distinguish development adoption, historical native observations and current product readiness.

Point 5 rendered all three synthetic alternatives plus the option-3/sidebar-1 refinement in native Preview, with keyboard navigation and useful zoom. Source dimensions/hashes and stable choice after reorder pass; no fresh owner design acceptance or full accessibility result is invented. Both templates are populated by the fixtures and this delivery/continuation record. No browser UI, hosting service, native executor admission framework or full lifecycle runner was added.

- 2026-10-19 — Revision 3 records authorized implementation, two independent repair reviews and final repaired-byte PASS. `qualification-1` and `qualification-2` remain historical earlier-byte diagnostics; `qualification-3` is also historical after the EOF whitespace correction; only final `qualification-4` binds the delivered source. Final staged-source verification and local adoption are linked in the delivery record. The original six outcomes and revision 2 dependency chain remain unchanged.
