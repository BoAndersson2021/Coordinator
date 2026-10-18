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
