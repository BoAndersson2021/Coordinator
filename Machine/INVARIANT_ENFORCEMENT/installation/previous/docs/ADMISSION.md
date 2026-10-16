# Bounded agent admission

This increment addresses the live onboarding gap: a Machine agent could inspect the repository but had no recorded route for accepting the owner's delegated scratch initialization. Session startup still grants no work. External project coordination remains inspection-only.

The local operator explicitly records one owner decision and a fresh observation of an existing idle Machine thread. `session-admit` binds the coordinator and target UUIDs, Machine root, one existing canonical scratch directory below `/private/tmp`, its device/inode, initialization owner, source context, and five implementation/instruction file hashes. The decision expires within 15 minutes. This is a local operator assertion, not an authenticated principal, signed grant, or hostile same-user isolation. `CODEX_THREAD_ID` and matching `CODEX_SESSION_ID` supply process identity; the CLI accepts no actor override. A same-user operator can modify files or environment. Harness permissions remain authoritative.

## Commands and exact scope

```sh
./Machine session-admit --observation /absolute/observation.json --owner-decision /absolute/decision.json --operation-id ADMISSION_UUID
./Machine permit-issue --admission-id ADMISSION_UUID --operation-id PERMIT_UUID
./Machine permit-inspect --permit-id PERMIT_UUID
./Machine permit-execute --permit-id PERMIT_UUID --request /absolute/Machine/.machine/admission/PERMIT_UUID.request.json
```

Admission and issuance are coordinator operations. Inspection is read-only and reports eligibility for the current process. Execution is permitted only for the recorded receiving thread and exact immutable request. The receiving model may inspect the local record and request; the other-thread message is a pointer, never the authority itself. Once these checks pass, the receiving agent may invoke this exact command under the owner's recorded scope without asking for duplicate task approval. A platform permission rejection must still be honored. This exception authorizes only initialization in the recorded scratch directory. It grants no project registration, claiming, builds, role replacement, source adoption, general shell execution, or game work.

The receiving harness assembles context, evaluates the model's tool request, and runs the CLI within its execution environment. The CLI verifies local admission, durably consumes the permit, directly calls the existing `Ledger.initialize` for the recorded directory and owner, and returns JSON. The model does not execute code by itself. The executor does not accept a command, executable, environment, or arbitrary arguments.

## Input records

Observation has exactly `schema_version: 1`, `thread_id`, `server_id`, `cwd`, `status: "idle"`, `observed_at`, and `source: "codex_tui.read_thread"`. The bridge operator must actually obtain this observation; the source label alone is not proof. Observation age is at most five minutes. `cwd` is the exact Machine root; server identity is explicitly recorded local custody.

Owner decision has exactly these fields:

```json
{
  "schema_version": 1,
  "kind": "scratch_init_admission",
  "owner": "OWNER_FROM_EXISTING_LEDGER",
  "owner_quote": "Owner's actual authorization for this bounded test",
  "machine_root": "/absolute/Machine",
  "coordinator_thread_id": "COORDINATOR_UUID",
  "target_thread_id": "TARGET_UUID",
  "scratch_root": "/private/tmp/test/studio",
  "init_owner": "BehaviorTest",
  "issued_at": "2026-10-14T00:00:00+00:00",
  "expires_at": "2026-10-14T00:15:00+00:00"
}
```

The operator records the owner's authorization faithfully; the CLI cannot authenticate a quote. Issued time must be no more than five minutes old, timezone-aware, and not future. The scratch directory must already exist, belong to the current OS user, contain the same verified source context, and contain no `.machine` entry. Symlink paths and overlap with live Machine are rejected. Existing direct `init` remains the explicit local owner setup command; this gate adds bounded delegation, not whole-system write mediation.

## Durability and recovery

Admission state is a separate private store under `.machine/admission`; existing SQLite state is not migrated or rewritten. Startup and permit inspection create nothing. Mutating admission commands can create the private store/lock even if later rejected. A process lock serializes admission, issuance, and execution. Checksums detect inconsistent retained bytes, not a hostile operator's rewrite. Files are written privately, synchronized, and atomically replaced; host filesystem durability beyond those operations remains unqualified.

Admission/issuance operation UUIDs bind exact inputs and return retained results on replay; changed inputs reject. Admission replay still requires fresh input records. One decision cannot be renamed to create another admission; an admission gets one permit. Issuance reserves its operation before publishing a fixed request filename. A crash in `issuing` remains blocked; replay never publishes again. The bridge records a pending delivery before sending and retains the real transport result; an acknowledgement is not execution. Neither the CLI nor the bridge automatically resends or retries uncertain work.

Execution records `executing` before initialization. Success records the returned result as `succeeded`. Exceptions record `outcome_unknown`; process interruption or a result-persistence failure can leave `executing`. All these states consume the permit. Recovery consists of inspecting retained state and scratch effects, never rerunning with that permit or changing its UUID to evade the unresolved result. A second attempt always rejects, even after success. At most one initializer entry is established under the local lock; exactly-once completion across crashes is not claimed.

Scope, actor, expiry, source/profile drift, request byte drift, scratch replacement, and existing scratch state are checked before consumption. This is the only enabled mutation adapter and remains a disposable initialization test. Native role lifecycle and authenticated scoped grants are separate unimplemented work.
