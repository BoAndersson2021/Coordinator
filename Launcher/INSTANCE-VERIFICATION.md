# Nordic names and Terminal colors — 2026-10-19

**PASS: installed Desktop entry completed named onboarding from independently reviewed source.**
The desktop launcher claims a Nordic alias and distinct dark background together,
sets per-terminal appearance, and passes the alias with its real `onboard` task.
The human alias supplements the actual session identity. Product missions and
existing unrelated terminals are outside this change.

Baseline: `main` at `18557aabb05821627ac414dc39ebbd67afb9d989`, with existing dirty
concurrent-instance instructions, registry additions and mission files preserved.
No staging, commit, push, hook-policy change or product mission execution occurred.

| Check | Observed result |
| --- | --- |
| CLI entry | Global shim and packaged native executable both reported `codex-cli 0.163.0`. Direct native exec preserves the lock in the actual TUI instead of an npm wrapper. |
| Native process ownership | Corrected candidate PID `27923`, cwd CodeExp2, retained descriptor 3 for `instance-claims/0.lock`. Kernel `F_GETLK` identified PID `27923` as the record-lock owner. |
| Real corrected crash | Killing only disposable native PID `27923` released Odin immediately. Its private helper `28336` had retained fd3 before the crash and exited before the post-crash liveness check. All five identified frontend/private-child PIDs were subsequently absent. A live surviving-helper claim is not made for this real run; the disposable regression proves that separate case. |
| Concurrency and child lifetime | Native regression starts 13 owners concurrently through self-exec, requires distinct names/colors, normal release and SIGKILL reuse. A separate child retains the exact fd/inode and stays alive after owner death; Odin must still be reclaimable. |
| Complete bounded pool | Self-test checks all 192 numeric color/name pairs; regression externally holds all 192 record locks and requires visible exhaustion refusal before any Codex launch. |
| Real Terminal color control | Terminal replied `OSC 11;rgb:4800/2400/4000` after the production Freya `#482440` background sequence, and `OSC 10;rgb:f400/f400/f400` for the light foreground. A prior disposable color probe also reported the requested `#173552` value. No saved/default profile was edited. |
| Initial alias onboarding | Earlier real Odin candidate thread `01a15418-366b-7031-8e07-f94ac7679368` completed turn `01a15418-38aa-7752-87ef-d9a08d7c7fe8` in 33,958 ms, introduced Coordinator Odin, and returned all four missions plus Start a NEW mission with no selection. This preceded the record-lock correction and title-display override. |
| Later candidate turns | Thor `01a1541a-dc42-7842-93ea-42272e624c45` and corrected Odin `01a1541f-cf9d-7da3-a5b3-074c82ec6641` introduced their assigned names and performed read-only onboarding, but collection reported interrupted turns. They do not establish completed corrected onboarding. Their disposable frontends were cleaned. |
| Complete regressions | All 20 tests passed in 32.985 seconds with native macOS access. Independent corrected launcher checks passed in 8.103 seconds. Initial sandbox `iconutil: Invalid Iconset` failure is retained as an environmental limit; native reruns passed. |
| Installed app | `python3 -B Launcher/build.py` rebuilt and signed the existing bundle in place; strict signature verification and preflight passed. Previous app retained at ignored `Launcher/build/identity-probe/previous-CodeExp2.app`. |
| Existing Desktop alias | `file` reports MacOS Alias file; native-access `mdls` reports `com.apple.alias-file`, display name CodeExp2 and kind Alias. No alias replacement was performed. |

The corrected installed executable SHA-256 is
`5122fdb2933f01ac67e576b6b7651e687b5e400c31256879570240d909672540`.
Exact reviewed source hashes and the resolved review finding are in the
[independent review receipt](INSTANCE-REVIEW.md).

Terminal appearance uses the documented [OSC title and dynamic-color controls](https://www.invisible-island.net/xterm/ctlseqs/ctlseqs.html).
Codex's [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
documents the terminal-title item setting; the launcher supplies an empty list
to prevent generated titles replacing its alias. This is its only config override.

Computer Use refused Terminal inspection. Its title query returned no reply, so
no screenshot or visually verified persistent title is claimed. Color evidence
is an actual per-terminal protocol reply; title evidence is emitted production
sequences, tested arguments and the Codex display setting. All 192 colors are
numerically unique; distinguishability of every overflow variant is unproven.
Claims apply to live instances sharing the permanent claim directory, not
arbitrary windows, historical conversations or deleted/replaced claim files.

Disposable protocol/process receipts remain under ignored
`Launcher/build/identity-probe/`.

## Final installed Desktop entry

Opening the existing `/Users/boandersson/Desktop/CodeExp2.app` alias launched
native PID `29207` on `ttys002` with the alias-bearing positional prompt and
`--config tui.terminal_title=[]`. The actual native process retained descriptor
3 for `instance-claims/0.lock`; kernel `F_GETLK` reported PID `29207` as owner.

Supported collection returned thread `01a15422-728b-7ce1-b84d-ca2fee2ca893`,
completed turn `01a15422-74ea-7e53-be82-abe06d472b54`, no error, in 42,916 ms.
Its final response began **Coordinator Odin — onboarding complete**, followed by
**Coordinator ready. No mission selected.** It listed all four current registered
missions and Start a NEW mission, preserved existing work, and left target
repositories unopened. Completed turn evidence, not thread loading status or
the terminal/process label, establishes this onboarding result.

The final installed Odin instance is left open for the owner at the mission
menu. It holds its alias/color until its actual frontend exits. Earlier
disposable frontends were terminated and the corrected crash-test frontend and
its four identified private children were confirmed absent. Shared services
and unrelated mission sessions were not stopped.
