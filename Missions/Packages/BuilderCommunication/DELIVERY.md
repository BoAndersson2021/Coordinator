# Mission delivery settings — installer template

Fill this file in the target repository. Replace every placeholder and record
unknown limits as unverified; this template is not an active mission setting.

| Setting | Mission value to establish |
| --- | --- |
| Repository root | `<absolute target repository root>` |
| Artifact root | `<repository-relative evidence directory>` |
| Run directory | `<artifact root>/<unique UTC run ID>/` |
| Full report | `<run directory>/<assignment ID>-report.json` |
| Assignment artifact | `<run directory>/<assignment ID>-request.json`, when needed for transport size limits |
| Tool route | `<supported send and collection tools>` |
| Request limit | `<observed/documented UTF-8 byte limit, or unverified>` |
| Inline reply budget | `<conservative UTF-8 byte budget including envelope>` |
| Coordinator access | `<same filesystem or existing authorized retrieval route>` |
| Write scope | `<how assignments authorize evidence writes and bound their paths>` |
| Retention | `<ignored local evidence vs committed/published evidence, and handover references>` |
| Qualification | `<not_run, pass, fail or not_proven; run identity and evidence>` |

```text
Full report written once to its assigned run path
    |
    v
Compact JSON completion: identity + outcome + path + SHA256 + limits
    |
    v
Coordinator collects completed turn, reads report and checks hash
    |
    +--> Complete and matching: assess the evidence
    +--> Truncated / missing / mismatch: collection remains incomplete
```

Assignments must name this delivery policy and authorize the specific evidence
directory or file writes needed. A source-read-only task may allow report writes
without permitting source edits; state that distinction explicitly. If no file
writes are authorized, report the constraint instead of creating artifacts.

Do not overwrite earlier reports or consume an unverified partial JSON response.
When recovering a truncated message, retain its incomplete status, reference the
original message ID, and collect a compact replacement with an authorized report
artifact. Identify reserialization rather than claiming a byte-exact transcript.
Do not rerun completed gameplay or investigation merely to collect its report.

Record the installed package source revision/dirty identity, date and relevant
evidence for the settings. A directory existing or being ignored by Git does not
prove delivery, durability, write authority or publication.
