# Nordic instance launcher source review — 2026-10-19

**PASS: independent exact-source review with no remaining required fixes.**
Reviewer `/root/nordic_launcher_review` returned completed
`builder-communication/1` verification `nordic-review-verification-002` for
assignment `nordic-launcher-review`, replying to `nordic-review-request-001`.
This receipt summarizes that completed inline JSON; it is not a byte-exact
transcript or a claim of independent runtime qualification.

The reviewer authored no implementation or instructions and changed no mission,
installed app, Git index, hook policy or remote. Its independent corrected-source
launcher run passed both focused regressions in 8.103 seconds with native macOS
access. Scoped whitespace checks passed. The complete Coordinator run separately
passed all 20 regressions in 32.985 seconds.

| Reviewed source | SHA-256 |
| --- | --- |
| `AGENTS.md` | `b48edcdb6d4500c167f0fe03553596559dc78f3bc12b89aa34ff493ab2dc0c34` |
| `Launcher/CodeExp2.swift` | `3d43e607be9f5e2ac570651a78b73e53544aa529100cc262ff9b28dc61c8931b` |
| `Launcher/README.md` | `e573ded1365d3a6e33439e28f962da6a19971f1efec6fe02873d19c44ff0d8fc` |
| `tests/test_commit_gate.py` | `e2bb85cfe509882ea3c8e464d061a8ebad8ea962b568d0135063cc5e208b2704` |
| Unchanged `Launcher/Start CodeExp2.command` | `ad19c330f2bd9957dff73f623ec15a9a6ef42f28b089e9483f612bff51e47417` |
| Unchanged `Launcher/build.py` | `db0f523f073e155c7887fe08103d921768db74500485d06e360a25dedd2f760b` |

The first implementation used `flock`. Review observed actual native Codex and
its private code-mode helper both retaining the claim descriptor, so a surviving
helper could retain that lock after TUI death. The corrected implementation uses
process-associated `fcntl(F_SETLK)` record locks: ownership survives native exec
and is not inherited by children. The added regression observes the exact claim
descriptor in a surviving sleep child, kills its owner, then immediately claims
Odin from a different process while the child is still alive.

Other reviewed cases cover 192 numerically unique names/colors, 13 concurrent
owners, suffix allocation, normal release, SIGKILL reuse, whole-pool exhaustion,
redirected-file refusal, non-TTY rejection and command-bridge path preservation.
Model/account/permission settings and structured session IDs remain separate
from human aliases; no mission is selected by launch.

The reviewer explicitly excluded installed-app rebuild, visual observation and
corrected live onboarding from its PASS. These remain Coordinator evidence in
[the runtime verification](INSTANCE-VERIFICATION.md). Perceptual distinction of
all 192 variants is unproven. POSIX locks release if their owning process closes
any descriptor for the same inode; no native code should reopen that claim file.
Changed CLI/config/provider descriptor or display behavior requires renewed
proof through the effective route.

The reviewed AGENTS alias instruction is adopted for workspace conduct under the
owner's naming request. This is separate from local commit-gate policy adoption.
No policy pins, staging, commit or push changed; future publication still needs
its normal authorization, reviewed exact-byte policy update and normal hook.
