# Agent-owned native-control startup

The owner clarified on 2026-10-19: “Using the shared runbook should not be a human manual step it should be wired to agent on start up no?” Coordinator Odin owns this correction, actual session `01a15430-7ddb-7f60-809e-a8443e7b9e1d`.

**Implementation:** [AGENTS](../../AGENTS.md) now requires reading the [native-control runbook](../../docs/native-control.md) in full on every `onboard`, before reporting readiness. The existing launcher already supplies that request (`Launcher/CodeExp2.swift`, `initialPrompt`); no launcher or native control executable was changed. The runbook is an agent operating instruction, and README plus the workspace handover now state the owner of its routine work explicitly.

```text
Desktop launch / onboard
          |
          v
Coordinator reads common rules + runbook
          |
          v
Mission menu (no connection or diagnostics)
          |
     User authorizes mission/task connection
          |
          v
Coordinator prepares environment, binding and evidence
          |
          v
Preflight + exact status -> supported mission setup / fresh ACK
          |
          v
Applicable recovery, visual review and closure by Coordinator
```

The human supplies mission/outcome and reserved decisions. Routine environment setup, JSON bindings, shell commands, evidence handling and agent-message relay are Coordinator work. This is automatic use through the agent's loaded instructions, not a new background service or full mission runner. Bare onboarding cannot select a mission, contact a receiver, run effectful qualification or resume ended work. The existing supported delivery and execution-setup requirements still apply before product assignments; the diagnostic client is not presented as a product transport. Independent review found and corrected an overly general route instruction: shared commands apply only within supported CodeExp2 inspection/owned diagnostics, while an external builder uses its mission's qualified route. Shared bindings and executable scope were not expanded.

## Evidence and adoption

Candidate/source snapshots, diff and observed Git state are retained privately under `Launcher/build/odin-startup-wiring-6swoud47/`. Final exact source/policy snapshot: `revision-2/SOURCE-MANIFEST.json`, SHA256 `5458451b3d8e1e359229f9383a692c510731ec7934fe07488a597e2f98861492`.

| Reviewed input | SHA256 |
| --- | --- |
| AGENTS.md | `6f10355195dc77a2a2cd901b09d1003bb006b4a2b2645dae011406c5f8c9703b` |
| Candidate policy | `10ab96848bee7374f4471c6d24548405abf94f918e122223c45362831d0ef30b` |
| Candidate bootstrap | `a30cc3127db4bc23db1f0e2f85c2171f32ad18516dfa732ff64c6526872377a3` |

Independent reviewer `/root/native_control_review` returned final **PASS**, no remaining findings. Report `Launcher/build/odin-startup-wiring-6swoud47/revision-2/independent/REPORT.json`, SHA256 `af25e25799d0102e4a32b2b29187f96603b9a7f2aba6cc2ff4d4756d8ee90a3a`. The full report was collected and hash-checked. The candidate staged documentation gate passed. The reviewed instruction pin and matching bootstrap policy digest are now adopted; every executable/data pin, other instruction/deletion requirement, mandatory test ID and trusted verifier remain unchanged. Previous hook/policy/verifier and unchanged configuration are preserved in `/Users/boandersson/Desktop/CodeExp2/.git/codeexp2-startup-instruction-adoption-f0uozme7`. Receipt ADOPTION.json SHA256 `5fba309935bcc2a900835f41c9c4d07c2134c1d9506b180e4182717d034daa49`, mirrored under the private evidence root. Normal hooks remain enabled.

No new native probe or mission effect is needed to validate this instruction change. The preceding six-operation proof remains bound to unchanged executable bytes, not a demonstration of a new startup run. Validation covers the existing launcher-to-onboard instruction path, instruction consistency, exact reviewed bytes, relative links and whitespace. No unattended execution or guaranteed model compliance is inferred from a written rule.

**Done:** agent-owned startup loading and route-aware operating instructions implemented, independently reviewed and adopted; source-chain, link, whitespace and staged documentation checks passed. **Remains:** no human manual runbook step and no new runtime behavior to implement in this correction. **Next:** future Coordinators load and carry out the applicable procedure within the authorized workflow. PANEL remains owner-ended; unrelated mission state is excluded. The local source checkpoint uses the installed normal hook; identify it with `git log -1 -- AGENTS.md`. No push is requested.
