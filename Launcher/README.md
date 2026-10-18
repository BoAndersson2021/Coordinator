# CodeExp2 desktop launcher

Open the native **CodeExp2** Finder alias on the Desktop. The Swift application
opens Terminal, enters `/Users/boandersson/Desktop/CodeExp2` and executes the
installed `/Users/boandersson/.local/bin/codex` with `onboard` as its positional
first prompt. Codex submits that task automatically and remains interactive.
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

Build, sign and run the focused preflight regressions (Xcode command-line tools):

```sh
python3 -B Launcher/build.py
```

Create the native Finder alias once; refuses to overwrite any existing item:

```sh
Launcher/build/CodeExp2.app/Contents/MacOS/CodeExp2 --install-alias
```

Check prerequisites without starting Codex or opening Terminal:

```sh
Launcher/build/CodeExp2.app/Contents/MacOS/CodeExp2 --preflight
```

The launcher inherits the installed Codex account, model, trust and permissions.
It sets no overrides. Initial authentication or trust prompts, if required by
Codex, remain visible in Terminal. Closing the Terminal session exits Codex.

The desktop alias targets `Launcher/build/CodeExp2.app`. Rebuild in place to
update it, then verify signing and the alias's original target again. Never
replace the native alias with a symbolic link.

The local commit gate now admits the independently reviewed exact launcher
inventory and requires all 20 staged regressions, including a real native build
and the shipped command bridge. See [publication evidence](PUBLICATION.md).
Future executable changes still need independently reviewed source identities;
the launcher does not bypass the hook or grant runtime authority.

Launch behavior follows the local [initial-prompt law](../../DOCTRINE/Codex%20Initial-Prompt%20Launch%20Law.md),
[launcher checklist](../../Tools%20%26%20Systems/Launchers/CODEX_LAUNCHER_PATTERN.md),
and [native Finder alias law](../../DOCTRINE/Native%20Finder%20Alias%20Identity%20Law.md).
