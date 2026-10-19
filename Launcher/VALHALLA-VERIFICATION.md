# Valhalla installation and verification — 2026-10-19

**Installed and verified for new CodeExp2 app launches.** The owner approved
execution of the proposed full-access setup. This is workspace launcher/tool
maintenance; no product mission was selected or executed.

This records the access-setup checkpoint before the subsequent Valhall rebrand.
The later owner-authorized [publication](VALHALL-PUBLICATION.md) reviews the final
staged sources separately; historical source hashes below retain their scope.

## Observed results

| Check | Result and scope |
| --- | --- |
| Profile installation | Installed `~/.codex/valhalla.config.toml`; source, installed and bundled bytes match. Installer does not write global `config.toml`. |
| Native application | Built in place and ad-hoc signed; `codesign --verify --deep --strict` passed. Missing/mismatched overlay is rejected visibly. |
| Desktop entry | The old Desktop alias was missing at verification time. The existing `--install-alias` route restored a native Finder alias to `Launcher/build/CodeExp2.app`; opening it started the actual native TUI. |
| Actual launch | Frontend PID `36992` started with `--profile valhalla --config tui.terminal_title=[]` and the Freya onboarding prompt. |
| Effective permissions | The actual session's recorded turn context reports `approval_policy: never`, `sandbox_policy.type: danger-full-access`, and disabled filesystem permission profile. Native `debug prompt-input` separately reported full filesystem/network access and never approval. |
| Onboarding | Session `01a1543d-4dbd-7b83-8643-4e22f757931e`, turn `01a1543d-5029-7411-ac8c-ffead5145426`, completed in 47,233 ms as Coordinator Freya: all five registered missions plus NEW choice; no mission selected. |
| Native macOS control | Existing supported Computer Use host opened Calculator and clicked `2 + 2 =`; accessibility state and screenshot showed `4`. |
| Screenshots | Calculator window and Safari website screenshots captured through `cua_repl`. No security/privacy prompt was encountered or approved by the agent. |
| Browser route | Dedicated browser inventory was empty and `iab` unavailable. Supported native Safari control opened a separate public example page, read its state and captured it. Only the disposable test tab was closed. |
| Debug/install tools | Installed LLDB ran successfully (`lldb-1703.0.236.103`). Python, Swift/Xcode, Homebrew, Node/npm, Git and curl are present. No speculative package installs were needed. |
| Native memory | Profile enables memory generation and use. Background consolidation/recall was not forced or proven; native idle/quota/eligibility rules remain. |
| Visualization/artifacts | Installed plugins enabled in the selected profile. No unrelated document, visualization, paid image or published website was created merely to test availability. Provider execution remains task-specific. |
| Regressions | All 20 existing suite tests passed in 34.019 s, including native launcher, claim lifecycle, bundled profile and installer backup/idempotence/global preservation/symlink refusal. Earlier focused 2/2 launcher tests passed. |

Computer Use tests above ran through this Coordinator's existing supported host,
not by sending a tool assignment into Freya. They prove that host's observed app
control/screenshot route. Freya's actual launch and effective permissions are
separately evidenced; they do not establish execution of every provider tool in
every future session. Existing terminals retain their original effective access.

## Review and adoption

Independent reviewer `/root/nordic_launcher_review` returned PASS with no material
defects or required fixes. The complete [source review](VALHALLA-REVIEW.json)
was collected, parsed, hash-checked and all eight reviewed source hashes matched.
Review receipt SHA-256:
`80092ccc19f96b18c95e5ca33da12816fc810d60b4b6a5ec80aef5519998fced`.

The reviewed root AGENTS capability-provisioning and technical-validation rule
is adopted for Coordinator conduct under the owner's approval. Reviewed AGENTS
SHA-256: `7f46977c643e25da3b90aee548f5a14e102c090e3eb8d6d94e443b4632be3949`.
Profile SHA-256: `b2a3f2030f69a67f7d0134e7ec35f3627f2d6026128f9bfaea284074305ee4ee`.

This is distinct from commit-gate adoption. No staging, hook-policy change,
commit or push was performed for this setup. Future publication still requires
normal exact-source gate review/adoption and mandatory staged checks. Unrelated
mission/registry work and existing owner instances were preserved.

## Evidence and limitations

Ignored local evidence remains under `Launcher/build/valhalla-verification/`:

- `app-session.json`, extracted only from the actual app-created session log:
  SHA-256 `aaa84817678011dac66190f76d112e92c20a4bd9c95d674b3da1602c719d7863`.
- `calculator.png`: SHA-256
  `b4f9bf9e43ba2ae9913413372ff5789998869dba6d340e86aa80d8a9adb0106f`.
- `safari.png`: SHA-256
  `e317c4c2479eec90bb55446e96986c1bc04cc991c7452a61c50d4f37e406dca1`.
- `prompt-input.json`: native rendered permission diagnostic before the later
  memory flag addition; the app-session context verifies final launch permissions.
- `source-review.json`: byte-identical local copy of the durable review above.

Preserved diagnostic failures: the root's sandbox initially denied native
prompt-input; its approved escalated retry succeeded. `features list` rejects
`--profile` by design; plain feature inventory succeeded. Initial Desktop open
failed because its alias was absent, then the native restoration/open succeeded.
The background thread API initially exposed an interrupted snapshot and refused
a message with `already has an active writer`; no assignment was delivered.
Later collection and the native log agree on the completed onboarding turn.

No general Full Disk Access, administrator elevation, provider authentication or
every-app consent is claimed. Host/provider restrictions remain, including
Computer Use's prohibited targets and inability to approve security/privacy
prompts. The currently loaded global legacy `sandbox_mode` also requests full
access; legacy or managed settings can affect merging. Recheck effective access
after relevant configuration/CLI changes rather than relying on source bytes.

Use the Desktop CodeExp2 alias for new Valhalla instances. Provision and verify
further capabilities when the selected task actually needs them; surface only
specific owner-controlled steps that supported tools cannot complete.
