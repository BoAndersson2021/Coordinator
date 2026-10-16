# Studio Capability System v0.1

Independent inert extension for frozen Agentic Game Studio v0.2. Requires Python 3.9+ and PyYAML for validation. No installation effects, network calls, or agent execution.

Run `python validation/validate.py` from the package root; run `python -m unittest discover -s validation/tests -v`. Validator checks file inventory and static safety contracts.

The extension declares sixteen capabilities, twelve contracts, five workflows, registries for laws/rules/tools, compatibility and acceptance records. Tool implementations are intentionally unbound. Static acceptance is not operational qualification. No baseline files are changed.
