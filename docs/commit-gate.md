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
                             Stage meaningful regressions too
                                    |
                                    v
                             Extract and test INDEX source
                                    |
                                    +-> mandatory successes + completion -> permit
                                    +-> missing / skipped / failed -> reject
```

The current adoption admits only the checker and its regression suite as
executable development files. It does not admit the future mission runner or
Machine runtime. Later feature work must extend the independently reviewed local
policy with its actual source and meaningful mandatory tests. Gate tests alone
cannot qualify a new mission feature.

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

Adoption must preserve the previous hook and configuration, copy only reviewed
bytes into an owned directory under this checkout's Git directory, install the
digest-pinned bootstrap and record the independent review and checks. Never
use `--no-verify` or install an unreviewed working-tree replacement. Keep adoption
separate from a source commit; no source commit is implied by installation.
