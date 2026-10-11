# Launching a repository app into Terminal and Codex

Use this pattern when a small desktop app should open a repository in an
interactive Codex CLI session. The app is a front door; the repository's
instructions and Codex CLI remain responsible for project context and work.

## Component chain

```text
User opens the desktop app or shortcut
  → app validates its configured repository and CLI paths
  → app asks the user's terminal to run a narrowly constructed command
  → terminal starts Codex with the intended repository as its working directory
  → Codex reads repository instructions and presents a scoped first task
  → the model responds or requests a tool action
  → Codex harness checks and routes allowed tool requests
  → tools execute in the configured environment
  → results return to the Codex conversation as new context
```

The model generates text or structured tool requests. It does not itself open
the terminal, inspect files, or execute commands. The CLI harness assembles
context, applies its permission rules, routes requests, runs tools through the
available execution environment, and returns their results. The desktop app
should not impersonate any of those roles or silently widen their access.

## Decide the launch contract

Before implementing a wrapper, establish:

- the canonical repository path, and how the app behaves if it moves or is
  unavailable;
- the terminal and Codex CLI entry points for the target operating system;
- the project instruction files Codex must read;
- a harmless startup action, such as showing status, help, or a project
  overview;
- which operations need additional user approval, such as editing, deleting,
  deployment, spending money, or running long or expensive jobs;
- how the wrapper will report a failed check or launch.

Keep project-specific rules in the repository (`AGENTS.md`, other scoped
instruction files, and project documentation). Keep the app's initial prompt
short: identify the repo, point to the relevant instructions, request one
read-only starting action, and name any explicit approval boundaries. A prompt
provides context; it does not override operating-system permissions, CLI
policies, or project command checks.

## A safe launch shape

The following is a shape, not a copy-paste installer. Replace the placeholders
with validated values and use the platform's proper argument APIs rather than
concatenating unchecked input into shell or AppleScript source:

```sh
cd /absolute/path/to/repository
exec codex -C /absolute/path/to/repository \
  "Read the repository instructions, then show a read-only project overview."
```

Prefer launching a terminal with an argument array when the desktop framework
supports it. If the platform requires a script handoff, write a private,
short-lived script with safely quoted values, restrictive permissions, and a
known cleanup policy. Do not place credentials, tokens, or arbitrary user text
in the script. Do not leave a world-writable command file or use a shared,
predictable temporary filename.

On macOS, a compiled AppleScript applet can open a private executable `.command`
file in Terminal through LaunchServices. If the applet is denied access to a
protected project folder, let Terminal run the repository checks and Codex
instead of having the applet read project files first. Use system-provided
utilities by their verified paths, and test the actual built `.app`; changing
source does not update an existing app bundle or desktop alias by itself. An
alternative is Apple Events control of Terminal, which may require the user to
grant the app Automation access in System Settings. Choose one handoff and
document the permission it needs.

On Linux or Windows, use the user's configured terminal application and its
documented launch interface. Do not assume macOS `.command` handling or
AppleScript permissions exist on those platforms.

## Keep startup read-only

The first launch should check that the repository exists, the CLI is available,
and required local configuration can be found without printing secrets. Then
open Codex in the intended repository and start with a read-only status/help
operation. Do not run dependency installation, model inference, project
initialization, migrations, deployment, or other state-changing setup merely
because the app opened. Let the user and project workflow decide those actions.

Where possible, let the repository's own supported CLI own project work. This
keeps validation, permissions, immutable-output rules, and result recording in
one place instead of duplicating them in the desktop wrapper.

## Verify the complete path

Verify each layer independently, then test the user-visible handoff when
authorized:

1. Inspect the repository's instruction files and the wrapper implementation.
2. Run a dry-run that displays the resolved repo, terminal, Codex path, and
   safely represented argument list without launching work.
3. Run a read-only preflight for the repo and CLI prerequisites.
4. Inspect the compiled app or generated launch script to confirm it points at
   the intended repo, constructs the expected command, and reports errors.
5. Open the app and confirm the terminal starts Codex in the correct repo.
6. Confirm Codex receives the intended instruction context and completes the
   harmless startup action.
7. Check that startup did not write project state or start expensive work.

Distinguish a successful build or dry run from a live terminal handoff. A live
Codex startup verifies the launch and initial context, but it does not prove
that every later tool call, external integration, or project operation works.

## Common failures

- **Missing CLI or wrong version:** resolve the executable path explicitly;
  report a useful error and show how to check the installed CLI's local help.
- **Wrong working directory:** pass the repository root through the CLI's
  supported working-directory option and verify it in the terminal.
- **Protected-folder denial:** determine which process touched the repo. Move
  that read into the terminal process when appropriate, or have the user grant
  the narrow operating-system permission required by the design.
- **Automation/terminal permission denied:** the app is trying to control the
  terminal through the platform's automation mechanism. Either have the user
  grant that exact permission or use a supported launch handoff that avoids it.
- **A source fix has no effect:** rebuild the app bundle, confirm the shortcut
  points to that bundle, and inspect the compiled launch script.
- **Command quoting or injection risk:** use argument arrays or safe platform
  quoting. Never treat shell metacharacters in repo paths or prompt text as
  harmless.
- **Secrets appear in logs or launch files:** remove the leak, rotate exposed
  credentials as appropriate, and use the existing provider sign-in mechanism.

## Reusable acceptance record

```text
Repository and configured path:
Desktop app / shortcut artifact:
Terminal and Codex command used:
Repository instructions loaded:
Read-only startup action and observed result:
Operating-system permissions required:
Build, dry-run and live-handoff checks:
State-changing work deliberately not started:
Remaining platform or integration limits:
Working tree / commit state:
```
