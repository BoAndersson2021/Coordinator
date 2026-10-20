# Launcher development admission — 2026-10-18

**PASS: independent exact-byte review and local development-policy adoption.**
The user authorized committing and pushing the completed Swift desktop launcher.
Publication uses the normal commit hook and configured `origin main:main` at
`https://github.com/BoAndersson2021/Coordinator.git`. Identify the source commit
with `git log -1 -- Launcher`; a successful push requires an observed matching
remote SHA. No hook bypass or Machine runtime authority is involved.

Independent reviewer `/root/launcher_publication_review` checked the actual
sources, file modes, candidate policy, bootstrap and source manifest. It passed
all 20 tests in 31.761 seconds with no skipped tests and no findings. The
Coordinator's separate complete run passed in 31.976 seconds. The existing 18
mandatory checks remain; the two added tests are:

- `test_launcher_native_build_preflight_and_terminal_boundary`: builds/signs
  exact source in a disposable directory; checks icon/bundle/command packaging,
  negative preflight cases, non-TTY refusal and unknown-option refusal.
- `test_launcher_terminal_bridge_preserves_paths_and_arguments`: executes the
  shipped command bridge with spaces, apostrophe and dollar in its bundle path;
  requires exactly `--terminal` and a visible failure when its executable is missing.

The tests never open Terminal or start a model task. The separate
[attended desktop test](VERIFICATION.md) covers the completed onboarding result.
Full native test execution needs normal macOS access: initial sandbox runs hit
the observed `iconutil` failure, and approved outside-sandbox runs passed.

The policy adds only five exact launcher paths (`.gitignore`, both Swift files,
`build.py` and `Start CodeExp2.command`), updates the regression suite's source pin
and adds the two test IDs. Previous instruction pins, reviewed deletions and
mandatory tests are preserved. The trusted verifier is byte-identical; the
bootstrap changes only its policy digest. All new source entries use mode `100644`;
the build creates the executable bundled command with mode `755`.

| Reviewed input | SHA-256 |
| --- | --- |
| Independent review receipt | `8d6366324c99e23f36241b53fb6c960b24a1058557b84d43b94e99825e591df2` |
| Unchanged verifier | `4f54ab68d6f7c379ea27f7359a145e3f05b93d4b48b082ffd08f5ccf04d4f286` |
| Adopted policy | `e6600eff52f7070fe385c8f09382dc7358ea5f70709bfacfd56404474b78d9c1` |
| Adopted bootstrap | `3cdf0c99f3d77de79040303995741ff1d4cdb09c95b38c5ddc387b2d94cb3282` |
| Regression suite | `5b204402c379b5d86e7fd6ae9369dcd6a6535ff7cc6f87634e48b664c7544428` |
| Independent native test log | `5a7a7968919f1ef862d937e94e5937c4b5b1a998e95db3304e7458ca89d10f7b` |

Before adoption, the Coordinator collected the completed matching review,
parsed its complete report, checked its hash and every referenced evidence hash,
and rechecked candidate, source, installed-input and Git-configuration identities.
Adoption at `2026-10-18T22:03:36.465179+00:00` preserved the previous installed gate,
unchanged Git configuration, exact manifest, complete review, successful native
log and failed sandbox log under
`.git/codeexp2-launcher-adoption-5ucktqqs/`. The adoption receipt lives there as
`adoption.json`. No HEAD, staged selection or runtime permissions were changed
by adoption. The subsequent normal commit hook verifies staged source and runs
every mandatory test; missing, skipped, failed or incomplete checks still block.

Generated app binaries, icons and build caches remain ignored and local. The
Desktop native alias remains installed and points to `Launcher/build/CodeExp2.app`.
The reviewed source can rebuild that application. A source commit neither
installs this local gate on another checkout nor selects any product mission.

## PANEL bridge admission — 2026-10-20

The owner authorized committing and pushing the Valhall PANEL entry. This adds
`--panel-agent`, its canonical-profile projection and three bounded bridge
regressions. PANEL continues to use native onboarding, aliases and mission
selection. No model conversation is created by the publication tests.

Independent PANEL builder `01a155cd-9b3e-7433-b0e7-eeb730e6be6d` reviewed the
Coordinator-authored root sources, candidate policy and bootstrap. Its final
review passed all three launcher gate tests in 15.614 seconds; the new wrapper
requires all three exact nested bridge successes and completion. The Coordinator
separately passed all **51 tests from the exact staged source**. The normal
installed commit hook remains required.

The policy updates three existing source pins, admits only
`Launcher/test_panel_bridge.py` as a new source path, and adds one mandatory test,
`test_launcher_panel_bridge_regressions`. All 22 previous mandatory IDs,
instruction pins, deletion requirements and other inventory entries remain.
The verifier is unchanged; the bootstrap changes only its policy digest.

The launcher build requires Python 3.11 or newer for standard-library `tomllib`.
The trusted Apple Python gate remains unchanged; launcher checks select and probe
a supported interpreter from their environment. The independent initial shell
lacked that interpreter on PATH; its failure is retained. A per-command PATH
exposing installed Homebrew Python 3.14.8 resolved it. The successful rerun used
`/usr/bin/env`, since this host's unqualified `env` is a PATH-only user helper.
No source repair, skipped check or global configuration change was needed.

| Reviewed/adopted input | SHA-256 |
| --- | --- |
| Independent final review | `29ba739c2f7b927e90c14753d9d3f7878357c2430c65c3a9a22a483f26fd4e56` |
| Policy | `894ae5121f1becb75bf1d1fb66adbcd631e0343aa1626e2dcb4bdda1c80b13da` |
| Bootstrap | `fc09b741c2b4905ba99d5671cc5561e75011905cd08eaa81eb6aa01c3ac09235` |
| Adoption receipt | `d84ca35cca68cf5691fbb5b0d9f35a328a05be8a9f73372cdda9e4086d13a312` |

After collecting the matching completed review and verifying all input hashes,
the Coordinator adopted only the reviewed policy/bootstrap. Previous trusted
bytes, unchanged Git configuration, both review attempts and successful staged
checks are retained privately under
`.git/codeexp2-panel-adoption-20261020-7vfy2qb_/`. The full review is also retained
in PANEL's `Evidence/Implementation/20261020-valhall/`. Binaries, account/native
frames, local conversation state and unrelated mission work are excluded.
