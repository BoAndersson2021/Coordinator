# Builder Communication — installation package

Package ID: `builder-communication`

Contract version: `1`

Status: reusable documentation package. Snapshots were installed and exercised
in BallisticsExperimental and WEBSITE; installed copies have their own adoption
state and source hashes.

Point a mission agent at this README to install a shared coordinator/builder
message format. The package contains instructions and JSON examples, with no
installer, executable validation, transport or runtime changes.

The target keeps two communication modes: JSON for agent recipients and its
existing presentation style for humans. Install the audience-selection rule
alongside the JSON contract; do not remove human communication guidance.

```text
Read target instructions and current Git state
    |
    v
Complete target's own scoped onboarding and startup
    |
    v
Copy contract and examples into target docs
    |
    v
Configure report directory and reply budget
    |
    v
Merge scoped snippet into target AGENTS.md
    |
    v
Review diff and links; record installed version
    |
    v
Existing authorized communication route
    +--> fresh ACK confirms contract read
    +--> bounded assignment and evidence-backed result
```

## Contents

| File | Purpose |
| --- | --- |
| [CONTRACT.md](CONTRACT.md) | Message envelope, roles, required fields and evidence rules. |
| [EXAMPLES.md](EXAMPLES.md) | JSON examples for assignment, acknowledgement, progress, blocker and completion. |
| [DELIVERY.md](DELIVERY.md) | Template the installer fills with the mission's artifact path, limits and verification status. |
| [AGENTS-SNIPPET.md](AGENTS-SNIPPET.md) | Text to merge into the target's existing instructions. |

## Install into an authorized mission repository

For CodeExp2-coordinated work, verify the mission's registration in
[the mission index](../../README.md#registered-missions) and its named running
guide before target installation or communication. The shared package is support
material, not a mission or a shortcut around registration. Keep each mission's
target settings, evidence paths and builder identity separate.

1. Confirm the exact target repository and that documentation installation is
   authorized. Read its ancestor/local instructions, current handover and Git
   state, including staged work. Preserve existing instructions and changes.
   Require the receiving agent to follow the target's own onboarding, startup
   and governance first. Inspect its real entry scripts before execution; do not
   replace native steps with this package, invent a start command, or resume an
   old task from its handover. Hold only steps actually blocked by scope/access.
   If a new session is explicitly authorized, follow the
   [mission startup procedure](../../README.md#start-a-new-repository-agent-when-authorized),
   then establish actual identity and native-onboarding readiness before editing.
2. Inspect this complete package. Copy `CONTRACT.md` and `EXAMPLES.md` into
   `docs/agent-communication/v1/` in the target. If that location already exists,
   compare it before updating; do not overwrite local amendments blindly. Preserve
   the target's actual directory capitalization, such as `Docs/`.
3. Merge the contents of `AGENTS-SNIPPET.md` into the target root `AGENTS.md`,
   preserving all existing rules. Adjust the link if the installation path or
   instruction-file location differs. Do not copy CodeExp2's root `AGENTS.md`
   wholesale, or install the snippet as a separate automatically loaded agent
   instruction file.
   Inspect existing communication wording: within authorized instruction edits,
   clarify that prose/diagram preferences govern human replies and this contract
   governs agent exchanges. Preserve higher-priority requirements and report any
   unresolved conflict instead of asserting that JSON overrides them.
4. Establish the report delivery path during installation. Fill a target-local
   `DELIVERY.md` beside the contract using the supplied template. Record the
   absolute repository root, repository-relative artifact directory, unique run
   and report naming, supported tool route, request limit, conservative reply
   budget, coordinator access and retention. Inspect receiving limits as well
   as sending limits; a large read setting may still return truncated messages.
   Each assignment must explicitly include any permitted report-file writes,
   even if its investigation otherwise allows only reading source. Do not leave
   directory choice or write authority for the builder to guess at completion.
5. Review the exact diff, links and JSON examples. Follow the target's required
   instruction review and normal commit hooks. Installation does not authorize
   changing hooks, launching agents, running the application or publication.
6. Record the package ID, contract version, source CodeExp2 revision plus dirty
   package identity when applicable, installed paths and target changes in the
   mission's canonical handover. Report installation/review status accurately.
7. During the next authorized connection, explicitly ask both parties to read
   and apply the installed contract. Confirm the fresh assignment/token in a
   completed acknowledgement through the existing supported communication tool.
   A copied file or delivery receipt does not establish adoption or readiness.
   Check that the ACK uses the agent JSON format and identifies its recipient.
   Confirm the builder understands that delegated final results also use JSON,
   while direct human replies retain their existing presentation style. Record
   this as unverified until actually observed; do not message agents solely
   because installation instructions describe the check.
   When a delivery test is authorized, verify the complete path: builder writes
   a full report to the configured run directory, returns a bounded completion
   with report path and SHA256, and coordinator collects a completed matching
   turn, reads/parses the file and verifies its hash. Record the result and any
   limits in target DELIVERY.md and handover. If execution is outside scope,
   leave the route explicitly unverified; document checks do not prove delivery.

Suggested installation request:

> In `<target repository>`, first follow its own onboarding, scoped startup,
> governance and handover; reconcile current authority and dirty work. Inspect
> the BuilderCommunication package at `<package path>/README.md`. Install its
> version 1 contract and examples under `docs/agent-communication/v1/`, merge the
> scoped snippet into root AGENTS.md. Fill target DELIVERY.md with the artifact
> directory, transport limits, reply budget, access and report-write scope. Record
> the package source identity, delivery settings and installation status in the
> canonical handover. Preserve existing work. Return
> changed paths, checks and unresolved conflicts. Documentation only; no agent
> launches, application execution, commits or pushes in this assignment.

Change the last sentence only to reflect authority actually granted by the user.

Observed BallisticsExperimental settings are documented in the
[mission guide](../../BallisticsExperimental/README.md#agent-json-and-report-delivery).
Use them as evidence for that host, not universal tool limits or a directory to
reuse in another repository.

The [WEBSITE mission](../../WEBSITE/README.md) also records a user-authorized
Terminal launch, native repository onboarding and a complete compact-reply/full-
artifact exchange. Its installed rules live under native `infra/`, and its
evidence uses existing ignored `.cache/`; neither is a universal installation path.

## Updating an installed copy

Treat the target copy as a recorded snapshot. Compare package and target changes,
preserve mission-specific additions, review compatibility, and update the handover
when adopting a revision. A package edit does not update or supersede installed
copies automatically. Keep the same version for compatible clarifications; use a
new contract version and an explicit migration when message meaning changes.

This package defines message content. It does not replace a mission's connection
protocol, delivery evidence, lifecycle controls, build rules or product laws.
It does not qualify Machine automation or install its enforcement.
