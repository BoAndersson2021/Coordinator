# Desktop startup verification — 2026-10-18

**PASS: the installed Desktop icon started a fresh attended Terminal Codex session
and automatically completed CodeExp2 onboarding to the mission menu.**

Baseline was `main` at `ccaad221a8b411ac455bd707978367460fb02d75`, with no existing
tracked, staged or untracked changes. At that test checkpoint, implementation
and documentation were local and uncommitted; see the subsequent
[publication evidence](PUBLICATION.md). This report is Coordinator verification, not
independent review or owner acceptance.

| Check | Observed result |
| --- | --- |
| Installed CLI interface | `codex --help` accepts `[PROMPT]` as the optional first task. |
| Build | Native arm64 Swift executable compiled with installed Swift 6.2.4; app ad-hoc signed; `codesign --verify --strict` passed. |
| Preflight | Fixed workspace, required onboarding documents and executable available; no model task or Terminal opened by `--preflight`. |
| Negative preflight cases | Missing workspace, missing AGENTS, non-executable Codex and redirected workspace all rejected using disposable fixtures. |
| Terminal requirement | Calling `--terminal` without a TTY rejected clearly and started no Codex session. |
| Native alias | `file /Users/boandersson/Desktop/CodeExp2.app` reports `MacOS Alias file`. |
| Metadata | `mdls` reports content type `com.apple.alias-file`, display name `CodeExp2`, kind `Alias`. |
| Finder presentation | Get Info displays the custom terminal/2 icon and Original `/Users/boandersson/Desktop/CodeExp2/Launcher/build/CodeExp2.app`. |
| Preserve existing Desktop content | Repeating `--install-alias` rejects the occupied path; alias SHA-256 unchanged. |
| Real launch | Opened the Desktop alias with Finder's normal Open action, without entering any Terminal input. |
| Actual process | Codex PID `84848`, parent node PID `84834`, TTY `ttys002`, started 14:49:49 PDT with argument `onboard`; `lsof` confirmed CodeExp2 cwd. |
| Actual task | New thread `01a150fe-1006-7c62-acc8-c58b8743734e`, cwd `/Users/boandersson/Desktop/CodeExp2`, first user message exactly `onboard`. |
| Completed response | Turn `01a150fe-14bb-72c1-aa9a-0726db76ef0d` completed with no error in 26,374 ms, reporting **Coordinator ready. No mission selected.**, BallisticsExperimental, WEBSITE and Start a NEW mission. |
| Continued interaction | Thread was idle after completion; Terminal session left open for the human. |

The completed turn was collected with the supported `read_thread` interface,
including its final response, rather than inferring readiness from a process or
title. Direct Terminal UI inspection was unavailable through Computer Use; Finder
presentation, process/cwd checks and the completed Codex turn established the
scoped result. No product mission was selected or contacted.

Icon conversion reported `Invalid Iconset` inside the filesystem sandbox even
though generated PNG dimensions were correct. The exact conversion succeeded
outside the sandbox with approval, and the full build/sign/check route then
passed there. No workaround to Terminal input or permission settings was used.

Verified executable SHA-256:

```text
3c44cee335d50738ae95108dcd707b4c35320fa04c04959f17e3b62a9e99714f
```

Source identities:

```text
8a1c0f2ab91ae71cd551ba4f145b03b0a62df95ef2f67565df82897213ff968e  CodeExp2.swift
259527312d9622271d6c9ad44d63dd0154cfc282e1cf4fbda85b07a47d0d4148  Icon.swift
db0f523f073e155c7887fe08103d921768db74500485d06e360a25dedd2f760b  build.py
ad19c330f2bd9957dff73f623ec15a9a6ef42f28b089e9483f612bff51e47417  Start CodeExp2.command
```

This verification covers the current installation and completed test launch;
future Codex updates, authentication or trust prompts can affect startup.
The positional prompt is also documented in the
[official CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli).
