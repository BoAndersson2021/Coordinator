"""Real disposable Git commits through the staged-development gate.

Fixtures use a tiny separately pinned test suite, avoiding recursive execution
of this integration suite. No live repository, remote or runtime is modified.
"""
import hashlib
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / 'scripts/check_staged.py'
spec = importlib.util.spec_from_file_location('candidate_commit_checker', CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
FIXTURE_TEST = '''import unittest
class CommitGateTests(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(2 + 2, 4)
'''


class CommitGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codeexp2-gate-case-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(('GIT_', 'PYTHON'))}
        self.env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
        # Configuration isolation applies to setup Git only; it is not passed
        # as a redirected hook input during the commits being tested.
        self.git('init', '-q')
        for key, value in [('user.name', 'Gate Fixture'), ('user.email', 'fixture@invalid'),
                           ('commit.gpgsign', 'false'), ('core.autocrlf', 'false')]:
            self.git('config', key, value)
        self.hooks = self.root / '.git/hooks'
        self.git('config', 'core.hooksPath', str(self.hooks))
        self.write('README.md', 'Fixture baseline.\n')
        self.write('tool.py', 'VALUE = 1\n')
        self.write(checker.TEST_PATH, FIXTURE_TEST)
        self.adopt()
        self.git('add', '--', 'README.md')
        self.assertEqual(self.commit().returncode, 0)

    def git(self, *args, check=True, env=None):
        return subprocess.run(['/usr/bin/git', '-C', str(self.root), *args],
                              env=env or self.env, capture_output=True, timeout=20,
                              check=check)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def adopt(self, tests=FIXTURE_TEST, mandatory=None, instructions=None,
              deletions=(), extra_files=()):
        """Simulate reviewed pins inside this disposable repository only."""
        code = self.root / 'tool.py'
        policy = {'version': 1, 'files': {
            'tool.py': {'mode': '100644', 'sha256': hashlib.sha256(code.read_bytes()).hexdigest()},
            checker.TEST_PATH: {'mode': '100644', 'sha256': hashlib.sha256(tests.encode()).hexdigest()}},
            'instructions': instructions or {}, 'mandatory_tests': mandatory or [
                'test_commit_gate.CommitGateTests.test_pass']}
        for name in extra_files:
            policy['files'][name] = {
                'mode': '100644',
                'sha256': hashlib.sha256((self.root / name).read_bytes()).hexdigest()}
        policy['files'].update({name: None for name in deletions})
        payload = (json.dumps(policy, sort_keys=True, indent=2) + '\n').encode()
        source = CHECKER.read_bytes()
        (self.hooks / 'check_staged.py').write_bytes(source)
        (self.hooks / 'reviewed-policy.json').write_bytes(payload)
        hook = self.hooks / 'pre-commit'
        hook.write_bytes(checker.bootstrap(hashlib.sha256(source).hexdigest(),
                                           hashlib.sha256(payload).hexdigest()))
        hook.chmod(0o755)

    def stage_feature(self, tests=FIXTURE_TEST):
        self.write(checker.TEST_PATH, tests)
        self.adopt(tests)
        self.git('add', '--', 'tool.py', checker.TEST_PATH)

    def commit(self, env=None):
        environment = dict(env or self.env)
        environment.pop('GIT_CONFIG_GLOBAL', None)
        environment.pop('GIT_CONFIG_NOSYSTEM', None)
        return self.git('commit', '-m', 'Disposable verification', check=False, env=environment)

    def blocked(self, result, reason=None):
        self.assertNotEqual(result.returncode, 0, result.stdout.decode())
        self.assertIn(b'COMMIT BLOCKED', result.stderr)
        if reason:
            self.assertIn(reason.encode(), result.stderr)

    def test_ordinary_document_add_edit_delete_pass(self):
        for operation in ('add', 'edit', 'delete'):
            with self.subTest(operation=operation):
                if operation == 'add':
                    self.write('notes.md', 'Useful notes.\n')
                elif operation == 'edit':
                    self.write('notes.md', 'Updated notes.\n')
                else:
                    (self.root / 'notes.md').unlink()
                self.git('add', '-A', '--', 'notes.md')
                self.assertEqual(self.commit().returncode, 0)

    def test_reviewed_staged_feature_and_regressions_pass(self):
        self.stage_feature()
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertIn(b'reviewed staged development checks passed', result.stdout + result.stderr)

    def test_executable_without_staged_regressions_blocks(self):
        self.git('add', '--', 'tool.py')
        self.blocked(self.commit(), 'requires staged invariant regressions')

    def test_unreviewed_executable_and_data_paths_block(self):
        for name in ('unknown.py', 'unknown.json'):
            with self.subTest(name=name):
                self.write(name, '{}\n')
                self.git('add', '--', name)
                self.blocked(self.commit(), 'unreviewed executable/data path')
                self.git('reset', '-q', 'HEAD', '--', name)

    def test_unreviewed_source_bytes_block_before_tests(self):
        self.stage_feature()
        self.write('tool.py', 'VALUE = 2\n')
        self.git('add', '--', 'tool.py')
        self.blocked(self.commit(), 'staged development bytes require review')

    def test_failing_staged_test_hidden_by_passing_worktree_blocks(self):
        bad = FIXTURE_TEST.replace('2 + 2, 4', '2 + 2, 5')
        self.stage_feature(bad)
        self.write(checker.TEST_PATH, FIXTURE_TEST)
        self.blocked(self.commit(), 'mandatory staged regressions failed')

    def test_passing_index_ignores_unstaged_failing_replacement(self):
        self.stage_feature()
        self.write(checker.TEST_PATH, FIXTURE_TEST.replace('2 + 2, 4', '2 + 2, 5'))
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(self.git('show', 'HEAD:' + checker.TEST_PATH).stdout.decode(), FIXTURE_TEST)
        self.assertIn('2 + 2, 5', (self.root / checker.TEST_PATH).read_text())

    def test_missing_renamed_skipped_xfail_and_failing_mandatory_tests_block(self):
        versions = {
            'missing': 'import unittest\n',
            'renamed': FIXTURE_TEST.replace('test_pass', 'test_other'),
            'skipped': FIXTURE_TEST.replace('    def test_pass', '    @unittest.skip("no")\n    def test_pass'),
            'xfail': FIXTURE_TEST.replace('    def test_pass', '    @unittest.expectedFailure\n    def test_pass').replace('2 + 2, 4', '2 + 2, 5'),
            'failure': FIXTURE_TEST.replace('2 + 2, 4', '2 + 2, 5'),
        }
        for kind, tests in versions.items():
            with self.subTest(kind=kind):
                self.stage_feature(tests)
                self.blocked(self.commit(), 'mandatory staged regressions failed')

    def test_runner_early_zero_exit_and_crash_block_without_completion(self):
        for code in ('import os\nos._exit(0)\n', 'raise RuntimeError("crash")\n'):
            with self.subTest(code=code):
                self.stage_feature(code)
                self.blocked(self.commit())

    def test_instruction_change_is_separately_reviewed(self):
        self.write('AGENTS.md', 'Invented authority.\n')
        self.git('add', '--', 'AGENTS.md')
        self.blocked(self.commit(), 'instruction/invariant change requires review')

    def test_protected_deletion_requires_explicit_review(self):
        name = 'AGENTS.md'
        self.write(name, 'Keep the execution invariant.\n')
        digest = hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        self.adopt(instructions={name: digest})
        self.git('add', '--', name)
        self.assertEqual(self.commit().returncode, 0)
        (self.root / name).unlink()
        self.git('add', '-u', '--', name)
        self.blocked(self.commit(), 'instruction/invariant change requires review')
        self.adopt()
        self.blocked(self.commit(), 'instruction/invariant change requires review')
        self.adopt(instructions={name: None})
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.write(name, 'Deletion approval cannot authorize new instructions.\n')
        self.git('add', '--', name)
        self.blocked(self.commit(), 'instruction/invariant change requires review')

    def test_reviewed_code_and_data_deletions_require_staged_regressions(self):
        names = ('obsolete.py', 'legacy.json', 'bundle.tar')
        for name in names:
            self.write(name, 'Historical fixture.\n')
        self.stage_feature()
        self.adopt(extra_files=names)
        self.git('add', '--', *names)
        self.assertEqual(self.commit().returncode, 0)
        for name in names:
            (self.root / name).unlink()
        self.git('add', '-u', '--', *names)
        self.adopt()
        self.blocked(self.commit(), 'unreviewed executable/data path')
        self.adopt(deletions=names)
        self.blocked(self.commit(), 'requires staged invariant regressions')
        updated_tests = FIXTURE_TEST + '\n'
        self.write(checker.TEST_PATH, updated_tests)
        self.git('add', '--', checker.TEST_PATH)
        self.adopt(tests=updated_tests, deletions=names)
        result = self.commit()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.write('bundle.tar', 'A reviewed deletion cannot authorize replacement.\n')
        self.git('add', '--', 'bundle.tar')
        self.blocked(self.commit(), 'requires staged invariant regressions')
        self.write(checker.TEST_PATH, updated_tests + '\n')
        self.git('add', '--', checker.TEST_PATH)
        self.adopt(tests=updated_tests + '\n', deletions=names)
        self.blocked(self.commit(), 'reviewed deletion still present')

    def test_binary_invalid_utf8_and_executable_documents_block(self):
        for content in (b'text\0binary', b'\xff', b'#!/bin/sh\nexit 0\n'):
            with self.subTest(content=content):
                (self.root / 'bad.md').write_bytes(content)
                self.git('add', '--', 'bad.md')
                self.blocked(self.commit(), 'unreviewed executable/data path')

    def test_symlink_and_executable_mode_block(self):
        link = self.root / 'redirect.md'
        link.symlink_to('README.md')
        self.git('add', '--', 'redirect.md')
        self.blocked(self.commit(), 'unreviewed executable/data path')
        self.git('reset', '-q', 'HEAD', '--', 'redirect.md')
        (self.root / 'README.md').chmod(0o755)
        self.git('add', '--', 'README.md')
        self.blocked(self.commit(), 'unreviewed executable/data path')

    def test_alternate_index_and_repository_inputs_block(self):
        self.write('notes.md', 'Unrelated index remains intact.\n')
        self.git('add', '--', 'notes.md')
        index = self.root / '.git/index'
        opening = self.git('ls-files', '--stage', '-z').stdout
        alternate = self.root / '.git/alternate-index'
        shutil.copyfile(index, alternate)
        for key, value in [('GIT_INDEX_FILE', str(alternate)),
                           ('GIT_WORK_TREE', str(self.root)),
                           ('GIT_OBJECT_DIRECTORY', str(self.root / '.git/objects')),
                           ('GIT_CONFIG_SYSTEM', '/dev/null'),
                           ('GIT_REPLACE_REF_BASE', 'refs/alternate/')]:
            with self.subTest(key=key):
                env = dict(self.env, **{key: value})
                self.blocked(self.commit(env), 'redirected Git input')
                self.assertEqual(self.git('ls-files', '--stage', '-z').stdout, opening)

    def test_missing_or_modified_trusted_inputs_block(self):
        for filename in ('check_staged.py', 'reviewed-policy.json'):
            path = self.hooks / filename
            original = path.read_bytes()
            for mutation in ('missing', 'modified'):
                with self.subTest(filename=filename, mutation=mutation):
                    if mutation == 'missing':
                        path.unlink()
                    else:
                        path.write_bytes(original + b'\n')
                    self.write('notes.md', 'Notes.\n')
                    self.git('add', '--', 'notes.md')
                    self.blocked(self.commit())
                    path.write_bytes(original)

    def test_unresolved_index_blocks(self):
        base = self.git('rev-parse', 'HEAD:README.md').stdout.decode().strip()
        records = ('0 ' + '0' * 40 + '\tREADME.md\n'
                   + ''.join('100644 ' + base + ' ' + str(stage) + '\tREADME.md\n'
                             for stage in (1, 2, 3)))
        subprocess.run(['/usr/bin/git', '-C', str(self.root), 'update-index', '--index-info'],
                       input=records.encode(), env=self.env, capture_output=True,
                       timeout=10, check=True)
        result = subprocess.run([str(self.hooks / 'pre-commit')], cwd=self.root,
                                env={k: v for k, v in self.env.items() if not k.startswith('GIT_')},
                                capture_output=True, timeout=10)
        self.blocked(result, 'unresolved staged entries')
        self.assertNotEqual(self.commit().returncode, 0)

    def test_failed_commit_preserves_head_index_and_unrelated_dirty_bytes(self):
        self.write('old-user-work.md', 'Leave this exact user content.\n')
        self.git('add', '--', 'old-user-work.md')
        self.write('README.md', 'Unstaged user edit.\n')
        self.git('add', '--', 'tool.py')
        head = self.git('rev-parse', 'HEAD').stdout
        index = self.git('ls-files', '--stage', '-z').stdout
        self.blocked(self.commit())
        self.assertEqual(self.git('rev-parse', 'HEAD').stdout, head)
        self.assertEqual(self.git('ls-files', '--stage', '-z').stdout, index)
        self.assertEqual((self.root / 'README.md').read_text(), 'Unstaged user edit.\n')
        self.assertEqual((self.root / 'old-user-work.md').read_text(), 'Leave this exact user content.\n')

    def launcher_python(self):
        """Use a verified 3.11+ interpreter for the launcher's stdlib TOML parser."""
        for executable in dict.fromkeys((sys.executable, shutil.which('python3'))):
            if not executable:
                continue
            probe = subprocess.run([executable, '-I', '-S', '-B', '-c',
                                    'import sys, tomllib; assert sys.version_info >= (3, 11)'],
                                   capture_output=True, timeout=10)
            if probe.returncode == 0:
                return executable
        self.fail('Launcher build and bridge checks require Python 3.11+ with tomllib')

    def test_launcher_panel_bridge_regressions(self):
        """Compile staged bridge bytes and require all three native no-model checks."""
        runner = r'''
import importlib.util, json, sys, unittest
from pathlib import Path
source = Path(sys.argv[1]) / 'Launcher/test_panel_bridge.py'
spec = importlib.util.spec_from_file_location('test_panel_bridge', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
expected = {
    'test_panel_bridge.PanelBridgeTests.test_projection_round_trips_exact_canonical_profile',
    'test_panel_bridge.PanelBridgeTests.test_native_profile_identity_and_shared_claim_release',
    'test_panel_bridge.PanelBridgeTests.test_stale_projection_and_terminal_boundaries_fail_before_launch',
}
class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = set()
    def addSuccess(self, test):
        self.successes.add(test.id())
        super().addSuccess(test)
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(
    unittest.defaultTestLoader.loadTestsFromModule(module))
passed = (result.wasSuccessful() and not result.skipped
          and not result.expectedFailures and result.successes == expected
          and result.testsRun == len(expected))
print(json.dumps({'panel_bridge_complete': passed, 'tests_run': result.testsRun,
                  'successes': sorted(result.successes)}))
sys.exit(0 if passed else 3)
'''
        result = subprocess.run([self.launcher_python(), '-I', '-S', '-B', '-c', runner, str(ROOT)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertIs(report['panel_bridge_complete'], True)
        self.assertEqual(report['tests_run'], 3)

    def test_launcher_native_build_preflight_and_terminal_boundary(self):
        """Build exact snapshot sources, verify signing and reject non-TTY launch."""
        with tempfile.TemporaryDirectory(prefix='codeexp2-native-build-') as directory:
            launcher = Path(directory) / 'Launcher'
            launcher.mkdir()
            for name in ('CodeExp2.swift', 'Icon.swift', 'build.py', 'Start CodeExp2.command',
                         'valhalla.config.toml', 'install_valhalla.py', 'valhall-icon.png'):
                shutil.copyfile(ROOT / 'Launcher' / name, launcher / name)
            result = subprocess.run([self.launcher_python(), '-B', str(launcher / 'build.py')],
                                    capture_output=True, text=True, timeout=60,
                                    env={k: v for k, v in self.env.items()
                                         if not k.startswith('GIT_')})
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for message in ('missing workspace', 'missing onboarding instructions',
                            'non-executable Codex', 'redirected workspace'):
                self.assertIn('PASS: ' + message, result.stdout)
            app = launcher / 'build/CodeExp2.app'
            plist = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
            self.assertEqual(plist['CFBundleExecutable'], 'CodeExp2')
            self.assertEqual(plist['CFBundleName'], 'Valhall')
            self.assertEqual(plist['CFBundleDisplayName'], 'Valhall')
            self.assertEqual(plist['CFBundleIdentifier'], 'local.codeexp2.coordinator-launcher')
            resources = app / 'Contents/Resources'
            self.assertEqual((resources / plist['CFBundleIconFile']).read_bytes()[:4], b'icns')
            bridge = resources / 'Start CodeExp2.command'
            self.assertTrue(os.access(bridge, os.X_OK))
            self.assertEqual(bridge.read_bytes(), (ROOT / 'Launcher/Start CodeExp2.command').read_bytes())
            self.assertEqual((resources / 'valhalla.config.toml').read_bytes(),
                             (ROOT / 'Launcher/valhalla.config.toml').read_bytes())
            self.verify_valhalla_installation(launcher)
            executable = app / 'Contents/MacOS/CodeExp2'
            self.verify_launcher_claims(executable)
            for args, reason in ((['--terminal'], 'interactive Terminal session'),
                                 (['--unknown'], 'Supported options')):
                rejected = subprocess.run([str(executable), *args], stdin=subprocess.DEVNULL,
                                          capture_output=True, text=True, timeout=10)
                self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
                self.assertIn(reason, rejected.stderr)

    def verify_launcher_claims(self, executable):
        """Race real processes through exec, normal exit and SIGKILL; no model tasks."""
        claim_root = self.root / 'instance-claims'
        processes = []
        inherited_children = []

        def start(with_child=False):
            mode = '--claim-probe-with-child' if with_child else '--claim-probe'
            process = subprocess.Popen([str(executable), mode, str(claim_root)],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            processes.append(process)
            return process

        def receipt(process):
            ready, _, _ = select.select([process.stdout], [], [], 5)
            self.assertTrue(ready, 'claim probe did not reply')
            line = process.stdout.readline()
            self.assertTrue(line, 'claim probe exited without a receipt')
            result = json.loads(line)
            self.assertEqual(result['pid'], process.pid)
            return result

        try:
            # Start together before collecting: a check-then-write allocator races.
            batch = [start() for _ in range(13)]
            reports = [receipt(process) for process in batch]
            self.assertEqual(len({r['alias'] for r in reports}), 13)
            self.assertEqual(len({r['color'] for r in reports}), 13)
            self.assertIn('Odin-2', {r['alias'] for r in reports})
            for report in reports:
                self.assertIn('\x1b]0;CodeExp2 — ' + report['alias'] + '\x07', report['appearance'])
                self.assertIn('\x1b]11;' + report['color'] + '\x07', report['appearance'])
                arguments = report['arguments']
                self.assertEqual(arguments[1:5], ['--profile', 'valhalla', '--config', 'tui.terminal_title=[]'])
                self.assertEqual(len(arguments), 6)
                self.assertTrue(arguments[5].startswith('onboard\n'))
                self.assertIn('Launcher-assigned instance alias: ' + report['alias'], arguments[5])
            owner = batch[next(i for i, r in enumerate(reports) if r['alias'] == 'Odin')]
            owner.stdin.close()
            self.assertEqual(owner.wait(timeout=5), 0)
            replacement = start()
            self.assertEqual(receipt(replacement)['alias'], 'Odin')
            replacement.kill()
            replacement.wait(timeout=5)
            recovered = start()
            self.assertEqual(receipt(recovered)['alias'], 'Odin')
            self.assertTrue((claim_root / '0.lock').is_file(), 'claim files must remain')
            recovered.stdin.close()
            self.assertEqual(recovered.wait(timeout=5), 0)
            parent = start(with_child=True)
            parent_report = receipt(parent)
            self.assertEqual(parent_report['alias'], 'Odin')
            descendant = parent_report['child_pid']
            inherited_children.append(descendant)
            self.assertGreater(descendant, 0)
            child_files = subprocess.run(['/usr/sbin/lsof', '-a', '-p', str(descendant),
                                          '-d', str(parent_report['fd']), '-Fn'],
                                         capture_output=True, text=True, timeout=10)
            self.assertEqual(child_files.returncode, 0, child_files.stderr)
            self.assertIn(str(claim_root / '0.lock'), child_files.stdout)
            parent.kill()
            parent.wait(timeout=5)
            os.kill(descendant, 0)  # Child deliberately stays alive with inherited fd.
            new_owner = start()
            self.assertEqual(receipt(new_owner)['alias'], 'Odin')
            # Fail visibly on redirected claim files; never lock an unrelated file.
            bad = self.root / 'redirected-claims'
            bad.mkdir()
            (bad / '0.lock').symlink_to(self.root / 'README.md')
            refused = subprocess.run([str(executable), '--claim-probe', str(bad)],
                                     input=b'', capture_output=True, timeout=5)
            self.assertEqual(refused.returncode, 1)
            self.assertIn(b'Cannot open instance claim', refused.stderr)
        finally:
            for child in inherited_children:
                try:
                    os.kill(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                for stream in (process.stdin, process.stdout, process.stderr):
                    if stream and not stream.closed:
                        stream.close()
        occupied = self.root / 'occupied-claims'
        occupied.mkdir()
        handles = []
        try:
            for index in range(192):
                handle = (occupied / f'{index}.lock').open('w+')
                handles.append(handle)
                fcntl.lockf(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            refused = subprocess.run([str(executable), '--claim-probe', str(occupied)],
                                     input=b'', capture_output=True, timeout=5)
            self.assertEqual(refused.returncode, 1)
            self.assertIn(b'All 192 CodeExp2 name/color pairs are occupied', refused.stderr)
        finally:
            for handle in handles:
                handle.close()

    def verify_valhalla_installation(self, launcher):
        config_home = self.root / 'disposable-codex-home'
        config_home.mkdir()
        global_config = config_home / 'config.toml'
        global_config.write_text('model = "leave-this-owner-value"\n')
        profile = config_home / 'valhalla.config.toml'
        profile.write_text('previous owner profile\n')
        installer = launcher / 'install_valhalla.py'
        command = [sys.executable, '-B', str(installer), '--config-home', str(config_home)]
        installed = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        self.assertEqual(global_config.read_text(), 'model = "leave-this-owner-value"\n')
        self.assertEqual(profile.read_bytes(), (launcher / 'valhalla.config.toml').read_bytes())
        backups = list((launcher / 'build/valhalla-profile-backups').glob('*/valhalla.config.toml'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'previous owner profile\n')
        repeated = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertIn('already matches', repeated.stdout)
        profile.unlink()
        profile.symlink_to(global_config)
        refused = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn('Refusing redirected', refused.stderr)
        self.assertEqual(global_config.read_text(), 'model = "leave-this-owner-value"\n')

    def test_launcher_terminal_bridge_preserves_paths_and_arguments(self):
        """The shipped bridge must exec its sibling binary with exactly --terminal."""
        contents = self.root / "a space and 'quote $ literal.app/Contents"
        resources = contents / 'Resources'
        macos = contents / 'MacOS'
        resources.mkdir(parents=True)
        macos.mkdir()
        bridge = resources / 'Start CodeExp2.command'
        shutil.copyfile(ROOT / 'Launcher/Start CodeExp2.command', bridge)
        executable = macos / 'CodeExp2'
        executable.write_text('#!/bin/zsh\nprintf "argc:%s\\narg:%s\\n" "$#" "$1"\n')
        executable.chmod(0o755)
        result = subprocess.run(['/bin/zsh', str(bridge)], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, 'argc:1\narg:--terminal\n')
        executable.unlink()
        missing = subprocess.run(['/bin/zsh', str(bridge)], cwd=self.root,
                                 capture_output=True, text=True, timeout=10)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn('no such file or directory', missing.stderr)


    def test_ballistics_host_control_offline_regressions(self):
        """Exercise staged host guards with transport forbidden, without native effects."""
        host = ROOT / 'Missions/BallisticsExperimental/host-control-20261019'
        runner = r'''
import json, sys, types, unittest
# Offline tests exercise real client logic with explicit fake clients. Import
# transport is unavailable under -S; forbid it rather than needing a live venv.
transport = types.ModuleType('websockets.sync.client')
def forbidden_transport(*args, **kwargs):
    raise AssertionError('Native transport is forbidden in staged regressions')
transport.unix_connect = forbidden_transport
sys.modules['websockets'] = types.ModuleType('websockets')
sys.modules['websockets.sync'] = types.ModuleType('websockets.sync')
sys.modules['websockets.sync.client'] = transport
sys.path.insert(0, sys.argv[1])
expected = {
    'test_host_control.ApprovalScopeTests.test_exact_command_and_native_shell_wrapper',
    'test_host_control.ApprovalScopeTests.test_shell_command_separators_never_count_as_argument_whitespace',
    'test_host_control.ApprovalScopeTests.test_other_effects_and_malformed_commands_refuse',
    'test_host_control.ApprovalScopeTests.test_unrelated_thread_and_unlisted_mutation_rejected_before_send',
    'test_host_control.RetirementTests.test_lost_start_response_is_reconciled_without_redispatch',
    'test_host_control.RetirementTests.test_interrupt_ack_without_final_state_is_not_cleanup',
    'test_host_control.RetirementTests.test_remaining_process_prevents_cleanup_claim',
    'test_host_control.RetirementTests.test_unknown_or_mismatched_start_does_not_interrupt_other_work',
    'test_host_control.RetirementTests.test_identical_payload_from_a_different_dispatch_is_not_owned',
    'test_host_control.SettingsTests.test_restoration_reads_actual_settings_and_preserves_permissions',
    'test_host_control.SettingsTests.test_finalizer_can_reconcile_lost_restoration_response',
    'test_host_control.SettingsTests.test_intervening_unowned_setting_change_is_preserved',
}
class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = set()
    def addSuccess(self, test):
        self.successes.add(test.id())
        super().addSuccess(test)
suite = unittest.defaultTestLoader.discover(sys.argv[1], pattern='test_host_control.py')
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
passed = (result.wasSuccessful() and not result.skipped
          and not result.expectedFailures and result.successes == expected
          and result.testsRun == 12)
print(json.dumps({'host_regressions_complete': passed,
                  'tests_run': result.testsRun, 'successes': sorted(result.successes)}))
sys.exit(0 if passed else 3)
'''
        result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', runner, str(host)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertIs(report['host_regressions_complete'], True)
        self.assertEqual(report['tests_run'], 12)
        self.assertEqual(len(report['successes']), 12)


    def test_native_control_offline_regressions(self):
        """Require every exact shared-client regression with native transport forbidden."""
        runner = "import json, sys, types, unittest\ntransport = types.ModuleType('websockets.sync.client')\ndef forbidden(*args, **kwargs):\n    raise AssertionError('Native transport forbidden in staged checks')\ntransport.unix_connect = forbidden\nsys.modules['websockets'] = types.ModuleType('websockets')\nsys.modules['websockets.sync'] = types.ModuleType('websockets.sync')\nsys.modules['websockets.sync.client'] = transport\nexpected = set(['test_native_control.NativeControlTests.test_all_foundation_fixtures_and_owner_acceptance_separation', 'test_native_control.NativeControlTests.test_changed_endpoint_rejected_before_initialize', 'test_native_control.NativeControlTests.test_different_run_cannot_claim_same_canonical_receiver', 'test_native_control.NativeControlTests.test_end_is_durable_and_cannot_be_overridden_by_stale_client', 'test_native_control.NativeControlTests.test_end_persistence_failure_blocks_the_receiving_client', 'test_native_control.NativeControlTests.test_exact_action_rejects_shell_injection_and_permission_amendments', 'test_native_control.NativeControlTests.test_handshake_refusal_and_timeout_leave_no_work_effect', 'test_native_control.NativeControlTests.test_incompatible_initialize_closes_owned_resources', 'test_native_control.NativeControlTests.test_incomplete_or_repeated_history_never_proves_unique_dispatch', 'test_native_control.NativeControlTests.test_late_resolution_after_completion_is_collected', 'test_native_control.NativeControlTests.test_loaded_transport_version_path_and_bytes_are_measured', 'test_native_control.NativeControlTests.test_lost_ack_intent_blocks_retry_and_disk_failure_sends_nothing', 'test_native_control.NativeControlTests.test_lost_start_reconciles_by_unique_identity_not_text', 'test_native_control.NativeControlTests.test_malformed_oversized_and_queue_overflow_fail_visibly', 'test_native_control.NativeControlTests.test_metadata_status_does_not_become_dispatch_eligibility', 'test_native_control.NativeControlTests.test_native_transcript_requires_correlated_receipts_and_separate_process', 'test_native_control.NativeControlTests.test_qualification_reuse_checks_source_settings_receiver_and_artifacts', 'test_native_control.NativeControlTests.test_readonly_wire_cannot_bypass_scope_or_receiver_checks', 'test_native_control.NativeControlTests.test_recovery_backend_swap_blocks_effect_and_records_failed_attempt', 'test_native_control.NativeControlTests.test_recovery_deadline_is_shared_by_rpc_pages_and_collection', 'test_native_control.NativeControlTests.test_replayed_request_handled_once_and_ambiguous_round_refuses', 'test_native_control.NativeControlTests.test_safe_artifact_reader_rejects_symlink_fifo_and_oversize', 'test_native_control.NativeControlTests.test_source_changed_recovery_has_no_native_effect', 'test_native_control.NativeControlTests.test_strict_json_rejects_duplicate_keys_and_nonfinite_values', 'test_native_control.NativeControlTests.test_summary_is_observation_only_and_preserves_partial_states', 'test_native_control.NativeControlTests.test_two_processes_share_operation_lock_and_send_once', 'test_native_control.NativeControlTests.test_visual_fixture_hashes_dimensions_lineage_and_reorder', 'test_native_control.NativeControlTests.test_whole_run_reconciliation_preserves_unrelated_uncertainty'])\nclass Result(unittest.TextTestResult):\n    def __init__(self,*args,**kwargs):\n        super().__init__(*args,**kwargs); self.successes=set()\n    def addSuccess(self,test):\n        self.successes.add(test.id()); super().addSuccess(test)\nsuite=unittest.defaultTestLoader.discover(sys.argv[1],pattern='test_native_control.py')\nresult=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)\npassed=result.wasSuccessful() and not result.skipped and not result.expectedFailures and result.successes==expected and result.testsRun==len(expected)\nprint(json.dumps({'native_regressions_complete':passed,'tests_run':result.testsRun,'successes':sorted(result.successes)}))\nsys.exit(0 if passed else 3)\n"
        result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', runner, str(ROOT / 'tests')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertIs(report['native_regressions_complete'], True)
        self.assertEqual(report['tests_run'], 28)


if __name__ == '__main__':
    unittest.main(verbosity=2)
