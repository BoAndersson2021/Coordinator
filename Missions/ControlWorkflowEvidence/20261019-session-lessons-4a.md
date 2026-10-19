# Stage 4a evidence foundation completion

**PASS for definition and fixture delivery, 2026-10-19.** Coordinator Odin completed the next stage of the approved [build chain](../../docs/codeexp2-session-lessons-build-plan.md), under the owner's “OK execute next” instruction. This is CodeExp2 workspace maintenance; PANEL remains owner-ended.

The [version 1 format](../../docs/native-control-evidence.md) defines the record fields, null explanations, scope and identity bindings, initial resource limits, private evidence handling and operation-specific inputs for later qualification. It distinguishes recorded observations, collection completeness, unresolved effects and owner acceptance. A fixture result never qualifies native behavior.

| Acceptance criterion | Evidence | Result |
| --- | --- | --- |
| Minimal record and limits defined | One documented JSON format, explicit initial budgets and rejection behavior; no service, registry or schema dependency added. | PASS |
| Distinct passing, failing, unknown, unrun and incomplete records | [21 self-contained synthetic fixture records](../../docs/fixtures/native-control-evidence-v1/cases.json), each with its expected interpretation. | PASS |
| Owner acceptance kept separate | Synthetic accepted visual scope remains a separate field and grants no native qualification. Missing decision reference is rejected. | PASS |
| Missing fields cannot preserve an embedded pass | Cases reject a missing object, missing identity field, unexplained null and forged qualification shortcut. | PASS |
| Artifact claims stay within configured scope | Traversal, wrong root, missing file, changed hash and wrong-worktree cases checked. Two isolated filesystem checks reject an escaping symlink and prevent a directory from counting as artifact bytes. | PASS |
| Checked definition and fixture consistency | All 23 content/filesystem checks passed. | PASS |

Fixture bytes are synthetic and nonsecret. The [sample artifact](../../docs/fixtures/native-control-evidence-v1/sample-evidence.txt) has SHA256 `458085d76c891327b50390b8e3e082e5d2853e1adffe961c801ebe16240fb6b8`. The format definition SHA256 is `904f9f8c2b6fd22610b1fd8d17750bd0dd3d16ea8045e3742934db66331fc968`; the fixture bundle SHA256 is `1b669673abcd025efca6a1da5cc15b45021e4245c47522bf60938893ef5f203e`.

The local [checkpoint](../../Launcher/build/odin-chain-4a-20261019-phc6q9wv/FOUNDATION.json), [check results](../../Launcher/build/odin-chain-4a-20261019-phc6q9wv/CHECKS.json) and [manifest](../../Launcher/build/odin-chain-4a-20261019-phc6q9wv/MANIFEST.json) retain source identities and the one-shot checker in ignored private storage. The checkpoint SHA256 is `765f69521f7b55c3c29dba3cded7fad31593113573bb819e3b8e2095fb42075e`. The checker validates this document's fixture interpretation; it is not the planned shared runtime parser, qualifier or mandatory staged regression suite.

**Ownership:** Coordinator Odin maintained the 4a documentation and fixtures. No builder or reviewer was launched or contacted. A point 2 code executor is not yet assigned; its scoped ownership must be established before coordinated implementation. This record is Coordinator verification, not independent review or a new owner acceptance decision.

**Remaining boundary:** the shared client, live enforcement, receiver setup, recovery and runtime qualification are not built. Data/executable publication still needs the normal independent exact-byte inventory/adoption and mandatory staged checks. No commit, push, gate change, native call or target mission work occurred in this stage. The earlier preflight remains dated evidence; it was not rerun for these document/data changes.

**Next:** establish point 2's implementation owner and build the reusable read-only `preflight` entry using this format and the already verified transport route. Point 5's visual-review template is independently eligible after 4a; full live closure remains dependent on 4b.
