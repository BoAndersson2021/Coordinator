# Native control commands

The shared entry is `scripts/native_control.py`. It observes the installed Unix WebSocket route and qualifies only its owned disposable diagnostics. It does not attach existing standalone Terminals, implement PANEL, run product assignments, select unattended automatic review or retire a native executor.

## Environment and binding

Use Python with the pinned dependency in [requirements-native-control.txt](../scripts/requirements-native-control.txt). A fresh authorized local environment can be prepared with:

```sh
python3 -m venv Launcher/build/native-control-venv
Launcher/build/native-control-venv/bin/python -m pip install -r scripts/requirements-native-control.txt
```

The current verification used the existing compatible `Launcher/build/thor-host-control/venv/bin/python`; it did not reinstall or change that mission's environment. Native socket access may require the host's approved route outside the execution sandbox. An attended host approval does not qualify unattended access.

Supply one private binding JSON file with these exact keys:

```json
{
  "format": "codeexp2-native-binding/1",
  "repository": "/Users/boandersson/Desktop/CodeExp2",
  "socket_path": "/Users/boandersson/.codex/app-server-control/app-server-control.sock",
  "coordinator_session_id": "ACTUAL_OBSERVED_COORDINATOR_ID",
  "authority_reference": "Reference to the actual authorized task",
  "receiver_id": null
}
```

Binding text records intent; it cannot grant host permission. For `status`, set the actual intended receiver ID. Qualification requires `receiver_id: null` and creates its own saved diagnostic receiver in a new private scratch workspace. It never substitutes another executor for an existing agent.

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
