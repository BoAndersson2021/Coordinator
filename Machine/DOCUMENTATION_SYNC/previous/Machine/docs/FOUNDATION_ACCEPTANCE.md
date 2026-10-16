# Machine foundation verification

Date: 2026-10-13. Scope: the first inspection-coordination implementation, not operational qualification of the full studio.

## Implemented behavior

The Machine front door exposes read-only status, source/ledger checks, assignment records, and retained evidence. Explicit setup creates private local state. Projects must be separate Git worktree roots and cannot share Machine's own Git history. Assignments pin the external revision, the two inspection inputs, studio context, and observed thread target.

Delivery attempts commit before a transport envelope is returned. State and evidence commit transactionally; stale versions, operation-identity reuse with changed inputs, mismatched receipts, incomplete reports, and unsupported schemas are rejected. Pending or uncertain delivery blocks redispatch until reconciliation. Inspection verification and closure provide no game-source or scene acceptance authority.

## Focused validation

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`

The foundation's 32 checks passed under Python 3.9.6. Its session-replacement extension brings the suite to 37 passing checks. Installed source and test digests match the reviewed candidate. Coverage includes source and observation drift, wrong workspaces, separate Git history, strict schema versions, operation replay, missing or changed evidence, report/review binding, uncertain delivery, concurrent dispatch, coordinator replacement, and a process crash before transaction commit. Replacement checks also cover exact queued-message identity, a durable removal intent, blocked dispatch after interruption or failed removal, preservation of the task and old attempt, and rejection of replacement after a report exists.

Read-only startup and status were checked for unchanged file bytes. Installed `status`, `help`, and `doctor` succeeded. Source comparison confirms that the original extracted Design bytes are unchanged. The three communication references match their recorded `CodeExp` source digests.

These are builder checks and fixture evidence. They establish the exercised behavior; they are not independent source review of a promoted autonomous Machine release.

## Live transport observation

The user selected `Desktop/Blender_Project` for the first bounded documentation inspection. Its pinned native route verified all fifteen source pins. Native thread metadata confirmed the registered Brainstorm workspace. The CLI accepted the 684-byte inspection prompt once and returned a queued-message UUID.

The original submission remained pending in the previous registered thread. The user then opened a new attended Brainstorm session, and the project registry moved to its new UUID. Machine preserved task `blender-inspection-001`, journaled a replacement intent, verified the exact old queue entry against its acknowledgement and prompt, and removed that pending message through the native API. The actual removal response was `deleted: true` and is retained with the old attempt.

Machine bound the freshly observed replacement thread and delivered the same inspection under a new attempt. That native attended session completed the inspection in a matching turn. Its report confirmed the pinned working directory and HEAD, accurately summarized the two documents' purpose, entry points, and role boundaries, and distinguished documentation from live runtime or scene readiness.

The coordinator independently reviewed the report against both pinned files; their SHA-256 identities and HEAD remained unchanged. Report and review evidence were retained, and the original task reached `closed` with verdict `verified`, version 10. Its first attempt remains `queue_removed`; the replacement delivery, completed report, and review remain in the same history.

The app server reported `notLoaded` even while the attended session processed its native queue. That field is not an attended-terminal liveness verdict. The proof is the exact matching completed turn and retained evidence.

The request permits inspection of `AGENTS.md` and `README.md` only. It does not request scene tools, project setup, repairs, saves, commits, or game/asset work. The native attended-session route and account billing policy are preserved.

## Remaining frontier

The first live inspection cycle and bounded session replacement are verified for their declared scope. Next qualify a reusable native transport bridge around current project role bindings and trusted receipt custody. Keep unknown or failed execution explicit.

The current local trust model relies on operator assertions and host custody. Authenticated grants, a reusable native transport bridge, protected domain adoption, live execution isolation qualification, resource reservations, production adapters, multi-host recovery, and controlled self-development promotion remain unimplemented or unqualified. The full studio and its economics remain unverified.
