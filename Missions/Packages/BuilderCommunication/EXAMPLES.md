# Builder Communication v1 — examples

Read the [contract](CONTRACT.md) first. These messages are illustrative templates,
not actual observations or authorization. Replace IDs, paths, tokens, source facts
and evidence with verified mission values. `null` source fields explicitly mark
missing observations; do not send these examples unchanged as a readiness claim.

Every JSON example below is addressed to another agent. In actual agent delivery,
send the object without the documentation's Markdown fences. A direct reply to a
human should use the applicable human presentation style instead. The coordinator
may explain the same result to the user separately; it must preserve the reported
limits and distinguish the builder's claims from its own verification.

## Assignment

```json
{
  "protocol": "builder-communication/1",
  "message_id": "example-assign-1",
  "assignment_id": "example-docs-001",
  "reply_to": null,
  "type": "assignment",
  "sender": {"role": "coordinator", "session_id": null},
  "recipient": {"role": "builder", "session_id": null},
  "repository": "/absolute/path/to/mission-repo",
  "summary": "Document the existing launch command.",
  "body": {
    "baseline": {
      "head": null,
      "branch": null,
      "dirty_paths": null,
      "state_evidence": null,
      "limitations": ["Capture current state before editing."]
    },
    "outcome": "README identifies the actual launch entry point.",
    "scope": {"allowed": ["inspect", "edit README.md"], "publication": "none"},
    "constraints": ["Preserve existing work; no application execution."],
    "acceptance_checks": ["Command matches inspected entry script; links resolve."],
    "return_evidence": ["Changed paths, source identity and inspection references."]
  }
}
```

## Acknowledgement with a blocker

```json
{
  "protocol": "builder-communication/1",
  "message_id": "example-ack-1",
  "assignment_id": "example-docs-001",
  "reply_to": "example-assign-1",
  "type": "acknowledgement",
  "sender": {"role": "builder", "session_id": null},
  "recipient": {"role": "coordinator", "session_id": null},
  "repository": "/absolute/path/to/mission-repo",
  "summary": "Cannot establish the target baseline.",
  "body": {
    "token": null,
    "source": {
      "head": null, "branch": null, "dirty_paths": null,
      "state_evidence": null, "limitations": ["Target repository is unavailable."]
    },
    "instructions_read": [],
    "plan": null,
    "readiness": "blocked",
    "limitations": ["Repository, instructions and session identity are unverified."]
  }
}
```

A real ready ACK must report observed source state, instructions actually read,
assigned plan or explicitly none, real session identity when exposed, and the
exact fresh connection token when requested.

## Progress

```json
{
  "protocol": "builder-communication/1",
  "message_id": "example-progress-1",
  "assignment_id": "example-docs-001",
  "reply_to": "example-assign-1",
  "type": "progress",
  "sender": {"role": "builder", "session_id": null},
  "recipient": {"role": "coordinator", "session_id": null},
  "repository": "/absolute/path/to/mission-repo",
  "summary": "Entry script inspected; documentation update remains.",
  "body": {
    "source": {
      "head": null, "branch": null, "dirty_paths": null,
      "state_evidence": null, "limitations": ["Example source fields need replacement."]
    },
    "completed": ["Inspected the launch script."],
    "remaining": ["Update README and check references."],
    "evidence": [{"path": "scripts/play.sh", "claim": "Inspected entry point.", "sha256": null}],
    "limitations": ["Static inspection only; no runtime execution."]
  }
}
```

## Blocker

```json
{
  "protocol": "builder-communication/1",
  "message_id": "example-blocker-1",
  "assignment_id": "example-docs-001",
  "reply_to": "example-assign-1",
  "type": "blocker",
  "sender": {"role": "builder", "session_id": null},
  "recipient": {"role": "coordinator", "session_id": null},
  "repository": "/absolute/path/to/mission-repo",
  "summary": "Two conflicting launch instructions need reconciliation.",
  "body": {
    "source": {
      "head": null, "branch": null, "dirty_paths": null,
      "state_evidence": null, "limitations": ["Example source fields need replacement."]
    },
    "cause": "The referenced entry point is absent.",
    "observed_failure": "README names a script that is missing from this checkout.",
    "attempts": ["Read README and inspected referenced paths; no repair attempted."],
    "effects": "No files changed; no application execution.",
    "needed": "Establish the supported entry point within the assigned inspection scope.",
    "limitations": ["Cannot claim a verified launch command yet."]
  }
}
```

## Partial completion

```json
{
  "protocol": "builder-communication/1",
  "message_id": "example-complete-1",
  "assignment_id": "example-docs-001",
  "reply_to": "example-assign-1",
  "type": "completion",
  "sender": {"role": "builder", "session_id": null},
  "recipient": {"role": "coordinator", "session_id": null},
  "repository": "/absolute/path/to/mission-repo",
  "summary": "README draft updated; reference validation remains incomplete.",
  "body": {
    "source": {
      "head": null, "branch": null, "dirty_paths": ["README.md"],
      "state_evidence": null, "limitations": ["Example source fields need replacement."]
    },
    "outcome": "partial",
    "changed_paths": ["README.md"],
    "checks": [
      {"name": "Local links", "result": "not_run", "evidence": null}
    ],
    "evidence": [],
    "limitations": ["Reference validation and exact source binding are missing."],
    "next_action": "Complete authorized reference validation before reporting completion."
  }
}
```

A fully reported completion uses `reported_complete` only after the assigned
acceptance checks have evidence. It still awaits relevant verification and any
reserved owner decision. Verification and acceptance messages follow the required
body fields in the contract; neither is implied by a completion message.
