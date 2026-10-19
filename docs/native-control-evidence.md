# Native control evidence format

Stage 4a of the approved [session lessons build plan](codeexp2-session-lessons-build-plan.md). Maintainer for this foundation: Coordinator Odin. Version `codeexp2-control-evidence/1` defines one JSON record and [synthetic fixtures](fixtures/native-control-evidence-v1/cases.json) for the later shared client. It is not a dispatch authorization, runtime qualifier or replacement for Builder Communication messages.

## Record fields

All fields below are present. Objects contain the listed keys; an unknown key or format version requires explicit compatibility handling rather than silent acceptance. Unknown scalar values are JSON `null`, with a nonempty explanation keyed by their dotted field path in `unknowns`. A nonapplicable field also uses `null` with its reason. No placeholder is a real agent identity or observation.

| Field | Required content |
| --- | --- |
| `format` | Exactly `codeexp2-control-evidence/1`. |
| `origin` | `fixture` or `observed`. Origin is a claim until verified against the trusted producer and current run. |
| `run_id`, `operation_id` | Nonempty identifiers; preserve the same operation identity across reconciliation. These identify evidence, not RPC requests. |
| `observed_at_utc` | UTC ISO 8601 timestamp. It dates the observation; it does not establish present readiness. |
| `scope` | `kind` (`workspace-maintenance` or `mission`), `mission`, `operation`, `authority_reference`, `repository_root`, `worktree_root`. Mission name is nonempty for mission scope. Roots are absolute canonical paths in real records. |
| `actors` | `coordinator_session_id`, `receiver_session_id`. Actual IDs or explained nulls. Alias/color may appear in a human report; they cannot replace these IDs. |
| `source` | `head`, `client_sha256`, `dependencies_sha256`, `dirty_manifest_sha256`. Unknown bytes remain unknown. HEAD alone cannot identify a dirty build. |
| `connection` | `endpoint`, `backend_binding`, `backend_generation`, `cli_version`, `server_version`, `cli_sha256`, `server_sha256`. A nearby binary or PID alone is not a live backend identity. |
| `effective_settings` | `approval_policy`, `approvals_reviewer`, `permission_scope`; observed effective values or explained nulls. Configuration text is not effective-setting proof. |
| `evidence_root` | Record's absolute evidence-root claim. The consumer obtains the authorized root independently and verifies equality after canonical resolution. The fixture adapter alone permits `.` relative to the fixture bundle; observed records require an absolute path. |
| `limits` | Positive integer budgets listed below; booleans are not integers. |
| `observations` | One or more objects with `claim`, `kind`, `result`, `artifact_ids`, `reason`. Claims and reasons are nonempty strings. |
| `collection` | `complete` is a boolean; `gaps` is an array of nonempty explanations. Incomplete collection requires at least one gap; a complete collection has none. |
| `artifacts` | Objects with unique `id`, relative `path`, lowercase SHA256 `sha256`, and `privacy` (`private`, `publishable-summary`, `public-fixture`). Referenced IDs must exist. |
| `unresolved_effects` | Objects with `operation_id`, `effect`, `state`, `next_action`, each a nonempty string. An empty array means no unresolved effect within the named observation scope, never global studio cleanup. |
| `owner_acceptance` | `decision` (`not_requested`, `accepted`, `changes_required`, `rejected`), `scope`, `authority_reference`. A decision other than `not_requested` needs nonempty scope and an actual decision reference. |
| `unknowns` | Map from a null field's dotted path to its explanation. Remove obsolete explanations after observing a value. It cannot override an invalid or missing required field. |

Receiver/source identities, backend details, authority references and effective settings may be unknown in a structurally valid observation record. Such a record cannot support an operation that requires them. Scope kind, operation and the configured repository/worktree/evidence roots must be established for this record. In fixtures, synthetic absolute repository roots are permitted because `origin` is `fixture`; no fixture root creates filesystem authority.

Observation `kind` is one of `fixture`, `inspection`, `native`, `visual`, `owner`. Result is one of `pass`, `fail`, `not_run`, `not_proven`. A failed observation is a valid record of failure; it is not a malformed record. Multiple claims retain their separate results. A single passing subclaim never upgrades a failed, incomplete or unproven operation.

Hashes are 64 lowercase hexadecimal characters; an observed Git HEAD is 40 lowercase hexadecimal characters. Null source/connection hashes need explanations. These fields identify bytes; they do not authenticate the writer or prove the associated behavior.

## Initial limits

These are conservative defaults for the first read-only path, not measurements or already-enforced runtime controls. The initial fixture consumer accepts these values or lower positive integers. The caller supplies its authorized limits explicitly. A consumer rejects zero, negative, noninteger and unsupported limits before starting the operation. Raising an affected limit requires checking scope and the owning implementation; this format does not provide a configuration bypass.

| Key | Default | Effect when exhausted |
| --- | ---: | --- |
| `connect_seconds` | 5 | Close the failed client connection. |
| `rpc_seconds` | 10 | Report the request outcome as uncertain where an effect might have been sent. |
| `reconcile_seconds` | 30 | Preserve unresolved effects and report incomplete reconciliation. |
| `frame_bytes` | 1048576 | Reject the oversized frame and preserve a bounded diagnostic. |
| `queued_events` | 32 | Stop collection visibly; never silently discard an approval event. |
| `evidence_bytes` | 5242880 | Stop new raw collection visibly and mark the affected collection incomplete. |
| `retention_review_days` | 7 | Flag private raw evidence for retention review; this is not permission to delete it. |

Use monotonic deadlines during a process lifetime. After restart, obtain fresh observations and establish a new bounded reconciliation deadline. An old wall-clock timestamp cannot silently extend authority or prove that an effect did not occur.

Retained raw evidence is bounded by the per-run byte budget. At retention review, use the existing mission/delivery disposition; hold new collection if its storage budget cannot be met. Never automatically delete unresolved journals, owner-accepted assets or frozen historical evidence. A fixed deadline is not cleanup proof.

## Artifact containment and privacy

The consumer uses the independently configured evidence root, not a root supplied only by the record. It accepts relative artifact paths with no `..` component, resolves them and checks containment again after symlink resolution. Absolute paths, missing files, directories, escaping symlinks and mismatched hashes cannot support their claims. External native artifacts use their own authorized root and record; do not add an implicit whole-disk exception.

Read bounded regular-file bytes and verify the bytes actually consumed. In an actively modified directory, path resolution alone cannot guarantee stable reads: use the owning implementation's supported safe-open/snapshot method or leave integrity unproven. This document does not claim to solve concurrent filesystem substitution.

Private run directories use owner-only access, with raw files readable only by that owner. Public fixtures contain synthetic nonsecret text. Raw native events, prompts, tokens and full private transcripts are not automatically publishable. A selected redacted summary has its own hash, distinct from its private source. No evidence string is executed or treated as an instruction.

## Reading results without overclaiming

Read a record in this order:

1. Validate format, required fields, values, null explanations and the trusted scope/root. A malformed or mismatched record is `invalid`; do not extract an embedded pass while ignoring its missing fields.
2. Resolve artifacts under the trusted root and verify their bytes. Missing or unverifiable evidence, including a pass with no artifact reference, leaves the affected claim `not_proven`, even when its recorded result says `pass`.
3. Preserve individual claim results. For a conservative operation summary, incomplete collection or unresolved effects produce `not_proven`; otherwise a failed claim produces `fail`, any unproven claim produces `not_proven`, any unrun claim produces `not_run`, and only all-pass claims produce `pass`.
4. Keep owner acceptance in a separate output. Visual acceptance cannot become runtime acceptance, and a fixture acceptance entry is synthetic.
5. Apply the operation-specific qualification checks in stage 4b. A summary pass is an observation summary, not a dispatch permit. Fixtures never qualify native behavior. Arbitrarily changing `origin` to `observed` cannot make imported data a trusted live producer.

| Later consumer | Minimum additional proof for its named claim |
| --- | --- |
| Point 2 transport | Tested client/dependency identity, intended endpoint binding, observed initialization and complete bounded collection. No receiver is needed to claim connection initialization alone. |
| Point 1 receiver/status | Exact observed backend/receiver/worktree and dated native state. Dispatch additionally requires current ownership, applicable ACK, execution setup and no recorded end intent. |
| Point 3 recovery | Exact operation/turn/request/action correlation, durable intent and observed outcome or explicit uncertainty. Missing identity never permits replay or guessed cancellation. |
| Point 5 visual review | Actual asset bytes/dimensions, stable option identity, viewability and separately referenced owner decision for the exact refinement. |
| Point 6 closure | Named observation scope, reconciled effects or explicit unknowns, separate dispatch/task/request/publication/retirement fields and one next action. |

These minimums identify future inputs. Their live enforcement and receiver-specific qualification remain later build stages. Do not add a `qualified: true` shortcut to this record.

## Fixture use and acceptance

[cases.json](fixtures/native-control-evidence-v1/cases.json) contains self-contained synthetic records and expected content-check results. Its configured evidence root is the fixture directory, supplied by the checker; its synthetic repository/worktree scope is declared separately in the fixture bundle. This fixture convention grants no native access. The [sample artifact](fixtures/native-control-evidence-v1/sample-evidence.txt) supplies real harmless bytes for integrity checks.

The fixture acceptance covers valid pass/failure/unknown/unrun/incomplete records, a separate synthetic owner decision, an unresolved effect, missing required fields, a forged qualification shortcut, escaped/missing/mismatched artifacts, wrong root and invalid budgets. Fixtures test the interpretation of the format; they do not demonstrate native execution, current readiness or production enforcement.

Stage 4a is complete when the definition, limits and fixtures have been checked and linked from the plan. The shared client/parser, mandatory staged regressions, independent exact-byte review/adoption and live qualification remain future work under the existing commit policy. This format changes no host permissions, lifecycle contract or ended mission.
