# Valhalla launch access

The owner approved this setup on 2026-10-19. Every new CodeExp2 app launch selects
`--profile valhalla`; existing sessions retain their original effective settings.
The Coordinator owns capability provisioning and final technical validation
within the owner's task. No product mission is selected by startup.

## One overlay, no permission service

[`valhalla.config.toml`](valhalla.config.toml) is copied to
`$CODEX_HOME/valhalla.config.toml` (normally `~/.codex/valhalla.config.toml`).
Current native Codex loads this separate profile file; it is not a legacy
`[profiles.valhalla]` table. Global `config.toml`, account and model are preserved.

| Setting | Selected behavior |
| --- | --- |
| `default_permissions = ":danger-full-access"` | Full local filesystem and network access |
| `approval_policy = "never"` | No CLI command approval prompts |
| `web_search = "live"` | Live web access |
| Apps default approval `approve` | Connected app tools preapproved, including write/open-world actions |
| Node REPL and unified Computer Use MCP approval `approve` | Those supported tools preapproved |
| Browser, Chrome, Computer Use, visualization and artifact plugins enabled | Route through installed capabilities |
| `features.memories = true` | Enable native local Codex memories |

Memory generation and use are enabled, with native eligibility, idle-time and
quota defaults retained. No Computer History capture is enabled. Required rules
and mission state remain in checked-in instructions and canonical handovers;
generated memory is helpful recall, not authority or a replacement registry.

Installation is idempotent, uses an atomic owner-readable file and preserves a
different previous overlay under ignored `Launcher/build/valhalla-profile-backups/`.
The installer refuses a symlink destination. Build bundles the exact overlay;
GUI startup, Terminal entry and `--preflight` all require an identical installed
file. An intentional profile edit requires reinstalling and rebuilding together.

```sh
python3 -B Launcher/install_valhalla.py
python3 -B Launcher/build.py
Launcher/build/CodeExp2.app/Contents/MacOS/CodeExp2 --preflight
```

The existing native Desktop alias continues to point to the app rebuilt in place.
No bypass flag, privileged helper, heartbeat, new database or global approval
service is introduced. Tool-specific or managed restrictions can still override
defaults; a configured flag does not establish execution or OS consent.

## Coordinator operation

Use built-in tools and installed plugins first. Discover/install missing tools
needed for the authorized task, configure their supported route and verify a
small real action before relying on them. Keep actual tool/provider limits in
the report. Do not install speculative integrations or change another instance's
settings. Newly needed credentials, paid accounts or reserved owner decisions
remain with the owner. Full tool access grants no unrelated sending, deletion,
publication or mission execution authority.

macOS Screen & System Audio Recording, Accessibility, Automation and Full Disk
Access are separate grants to the actual responsible application/process.
Grant them only through supported system controls when needed. Computer Use
cannot approve security/privacy prompts, authenticate as administrator, or
automate prohibited targets such as Terminal and ChatGPT. Never bypass a denied
Computer Use target through screenshots, AppleScript or another automation path.
Host and provider rules remain in force even with CLI approvals disabled.

An already running session cannot acquire new launch permissions retroactively.
Open the CodeExp2 Desktop alias for the configured profile; a live check must
identify that new process/session. Existing sessions and mission work stay alone.

## References

These describe configuration and boundaries; runtime observations are recorded
separately in the verification record.

- [Codex permissions](https://learn.chatgpt.com/docs/permissions)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Computer Use permissions and restrictions](https://learn.chatgpt.com/docs/computer-use)
- [Local memories](https://learn.chatgpt.com/docs/customization/memories)
