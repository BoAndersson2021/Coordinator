# Agentic Game Studio — handoff v0.2

## Status

**Source-verified bootstrap, not an operational studio.** The package synchronizes the corpus and installation contract. Game Project Architecture remains specification v1.2. No source integration, model runtime, authority service, build farm, or release pipeline is installed by this package.

## Contents

- `corpus/`: four source documents; first three normative, `system-position.txt` contextual.
- `agentic-studio.install.yaml`: installation contract v0.2 with pinned corpus digests.
- `installer/installer.py`: offline discovery, planning, staging approval, source staging, blocked qualification.
- `tests/`: bounded installer regression tests.
- `evidence/`: release checks and inventory.

## Requirements

Python 3.9+ and PyYAML. Run from the extracted package root. No network calls are made by the installer.

## Operator workflow

```bash
python installer/installer.py discover
python installer/installer.py plan --manifest agentic-studio.install.yaml --source-dir . --plan studio-plan.json
# plan exits 2 because the operational bindings remain unresolved; inspect the JSON
python installer/installer.py approve --manifest agentic-studio.install.yaml --source-dir . --plan studio-plan.json --approval studio-approval.json --operator OPERATOR_ID
python installer/installer.py stage --manifest agentic-studio.install.yaml --source-dir . --plan studio-plan.json --approval studio-approval.json --destination ../studio-staging
python installer/installer.py qualify --manifest agentic-studio.install.yaml --source-dir . --plan studio-plan.json
```

Approval only permits exact-source staging into a new directory. It is not a cryptographically authenticated identity assertion. Protect approval files from untrusted writers. `qualify` is expected to exit 2, and all operational gates remain unverified.

## Required next boundary

Supply concrete, version-pinned implementations for the 19 unresolved bindings and the listed installation dependencies; separately specify promotion authority, crash durability, and executable qualification tests. Do not interpret staging success as installation success.

## Source precedence

The three normative corpus documents define intended contracts; the manifest governs only bootstrap installation behavior. `system-position.txt` is contextual and must not silently override normative sources. Where texts conflict, fail closed and request explicit resolution rather than infer precedence.
