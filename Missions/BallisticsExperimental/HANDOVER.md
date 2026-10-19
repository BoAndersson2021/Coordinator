# BallisticsExperimental — pickup checkpoint, 2026-10-19

**Parked at the owner's request. The suspension/contact repair is preflighted,
but has not been implemented or tested live.** Frontal wall pinning remains
unresolved. This checkpoint neither closes the mission nor resumes execution.

The owner authorized “OK execute and test live”, then asked to leave a handover
after the host-control gap was established. Preserve that authorization history;
do not silently restart work from it. The latest direction is documentation and
parking, with no more host investigation in this task.

## Where to resume

- Read the game's canonical [MISSION_PROTOCOL.md](../../../BallisticsExperimental/MISSION_PROTOCOL.md)
  and its current pickup section first.
- The builder owns the existing [PLAN.md](../../../BallisticsExperimental/Engineering/Investigations/BE-CONTACT-ARRIVAL-001/PLAN.md).
  Keep that plan as the shared baseline; do not create a replacement roadmap.
- Exact coordination decisions, assignments, completed turns and evidence hashes
  are in [BE-CONTACT-FRONTAL-001-COORDINATION.json](BE-CONTACT-FRONTAL-001-COORDINATION.json).
- Existing builder: `01a14b73-b7a5-7062-865e-ebd47b6b3ce0`, repository
  `/Users/boandersson/Desktop/BallisticsExperimental`. Coordinator session:
  `01a15110-c19a-7013-9180-764adda5c068`. Recheck actual availability on resume.

## What is established

The low-speed suspension can reach its target radius while stored normal
velocity continues cycling. The hover correction overwrites the damped spring
velocity. Retained actual wall-contact evidence connects the competing normal
updates to the pin; both latest rendered frontal escape directions still fail.

The reviewed proposal replaces competing writes with one normal update around
the existing hover target and a consistent contact remainder. Existing
coefficients are the first candidate's inputs; no new hardening profile is
adopted. Ordinary collision-free forward/strafe movement stays unchanged.
The precise geometric/kinetic velocity distinction and remaining-time policy
are mandatory parts of the proposal:

- [PREFLIGHT.json](../../../BallisticsExperimental/Saved/Investigations/BE-CONTACT-FRONTAL-001/normal-preflight-1/PREFLIGHT.json)
  — SHA-256 `b408daf2da280492eb00f713b2d8aa5f23f596ac8c40cbb68b5a2934de1c4472`.
- [CLARIFICATION.json](../../../BallisticsExperimental/Saved/Investigations/BE-CONTACT-FRONTAL-001/normal-preflight-1/CLARIFICATION.json)
  — SHA-256 `dd7a62d3cc02e03fdb4a8228828a9288cd5ee0e085e08f775c37d5f45f83f9ad`.

All 12 numerical attempts and stopped approaches carry forward. Candidate 13
never started. The reviewed floor-direction component remains unintegrated.
The current source11 runtime is **unqualified**; preserved earlier timing/Scale
passes do not qualify it. Existing dirty work and baseline/evidence archives
must be retained. No staging, commit or push is part of this handover.

## External execution boundary

The newly adopted [execution setup procedure](../README.md#required-mission-execution-setup)
requires receiver-bound approval/cancellation proof before product dispatch.
The exposed thread tools provide no pending-request decision or exact-turn
interrupt action. Computer Use also refused Terminal access for safety reasons.
No pending-approval probe or product execution was started.

The owner attributes this to Codex/Apple. The observed limitation is this host's
current capabilities/access, not proof that every future host version is
unfixable. Full setup evidence is retained in
[EXECUTION_SETUP.json](../../../BallisticsExperimental/Saved/AgentCommunication/BE-CONTACT-FRONTAL-001-NORMAL-LIVE-20261019-1/EXECUTION_SETUP.json)
— SHA-256 `ea90b94c3bf25ef292cb4229d6ba6dde04b23b1d890be2698f180c601554caf3`.

## Recommended next action

On an explicit owner resume, reconcile the canonical handover, actual dirty
tree, builder and supported execution route under the then-applicable
instructions. Continue from the reviewed bounded candidate; do not repeat the
settling investigation or infer missing product consent.

Actual captured replays, both rendered frontal escape directions and the
existing final contact/recovery/fault, unchanged 120-second timing guard and
full Scale/results/restart gates remain required. Review the actual diff,
`STEERING_REPORT.md` and evidence before any baseline commit. Camera reliability,
then Investigation 028's minute hitch and input-to-display latency, remain
separate queued work.

The documentation handover completed in builder turn
`01a15401-e40d-7503-933c-110a5204316e`; the builder was observed idle afterward.
The [completed handover report](../../../BallisticsExperimental/Saved/AgentCommunication/BE-CONTACT-FRONTAL-001-HANDOVER-20261019-1/BE-HANDOVER-report.json)
has SHA-256 `9528db1b8ef6ba543ea686df252ada3b811b98a8d2bc8f56dfb898e9546c2d7a`.
Canonical pickup is now PLAN R26. Product bytes were verified unchanged, and
historical handover/plan text was preserved. Nothing was staged, committed or
pushed. Documentation is complete; execution remains parked.

## Subsequent documentation publication

After handover completion, the owner authorized “commit push” for these
handover updates. The game documentation is published at commit
`bf8753ed55da5e94e9e85042c98b0b0d6b6559c9` on the approved experimental
`origin/main`; the remote SHA was verified. That commit contains only
`MISSION_PROTOCOL.md` and the existing investigation's `PLAN.md`.

The Coordinator publication contains this pickup note and its mission-guide
link. Earlier no-publication statements describe the preceding handover
checkpoint. Solver/runtime/test changes remain uncommitted and unqualified;
documentation publication does not promote a repaired solver baseline.
Detailed coordination JSON, other untracked investigation files and ignored
`Saved/` evidence remain local working-copy references and are not included
in these documentation commits. Preserve them for pickup. No implementation,
live test or host investigation was resumed.
