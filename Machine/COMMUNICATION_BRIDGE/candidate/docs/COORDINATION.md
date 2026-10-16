# Inspection coordination contract

## Ownership and execution

Machine's first operating slice is read-only repository inspection. Its SQLite ledger owns coordination records. External repositories own their source and instructions; project executors and domain owners retain their permission and adoption boundaries.

The request chain is user intent, recorded assignment, verified thread target, pending delivery journal, Codex thread message, target harness context assembly, model response or tool request, harness permission checks, tool execution, returned tool results, completed report, independent inspection review, and coordination closure.

Machine can emit a transport envelope for a bridge operator using the existing `codex_tui` thread tools. The [native inspection bridge](NATIVE_BRIDGE.md) also supports explicit direct queue delivery and response collection through a configured existing local project route. Both preserve projects with attended embedded Codex terminals. Neither moves agents onto another execution server, replaces their local adapters, or introduces API-key model calls.

## State and integrity

State lives under `.machine/`, outside Git tracking. Explicit `init` creates the directory with mode 0700 and the SQLite file with mode 0600. SQLite transactions use full synchronization and full-fsync where supported. Domain records, evidence bytes, operation identities, and their event records commit in one local transaction.

This is a single-host local ledger. Its hash chain detects inconsistent record, operation, and evidence edits against the retained journal; it is not a signature or protection against an operator rewriting the entire database. The durability boundary is SQLite and the host filesystem. Power-loss durability beyond that boundary and multi-host replication remain unqualified.

Every record declares schema version 1. Unsupported state versions are rejected without implicit migration. Mutation operation UUIDs bind exact request inputs. A repeated committed operation returns its retained response with `replayed: true`; dispatch replays also return `dispatchable: false`. Changed inputs under the same operation ID are rejected.

Task transitions require the current version. SQLite writer serialization and version preconditions prevent two coordinators from dispatching the same prepared task. An interrupted uncommitted transaction is rolled back by SQLite recovery. An already committed pending delivery remains unresolved after replacement.

## Records

| Record | Meaning |
| --- | --- |
| Project | Exact external Git worktree root, common Git directory, observed revision, owner label, supported inspection operation. |
| Agent | Thread UUID, named server boundary, observed workspace/status/time, and retained observation digest. |
| Task | Requester and authorization assertion, read-only brief, source context digests, HEAD, pinned `AGENTS.md` and `README.md`, target, version, and delivery attempts. |
| Receipt | Attempt, task, thread, server, observed delivery outcome, tool provenance, and detail. |
| Report | Completed turn identity, source tool, matching task/attempt/target, and scoped final report body. |
| Review | Exact report digest, revision, reviewer identity assertion, observations and file digests for both pinned inputs, and verdict. |

Authorization assertions and imported observations are supplied by the local operator. This version does not authenticate principals, sign receipts, validate arbitrary grant schemas, or enforce a target thread's operating-system sandbox. External project tasks support only inspection. A separate [bounded admission store](ADMISSION.md) permits one exact disposable scratch initialization; it does not enable project mutations.

## Read-only commands

`./Machine`, `status`, `doctor`, `task-show`, `evidence-show`, `work-view`, and `--help` do not create coordination state or dispatch. `task-show --id TASK` reads a complete task; `evidence-show --sha256 DIGEST` retrieves a retained observation, receipt, report, or review. `bridge-collect` never sends but can persist observed delivery reconciliation and a completed report; it is not a read-only command.

`doctor` pins the three normative corpus documents, contextual position, bootstrap manifest, capability inventory, three communication snapshots, and the studio intent/value documents. It verifies hashes, not the full semantics of YAML contracts or runtime compliance.

## Explicit write commands

All commands return JSON. Coordination mutations require a canonical `--operation-id` UUID except initial creation. The separate scratch executor consumes an already-issued permit UUID instead. Generate one for each new operation and retain it with the assignment; never change an uncertain operation's identity to evade recovery.

```sh
./Machine init --owner OWNER
./Machine project-register --id PROJECT --repo /absolute/external/repo --owner OWNER --operation-id UUID
./Machine agent-bind --id AGENT --project PROJECT --observation observation.json --operation-id UUID
./Machine task-prepare --id TASK --project PROJECT --agent AGENT --brief "Summarize repo purpose and entry points." --requested-by OWNER --authorization "User authorized bounded read-only inspection" --operation-id UUID
./Machine task-dispatch --id TASK --expected-version 1 --operation-id ATTEMPT_UUID
```

The target must be an exact Git worktree root with an existing HEAD. Agent observations must be no more than five minutes old and have a matching working directory. Dispatch rechecks the observation, repository identity, HEAD, context digests, and both pinned file hashes. The prompt must fit the current 1,000-byte thread-tool limit; an oversized prompt is rejected before a pending attempt is committed.

An observation has exactly these fields:

```json
{
  "schema_version": 1,
  "thread_id": "TARGET_UUID",
  "server_id": "EXPLICIT_SERVER_BOUNDARY",
  "cwd": "/absolute/external/repo",
  "status": "idle",
  "observed_at": "2026-10-13T20:00:00+00:00",
  "source": "codex_tui.list_threads"
}
```

`agent_identity_handshake` is also a supported observation source when the task listing omits workspace metadata. Verify the returned directory; a guessed directory or stale title is insufficient. Server identity is an explicit operator binding, not inferred global visibility.

`codex_local.read_thread` records observation through a project's existing native control route. Its envelope selects `codex_queue`, which must target the registered attended terminal through that route. A `notLoaded` app-server observation alone cannot authorize resuming the task through app-server messaging. Native queue admission may still reject a stopped terminal; preserve its outcome rather than starting a replacement or migrating execution.

`notLoaded` describes app-server loading, not whether an attended embedded terminal is open. The live Blender pilot processed its native queue while the app server continued reporting `notLoaded`. Use the current project role registry, native route, and exact matching execution turn; do not infer terminal liveness or failure from that status alone.

## Delivery and recovery

The normal sequence is `prepared → delivery_pending → delivered → reported → verified/rejected → closed`. Recording pending delivery precedes external send. After interruption, status flags both `delivery_pending` and `recovery_required` as requiring reconciliation. No background process retries either state.

```sh
./Machine task-acknowledge --id TASK --expected-version 2 --operation-id UUID --attempt-id ATTEMPT_UUID --evidence receipt.json
./Machine task-report --id TASK --expected-version 3 --operation-id UUID --evidence report.json
./Machine task-verify --id TASK --expected-version 4 --operation-id UUID --evidence review.json
./Machine task-close --id TASK --expected-version 5 --operation-id UUID
```

A delivery receipt has exactly `schema_version`, `task_id`, `attempt_id`, `thread_id`, `server_id`, `outcome`, `source`, and `detail`. Acknowledgement requires `outcome: delivered`. Source is `codex_tui.send_message_to_thread`, native `codex.queue`, or thread reconciliation through `codex_tui.read_thread` or `codex_local.read_thread`. Preserve the actual response in the bounded detail; do not manufacture success from a timeout.

Use `task-uncertain` with the matching attempt and a reason when outcome is unknown. Use `task-reconcile` with retained evidence and `--outcome delivered` or `not_delivered` after establishing the outcome. Non-delivery requires thread reconciliation provenance and affirmative evidence; a missing message in an incomplete page does not prove absence. The tool provenance is an operator assertion, so the bridge operator must perform that check. Confirmed non-delivery returns the task to prepared; another dispatch still needs an explicit new operation and current target checks.

Transport is not assumed to be idempotent. A pending journal and disabled automatic retry prevent blind local repetition; they do not prove exactly-once delivery or external execution.

## Replacing an attended session

When the project's registered role moves to a new thread, preserve the original task and agent record. Do not silently overwrite a binding or send another copy while its previous queued message can still execute.

Register the replacement as a new agent identity with a fresh native workspace/server observation. For an accepted but unreported native queue submission, `task-replacement-begin` validates a `thread/queue/list` observation against the original message UUID, target, attempt, and exact prompt digest. It journals the removal intent and enters `replacement_pending` before any external removal. This state requires reconciliation and blocks dispatch after interruption.

Only remove the exact owned pending submission through `thread/queue/delete`. This cannot be substituted with interrupting a turn, deleting a conversation, or inferring non-execution from a partial history page. If removal is rejected, uncertain, or reports `deleted: false`, preserve the journal and send nothing to the replacement.

`task-replacement-finish` requires the matching operation and an exact `deleted: true` receipt. It retains the old attempt and reconciliation evidence, records the old/new identities, and returns the same task to prepared under the replacement. Dispatch then rechecks the original pinned inputs and a fresh target observation. A new send requires a new attempt UUID; the task identity, scope, requirements, and prior history remain intact.

```sh
./Machine task-replacement-begin --id TASK --expected-version VERSION --new-agent REPLACEMENT --evidence queue-observation.json --operation-id REMOVAL_UUID
# Perform the exact native queue removal once; retain its actual response.
./Machine task-replacement-finish --id TASK --expected-version NEXT_VERSION --replacement-operation-id REMOVAL_UUID --evidence removal-receipt.json --operation-id UUID
```

The queue observation has exactly `schema_version`, `task_id`, `attempt_id`, `thread_id`, `server_id`, `queued_submission_id`, `prompt_sha256`, and `source: codex_local.thread/queue/list`. The removal receipt has exactly `schema_version`, `task_id`, `attempt_id`, `thread_id`, `server_id`, `queued_submission_id`, `replacement_operation_id`, `source: codex_local.thread/queue/delete`, and `response: {"deleted": true}`. Both remain operator-supplied custody records under the local trust model.

Queue inspection/removal use the installed CLI's generated protocol schemas and a narrowly constrained native control client. The connection opts into the documented experimental protocol capability; this changes neither model execution, credentials, billing, nor the receiving agent's tool permissions. See the [official app-server initialization contract](https://learn.chatgpt.com/docs/app-server).

## Reports and independent inspection review

A report has exactly `schema_version`, `task_id`, `attempt_id`, `thread_id`, `server_id`, `turn_id`, `turn_status`, `source`, and `body`. It must reference the matching attempt/target, a canonical turn UUID, `turn_status: completed`, and source `codex_tui.read_thread` or `codex_local.read_thread`. Retain the final scoped report rather than the entire conversation. Acknowledgement and an unfinished turn cannot be attached as completed inspection.

A review has exactly `schema_version`, `task_id`, `report_digest`, `revision`, `reviewer`, `checks`, and `verdict`. Each check has `file`, `sha256`, and `observation`. Cover both pinned files; actual bytes must still match. The reviewer identity must differ from the executor's binding and thread UUID. Owner identity and independence are declared by the operator, not authenticated by this version. The reviewer reads the report and source, evaluates its claims, and supplies meaningful observations; matching hashes alone do not assess prose correctness.

Inspection verification and closure authorize no source adoption, scene acceptance, build, or release. An independent review may reject the report while preserving its receipts and evidence.
