# How to work on WEBSITE as a CodeExp2 agent

This mission is registered in [the mission index](../README.md#registered-missions).
Load this guide after explicit selection; its state applies only to this mission
and does not select, stop or replace any other ongoing mission.

Use this guide for authorized coordination of the standalone
`/Users/boandersson/Desktop/WEBSITE` repository. CodeExp2 owns this mission guide
and reusable instructions; the verified WEBSITE builder owns assigned target
documentation, implementation and evidence. The user owns scope and acceptance.
This guide does not select a product task, launch a server or authorize publication.

Read [current coordination state](HANDOVER.md) for the latest dated reconnect
result and its limits; recheck receiving readiness rather than treating it as
permanent liveness.

For `Mission END WEBSITE` / `END MISSION WEBSITE`, follow the accepted
[close sequence](../CONTROL_WORKFLOW_PROPOSAL.md#corrected-close-chain): native
handover, owned staging, target-first publication and separate retirement proof.
Preserve pre-existing dirty work and reconcile every commit a push would publish.
These are conversational entries; no shell mission runner is installed. Record
native approval waits, partial publication and unverified retirement explicitly.

At the 2026-10-18 close, the user approved archival and coordinator takeover
of a stalled staging request, then publication of the close and thirteen older
commits. WEBSITE remote main was verified at `d79c4d4038a69d2bcb539ae7406d32852b98735a`.
See the current handover for receipts, preserved dirty work and the unresolved
native process-retirement limit. A saved archived thread needs fresh receiving
readiness before future work.

## Native WEBSITE onboarding comes first

Read the target's [AGENTS.md](../../../WEBSITE/AGENTS.md),
[README.md](../../../WEBSITE/README.md), [Handover.md](../../../WEBSITE/Handover.md),
[site factory workflow](../../../WEBSITE/infra/SITE_FACTORY.md) and
[documentation maintenance rules](../../../WEBSITE/infra/DOCUMENTATION_MAINTENANCE.md).
Apply applicable ancestor instructions, including [Desktop AGENTS.md](../../../AGENTS.md).
Inspect any actual startup script before running it. Do not replace the target's
onboarding, governance, start procedure or handover with this guide or the package.

```text
Enter WEBSITE and reconcile current request / Git / native handover
    |
    v
Follow its own scoped onboarding and required entry checks
    |
    v
Read the installed agent communication contract and delivery settings
    |
    v
Fresh identity/readiness ACK to CodeExp2
    |
    v
One bounded assignment within native repository governance
```

At the 2026-10-18 setup, no repository `start.sh` or standalone onboarding harness
was found. Native entry was the root documents above plus the applicable Desktop
read-only `desktop-frontdoor run-system` check, which returned READY. Respect any
Janus router-owned startup exception in current Desktop instructions. Do not
invent a start script or automatically run README examples such as `npm ci`,
browser installation or a dev server to manufacture onboarding completion.
Reinspect current instructions rather than assuming this observation remains true.

Also read CodeExp2 [AGENTS.md](../../AGENTS.md), [README.md](../../README.md),
[continuation state](../../Mission_Sofar.md) and
[Delivery Discipline](../../docs/delivery-discipline.md). Apply the
[coordinator guide](../../docs/how-to-coordinate-with-a-builder-agent.md) before
delegation, the [plan guide](../../docs/how-to-follow-and-refresh-a-plan.md) before
executing/editing an assigned plan, and the
[runtime-target guide](../../docs/how-not-to-overengineer.md) for implementation
toward running software. Preserve WEBSITE's own governance and proof contracts;
Machine's installed runtime state is not adopted by this mission.

## Inspect and preserve the actual baseline

```sh
website_repo=/Users/boandersson/Desktop/WEBSITE
git -C "$website_repo" rev-parse --show-toplevel
git -C "$website_repo" status --short --branch
git -C "$website_repo" rev-parse HEAD
git -C "$website_repo" diff --stat
git -C "$website_repo" diff --cached --name-only
git -C "$website_repo" log -5 --oneline
git -C "$website_repo" remote -v
```

Opening setup HEAD was `d4af3dfe8f42ed2c404523e369f6d13ee9694780`, branch `main`,
thirteen commits ahead of recorded `origin/main`. There were **34 existing dirty
paths**, including root AGENTS/Handover and a broad documentation audit. The
index was empty. These are dated local observations, not fresh remote status.
Preserve the audit and unfinished work; do not reset, stash, reformat or commit
them merely to install the communication package. Keep the WEBSITE index separate
from CodeExp2 and Desktop Git.

Snapshot relevant opening files/status before additive edits. During installation,
root AGENTS is extended and a current handover section added while preserving
the original content. Existing unrelated dirty files retain their bytes. Do not
quietly resume a stopped thread's old implementation or publication request.

## Start or reconnect to the repository agent

Follow the [mission startup procedure](../README.md#start-a-new-repository-agent-when-authorized).
Discover an existing appropriate executor first. When a new Terminal session is
explicitly authorized, validate WEBSITE and the installed Codex executable, open
Terminal there, and pass the native-onboarding task as Codex's initial positional
prompt. Do not inject a prompt after Codex starts or override model/account/trust.

On 2026-10-18 the user explicitly authorized opening Terminal, changing to the
repository and starting Codex. The coordinator opened one attended session using
`/Users/boandersson/.local/bin/codex`, without a model/permission override. The
known first task required WEBSITE's own onboarding and a unique completed ACK.
Old WEBSITE sessions were inspected for context and left unchanged.

| Role | Recorded thread ID | Expected repository |
| --- | --- | --- |
| CodeExp2 coordinator | `01a14b70-e481-7e13-9cb1-6d5f0d0e814a` | `/Users/boandersson/Desktop/CodeExp2` |
| New WEBSITE builder | `01a15088-a22b-72e1-ab5b-ef34cc3e799b` | `/Users/boandersson/Desktop/WEBSITE` |

Lifecycle update, 2026-10-18: the user reported manually terminating the WEBSITE
Terminal. A subsequent read-only `read_thread` for the exact builder above still
reported `idle`, with its last installation turn `completed`. This observation
does not establish an attached Terminal or verified executor retirement. Treat
the old Terminal connection as ended by user report; do not send work to the
saved thread or relaunch it without the applicable readiness and launch checks.
This was manual termination, not completion of the proposed automatic END
MISSION sequence. No close-time publication or automated shutdown was performed.

These are rediscovery hints, not live readiness. Use current supported
`mcp__codex_tui__list_threads`/`read_thread` tools to reconcile exact identity and
repository. Send a fresh unique orientation token with no implementation work;
collect a completed matching ACK through `wait_threads` and inspect the actual
response. Verify native instructions read, cwd/root, current source, outstanding
work, assigned plan or none and readiness scope. A Terminal window, old ACK,
thread title or delivery receipt is insufficient.

## Installed communication and report path

The [reusable package](../Packages/BuilderCommunication/README.md) is installed
under WEBSITE's shared-infrastructure namespace:

- [CONTRACT.md](../../../WEBSITE/infra/agent-communication/v1/CONTRACT.md)
- [EXAMPLES.md](../../../WEBSITE/infra/agent-communication/v1/EXAMPLES.md)
- [DELIVERY.md](../../../WEBSITE/infra/agent-communication/v1/DELIVERY.md)

Root AGENTS routes to these local documents. JSON applies to actual agent
recipients, including delegated final responses. Direct human updates retain
the applicable human presentation style. Neither mode changes authority.

The evidence root is
`/Users/boandersson/Desktop/WEBSITE/.cache/agent-communication/`. This is shared
coordination evidence, not product site output. Use unique UTC run directories
and assignment-specific request/report names. The existing `.cache/` ignore rule
keeps these local; handover references do not commit or publish them.

The observed tool request maximum is 1,000 UTF-8 bytes. Keep inline replies within
the configured **3,500 UTF-8 byte budget**, including their entire JSON envelope.
Give large assignments through an authorized local request artifact; write full
reports to the explicitly assigned run path and return compact JSON with path,
SHA256, outcome and limits. Each assignment must permit its evidence writes,
even if source inspection is otherwise read-only. Coordinator and builder share
the local filesystem. Do not invent transport or write authority.

Collect a completed matching turn, parse the complete reply, read the referenced
file, verify its hash and inspect the evidence supporting its claims. Retain
truncated/failed deliveries as incomplete; reconcile effects before retrying.
No report is independently verified or owner accepted merely because JSON parses.

## Product boundaries and actual entry commands

This mission setup concerns shared coordination documentation; **no product site
is selected for implementation**. Actual websites belong only in
`SITES/<site-name>/`. Before a product assignment, select exactly one site and
read its own instructions, brief/intent, asset metadata and handover. Shared
tooling/rules remain in their native `scripts/`, `infra/` and deliberately shared
runtime locations. Preserve the single root Git repository/dependency tree and
the reference site's source-bound evidence.

| Purpose when authorized | Entry point from WEBSITE root |
| --- | --- |
| Inspect known site identities | `npm run site:list` |
| Develop selected site | `npm run site:dev -- <site-name>` |
| Build selected site | `npm run site:build -- <site-name>` |
| Verify selected site | `npm run site:verify -- <site-name>` |
| Verify shared tooling | `npm run verify:factory` plus affected-site requirements |

Commands were inspected in `package.json`, `scripts/site.mjs` and native guides;
they were not executed for mission setup. README/package pins specify Node
24.13.1 and npm 11.8.0; inspect the actual installed toolchain before execution.
Do not run reference-only aliases against Mammuth or treat a source push as site
deployment. Use the repository's own artifact/review/release contracts.

The opening handover identifies Mammuth v0.6.1-b2 and pending owner review of
four B2 motions, with device/Safari/rights/release and shared proof gaps. Those
facts are context, not authority to resume product work. This setup neither
changes the native proof plan nor creates an alternative roadmap.

## Remote, handover and setup evidence

Configured remote at setup: `https://github.com/WRRTREPO/WEBSITE.git`, `origin`.
Recheck URLs and branches before publication. This setup authorizes no commit,
push, deployment, public sharing or automatic publication of existing ahead
commits. Preserve hooks and use explicit reviewed paths when later authorized.
Keep CodeExp2 commits/pushes separate from WEBSITE operations.

WEBSITE's [Handover.md](../../../WEBSITE/Handover.md) is canonical for current
installation, native frontier and next assignment. Product handovers stay
site-owned. Leave source-bound approvals and historical receipts unchanged.

Setup run: `.cache/agent-communication/20261018-194117-5378f3/` in WEBSITE.
It retains launch receipt, initial prompt/assignment, opening status/diff and
34 file hashes, fresh native-onboarding ACK, package identity and installation
request. The fresh ACK matched the new thread and source and confirmed native
onboarding. Installation/artifact collection then passed: a completed matching
2,530-byte collected JSON reply identified a 23,101-byte full report with SHA256
`2ffecab296c3a79a53e44fb3a801ec222bc538748a650a3ca684f252c79160a4`.
The coordinator parsed both, verified all 37 reported file hashes, checked the
32 unrelated dirty files remained unchanged, reconstructed the original handover
and checked AGENTS retained its exact original prefix. Installed payloads use
native Prettier formatting; their JSON data and non-format text match the package.
The builder's initial new-section formatting warning was corrected and retained
in its report; final scoped formatting passed. See `coordinator-verification.json`
and `WEBSITE-COMMS-INSTALL-001-report.json` in the run directory.

This proves the observed Terminal launch, native onboarding and one complete
agent/artifact exchange. It does not qualify automatic lifecycle supervision,
installed schema enforcement or product acceptance. At setup the new builder
was left interactive in Terminal with its assigned turn completed; the later
user-reported termination is recorded in the lifecycle update above. No website build or
preview, commit or push was part of this setup. Recheck all current state next
session; retain the original dirty documentation audit and the separate product
frontier.
