# CodeExp2 commit gate

The development gate checks commits; it does not launch missions or authorize
runtime workflows. [Avoid excessive blocks](how-not-to-overblock-development.md)
and preserve the separate Machine execution invariant.

The checker is `scripts/check_staged.py` with `tests/test_commit_gate.py`.
Independent exact-byte review passed and local adoption took place on 2026-10-18.
See [the adoption and verification evidence](../Missions/ControlWorkflowEvidence/20261018-commit-gate.md)
for installed source hashes, scope, previous-hook backup and actual check results.

```text
Normal git commit
      |
      v
Installed bootstrap verifies its pinned verifier and reviewed policy
      |
      v
Reject redirected Git inputs and unresolved stages
      |
      +-> ordinary documents -> lightweight content checks -> permit
      +-> instruction edits  -> independently reviewed exact bytes -> permit
      +-> executable/data    -> reviewed development inventory
                                    |
                                    v
                       Declare related features + preservation receipt
                                    |
                                    v
                    Stage requested-path and counterpart regressions too
                                    |
                                    v
                 Extract INDEX source; receipt checks must all pass
                                    |
                                    +-> mandatory successes + completion -> permit
                                    +-> missing / skipped / failed -> reject
```

The initial adoption admitted only the checker and its regression suite as
executable development files. The independently reviewed
[launcher publication](../Launcher/PUBLICATION.md) extends that exact inventory
to the native Swift desktop launcher, with two additional mandatory regressions.
It does not admit a mission runner or Machine runtime. Later feature work must
extend the independently reviewed local policy with its actual source and
meaningful mandatory tests. Gate tests alone cannot qualify a mission feature.

The installed policy records exact file modes, SHA-256 identities and mandatory
test IDs. The installed bootstrap pins the verifier and policy before executing
either. Staged replacement scripts cannot become their own trusted validators.
The verifier creates a temporary index snapshot and runs its tests there;
unstaged repairs cannot hide staged failures. A zero exit without the runner's
completion record fails. Reviewed deletions can be admitted explicitly.

Run candidate regressions from CodeExp2:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_commit_gate.py' -v
```

The suite makes real commits in disposable repositories with local fixture
policies. It does not modify the live index, hooks, target repositories, remotes
or runtime processes. The fixture policy is test setup, not live adoption.
Git may refresh index cache metadata during a rejected commit; tests preserve
the staged paths, modes and object identities, plus HEAD and dirty file content.

Mandatory regression groups are scoped to the staged source paths they protect.
The core commit-gate suite runs for reviewed gate changes; Launcher and native
control regressions run when their owned paths change. This prevents unrelated
uncommitted work from making a reviewed documentation or gate correction
uncommittable, while preserving the required regression for each protected
feature path.

## Feature-preservation receipt

For every admitted system-change scope, a preservation-enabled reviewed
development policy requires a `feature_preservation_receipts` entry. It is
checked by the existing staged-source verifier; it is not a new service,
database, hook, or runtime workflow. The candidate is not installed hook
enforcement until independent review and adoption complete.
The entry names the changed boundary, exact covered staged paths, discovery
evidence, each related feature and counterpart check, limitations, and the
required truthful attestation. Its checks are added to the index-snapshot run.

A receipt passes only when every identified related feature is preserved, or an
explicit owner decision names its intentional replacement and acceptance check.
Empty inventories without discovery evidence, UNKNOWN/failed states, stale
candidate references, new-path-only tests, a counterpart check reused from the
requested-change check, omitted covered paths, or a missing counterpart check are
commit-blocking failures. A receipt proves declared checks
ran; it cannot prove an agent discovered every product behavior. The mandatory
pre-edit inventory in Feature Preservation therefore remains required.

This is additive: the receipt validator is another branch in the existing
`scripts/check_staged.py` verifier reached by the existing pre-commit bootstrap.
It does not replace the hook, bootstrap, pinned policy, redirected-input defense,
instruction protection, reviewed-source inventory, index snapshot, or any prior
mandatory regression. A receipt never substitutes for one of those checks.

The local hook remains checkout-scoped. Each mission target adopts the same rule
through its own existing candidate-source gate during host adoption; copying this
hook into a target is neither required nor sufficient.

For the user-authorized local Machine/archive cleanup, the deletion regression
first reproduced the missing protected-file passing route. The verifier now
accepts a protected deletion only when that exact path has an explicit `null`
entry in the independently reviewed instruction policy. Missing entries, old
content pins and replacement instructions still reject deletion or replacement.
Executable/data deletions also require an explicit reviewed inventory and
successful staged regressions. This does not authorize deleting other paths or
change Machine runtime enforcement.

The cleanup correction received independent exact-byte PASS from
`/root/review_folder_removal`. All 18 tests passed in the working tree,
independent review (24.864 seconds) and the real staged snapshot through the
candidate bootstrap (24.918 seconds). The adopted policy enumerates exactly
24 protected deletions and 697 executable/data deletions, plus the reviewed root
instruction hash and checker/test hashes. The remaining 353 deletions are
ordinary documents. No wildcard deletion permission was added.

The installed gate remains `.git/codeexp2-commit-gate/`. Previous installed
bytes, unchanged configuration hash, exact candidate identities, independent
review and adoption receipt are retained under
`.git/codeexp2-cleanup-adoption-20261018-931empp8/`. Review SHA-256:
`1629dc83b8617279419e471e05e171099aa42330b27afd539004cc3c2fb5990e`.
The installed bootstrap continues to verify its policy and verifier before
running staged-source checks; no hook bypass or runtime change was used.

Adoption must preserve the previous hook and configuration, copy only reviewed
bytes into an owned directory under this checkout's Git directory, install the
digest-pinned bootstrap and record the independent review and checks. Never
use `--no-verify` or install an unreviewed working-tree replacement. Keep adoption
separate from a source commit; no source commit is implied by installation.

## Shared native-control development admission — 2026-10-19

The independently reviewed session-lessons inventory adds the bounded native
control client, evidence checker, diagnostic/proof reader, declared transport,
28 offline regressions and fixture data. One new mandatory wrapper requires all
28 exact successes/completion with native transport forbidden; the prior 21
mandatory IDs, file/instruction/deletion requirements and verifier are preserved.
Final exact staged source passed 50 tests through the reviewed pinned bootstrap.
The exact policy/bootstrap are adopted with previous trusted bytes and unchanged
configuration preserved. See the [delivery/adoption record](../Missions/ControlWorkflowEvidence/20261019-session-lessons-delivery.md)
for hashes, backup, independent source review, native proof and continuation.
This extends development admission; product mission dispatch and executor
retirement still need their own applicable authority and runtime evidence.

## Structured mission documentation

The owner authorized a bounded correction after the gate rejected IMPACT's
canonical coordination record as executable data. The documentation route also
admits regular non-executable UTF-8 JSON files at these exact mission locations:

| Path under `Missions/<mission>/` | Required `format` |
| --- | --- |
| `MISSION.json` | `codeexp2-mission-coordination/1` |
| `REPOSITORY-RENAME.json` | `codeexp2-repository-relocation/1` |
| `REMOTE-DECOMMISSION.json` | `codeexp2-remote-decommission/1` |

Each record must be an object with a nonempty string `mission`, and a `consumer`
object declaring `kind: "agent-interpreted"` and
`grants_execution_permission: false`. Duplicate keys, non-finite numbers,
malformed JSON, unsupported formats, executable modes and symlinks are rejected.
The maximum document size is 1 MiB. Both old and new staged bytes are checked
for edits; deletion requires a valid old document. Shared package/evidence
directories and nested paths are excluded.

This is a content classification for committing documents. It does not validate
their full semantics, establish registration/readiness, authorize commands, or
grant runtime effects. Operational/configuration JSON still needs reviewed
development admission. Protected instructions retain their independent review
checks. No generic JSON exception is installed.

## Mission evidence records

Root-level evidence records may use the narrow `codeexp2-mission-evidence/1`
content route when their filename matches `*-VERIFICATION.json` under
`Missions/<mission>/`. They must include a nonempty `schema` and `mission`,
`evidence_only: true`, and an agent-interpreted consumer that explicitly grants
no execution permission. This route rejects nested paths, packages, shared
control evidence, executable modes, malformed JSON, non-finite values and
duplicate keys.

This permits inert coordinator/reviewer observations only. Assignments,
acknowledgements, setup requests, Builder Communication envelopes, configuration
and any record that can direct a receiver remain executable/data changes subject
to the exact reviewed development inventory. The route does not validate evidence
truth, create a runtime consumer, grant authority or permit an operational JSON
exception. It rejects every Builder Communication envelope field even when a
record falsely claims the evidence format.

Five mandatory disposable-commit regressions cover legitimate add/edit/delete,
malformed or permission-granting records, path/mode boundaries, staged-versus-
working-tree bytes, and operational/protected JSON refusal. Existing mandatory
tests and policy protections remain required. Adoption preserves the previous
gate and Git configuration under `.git/codeexp2-mission-doc-adoption-*/`; its
exact-byte manifest, independent review, test logs and adoption receipt identify
the installed correction. No hook bypass or runtime qualification is implied.
