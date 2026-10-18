# Builder Communication — installation package

Package ID: `builder-communication`

Contract version: `1`

Status: prepared documentation package; not installed in a mission repository.

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
Copy contract and examples into target docs
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
| [AGENTS-SNIPPET.md](AGENTS-SNIPPET.md) | Text to merge into the target's existing instructions. |

## Install into an authorized mission repository

1. Confirm the exact target repository and that documentation installation is
   authorized. Read its ancestor/local instructions, current handover and Git
   state, including staged work. Preserve existing instructions and changes.
2. Inspect this complete package. Copy `CONTRACT.md` and `EXAMPLES.md` into
   `docs/agent-communication/v1/` in the target. If that location already exists,
   compare it before updating; do not overwrite local amendments blindly.
3. Merge the contents of `AGENTS-SNIPPET.md` into the target root `AGENTS.md`,
   preserving all existing rules. Adjust the link if the installation path or
   instruction-file location differs. Do not copy CodeExp2's root `AGENTS.md`
   wholesale, or install the snippet as a separate automatically loaded agent
   instruction file.
   Inspect existing communication wording: within authorized instruction edits,
   clarify that prose/diagram preferences govern human replies and this contract
   governs agent exchanges. Preserve higher-priority requirements and report any
   unresolved conflict instead of asserting that JSON overrides them.
4. Review the exact diff, links and JSON examples. Follow the target's required
   instruction review and normal commit hooks. Installation does not authorize
   changing hooks, launching agents, running the application or publication.
5. Record the package ID, contract version, source CodeExp2 revision plus dirty
   package identity when applicable, installed paths and target changes in the
   mission's canonical handover. Report installation/review status accurately.
6. During the next authorized connection, explicitly ask both parties to read
   and apply the installed contract. Confirm the fresh assignment/token in a
   completed acknowledgement through the existing supported communication tool.
   A copied file or delivery receipt does not establish adoption or readiness.
   Check that the ACK uses the agent JSON format and identifies its recipient.
   Confirm the builder understands that delegated final results also use JSON,
   while direct human replies retain their existing presentation style. Record
   this as unverified until actually observed; do not message agents solely
   because installation instructions describe the check.

Suggested installation request:

> In `<target repository>`, read and apply your applicable instructions. Inspect
> the BuilderCommunication package at `<package path>/README.md`. Install its
> version 1 contract and examples under `docs/agent-communication/v1/`, merge the
> scoped snippet into root AGENTS.md, and record the package source identity and
> installation status in the canonical handover. Preserve existing work. Return
> changed paths, checks and unresolved conflicts. Documentation only; no agent
> launches, application execution, commits or pushes in this assignment.

Change the last sentence only to reflect authority actually granted by the user.

## Updating an installed copy

Treat the target copy as a recorded snapshot. Compare package and target changes,
preserve mission-specific additions, review compatibility, and update the handover
when adopting a revision. A package edit does not update or supersede installed
copies automatically. Keep the same version for compatible clarifications; use a
new contract version and an explicit migration when message meaning changes.

This package defines message content. It does not replace a mission's connection
protocol, delivery evidence, lifecycle controls, build rules or product laws.
It does not qualify Machine automation or install its enforcement.
