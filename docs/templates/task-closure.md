# Task closure and continuation

Task and scope: `<named task/mission or workspace maintenance>`.
Coordinator and implementation owner: `<aliases plus actual session IDs when observed>`.
Source and dirty-work ownership: `<commit, exact tested bytes, owned changes, excluded shared work>`.

**Done:** `<usable outcome, checks and evidence within their actual scope>`.
**Remaining:** `<unfinished behavior, unknowns and uncertain effects>`.
**Next:** `<one exact proposed action, actor and prerequisites; mark owner-ended work as requiring explicit resumption>`.

| State | Observation and dated evidence |
| --- | --- |
| Dispatch ended | `<yes/no/unknown; durable end intent reference>` |
| Task final | `<exact turn and final state, or unknown>` |
| Requests resolved | `<pending/resolved/uncertain, scoped IDs>` |
| Effects reconciled | `<known effects, uncertain sends and reconciliation action>` |
| Owned processes | `<inventory scope, remaining processes or incomplete inventory>` |
| Publication | `<not requested, local only, partial or verified remote SHA>` |
| Executor retirement | `<verified exit proof or not proven; never infer from turn completion>` |

Accepted decisions: `<scope and actual owner reference; include visual lineage only when relevant>`.
Canonical native handover: `<target path; workspace-only tasks may use this workspace's continuation document>`.
Evidence: `<durable paths and hashes; private raw logs stay private>`.

An observation-only summary does not cancel or end anything. An authorized end action records end intent before subsequent cooperating-client sends, then reconciles in-flight work. Unknown effects stay visible. Ending one mission does not affect another, close the shared daemon or prove executor retirement. A handover never resumes an ended mission by itself.

For bounded agent-to-agent closeout, use the optional structured fragments in
the [bounded-delivery guide](../../.agents/guides/bounded-delivery-session.json)
inside the existing communication envelope. This human-facing template and its
lifecycle observations remain applicable; source freeze/review and final
reconciliation do not establish process retirement or publication.
