# Native control commands

The shared entry is `scripts/native_control.py`. It observes the installed Unix WebSocket route and qualifies only its owned disposable diagnostics. It does not attach an arbitrary existing standalone Terminal, implement PANEL, run product assignments, select unattended automatic review or retire a native executor.

## Coordinator-owned startup and use

Every Coordinator must read this runbook during `onboard`, including startup
from the desktop launcher. The human supplies the intended outcome, selected
mission/task and reserved decisions. The Coordinator owns procedure, tool setup,
binding creation, command execution, evidence and continuation; command examples
below are for the agent to execute within existing authority.

| Trigger | Coordinator action |
| --- | --- |
| Bare startup / `onboard` | Read this runbook, workspace rules and actual Git state; present the mission menu. Do not connect to receivers or create diagnostics merely to onboard. |
| Authorized mission/task connection | Choose the supported route and verify actual ownership/session/receiver/workspace/authority. For supported CodeExp2 inspection/owned diagnostics, prepare the interpreter/dependency, private binding/evidence and run shared `preflight`/exact `status`. For an external builder, automatically use its mission's supported qualified setup/status/recovery route; never substitute a CodeExp2 binding to force access. |
| Product assignment | Verify the selected mission's delivery route, fresh matching completed builder ACK and all required execution setup. This client alone cannot send product assignments or qualify unattended review. |
| Connection uncertainty | Use the same supported route to reconcile the exact owned operation without replay. Shared `reconcile` applies only to its owned diagnostic run. Preserve unknowns and block only effects dependent on missing proof. |
| Authorized diagnostic qualification | Reuse matching evidence; run `qualify` only when the task actually authorizes its disposable effects and new proof is needed. No startup model/approval probes by default. |
| Visual decision / closure | Use the linked templates, retain stable asset identities and actual owner decisions, and generate summary/continuation automatically for the applicable task. |

Do not make the human activate environments, run these commands, assemble JSON
bindings, relay messages or inspect evidence as a prerequisite to ordinary
agent-owned work. Ask only for a material reserved decision or a specific
host/provider step that the Coordinator cannot complete through authorized
supported routes. Readiness observations and historical proof do not resume
ended work or grant mission execution authority.

## Environment and binding

Use Python with the pinned dependency in [requirements-native-control.txt](../scripts/requirements-native-control.txt). A fresh authorized local environment can be prepared with:

```sh
python3 -m venv Launcher/build/native-control-venv
Launcher/build/native-control-venv/bin/python -m pip install -r scripts/requirements-native-control.txt
```

The current verification used the existing compatible `Launcher/build/thor-host-control/venv/bin/python`; it did not reinstall or change that mission's environment. Native socket access may require the host's approved route outside the execution sandbox. An attended host approval does not qualify unattended access.

For an owned disposable diagnostic, supply one private binding JSON file with these exact keys:

```json
{
  "format": "codeexp2-owned-diagnostic-binding/2",
  "repository": "/Users/boandersson/Desktop/CodeExp2",
  "socket_path": "/Users/boandersson/.codex/app-server-control/app-server-control.sock",
  "authority_reference": "Reference to the actual authorized task",
  "receiver_id": null
}
```

Binding text records intent; it cannot grant host permission. For `status`, set the actual intended receiver ID. Qualification requires `receiver_id: null` and creates its own saved diagnostic receiver in a new private scratch workspace. It never substitutes another executor for an existing agent.

For a launcher-created Desktop TUI, use only a current host-issued receipt:

```json
{
  "format": "codeexp2-desktop-session-bridge/2",
  "receipt_path": "/Users/boandersson/Desktop/CodeExp2/Launcher/build/desktop-bridges/Loki-<id>/receipt.json",
  "authority_reference": "Reference to the actual authorized task"
}
```

The v2 receipt is issued before onboarding begins. It binds the alias, workspace, bridge-created exact receiver, loopback WebSocket capability, capability-token hash, host/server/TUI PIDs plus observed process start times, and an eight-hour expiry. The broker requires its private capability token; `status` rechecks token custody, expiry, process lifetimes and exact route before it reads the receiver. A supervisor retires the server and TUI if the host ends abruptly. Clock rollback or a receipt outside the eight-hour window fails closed. Receipt validation returns stable `DESKTOP_BRIDGE_*` codes for invalid custody, endpoint, capability, process, workspace, order and expiry states.

An alias, a historical receiver/session ID, a daemon-global socket, a null receiver, `mcp__codex_tui`, queues and terminal input are never a bridge. The retired `codeexp2-native-binding/1` and bridge v1 formats fail closed with `NO_SUPPORTED_DESKTOP_SESSION_BRIDGE`.

The current route is limited to controlled same-user coordination. It does not establish hostile same-user-process identity or attachment to an arbitrary existing Desktop session. Visible Finder-to-Terminal observation is optional host evidence when the presenter permits Terminal control; it is not a bridge release gate. The canonical [Desktop session bridge repair plan](desktop-session-bridge-repair-plan.json) records that boundary.

## Read only and effectful operations

The examples below use the explicit interpreter from the environment created above. Substitute the exact authorized compatible environment path if using an existing one.

Use a new evidence directory each time for `preflight`, `status` or `qualify`. Existing run directories are never silently overwritten or replayed.

```sh
Launcher/build/native-control-venv/bin/python scripts/native_control.py preflight --binding /absolute/binding.json --evidence /absolute/new-preflight
Launcher/build/native-control-venv/bin/python scripts/native_control.py status --binding /absolute/binding.json --evidence /absolute/new-status
Launcher/build/native-control-venv/bin/python scripts/native_control.py qualify --binding /absolute/binding.json --evidence /absolute/new-diagnostic
Launcher/build/native-control-venv/bin/python scripts/native_control.py reconcile --run /absolute/existing-diagnostic
Launcher/build/native-control-venv/bin/python scripts/native_control.py summary --run /absolute/existing-diagnostic
```

`preflight`, `status`, default `reconcile` and `summary` send no work/approval/settings/lifecycle effects. They may retain local evidence. `summary` reads only local state. A loaded or idle thread never becomes eligible for product work merely from its status.

`qualify` is a fixed authorized test: ordinary touch, streamed nonce, exact scoped accept/decline, pending cancellation and a separate-process reconnect/cancel. No arbitrary shell or RPC passthrough is provided. The native `user` reviewer is selected only for that disposable test; this is not unattended builder qualification.

Explicit owned cancellation and dispatch end use:

```sh
Launcher/build/native-control-venv/bin/python scripts/native_control.py reconcile --run /absolute/existing-diagnostic --cancel
Launcher/build/native-control-venv/bin/python scripts/native_control.py end --run /absolute/existing-diagnostic
Launcher/build/native-control-venv/bin/python scripts/native_control.py end --run /absolute/existing-diagnostic --cancel
```

End records a durable client-local dispatch boundary. A send already in flight remains subject to reconciliation. The local operation lock coordinates participating clients in this CodeExp2 checkout; it is not a native fence over other apps. A changed source/backend/workspace, unknown dispatch or unresolved request blocks effectful recovery rather than triggering a replay.

## Evidence and handover

Each diagnostic retains private `run-state.json`, raw events with connection generation and producer process, exact source snapshots, loaded transport version/package-byte manifest, effective settings, per-case qualification, reconciliation and the [versioned evidence record](native-control-evidence.md). `summary` separates ended dispatch, uncertain sends, unresolved requests, publication and executor retirement. Historical reuse derives each operation from correlated native requests, replies, turn/item/dispatch identities, request resolutions and actual marker outcomes. Empty logs or saved pass flags cannot qualify a run. The private local producer/custody is trusted; hashes do not authenticate a hostile same-user producer. Current readiness must still be established.

Recovery shares one 30-second collection deadline across connect, RPC, pagination and late events; resource release follows it. Each ordinary RPC is at most 10 seconds and connection opening at most 5 seconds. Raw evidence is at most 5 MiB, frames 1 MiB and queued events 32. An exhausted limit records uncertainty, never a silent replay. Whole-run possible sends and older unresolved requests prevent confirmed cleanup; only exact observed dispatch/final-turn identities can settle relevant lost acknowledgements. Review retention is seven days and grants no deletion authority.

Use the [visual review template](templates/visual-review.md) for numbered alternatives and exact asset lineage. The [synthetic example](fixtures/visual-review/REVIEW.json) preserves option 3 plus sidebar 1 after reordering; it is not a new owner decision. Use the [closure template](templates/task-closure.md) to leave the exact continuation point and unresolved effects.

Independent source admission and mandatory staged-source regressions govern adoption through the normal commit gate. Raw evidence and the local environment remain ignored; they are not automatically published. See the [delivery record](../Missions/ControlWorkflowEvidence/20261019-session-lessons-delivery.md) for final verification, exact reviewed bytes, adoption and continuation.
