# Missions

This folder contains running instructions for missions carried out in different
repositories, such as **BallisticsExperimental**.

Available mission guides:

- [How to work on BallisticsExperimental as a CodeExp2 agent](BallisticsExperimental/README.md)

Reusable installation packages:

- [Builder Communication v1](Packages/BuilderCommunication/README.md) — structured
  coordinator/builder messages and a scoped target `AGENTS.md` addition.

Each mission's instructions should identify its target repository, purpose,
startup procedure, relevant guidance, build and play commands, verification
requirements, and handover location. When a builder agent is involved, include
the mission's connection and coordination procedure.

Keep repository-specific instructions under a clearly named mission folder.
Link to the target repository's canonical instructions and handover so the
mission can resume from its current state next session.

For example, a BallisticsExperimental mission can reference its `AGENTS.md`,
`MISSION_PROTOCOL.md`, and `QuickPlay.sh` workflow in
`/Users/boandersson/Desktop/BallisticsExperimental`.

Follow the target repository's applicable instructions and the user's current
assignment. Recorded commands and historical results do not grant execution
authority or establish the repository's current status.

## Set up a mission for a new repository

1. **Define the mission.** Record the user's intended outcome, repository name,
   local path and authorized scope. Distinguish investigation, implementation,
   build/run, and publication authority. Setting up running instructions does
   not itself authorize executing all the commands they describe.

2. **Establish the target repository.** Keep the project at its own agreed
   location, for example `/Users/boandersson/Desktop/<RepoName>`, rather than
   nesting it inside CodeExp2. For an existing repository, inspect its current
   branch, HEAD, working tree, staging area and remotes before changing anything.
   Preserve existing work. Create, initialize or clone a repository only when
   that action is part of the user's request; do not re-import an existing
   mission's source to start another session.

3. **Read the applicable instructions.** Read CodeExp2's
   [AGENTS.md](../AGENTS.md) and
   [Delivery Discipline](../docs/delivery-discipline.md), together with the
   target repository's applicable ancestor and local instructions, orientation
   and handover. Read the coordinator guide for builder coordination, the runtime
   guide for application work, and the plan guide before executing or updating
   a plan. Identify the current assigned plan, or explicitly record that none is
   assigned. Do not transfer Machine-specific installed capabilities to another
   repository by assumption.

4. **Create the running guide.** Add `Missions/<RepoName>/README.md` in CodeExp2
   and link it in the available mission guides above. Use the
   [BallisticsExperimental guide](BallisticsExperimental/README.md) as a worked
   example, adapting its paths, roles and restrictions to the new mission.
   Keep canonical project instructions, implementation plans and continuation
   state in the target repository; link to them instead of maintaining competing
   copies in CodeExp2.

5. **Establish ownership and communication.** Record the coordinator's role,
   the execution owner and the repository each uses. If builder coordination is
   authorized, follow the
   [coordinator guide](../docs/how-to-coordinate-with-a-builder-agent.md).
   Discover the intended existing builder through supported tools, verify its
   repository and identity, and obtain a fresh acknowledgement before delegating
   work. A saved thread ID is a discovery hint, not proof of receiving readiness.
   Explicitly supply the instructions the builder must read and apply. Do not
   spawn a replacement or start work merely because the guide describes one.

6. **Record the real delivery path.** Identify the project's actual build,
   launch/play and focused verification commands, including their working
   directory, configuration and evidence locations. Define observable acceptance
   for the requested outcome and the behavior that must be preserved. Mark
   commands and capabilities as unverified when they have not been checked;
   execute them only within the current assignment's authority.

7. **Set the remote boundaries.** Record the approved fetch and push destination,
   branch and any source repository restrictions. Distinguish an imported source
   from the mission's publication remote. Inspect existing Git configuration
   before changing it, preserve applicable protection and hooks, and never infer
   permission to synchronize or push from a documented URL. When publication is
   authorized, verify the destination and scope before using an explicit branch
   refspec.

8. **Start with a bounded assignment and leave a handover.** Give the execution
   owner a concrete outcome, scope, preservation requirements and required
   evidence. Review returned results against that assignment. Update the target
   repository's canonical handover with the exact checkpoint, dirty work,
   evidence paths, unresolved limits and next authorized step. Keep the CodeExp2
   guide focused on how to resume; dated historical results must be clearly
   identified and rechecked next session.

## Minimum contents of a mission guide

- Purpose, authorized scope and preservation requirements.
- Target repository path and links to its instructions, plan and handover.
- Coordinator/builder roles and the verified connection procedure, if applicable.
- Read-only startup checks for current Git state and continuation state.
- Build, run/play and verification entry points, with evidence requirements.
- Approved remotes, source restrictions and commit/push boundaries.
- Handover procedure and any clearly dated checkpoint notes.

A future session should be able to find the correct repository, establish its
current state, connect to the intended executor when applicable, and identify
the next authorized action without relying on this chat's history.
