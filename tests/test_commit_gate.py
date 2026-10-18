"""Real disposable Git commits through the staged-development gate.

Fixtures use a tiny separately pinned test suite, avoiding recursive execution
of this integration suite. No live repository, remote or runtime is modified.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
