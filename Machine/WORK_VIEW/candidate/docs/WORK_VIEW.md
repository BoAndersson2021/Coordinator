# Work state explanation in the CLI and dashboard

`./Machine work-view` and the managed dashboard now use the same core
`work_observation` projection. They distinguish delivery custody, unestablished
live execution, historical completion/review evidence and original evidence time.
Reading a ledger now does not establish that an executor is running now.

`work-view` remains structured JSON, reports the failed workflow invariant on
stdout/stderr, and exits 3. Each task exposes:

| Field | Meaning |
| --- | --- |
| `workflow_status` | `blocked` while automatic workflow providers remain unqualified. |
| `delivery_status` | `not_attempted`, `uncertain`, or `receipt_retained`; receipt custody is not execution. |
| `execution_status` | `not_established`; this local view makes no live-agent observation. |
| `completion_status` | `no_completed_report` or `historical_report_retained`. |
| `verification_status` | `not_reviewed` or `historical_review_retained`; see the separate historical verdict. |
| `evidence_at` | Original last-record/creation timestamp, never the current read time. |
| `evidence_freshness` | `historical_record`, or `unknown` when evidence time is absent; never a live-runtime claim. |

Readable delivery/receiver descriptions, attempts and exact attempt identity,
ledger state/version, report/review flags and historical verdict remain included.
Top-level counts and scope match the dashboard. `observed_at` timestamps the ledger
read only. The next-state explanation reports the missing system capability rather
than instructing a person to collect/relay messages as a workflow step.

The bridge CLI preserves its previous task identifiers, state fields and explicit
retained report access. Dashboard JSON uses only the safe shared projection and
never exposes those report bodies. Neither display contacts agents, starts or
stops executors, dispatches, collects replies, writes task state, or awards review.
The existing managed dashboard remains automatically supervised and refreshed.

Meaningful equality/no-effect coverage is part of the already mandatory dashboard
invariant test: real CLI output and HTTP snapshots must agree about a queued task
without a live receiver and preserve its original time and database bytes. Other
tests cover historical report/review flags and missing evidence. All new/edited
features remain governed by `MACHINE_AUTOMATED_EXECUTION_REQUIRED`; no workflow
allow branch, provider qualification or manual fallback is introduced.
