# CodeExp2 development-gate correction and adoption

Date: 2026-10-18. Scope: development verification, not mission runtime.

The user requested the needed regressions, challenged blanket executable denial
and requested [a guide against excessive blocking](../../docs/how-not-to-overblock-development.md).
That guide is linked from AGENTS and README. The development gate now has a
reviewed passing route for the exact checker and regression sources below.
Other executable/data paths still require their own reviewed source inventory
and meaningful tests. No mission controller or Machine runtime is qualified.

## Verification and independent review

| Check | Outcome | Evidence |
| --- | --- | --- |
| Initial work-tree suite | Failed on index-cache byte comparisons and Git hook output routing | [Retained failed log](20261018-commit-gate-first.log) |
| Corrected suite | All 16 tests passed | [Second log](20261018-commit-gate-second.log) |
| Independent exact-source review and execution | PASS; all 16 tests, 19.623 seconds | Reviewer `/root/commit_gate_review`, exact-byte review returned in the coordinator session |
| Real staged snapshot through candidate bootstrap | All 16 tests passed, 19.710 seconds | [Staged log](20261018-commit-gate-staged.log) |
| Installed bootstrap on real staged snapshot | All 16 tests passed, 20.197 seconds | [Installed log](20261018-commit-gate-installed.log) |

The corrected assertions compare staged paths, modes and object identities,
HEAD and dirty content. Git can refresh index cache metadata before invoking
hooks, even on a rejected commit. Hook output may be routed to stderr by Git.
These corrections preserve the actual staging and content requirements.

The tests perform real passing and rejected commits in disposable repositories.
They cover ordinary document add/edit/delete, reviewed code admission, missing
staged regressions, unknown paths, unreviewed source bytes, staged failures hidden
by repaired working copies, passing staged source with unstaged failing edits,
missing/renamed/skipped/expected-failure/failing mandatory tests, early zero exit
and missing completion, protected instructions, malformed documents, symlinks,
executable document modes, redirected Git inputs, missing/changed trusted inputs,
unresolved stages and preservation of unrelated work.

## Independently reviewed identities

| Artifact | SHA-256 |
| --- | --- |
| `scripts/check_staged.py` | `5078f298fa2840e7917385bb09133978056215e1751182405d5ace86e9e07508` |
| `tests/test_commit_gate.py` | `ad0885a542db0ed362e8a9c6f59cbf454185fee799733edb613e9629447c1084` |
| Installed `reviewed-policy.json` | `09c3a2831de1718255ad3392aa5a41c877fe13e87c4aef7ff910e636eafb77da` |
| Installed `pre-commit` | `8d1189c8b5d81802fc4bfe17eb07c9e00579187644a5eb7b46151b481f782c46` |
| Reviewed root `AGENTS.md` | `9c7b696bde118cf714446237597f6775dd153ac7c266ee9676c32928e01d49a3` |
| New overblocking guide | `9e0411960fab0038144faef78772293f472ea9c6cc8e46a280fa1d7f2d10d847` |

The reviewer inspected the actual candidate policy and bootstrap, not a future
inventory description. The policy contains exactly the two development sources,
their modes and hashes, all 16 mandatory test IDs, and the reviewed root/Machine
instruction pins. The original Machine instruction pin is unchanged.

## Local adoption

Installed directory: `.git/codeexp2-commit-gate/`. Git's local `core.hooksPath`
now points there. Its bootstrap verifies the installed verifier and policy
digests before running isolated stdlib Python. The verifier tests index blobs
in a temporary snapshot and requires successful mandatory IDs plus completion.
It cannot substitute a working-tree repair or execute a staged replacement as
its trusted verifier.

The previous hook remains untouched at `.git/hooks/pre-commit`; its SHA-256 is
`a1eb34aea33431123ae66a33a4f887ff52cae5fc778cb9e0810b35b6b41077c9`.
Copies of that hook and the opening Git config are retained as
`previous-pre-commit` and `previous-git-config` in the installed directory.
The previous local `core.hooksPath` was unset. `adoption.json` there retains
the opening state, source identities, installed result and staged selection.
The reviewed candidate directory is also retained under `.git/`.

The opening index was empty. Six owned candidate files were staged: AGENTS,
README, the two guides and the checker/test sources. Other pending mission
documentation and `Machine/TASK_TIMELINE/` were preserved. HEAD remains
`5ddad03e16d3728bae68adbe55ea2fba6e0c1fb4`. No source commit, push, hook bypass,
target repository edit, project execution or lifecycle dispatch occurred.

The adoption report and four gate logs were subsequently added to the selected
candidate so its evidence links will survive a later source commit. Other
pending mission notes remain outside this staged selection.

Authored source/document whitespace checks pass. The raw failed-run log retains
one trailing terminal space emitted by unittest; it is deliberately preserved
as evidence and excluded from the authored-content whitespace check.

This adoption qualifies the bounded development gate. The next mission feature
still needs its actual native custody/retirement implementation and its own
regressions; these 16 gate tests cannot establish that behavior.
