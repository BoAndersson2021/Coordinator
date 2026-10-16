# Work-view corrected fixture V2

Read REVIEW_BRIEF.md for the original scope. Review exact REVIEW_MANIFEST_V2.json pins read-only; no imports/execution/tests, edits, sends, lifecycle or adoption. Return exact-manifest PASS/REJECT with blockers.

The V1 candidate is frozen. Builder tests caught a fixture bug: unresolved /var TemporaryDirectory alias was inserted as machine_root, while Ledger canonicalizes /private/var, so integrity correctly rejected HTTP snapshot with503. V2 differs in exactly one source line: mandatory test fixture root = Path(folder).resolve(). Production source is identical to V1. V1_TEST_FAILURE.log retains the actual failed test.

Core shared projection, CLI report compatibility, safe HTTP fields, original evidence time, unconditional workflow denial and no-effects scope are unchanged. Existing installed checker remains unchanged and requires the enhanced mandatory comparison test to actually succeed. Full V2 suite expected114; actual staged commit proofs and service API/CLI equality follow separately. No installation or running-service changes until independent exact-source PASS.
