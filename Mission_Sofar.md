# Workspace state and handover

This file covers CodeExp2 workspace state. It is not a global active-mission
pointer or a mission implementation plan. Read mission-specific state only after
explicit selection through [the registry](Missions/README.md#registered-missions).

## Swift desktop launcher — 2026-10-18

The user requested a desktop icon that opens Terminal, starts Codex in CodeExp2
and automatically completes onboarding to the mission menu. The native Swift
launcher is implemented under [Launcher/](Launcher/README.md), built and ad-hoc
signed at `Launcher/build/CodeExp2.app`. `/Users/boandersson/Desktop/CodeExp2.app`
is a native Finder alias to that bundle with its custom icon verified in Finder.
Keep the generated app in place; source and rebuild instructions are in Launcher.

The launcher passes the fixed `onboard` first prompt directly at process start,
following the local launch law. It does not type into a running Codex UI, choose
a mission, reuse a session or override model, account, trust or permissions.
The actual Desktop alias was opened and a fresh Terminal Codex session completed
onboarding to **Coordinator ready. No mission selected.**, with both registered
missions and the new-mission choice. That interactive test session was left open.
See [verification](Launcher/VERIFICATION.md) for exact scope and identities.

The user subsequently authorized committing and pushing the launcher. Independent
review `/root/launcher_publication_review` passed its exact source inventory,
bounded policy update and all 20 tests. The reviewed inventory was adopted with
the previous installed gate and unchanged configuration preserved under
`.git/codeexp2-launcher-adoption-5ucktqqs/`. The verifier, existing instruction and
deletion pins, and all 18 earlier mandatory checks remain unchanged; two native
launcher regressions are now mandatory too. See [publication evidence](Launcher/PUBLICATION.md).
Publication uses the normal staged-source hook and explicit `origin main:main`;
identify the resulting source commit with `git log -1 -- Launcher`. This is
workspace startup tooling, not a selected product mission or Machine automation.

## Startup and mission registry — 2026-10-18

The CodeExp2 agent is the **Coordinator** and identifies itself that way to the
human and other repository agents. Root AGENTS now directly defines this role,
native builder ownership, onboarding duties and the mission directory layout.
Legacy Machine installation/startup narratives and absolute target pointers were
removed from AGENTS. The human communication advice, all eight how-to/contract
guides and the CLI workflow review procedure are retained. Applicable Machine
requirements remain in a concise scoped rule and the existing contract guides;
no executable enforcement or permissions changed. Agent JSON retains the schema's
lowercase `coordinator` role value.

The user requires `onboard` to load common rules and actual workspace Git state,
then present every valid registered mission plus **Start a NEW mission**.
No mission is selected, recommended or read into by default, even when it was
recently discussed or is the only registered entry. Explicit selection with the
startup request permits that mission's subsequent intake.

`Missions/README.md` is the canonical index. Every mission needs both its table
entry and `Missions/<name>/README.md` before builder connection, launch,
installation or execution. An external repository, root historical document or
saved session is not an alternative registration route. New registration records
the guide and index entry first, then uses read-only target inspection to fill
native references; it does not run mission work.
Product source stays in the registered target; coordination stays in its mission
folder. Ordinary CodeExp2 instruction/registry maintenance is workspace work.

Several missions may remain ongoing. Maintain each one's builder, scope, plan
reference, assignments, evidence, coordination handover and lifecycle separately.
Selecting, adding or closing one does not replace or stop the others. The shared
coordination guide and accepted start/close design now state this explicitly.
Registry entries describe selectable missions, not freshly verified live builders.

Root README, AGENTS and this handover now avoid mission-specific startup intake.
The common onboarding checklist is in [Missions/README.md](Missions/README.md#coordinator-onboarding-onboard).
No target mission was selected, contacted, started, stopped or changed by this
instruction update. It is documentation work, not runtime automation or a live
startup test. The user subsequently authorized committing and pushing this
documentation update. Publication uses the normal hook and the configured
`origin main:main` destination; completion requires a matching observed remote
SHA. Identify the resulting instruction commit with `git log -1 -- AGENTS.md`.

Independent review `/root/review_folder_removal` passed the current Coordinator
role, onboarding, directory structure, registry and scope instructions. The
human communication advice and complete guide catalog remain byte-identical to
the published version; the CLI review body changes only a heading level.
Reviewed root AGENTS SHA-256:
`85479bf75238c44036c6f4cf8658498bbaf6df5af669d52e3b5d03aca452ed37`.
Links, heading anchors and whitespace checks passed. This source review
establishes instruction consistency, not live startup behavior.

For the authorized publication, a separate independent review passed the local
policy update that changes only the root AGENTS hash and the bootstrap's matching
policy digest. The verifier, source inventory and all 18 mandatory test IDs are
unchanged. The reviewed pin was adopted; previous trusted bytes, unchanged
configuration hash, exact manifest, review and adoption receipt are retained in
`.git/coordinator-onboarding-adoption-6pgzf021/`. Review receipt SHA-256:
`0a9c88247d4322c89837e3b90bc59180e290115248a4fc66756ca503fbd3a9bd`.
This changes no runtime permissions and uses no hook bypass.

## Published workspace cleanup

Cleanup commit `5cf2f9d7a269709646706420a3eb533a50340ff4` was pushed to CodeExp2's
configured `origin/main` and independently matched the remote on 2026-10-18.
The earlier communication-guidance commit `c7ad298` was published with it.

The user authorized removing the local `Machine/` folder, including the untracked
task-timeline candidate, and three misplaced root `.tar` files because their
material is stored elsewhere. Do not restore or resume them during onboarding.
Machine is not currently a registered mission; new work on it requires normal
registration and explicit selection. Its invariant remains applicable within
Machine scope and is unchanged by registry maintenance.

The local commit gate was independently reviewed and adopted with its previous
installation preserved. All 18 mandatory regressions passed through the normal
commit hook. See [the gate documentation](docs/commit-gate.md) for exact scope
and adoption evidence. Instruction changes still require independent review and
recorded adoption; executable changes require meaningful staged regressions.
Neither documentation nor a commit grants mission runtime authority.

## History and optional system-design work

Per-mission guides and coordination handovers live under their registered mission
folders. Target repositories retain their native canonical handovers and plans.
Detailed earlier global WEBSITE/Machine history remains in Git, including
`git show 5cf2f9d:Mission_Sofar.md`; it is historical evidence, not startup intake.
Do not follow its old resume directives or treat its dated capabilities as live.

The accepted shared [mission start/close design](Missions/CONTROL_WORKFLOW_PROPOSAL.md)
remains unimplemented beyond recorded diagnostics. Automatic native custody and
retirement remain unqualified; no mission CLI is installed. Its evidence and
failures are retained under `Missions/ControlWorkflowEvidence/`. This shared
workspace design is not a selected product mission or a reason to pick one.
