# Workspace state and handover

This file covers CodeExp2 workspace state. It is not a global active-mission
pointer or a mission implementation plan. Read mission-specific state only after
explicit selection through [the registry](Missions/README.md#registered-missions).

## Authorized Valhall publication — 2026-10-19

The owner subsequently requested commit and push of the Valhall app/name/icon
and earlier full-access setup. The [publication record](Launcher/VALHALL-PUBLICATION.md)
defines the exact scoped changes, normal hook checks, independent review and
guarded local pin adoption. Historical setup entries saying uncommitted or no
policy change describe those earlier checkpoints. The verifier and all 20
mandatory regressions stay unchanged. Unrelated mission registrations/files
remain excluded. Publication is complete only when the source commit matches
the observed configured `origin/main`; identify it with `git log -1 -- Launcher`.
No product mission is selected, resumed or executed by this publication.

## Valhall app name and Viking icon — 2026-10-19

The owner requested **Valhall**, the Swedish spelling, as the app's visible name
and new Viking artwork. The launcher now builds with Valhall bundle display/name
metadata and a generated helmet/ravens/knotwork icon. The internal app path,
executable, bundle identifier, workspace and `valhalla` permission profile stay
stable. `--install-alias` migrates only a verified matching old native Desktop
alias to `Valhall.app`, refreshes a matching alias's artwork, and preserves
unrelated entries. Source art and the final built-in ImageGen prompt are retained
under [Launcher](Launcher/VALHALL-ICON.md). No product mission is selected by this
workspace presentation change.

Installed and ad-hoc signed in place. The native Desktop entry is now
`/Users/boandersson/Desktop/Valhall.app`; Finder Get Info verified its name,
Viking icon (header and large preview), Alias kind and unchanged original target.
Both focused native launcher regressions passed (8.138 s), including display
metadata/icon packaging and earlier profile/claim checks. Updating the enclosing
app timestamp refreshed an initially stale Finder artwork preview. Changes
remain uncommitted; unrelated Desktop items and mission work are preserved.

## Valhalla full-access startup — 2026-10-19

The owner approved installing the proposed shared launch profile. New app-created
instances explicitly use `--profile valhalla`: full local/network access, CLI
approval policy `never`, live web, supported tool preapprovals and native local
memory. The standalone overlay preserves global configuration, account and model.
The rebuilt/signed app requires matching installed/bundled profile bytes. The
missing native Desktop alias was restored to the existing app path.

Actual Desktop-created Coordinator Freya completed onboarding without selecting
a mission. Its session context records `danger-full-access` and `never`;
supported host Calculator control, native Safari navigation and screenshots
worked. All 20 regressions passed. Existing terminals keep their earlier settings;
their ongoing work was left alone. See [setup](Launcher/VALHALLA.md) and
[verification/review adoption](Launcher/VALHALLA-VERIFICATION.md) for exact
identities, tested scope, evidence and host/provider limitations.

Independent source/instruction review passed; the reviewed Coordinator rule is
adopted. The Coordinator owns technical validation and routine tool provisioning
within owner scope. This grants no unrelated effects, mission selection,
provider credentials or OS consent. Earlier launcher history describing inherited
permissions predates this explicit owner-approved change. No staging, commit,
push or local gate-policy change was performed for this setup; unrelated mission
files/registry edits are preserved. Use new Desktop launches for Valhalla access.

## Authorized Nordic/concurrency publication — 2026-10-19

The owner authorized commit and push of this conversation's launcher and
Coordinator concurrency changes. Independent exact staged-source and bounded
policy/bootstrap review passed; all 20 tests passed through the candidate normal
bootstrap. The guarded adoption preserved previous trusted bytes and unchanged
Git configuration under `.git/codeexp2-nordic-adoption-tmrs0ma3/`, and changed
only the reviewed exact pins. The verifier and mandatory tests are unchanged.
See [publication admission](Launcher/INSTANCE-PUBLICATION.md) for hashes and scope.

Publication uses the normal installed hook and explicit `origin main:main` at
the configured Coordinator remote. Identify its source commit with
`git log -1 -- Launcher/CodeExp2.swift`; completion requires matching the remote
SHA. The two earlier registry additions and unrelated untracked mission files
are excluded and preserved. Earlier entries saying no index/policy/publication
change occurred describe their implementation checkpoints before this separate
authorized publication task. No product mission is selected or resumed.

## Nordic instance aliases and colors — 2026-10-19

The owner agreed to Nordic human aliases with OS-held name claims and requested
automatically distinct Terminal colors. The existing native launcher now owns
both as one atomic process-associated record lock. Twelve base names have fixed
dark colors; suffix/color variants cover 192 live instances. No PID register,
heartbeat, stale-claim reaper, supervisor or database was added. Permanent claim
files stay in ignored `Launcher/build/instance-claims/`; never unlink/replace
them while instances may be live. Process death/reboot releases ownership even
if a helper retains the descriptor.

The launcher uses the already installed native arm64 Codex executable directly
so the real TUI retains the claim through exec. The global shim is untouched.
Only its terminal-title display items are overridden; account, model, trust,
approval and sandbox settings are inherited. The existing Desktop alias targets
the rebuilt/signed app in place. New onboarding receives its human alias and
actual structured session identities remain unchanged. Existing sessions receive
no retroactive alias/color and no mission is selected by launch.

Independent exact-source review passed after finding and correcting descendant
retention in the first `flock` implementation. All 20 regressions passed,
including a surviving-child crash test; the reviewed alias instructions are
adopted for workspace conduct. See the [review receipt](Launcher/INSTANCE-REVIEW.md)
and [runtime verification](Launcher/INSTANCE-VERIFICATION.md) for exact hashes,
observations, historical failed/interrupted probes and display limits.
The final Desktop-entry session completed onboarding as Coordinator Odin with
all four mission choices and no selection (42,916 ms). That named instance is
left open for the owner at the menu; its actual frontend holds the name/color
claim. Closing it releases the pair. Earlier disposable frontends were cleaned;
no shared service or unrelated mission was stopped.
No index, commit, push or hook policy was changed. Future publication needs its
normal authorization and exact-byte policy review/adoption; preserve other work.

## Concurrent instances are Coordinator-owned — 2026-10-19

The owner clarified that coordination between CodeExp2 instances is the
Coordinator's job. The [concurrent-instance procedure](Missions/README.md#concurrent-codeexp2-instances)
now assigns session/mission separation, overlap resolution, shared-file and Git
ownership, routine worktree arrangements and scoped handover to Coordinators.
The human selects outcomes/scope and retains reserved decisions; do not delegate
coordination bookkeeping or terminal/message relay to the human.

AGENTS and README link the procedure. It preserves bare onboarding, explicit
selection, native builder ownership, permission boundaries and independent
mission lifecycles. This is instruction maintenance, not a demonstrated locking
system or automatic controller. No mission was selected, contacted or executed;
existing dirty registry additions and mission files are preserved.

Independent reviewer `/root/concurrent_instruction_review` returned PASS with no
required fixes; reviewed source hashes and scope are retained in the
[review and instruction-adoption record](Missions/ControlWorkflowEvidence/20261019-concurrent-instances-review.json).
The reviewed workspace instructions are adopted for Coordinator conduct under
the owner's clarification. Links and whitespace checks passed. This is distinct
from commit-gate policy adoption: no hook policy, staging, commit or push was
changed/performed. Future publication requires its normal authorization and
exact-byte gate review/adoption; unrelated work must remain separate.

## Task closing communication — 2026-10-19

The owner requested [How to end a task](docs/how-to-end-a-task.md): state what is
done, what remains and the recommended next action. If an action option remains,
recommend it clearly, with its owner and any real decision/access boundary.
A failed approach must not silently imply that no alternative remains. Continue
necessary feasible work already authorized; respect explicit owner stops.

The guide is linked from the root AGENTS catalog, README, Delivery Discipline
and the coordinator guide. It preserves structured agent reply contracts and
does not authorize execution, publication or resumption of ended missions.

## Required mission execution setup — 2026-10-19

The owner required the three approval-workflow setup steps to be codified for
mission establishment. [The canonical procedure](Missions/README.md#required-mission-execution-setup)
now requires native approval review, ordinary mission permissions, and supported
approval/cancellation control before execution readiness or product dispatch.
This also applies when an investigation expands into execution and when resuming
an existing mission. A completed communication ACK alone is insufficient.

The owner further clarified that establishing the host controls belongs inside
mission establishment. The Coordinator must arrange provision/configuration,
connection and verification, with a named host/provider owner for missing
controls. Recording an unavailable control does not finish establishment; its
bounded setup/repair remains a prerequisite, subject to actual scope and access.

The record must bind real passing evidence to the receiver, effective settings,
workspace and control route, including a successful approval, a visible refusal,
cancellation while approval is pending, and reconnect reconciliation without
replay. Reuse matching proof; repeat only checks affected by changed conditions.
Missing capability produces `EXECUTION_BLOCKED` for the dependent scope, while
registration and independent authorized inspection remain available. No hidden
terminal task is assigned to the owner.

This is workspace procedure maintenance, not permission configuration or a
qualified runtime admission controller. No mission is selected/resumed, no
builder launched, and no approval/cancellation route is implemented by this
documentation update. Existing missions retain their recorded lifecycle and
outstanding effects; do not resume owner-ended work from historical approval.

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
