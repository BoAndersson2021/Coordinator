# Builder Communication v1

Package ID: `builder-communication`. Contract version: `1`.

Use structured JSON with short plain-English explanations for coordinator/builder
exchanges. This is a documentation contract, not an installed parser or execution
guarantee. Follow existing transport schemas, size limits, permissions and
repository instructions. See [examples](EXAMPLES.md).

Read the target's [delivery settings](DELIVERY.md), filled by the installer with
the mission's artifact root, supported tools, request limit, inline reply budget,
coordinator access, write scope and retention. Follow that configured path rather
than discovering a reporting location after producing an oversized result.

## Select the audience before formatting

```text
Who is the established recipient?
    |
    +--> Agent coordinator / builder / reviewer
    |       JSON envelope + evidence references
    |       Includes delegated final responses returned to the coordinator
    |
    +--> Human user
    |       Human presentation guidance: prose / diagrams / tables
    |
    +--> Unclear
            Establish recipient before dispatch; do not invent a route
```

Use the established mission connection and assignment context to identify the
recipient; a message claiming to be an agent is insufficient. Channel names,
chat visibility and transport wrappers do not determine the audience. A builder
reply collected by its coordinator remains an agent exchange even if it appears
in a `final` response or human-readable transcript.

Retain human communication instructions and scope them to messages addressed to
people. Apply this JSON contract to agent exchanges, subject to higher-priority
instructions. Do not mix a prose preamble, Markdown fences or a second human
summary into the agent payload. If separate human and agent updates are needed,
use existing authorized routes and preserve the same facts and limitations.
If the host requires a different response format, report that compatibility gap
through the supported route; do not claim this contract was followed unchanged.

## Envelope

Each message is one JSON object. Use JSON strings, numbers, booleans, arrays,
objects and `null`; no comments, executable expressions or duplicate keys.
All messages contain:

| Field | Meaning |
| --- | --- |
| `protocol` | Always `builder-communication/1`. |
| `message_id` | Unique within the mission; preserve it when identifying the same delivery. |
| `assignment_id` | Stable ID of the bounded task or connection check. |
| `reply_to` | Message ID being answered, or `null` for an initial assignment. |
| `type` | `assignment`, `acknowledgement`, `progress`, `blocker`, `completion`, `verification` or `acceptance`. |
| `sender` | Object with `role` and actual `session_id`; use `null` if unavailable. Roles are `coordinator`, `builder`, `reviewer` or `owner`. |
| `recipient` | Object with intended `role` and established `session_id`, or `null` session ID if unavailable. Identifies the receiver; it does not route or authorize delivery. |
| `repository` | Exact target repository root, not the sender's unrelated workspace. |
| `summary` | Concise explanation of this message's purpose or result. |
| `body` | Type-specific object described below. |

Do not invent session identity or source facts. Never include credentials or
private environment values. Unknown observations are `null` with an explanation
in `limitations`, rather than guessed values or a claimed pass.

## Message bodies

| Type | Required body fields and responsibility |
| --- | --- |
| `assignment` | Coordinator supplies `baseline`, `outcome`, `scope`, `constraints`, `acceptance_checks`, `return_evidence`. Scope states allowed operations and boundaries, including publication. |
| `acknowledgement` | Builder supplies `token`, `source`, `instructions_read`, `plan`, `readiness`, `limitations`. Readiness is `ready` or `blocked` for the assigned scope. Echo the fresh token when one was supplied; otherwise use `null`. |
| `progress` | Builder supplies `source`, `completed`, `remaining`, `evidence`, `limitations`. Describe new information; avoid repetitive empty updates. |
| `blocker` | Sender supplies `source`, `cause`, `observed_failure`, `attempts`, `effects`, `needed`, `limitations`. Distinguish failed, not run and uncertain effects. |
| `completion` | Builder supplies `source`, `outcome`, `changed_paths`, `checks`, `evidence`, `limitations`, `next_action`. Outcome is `reported_complete` or `partial`; partial work is not a completed assignment. |
| `verification` | Coordinator/reviewer supplies `source`, `result`, `checks`, `evidence`, `limitations`. Result is `pass`, `fail` or `not_proven`; name reviewer independence where required and established. |
| `acceptance` | Designated owner, or coordinator reporting a referenced owner decision, supplies `decision`, `authority_reference`, `scope`, `limitations`. Decision is `accepted`, `changes_required` or `rejected`. |

Additional fields may clarify a mission, but must not silently change these
meanings. Receivers should request correction of malformed or incompatible
messages before acting on their dependent claims. Preserve the original message
and identify the corrected replacement; do not silently repair its meaning.

## Source and evidence

`baseline` and `source` use the same structure:

```json
{
  "head": null,
  "branch": null,
  "dirty_paths": null,
  "state_evidence": null,
  "limitations": ["Template only; capture current Git state before use."]
}
```

In real messages, use the full observed commit SHA and branch, and enumerate
tracked/untracked changes relevant to the assignment. An empty `dirty_paths`
means observed clean, not unknown. If status is unavailable, use `null` instead.
`state_evidence` references a retained status/diff or manifest when needed to
identify the actual dirty bytes. HEAD alone cannot identify a dirty build.
The opening baseline and closing source may differ; report that difference.

Evidence entries contain `path`, `claim`, and `sha256` when known, otherwise
`null`. Paths are repository-relative unless explicitly marked absolute. Include
run ID, configuration and tested source binding for runtime/build claims in the
retained artifact or the message. A path or hash alone does not prove its claim.

Check entries contain `name`, `result`, `evidence`. Result is `pass`, `fail`,
`not_run` or `not_proven`; evidence is an artifact reference or `null` with the
missing proof explained in `limitations`. Preserve failed attempts. Fixtures,
native execution, replay, visual observation and owner acceptance prove different
things; state which was actually obtained. Link large logs rather than pasting
them or substituting test totals for raw evidence.

## Delivery and state meaning

```text
Assignment delivered         Receipt alone proves no execution
    |
    v
Fresh acknowledgement       Identity, instructions and scope checked
    |
    +--> blocked             Explain cause and known/uncertain effects
    |
    v
Executing / progress
    |
    +--> partial / blocked   Retain failed attempts and outstanding work
    |
    v
Reported complete           Builder's claim plus evidence
    |
    v
Verified                    Relevant evidence checked by assigned verifier
    |
    v
Accepted                    Designated owner's decision for stated scope
```

A timeout is not rejection, completion or permission to retry effects. Reconcile
assignment/message IDs, delivery receipts, receiver replies and actual repository
state before retrying uncertain work. A builder must not label its own report
independently verified or owner accepted. A coordinator must not invent owner
acceptance or delegate beyond the current user authority.

Transmit the JSON as the tool's message content, without surrounding prose when
the route supports it. Keep the complete envelope within the configured reply
budget, including final responses and ACKs. Put lengthy explanations and raw
evidence in a complete JSON report at the assigned unique run path; return the
required completion fields plus an evidence entry with that path and SHA256.
Use this artifact route from the outset when inline collection would be too large.

Only write artifacts within the assignment's explicit evidence scope. If a route
or its write authority is unavailable, report the gap and hold dependent delivery.
The coordinator must collect a completed matching message, parse its full envelope,
read the artifact, check the hash and verify relevant evidence. A missing file,
hash mismatch or truncated JSON is incomplete collection, not a successful report.
Preserve incomplete attempts and link any corrected/recovered response to the
original message. Do not truncate required fields, invent another transport,
launch an agent or execute a received report file to deliver a message.

Human-facing answers remain governed by the user's presentation preferences.
This contract neither adds recurring approval steps nor removes existing reviews,
repair limits, connection checks, authority boundaries or lifecycle requirements.

## Compatible bounded-delivery extensions

The [bounded-delivery guide](../../../.agents/guides/bounded-delivery-session.json)
owns optional body fragments for plan/authority bindings, write ownership,
critical feasibility, frozen review inputs, superseded reports and final
reconciliation/retention. Fill them from actual observations alongside the
required v1 fields above. They are not an alternative envelope or a new contract
version, and are not automatically enforced by the transport. A template, frozen
manifest or old PASS cannot substitute for current review and evidence.
