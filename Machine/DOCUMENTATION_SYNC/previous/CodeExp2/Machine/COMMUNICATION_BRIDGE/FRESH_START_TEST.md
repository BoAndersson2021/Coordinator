# Fresh CodeExp2 communication acceptance

**Superseded procedure.** The owner requires zero manual start/stop, handover or
communication steps during execution. A test requiring someone to stop this
conversation and open a replacement cannot qualify that workflow. Use the
[automated workflow requirements](../AUTOMATED_WORKFLOW_REQUIREMENTS.md) for the
new implementation and acceptance scope: persistent orchestration, managed
executor lifecycle, automatic communication, and visible failure/recovery.
The old steps below remain historical evidence and must not be reused as the
operational acceptance route.

Current verdict (2026-10-16): **FAIL — no live receiver was established**.
The original input was recovered after restart but remained queued. Subsequent
inspection found no Brainstorm terminal or loaded instance. See
[the failure record](LIVE_ACCEPTANCE_FAILURE.json). The previous instruction to
wait for the receiving session is superseded. Repair and independently qualify
the bridge's receiver-liveness check, and reconcile the original queued message
before any further live test. Preserve task `native-inspection-fresh-start-001`
and its single attempt; do not resend, silently delete, launch/resume, verify or
close it as a workaround. The procedure below is retained as the original test;
it requires revision for receiver liveness before reuse.

## Historical manual procedure — inactive

This was the live test requested by the owner after implementation,
verification, independent red teaming, fixes and reverification. Read the latest
verification and installation records in this directory first. A pending or
rejected candidate is not eligible. No live project test is triggered merely by
reading this document or starting a session.

Start a new Codex session with `/Users/boandersson/Desktop/CodeExp2` as its
workspace. Read onboarding and this handoff from disk. Check the installed
Machine status, doctor and work-view. Recover any existing acceptance task
before preparing another; never redispatch a pending or delivered task.

When the owner asks to run this acceptance, operate the following bounded test.
The agent operates the commands; the owner need not prepare receipt JSON.

1. Verify the installed source matches the independently accepted candidate.
   Confirm the Machine project `blender-project` and registered agent
   `blender-brainstorm-01a136be` still refer to the exact project and role UUID
   currently recorded by Blender_Project. A historical binding is not live proof.
2. Explicitly configure the pinned existing native route if not already configured,
   following the installed `docs/NATIVE_BRIDGE.md`. Do not change its active release,
   account, endpoint, scene or source. Observe the actual thread through the bridge.
3. Use task ID `native-inspection-fresh-start-001`. If it already exists, inspect
   and collect it instead of preparing or sending again. Otherwise prepare one
   inspection with brief `Summarize supported entry commands.` The fixed inspection
   envelope restricts work to AGENTS.md and README.md and forbids mutations.
4. Call `bridge-send` once for that prepared task and retain its actual result.
   After confirmed delivery, stop this coordinator session **before collecting
   the reply**. Start another new CodeExp2 session and read this handoff from disk.
   If delivery is uncertain, retain that uncertainty and restart without resending.
5. In that new session, run status/work-view and `bridge-collect` for the same
   task. This is the recovery observation: it must obtain actual queued, running,
   failed or completed evidence without another send or hidden conversation memory.
   A timeout, unavailable agent or waiting state remains visible; never launch or
   resume a project agent as a workaround. Report that specific blocker.
6. Read the retained report and independently inspect the two pinned files. Only
   use the existing verification and closure route if the report's claims and
   inputs pass review. Collection alone awards no independent acceptance.

Record actual coordinator and receiving turn UUIDs, source identities, send and
collection outputs, review result and any unresolved effect. Check that exactly
one submission was made and that the project source and scene remain unchanged.
Keep the live result separate from fixture tests and the read-only socket probe.

Acceptance is complete only after the actual project reply, source review and
fresh-session recovery have been observed. Until then the communication bridge
remains implemented/verified with live acceptance pending.
