# Ballistics host-control publication — Coordinator Thor

The owner's subsequent **“commit and push”** authorizes publishing this host
installation and its coordination checkpoint in CodeExp2. The earlier
no-publication statements in the dated installation/resume records and handover
describe their original checkpoints. Product repair and game qualification remain
unfinished; this publication does not change their state.

The published files contain the final reviewed native client, qualification
drivers, twelve offline regressions, pinned dependency, installation receipt,
source identities and test result. The commit-gate suite adds one mandatory test
that runs all twelve named host regressions from the staged snapshot. It rejects
missing, skipped, failed or incomplete tests and forbids native transport during
that check. Existing commit-gate tests and trusted verifier remain in place.

Raw native messages, retained failed versions, full session history and the local
virtual environment remain local. Review and native evidence paths in
`INSTALLATION.json` refer to retained local artifacts, including the builder's
ignored `Saved/AgentCommunication/` directory. They are not shipped evidence.
The two qualification drivers are archived one-shot procedures with fixed run
identities; the lost-start driver additionally requires its retained local probe
request. Do not treat either as an automatically runnable clean-checkout test.

**Local installation.** From CodeExp2, create the ignored environment if needed:

```sh
python3 -m venv Launcher/build/thor-host-control/venv
Launcher/build/thor-host-control/venv/bin/python -m pip install -r Missions/BallisticsExperimental/host-control-20261019/requirements.txt
```

The verified installation used Python 3.14.8 and `websockets==17.2`. The client
connects to the existing Codex 0.163.0 Unix WebSocket daemon. It is bound to the
specific Ballistics builder and repository recorded in its source. Dependency
installation does not start a daemon, reconnect an agent, widen permissions or
assign product work. Native use requires the applicable mission scope and fresh
receiver checks.

**Offline verification.** This command needs only the repository's system Python
and disposable Git fixtures; the host test forbids opening the native connection:

```sh
/usr/bin/python3 -B -m unittest discover -s tests -p test_commit_gate.py -k ballistics -v
```

The full mandatory suite also builds the desktop launcher in a disposable
directory and needs ordinary macOS build access. Publication runs through the
normal installed hook, then pushes only CodeExp2 `main` to
`https://github.com/BoAndersson2021/Coordinator.git` using an explicit refspec.
The source commit is discoverable with `git log -1 --` on this directory. A push
is verified by matching local HEAD with the actual remote `refs/heads/main`.

**Independent admission and local adoption.** The existing builder
`01a14b73-b7a5-7062-865e-ebd47b6b3ce0` independently reviewed the
Coordinator-authored publication test and exact policy/bootstrap, returning PASS
with no required fixes. The complete report is retained at
`BallisticsExperimental/Saved/AgentCommunication/THOR-PUBLISH-REVIEW-20261019-1/PUBLICATION-report.json`;
its SHA-256 is `88a73c37be004783103208e3f018d956a6bfb8491d837a46f4ef6c2aa516529e`. Every referenced evidence hash was checked.
The reviewer passed all 21 tests in 33.299 seconds; the Coordinator separately
passed all 21 in 30.252 seconds. These include the 12 host regressions.

Adoption at `2026-10-19T13:57:02.715716+00:00` preserved the prior installed gate and unchanged Git
configuration under `.git/codeexp2-host-adoption-20261019-p5lfc8mn`. The
trusted verifier is unchanged (`4f54ab68d6f7c379ea27f7359a145e3f05b93d4b48b082ffd08f5ccf04d4f286`);
the adopted policy is `78b811a3cebe3e2b02302c11e2d5e60e9f706dae21bef7767f0bbe2a1e46beb2`
and bootstrap is `cb189dd7274ad1fd7a892c61715d00c95dde052ff83925fd18bb131f87a571b8`.
All prior instruction/deletion pins and 20 mandatory tests remain. The added
inventory has exact paths, modes and hashes. A normal source commit still requires
the hook to test these staged bytes; local adoption grants no runtime authority
and does not install this gate on another checkout.
