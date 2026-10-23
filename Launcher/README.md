# Valhall — CodeExp2 desktop launcher

Open the native **Valhall** Finder alias on the Desktop. The Swift application
opens Terminal, enters `/Users/boandersson/Desktop/CodeExp2` and executes the
installed native Codex executable with `onboard` and its assigned human alias as
the positional first prompt. Codex submits that task automatically and remains interactive.
Onboarding follows the current workspace instructions and stops at the mission
menu with no mission selected. Existing Codex sessions are left alone.

The launcher checks the fixed workspace, required onboarding documents and
executable before launch. Terminal receives the bundled `.command` through
macOS Launch Services; it needs no Apple Events or Accessibility permission.
There is no delay, terminal polling or simulated typing/Return. Successful app
opening is not a claim that Codex has finished onboarding: its actual completed
response is the readiness evidence.

Source is in this folder. Generated binaries, icons and build caches are ignored
under `build/`; keep that directory because the Desktop alias points into it.
This is CodeExp2 workspace startup tooling, not a product mission or mission runner.

Build, sign and run the focused preflight regressions (Xcode command-line tools
and Python 3.11 or newer):

```sh
python3 -B Launcher/install_valhalla.py
python3 -B Launcher/build.py
```

Install/refresh the native Finder alias. A matching former `CodeExp2.app` Desktop
alias is renamed to `Valhall.app`; an existing matching Valhall alias gets its
icon refreshed. Unrelated Desktop entries are preserved:

```sh
Launcher/build/CodeExp2.app/Contents/MacOS/CodeExp2 --install-alias
```

Check prerequisites without starting Codex or opening Terminal:

```sh
Launcher/build/CodeExp2.app/Contents/MacOS/CodeExp2 --preflight
```

The launcher selects the owner-approved **Valhalla** profile for full local and
network access, no CLI approval prompts, live web search, native local memory and
supported tool approvals. Account, model and trust remain inherited. See
[setup, capabilities and limits](VALHALLA.md). Source and installed profile must
match; a missing/different overlay fails visibly before starting a session.
`tui.terminal_title=[]` keeps the instance alias visible instead of Codex's
generated progress title. Initial authentication or trust prompts, if required
by Codex, remain visible in Terminal. Closing the Terminal session exits Codex.

## PANEL chat entry

PANEL's **Spawn new agent in new chat** uses the same built executable with
`--panel-agent`. This entry validates the workspace and installed profile,
claims an alias through the existing lock pool and emits one local JSONL
`valhall/launch` notification containing its alias, color, process ID, fixed
workspace and existing onboarding prompt. It then directly executes the native
Codex app server over stdio. PANEL initializes that receiver, creates one chat
and submits the normal onboarding prompt; CodeExp2 supplies the mission menu.
The notification alone proves neither native readiness nor completed onboarding.

The installed app server does not accept `--profile`. `build.py` derives
`valhall-panel-profile.json` from the same canonical `valhalla.config.toml`,
using native `--config` arguments and a source hash. There is no second profile,
mission registry or alias allocator. The bridge refuses a missing/stale
projection. Native account, model, managed requirements and unrelated inherited
configuration remain in effect.

The actual server process holds its alias lock until it exits. Closing its
stdio input stops that owned server. PANEL retains the native conversation ID;
a later explicit reconnect can claim another running-instance alias while
resuming that same saved conversation, without replaying onboarding. This entry
does not attach an existing standalone Terminal.

Run the bounded bridge regressions with `python3 -B Launcher/test_panel_bridge.py`.
They build a disposable launcher and verify exact effective profile values,
simultaneous claims, release on exit, projection drift and launch boundaries.
They create no model conversation and open no Terminal.

## Instance names and colors

Each new launcher-created instance claims the first free pair from this fixed
Nordic list. The Terminal title becomes **CodeExp2 — Odin**, for example, and
onboarding introduces **Coordinator Odin**. The human alias supplements the real
session ID; it is not a mission selection or a permanent conversation identity.

| Alias | Background |
| --- | --- |
| Odin | `#19334d` blue |
| Thor | `#4c211b` rust |
| Freya | `#482440` plum |
| Loki | `#18422c` green |
| Tyr | `#483a16` ochre |
| Heimdall | `#124346` teal |
| Balder | `#2e2853` indigo |
| Frigg | `#4d2630` rose |
| Njord | `#163f59` ocean |
| Freyr | `#35451e` olive |
| Skadi | `#2c3f49` slate |
| Idunn | `#40304c` violet |

One nonblocking OS record lock (`fcntl(F_SETLK)`) reserves both name and color atomically. Claim files
stay under ignored `Launcher/build/instance-claims/`; **never delete them while
instances may be running**. File existence is not occupancy. The inherited open
descriptor holds the lock in the actual Codex process (TUI or PANEL server); normal exit,
crash or reboot releases it without a heartbeat, PID register or cleanup job.
The lock belongs to that process and is not inherited by its children, even
when they retain a copy of the descriptor. No native code should reopen/close
the same claim file: POSIX record locks are also released if their owning
process closes another descriptor for that inode.
An alive but hung process retains its name. A saved conversation may outlive the
Terminal instance; resuming it does not reclaim its former alias automatically.

After twelve live instances, names continue `Odin-2`, `Thor-2`, etc., with distinct
lighter color variants. The bounded pool contains 192 unique name/color pairs;
exhaustion fails visibly before launching Codex. Color uniqueness applies to
instances started by this launcher, not unrelated Terminal windows or older
sessions. Appearance uses per-terminal OSC title/foreground/background/cursor
controls; saved/default Terminal profiles remain unchanged.

The fixed native entry is the arm64 executable in the installed npm package:
`/Users/boandersson/.npm-global/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex`.
The previous shell/Node entry launches a child without retaining extra file
descriptors there. Direct native `execv` keeps the lock with the real TUI and
avoids a supervisor. The global shim is untouched. If the native installation
moves or disappears, preflight fails clearly; it does not silently use a wrapper
that would weaken claim lifetime.

`--preflight` and the app's GUI phase claim no name; the checked Terminal and
PANEL entries do. The private `--claim-probe` regression entry re-execs the same binary
and holds a disposable claim until EOF/termination; it launches no model task.
The native self-test checks the complete palette. The existing
launcher regression exercises concurrent processes, exec inheritance, normal
exit, SIGKILL/reuse with a surviving descriptor-inheriting child, whole-pool
exhaustion and redirected-file refusal.

The desktop alias targets `Launcher/build/CodeExp2.app`. Rebuild in place to
update it, then verify signing and the alias's original target again. Never
replace the native alias with a symbolic link.

The app's visible name is **Valhall**, using the Swedish spelling. Internal
workspace paths, executable and bundle identifier retain CodeExp2 for continuity.
The Viking artwork is project-owned [`valhall-icon.png`](valhall-icon.png),
packaged into all native icon resolutions by `Icon.swift`. Regenerate only when
requested; builds use the checked-in source image and make no image-service call.
On hosts where `iconutil` rejects every generated iconset, the build uses the
checked-in valid [`Valhall.icns`](Valhall.icns) only when both its own hash and
its source-PNG hash match; an artwork change must package a fresh icon rather
than silently reuse it.
See the [artwork prompt](VALHALL-ICON.md).

The local commit gate now admits the independently reviewed exact launcher
inventory and requires all 20 staged regressions, including a real native build
and the shipped command bridge. See [publication evidence](PUBLICATION.md).
Future executable changes still need independently reviewed source identities;
the launcher does not bypass the hook or grant runtime authority.

Launch behavior follows the local [initial-prompt law](../../DOCTRINE/Codex%20Initial-Prompt%20Launch%20Law.md),
[launcher checklist](../../Tools%20%26%20Systems/Launchers/CODEX_LAUNCHER_PATTERN.md),
and [native Finder alias law](../../DOCTRINE/Native%20Finder%20Alias%20Identity%20Law.md).
